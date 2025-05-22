from django.test import TestCase, Client
from django.urls import reverse

from dashboard.models import Lead, Message


class GenerateAIMessageTest(TestCase):
    """POST /generate-ai/ should return a JSON payload with message + status."""

    def setUp(self):
        self.client = Client()
        self.lead = Lead.objects.create(name="AI Lead", cellphone="1234567890")

    def test_generate_ai_message(self):
        url = reverse("generate_ai_message")
        response = self.client.post(url, {"lead_id": self.lead.id})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("message", data)
        self.assertIn("status", data)


class ManualMessageTest(TestCase):
    """POST /api/send-message/ should create a Manual Message entry."""

    def setUp(self):
        self.client = Client()
        self.lead = Lead.objects.create(name="Manual Lead", cellphone="1112223333")

    def test_manual_message_logged(self):
        url = reverse("send_message")
        payload = {"lead_id": self.lead.id, "content": "Hello"}
        response = self.client.post(url, payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            Message.objects.filter(
                lead=self.lead, content="Hello", source="Manual"
            ).exists()
        )


class MessageRetrievalTest(TestCase):
    """GET /message-thread/<lead_id>/ should return all logs in chronological order."""

    def setUp(self):
        self.client = Client()
        self.lead = Lead.objects.create(name="Thread Lead", cellphone="9998887777")
        Message.objects.create(lead=self.lead, content="First", source="Manual")
        Message.objects.create(lead=self.lead, content="Second", source="IN")

    def test_message_thread_returns_logs(self):
        url = reverse("get_message_thread", args=[self.lead.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["content"], "First")
        self.assertEqual(data[1]["content"], "Second")
