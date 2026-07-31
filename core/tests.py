from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from chatbot.models import KnowledgeBase

from .models import ContactMessage


class HomePageTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vivek Verma")

    def test_home_page_sets_csrf_cookie(self):
        response = self.client.get(reverse("core:home"))
        self.assertIn("csrftoken", response.cookies)

    def test_success_page_sets_csrf_cookie(self):
        # Regression: the chat widget lives on every page via base.html, so
        # every page must guarantee the CSRF cookie exists, not just the one
        # with a <form> on it.
        response = self.client.get(reverse("core:home_success"))
        self.assertIn("csrftoken", response.cookies)

    def test_faq_renders_published_knowledge_base_entries(self):
        KnowledgeBase.objects.create(question="Published Q", answer="Published A", is_published=True)
        KnowledgeBase.objects.create(question="Draft Q", answer="Draft A", is_published=False)
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Published Q")
        self.assertNotContains(response, "Draft Q")


class ContactFormSubmissionTests(TestCase):
    valid_payload = {
        "name": "Jane Client",
        "email": "jane@example.com",
        "company": "Acme Inc",
        "country": "USA",
        "service_needed": "api",
        "budget": "2000 USD",
        "message": "We need help testing our public API before launch.",
    }

    def test_valid_submission_saves_and_redirects(self):
        response = self.client.post(reverse("core:home"), data=self.valid_payload)
        self.assertRedirects(response, reverse("core:home_success"))
        self.assertEqual(ContactMessage.objects.count(), 1)
        saved = ContactMessage.objects.first()
        self.assertEqual(saved.email, "jane@example.com")

    def test_valid_submission_sends_notification_email(self):
        self.client.post(reverse("core:home"), data=self.valid_payload)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Jane Client", mail.outbox[0].body)

    def test_success_page_does_not_leak_into_next_page(self):
        # Regression: messages.success() used to be queued on submit and
        # never displayed on the redirect target, so it would silently pop
        # up on whatever page the visitor viewed next.
        self.client.post(reverse("core:home"), data=self.valid_payload)
        self.client.get(reverse("core:home_success"))
        response = self.client.get(reverse("core:home"))
        self.assertNotContains(response, "Thanks for reaching out")

    def test_invalid_submission_does_not_save_and_shows_errors(self):
        payload = dict(self.valid_payload, email="not-an-email")
        response = self.client.post(reverse("core:home"), data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(response, "correct the errors")

    def test_missing_required_field_rejected(self):
        payload = dict(self.valid_payload)
        del payload["message"]
        response = self.client.post(reverse("core:home"), data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_db_save_failure_shows_error_instead_of_500(self):
        # Regression: a failing form.save() (e.g. a database error in
        # production) used to be unhandled and crashed the request with a
        # raw 500 instead of degrading gracefully.
        with patch(
            "core.forms.ContactForm.save", side_effect=Exception("simulated db failure")
        ):
            response = self.client.post(reverse("core:home"), data=self.valid_payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong saving your message")
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_email_failure_does_not_block_success_redirect(self):
        # The DB write is the source of truth; a broken SMTP config
        # shouldn't stop a successfully-saved lead from reaching the
        # thank-you page.
        with patch("core.views.send_mail", side_effect=Exception("simulated smtp failure")):
            response = self.client.post(reverse("core:home"), data=self.valid_payload)
        self.assertRedirects(response, reverse("core:home_success"))
        self.assertEqual(ContactMessage.objects.count(), 1)

    @override_settings(RESEND_API_KEY="test-key", RESEND_FROM_EMAIL="onboarding@resend.dev")
    def test_uses_resend_api_when_configured(self):
        with patch("core.views.requests.post") as mock_post:
            mock_post.return_value.raise_for_status.return_value = None
            response = self.client.post(reverse("core:home"), data=self.valid_payload)

        self.assertRedirects(response, reverse("core:home_success"))
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-key")
        self.assertIn("Jane Client", kwargs["json"]["text"])

    @override_settings(RESEND_API_KEY="test-key")
    def test_resend_failure_does_not_block_success_redirect(self):
        with patch("core.views.requests.post", side_effect=Exception("simulated network block")):
            response = self.client.post(reverse("core:home"), data=self.valid_payload)
        self.assertRedirects(response, reverse("core:home_success"))
        self.assertEqual(ContactMessage.objects.count(), 1)


class ContactMessageModelTests(TestCase):
    def test_str_representation(self):
        msg = ContactMessage.objects.create(
            name="Jane", email="jane@example.com", service_needed="api", message="hi"
        )
        self.assertIn("Jane", str(msg))
        self.assertIn("jane@example.com", str(msg))
