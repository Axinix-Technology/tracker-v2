from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.models import Role
from tickets.models import Ticket, TicketComment, TicketParticipant, TicketStatusHistory
from tasks.models import Task

User = get_user_model()


class TicketLifecycleAndSecurityTestCase(TestCase):
    def setUp(self):
        self.role_emp, _ = Role.objects.get_or_create(
            name="Employee", defaults={"is_superadmin": False, "status": 1}
        )

        self.alice = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="AlicePassword123!",
            role=self.role_emp
        )

        self.bob = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="BobPassword123!",
            role=self.role_emp
        )

        self.client = APIClient()

    def test_ticket_creation_and_creator_anti_spoofing(self):
        self.client.force_authenticate(user=self.alice)
        res = self.client.post(
            "/api/populate/create/ticket/",
            {
                "title": "Bug in billing portal",
                "description": "Invoices not generating PDF",
                "priority": "High",
                "created_by": self.bob.id,  # Spoofing attempt
            },
            format="json"
        )
        self.assertEqual(res.status_code, 201)
        data = res.data["data"]
        ticket_id = data[0]["id"] if isinstance(data, list) else data["id"]

        ticket = Ticket.objects.get(id=ticket_id)
        # Anti-spoofing: Creator must strictly be Alice, ignoring Bob
        self.assertEqual(ticket.created_by.id, self.alice.id)
        self.assertTrue(ticket.ticket_id.startswith("TCK-"))
        self.assertEqual(ticket.ticket_status, "Open")

        # Initial status history and participant checks
        history = TicketStatusHistory.objects.filter(ticket=ticket)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().to_status, "Open")

        self.assertTrue(
            TicketParticipant.objects.filter(ticket=ticket, user=self.alice, role="creator").exists()
        )

    def test_status_transition_records_duration_and_history(self):
        self.client.force_authenticate(user=self.alice)
        ticket = Ticket.objects.create(
            title="Database performance issue",
            ticket_status="Open",
            created_by=self.alice
        )
        TicketStatusHistory.objects.create(
            ticket=ticket,
            from_status=None,
            to_status="Open",
            changed_by=self.alice,
            duration_seconds=0
        )

        # Transition status to "In Progress"
        res = self.client.post(
            f"/api/populate/update/ticket/{ticket.id}/",
            {"ticket_status": "In Progress"},
            format="json"
        )
        self.assertEqual(res.status_code, 200)

        histories = TicketStatusHistory.objects.filter(ticket=ticket).order_by("id")
        self.assertEqual(histories.count(), 2)

        latest_history = histories.last()
        self.assertEqual(latest_history.from_status, "Open")
        self.assertEqual(latest_history.to_status, "In Progress")
        self.assertEqual(latest_history.changed_by.id, self.alice.id)

    def test_unrelated_edit_does_not_duplicate_status_history(self):
        self.client.force_authenticate(user=self.alice)
        ticket = Ticket.objects.create(
            title="UI Alignment glitch",
            ticket_status="Open",
            priority="Low",
            created_by=self.alice
        )
        TicketStatusHistory.objects.create(
            ticket=ticket,
            from_status=None,
            to_status="Open",
            changed_by=self.alice,
            duration_seconds=0
        )

        initial_history_count = TicketStatusHistory.objects.filter(ticket=ticket).count()

        # Update description and priority only (no status change)
        res = self.client.post(
            f"/api/populate/update/ticket/{ticket.id}/",
            {
                "description": "Updated detail about button margin.",
                "priority": "High"
            },
            format="json"
        )
        self.assertEqual(res.status_code, 200)

        # History count must NOT increase
        after_history_count = TicketStatusHistory.objects.filter(ticket=ticket).count()
        self.assertEqual(initial_history_count, after_history_count)

    def test_comment_author_anti_spoofing(self):
        self.client.force_authenticate(user=self.alice)
        ticket = Ticket.objects.create(
            title="Server slow response",
            ticket_status="Open",
            created_by=self.alice
        )

        res = self.client.post(
            "/api/populate/create/ticket_comment/",
            {
                "ticket": ticket.id,
                "content": "Looking into the Redis cache stats now.",
                "author": self.bob.id,  # Alice attempts to spoof Bob as author
            },
            format="json"
        )
        self.assertEqual(res.status_code, 201)
        comment_id = res.data["data"][0]["id"] if isinstance(res.data["data"], list) else res.data["data"]["id"]

        comment = TicketComment.objects.get(id=comment_id)
        self.assertEqual(comment.author.id, self.alice.id)

    def test_bi_directional_task_sync_on_resolve(self):
        self.client.force_authenticate(user=self.alice)
        task = Task.objects.create(
            title="Investigate billing discrepancy",
            status="In Progress",
            progress=40,
            createdBy=self.alice
        )
        ticket = Ticket.objects.create(
            title="Billing discrepancy ticket",
            ticket_status="In Progress",
            created_by=self.alice,
            linked_task=task
        )

        # Resolve the ticket
        res = self.client.post(
            f"/api/populate/update/ticket/{ticket.id}/",
            {"ticket_status": "Resolved"},
            format="json"
        )
        self.assertEqual(res.status_code, 200)

        ticket.refresh_from_db()
        self.assertEqual(ticket.ticket_status, "Resolved")
        self.assertIsNotNone(ticket.resolved_at)

        task.refresh_from_db()
        self.assertEqual(task.status, "Done")
        self.assertEqual(task.progress, 100)
