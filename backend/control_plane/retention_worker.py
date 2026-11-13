"""
Automated Multi-Tenant Data & Storage Retention Worker
======================================================
Cleans up physical files (Local disk & S3/R2) and MySQL database records
when a tenant module's retention grace period expires:
1. Snapshots cross-module linkages (e.g. Tasks linked to Tickets).
2. Generates cold export archive bundle (ZIP).
3. Purges physical files from Local disk (shutil.rmtree) or S3 (prefix delete).
4. Cascades MySQL database purge to reclaim primary storage.
5. Updates RetentionEvent audit ledger.
"""

import os
import shutil
import json
import logging
import datetime
import zipfile
from typing import Dict, Any, List
from django.conf import settings
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger("control_plane.retention")


class StorageRetentionWorker:
    """
    Automated Physical & Database Storage Purge Worker.
    """

    @classmethod
    def get_storage_backend(cls) -> str:
        return getattr(settings, "STORAGE_BACKEND", "local").lower().strip()

    # ------------------------------------------------------------------------
    # 1. PHYSICAL STORAGE PURGE (LOCAL & S3 / R2)
    # ------------------------------------------------------------------------

    @classmethod
    def purge_physical_storage(cls, tenant_id: str, module_name: str) -> Dict[str, int]:
        """
        Permanently deletes physical files associated with a tenant's module.
        Works across Local filesystem and Cloud S3/R2 object storage.
        """
        backend = cls.get_storage_backend()
        reclaimed_bytes = 0
        reclaimed_files_count = 0

        # A. LOCAL STORAGE PURGE
        media_root = getattr(settings, "MEDIA_ROOT", os.path.join(settings.BASE_DIR, "media"))
        tenant_mod_dir = os.path.join(media_root, "tenants", str(tenant_id), str(module_name))

        if os.path.exists(tenant_mod_dir):
            try:
                for root, _, files in os.walk(tenant_mod_dir):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            reclaimed_bytes += os.path.getsize(fp)
                            reclaimed_files_count += 1
                        except Exception:
                            pass
                shutil.rmtree(tenant_mod_dir)
                logger.info(f"Local storage purged for {tenant_id}/{module_name}: {reclaimed_files_count} files, {reclaimed_bytes} bytes.")
            except Exception as exc:
                logger.warning(f"Error purging local storage for {tenant_id}/{module_name}: {exc}")

        # B. CLOUD S3 / R2 OBJECT STORAGE PURGE
        if backend in ("s3", "r2") and hasattr(settings, "AWS_STORAGE_BUCKET_NAME"):
            try:
                import boto3
                s3 = boto3.resource("s3")
                bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
                prefix = f"tenants/{tenant_id}/{module_name}/"

                objects_to_delete = bucket.objects.filter(Prefix=prefix)
                for obj in objects_to_delete:
                    reclaimed_bytes += obj.size or 0
                    reclaimed_files_count += 1
                objects_to_delete.delete()
                logger.info(f"Cloud S3 prefix '{prefix}' purged for tenant {tenant_id}.")
            except Exception as exc:
                logger.warning(f"Error purging S3 storage for {tenant_id}/{module_name}: {exc}")

        return {
            "reclaimed_bytes": reclaimed_bytes,
            "reclaimed_files_count": reclaimed_files_count,
        }

    # ------------------------------------------------------------------------
    # 2. COLD ARCHIVAL & EXPORT BUNDLE GENERATION
    # ------------------------------------------------------------------------

    @classmethod
    def generate_cold_archive(cls, tenant_id: str, module_name: str) -> str:
        """
        Compresses database records and metadata into a cold archive ZIP
        before MySQL deletion, providing a customer export bundle.
        """
        archive_dir = os.path.join(
            getattr(settings, "MEDIA_ROOT", os.path.join(settings.BASE_DIR, "media")),
            "archives", "tenants", str(tenant_id)
        )
        os.makedirs(archive_dir, exist_ok=True)
        timestamp_str = timezone.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"{tenant_id}_{module_name}_archive_{timestamp_str}.zip"
        zip_path = os.path.join(archive_dir, zip_filename)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            meta = {
                "tenant_id": tenant_id,
                "module_name": module_name,
                "archived_at": timezone.now().isoformat(),
                "retention_policy": "90_day_purge",
            }
            zf.writestr("manifest.json", json.dumps(meta, indent=2))

            # Export module specific rows if tickets
            if module_name == "tickets":
                try:
                    from tickets.models import Ticket, TicketAttachment
                    tickets_data = list(Ticket.objects.values())
                    zf.writestr("tickets.json", json.dumps(tickets_data, indent=2, default=str))
                except Exception:
                    pass

        return f"/media/archives/tenants/{tenant_id}/{zip_filename}"

    # ------------------------------------------------------------------------
    # 3. DATABASE CASCADE PURGE & TASK SNAPSHOTTING
    # ------------------------------------------------------------------------

    @classmethod
    def purge_database_records(cls, tenant_id: str, module_name: str) -> int:
        """
        Purges MySQL rows for the degraded module and ensures any linked Tasks
        have permanent immutable ticket snapshots.
        """
        purged_rows = 0

        if module_name == "tickets":
            try:
                from tickets.models import (
                    Ticket, TicketAttachment, TicketComment,
                    TicketActivityLog, TicketParticipant, TicketStatusHistory
                )
                from tasks.models import Task

                # Step A: Backfill snapshots for all tasks linked to tickets
                linked_tasks = Task.objects.filter(linkedTicketId__isnull=False).select_related("linkedTicketId")
                for tsk in linked_tasks:
                    if tsk.linkedTicketId and not tsk.ticket_snapshot:
                        tck = tsk.linkedTicketId
                        tsk.ticket_snapshot = {
                            "ticket_id": tck.ticket_id,
                            "title": tck.title,
                            "priority": getattr(tck, "priority", "Medium"),
                            "ticket_status": getattr(tck, "ticket_status", "Open"),
                            "archived_at": timezone.now().isoformat(),
                        }
                        tsk.save(update_fields=["ticket_snapshot"])

                # Step B: Cascading delete of ticket sub-entities
                purged_rows += TicketAttachment.objects.all().delete()[0]
                purged_rows += TicketComment.objects.all().delete()[0]
                purged_rows += TicketActivityLog.objects.all().delete()[0]
                purged_rows += TicketParticipant.objects.all().delete()[0]
                purged_rows += TicketStatusHistory.objects.all().delete()[0]

                # Step C: Delete ticket rows (ForeignKey turns NULL on Task with SET_NULL)
                purged_rows += Ticket.objects.all().delete()[0]

            except Exception as exc:
                logger.warning(f"Error purging database records for {tenant_id}/{module_name}: {exc}")

        return purged_rows

    # ------------------------------------------------------------------------
    # 4. ORCHESTRATE PURGE EVENT
    # ------------------------------------------------------------------------

    @classmethod
    def execute_purge_event(cls, event: Any) -> Dict[str, Any]:
        """
        Executes complete end-to-end purge for a RetentionEvent:
        Archival -> Physical Storage Purge -> DB Purge -> Update Event.
        """
        tenant_id = event.tenant.tenant_id if event.tenant else "default"
        module_name = event.module_id

        logger.info(f"Initiating purge event #{event.id} for tenant {tenant_id}, module {module_name}")

        # 1. Cold Archive
        archive_url = cls.generate_cold_archive(tenant_id, module_name)

        # 2. Physical Storage Purge
        storage_result = cls.purge_physical_storage(tenant_id, module_name)

        # 3. MySQL Database Purge
        db_rows = cls.purge_database_records(tenant_id, module_name)

        # 4. Update Event Record
        event.status = "Purged"
        event.archive_file_url = archive_url
        event.reclaimed_bytes = storage_result["reclaimed_bytes"]
        event.reclaimed_files_count = storage_result["reclaimed_files_count"]
        event.reclaimed_db_rows_count = db_rows
        event.purged_at = timezone.now()
        event.save()

        logger.info(f"Purge event #{event.id} completed. Reclaimed {event.reclaimed_bytes} bytes, {db_rows} DB rows.")

        return {
            "status": "Purged",
            "archive_file_url": archive_url,
            "reclaimed_bytes": event.reclaimed_bytes,
            "reclaimed_files_count": event.reclaimed_files_count,
            "reclaimed_db_rows_count": db_rows,
        }

    # ------------------------------------------------------------------------
    # 5. AUTOMATED DAILY RETENTION CYCLE
    # ------------------------------------------------------------------------

    @classmethod
    def run_daily_retention_cycle(cls) -> Dict[str, int]:
        """
        Automated Daily Engine:
        1. Detects degraded modules on tenants and schedules RetentionEvent.
        2. Executes purges for all events whose grace period has expired.
        """
        from control_plane.models import Tenant, RetentionEvent, RetentionPolicy

        processed_purges = 0
        scheduled_events = 0
        now = timezone.now()

        # Step A: Get default policy (e.g. 90 days grace period)
        policy = RetentionPolicy.objects.filter(is_active=True).first()
        grace_days = policy.grace_period_days if policy else 90

        # Step B: Scan tenants for degraded modules
        all_modules = {"attendance", "payroll", "crm", "billing", "tasks", "tickets", "assets", "recruitment", "hr", "feed"}
        tenants = Tenant.objects.filter(status="Active")

        for t in tenants:
            enabled = set(t.enabled_modules or [])
            missing_modules = all_modules - enabled

            for mod in missing_modules:
                # Check if an active retention event already exists
                existing = RetentionEvent.objects.filter(
                    tenant=t,
                    module_id=mod,
                    status__in=["Scheduled", "Notified", "Archived"]
                ).first()

                if not existing:
                    # Register new retention event
                    purge_date = now + datetime.timedelta(days=grace_days)
                    RetentionEvent.objects.create(
                        tenant=t,
                        module_id=mod,
                        status="Scheduled",
                        degraded_at=now,
                        purge_scheduled_at=purge_date,
                    )
                    scheduled_events += 1

        # Step C: Execute purges for events that exceeded their purge_scheduled_at
        ready_events = RetentionEvent.objects.filter(
            status__in=["Scheduled", "Notified"],
            purge_scheduled_at__lte=now
        )

        for ev in ready_events:
            cls.execute_purge_event(ev)
            processed_purges += 1

        return {
            "scheduled_events": scheduled_events,
            "processed_purges": processed_purges,
        }
