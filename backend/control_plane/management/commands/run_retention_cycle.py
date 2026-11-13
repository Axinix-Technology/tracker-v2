from django.core.management.base import BaseCommand
from control_plane.retention_worker import StorageRetentionWorker


class Command(BaseCommand):
    help = "Executes automated multi-tenant storage and data retention lifecycle cycle"

    def handle(self, *args, **options):
        self.stdout.write("Running automated multi-tenant retention cycle...")
        result = StorageRetentionWorker.run_daily_retention_cycle()
        self.stdout.write(
            self.style.SUCCESS(
                f"Retention cycle completed: {result['scheduled_events']} new events scheduled, "
                f"{result['processed_purges']} expired module purges executed."
            )
        )
