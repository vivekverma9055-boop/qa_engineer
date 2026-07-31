import json

from django.test import TestCase
from django.urls import reverse

from .matching import find_answer
from .models import ChatQuery, KnowledgeBase


class MatchingEngineTests(TestCase):
    def setUp(self):
        self.kb = KnowledgeBase.objects.create(
            question="Do you test iOS apps and devices?",
            keywords="ios, iphone, ipad, apple, xcode",
            answer="Yes, I test iOS apps and devices.",
            is_published=True,
        )

    def test_close_phrasing_matches(self):
        kb, confidence = find_answer("do you test ios devices?")
        self.assertEqual(kb, self.kb)
        self.assertGreater(confidence, 0)

    def test_unpublished_entries_are_never_matched(self):
        self.kb.is_published = False
        self.kb.save()
        kb, _ = find_answer("do you test ios devices?")
        self.assertIsNone(kb)

    def test_unrelated_question_does_not_match(self):
        kb, confidence = find_answer("can you paint my house purple")
        self.assertIsNone(kb)


class ChatApiTests(TestCase):
    def setUp(self):
        self.kb = KnowledgeBase.objects.create(
            question="What are your rates / how much do you charge?",
            keywords="price, pricing, cost, rate, budget",
            answer="Custom quote based on scope.",
            is_published=True,
        )
        self.url = reverse("chatbot:chat_api")

    def _post(self, payload_dict=None, raw_body=None):
        self.client.get(reverse("core:home"))  # ensure csrftoken cookie exists
        csrf_token = self.client.cookies["csrftoken"].value
        body = raw_body if raw_body is not None else json.dumps(payload_dict)
        return self.client.post(
            self.url,
            data=body,
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

    def test_matched_question_returns_answer_and_logs_query(self):
        response = self._post({"message": "how much do you charge"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["matched"])
        self.assertIn("Custom quote", data["reply"])
        query = ChatQuery.objects.latest("created_at")
        self.assertFalse(query.needs_answer)
        self.assertEqual(query.matched_kb, self.kb)

    def test_unmatched_question_falls_back_and_flags_needs_answer(self):
        response = self._post({"message": "can you paint my house purple"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["matched"])
        query = ChatQuery.objects.latest("created_at")
        self.assertTrue(query.needs_answer)

    def test_times_matched_increments(self):
        self._post({"message": "how much do you charge"})
        self._post({"message": "how much do you charge"})
        self.kb.refresh_from_db()
        self.assertEqual(self.kb.times_matched, 2)

    def test_empty_message_returns_400(self):
        response = self._post({"message": "   "})
        self.assertEqual(response.status_code, 400)

    def test_missing_message_key_returns_400(self):
        response = self._post({})
        self.assertEqual(response.status_code, 400)

    def test_non_dict_json_body_returns_400_not_500(self):
        response = self._post(raw_body=json.dumps([1, 2, 3]))
        self.assertEqual(response.status_code, 400)

    def test_non_string_message_returns_400_not_500(self):
        response = self._post({"message": 12345})
        self.assertEqual(response.status_code, 400)

    def test_invalid_json_returns_400_not_500(self):
        response = self._post(raw_body="not json at all {")
        self.assertEqual(response.status_code, 400)

    def test_get_request_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_missing_csrf_token_is_rejected(self):
        from django.test import Client

        strict_client = Client(enforce_csrf_checks=True)
        strict_client.get(reverse("core:home"))  # sets the csrftoken cookie, but we won't send it
        response = strict_client.post(
            self.url, data=json.dumps({"message": "hi"}), content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)


class KnowledgeBaseAdminActionTests(TestCase):
    def test_promote_creates_knowledge_base_entry(self):
        from django.contrib.admin.sites import AdminSite
        from django.contrib.auth import get_user_model
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.test import RequestFactory

        from .admin import ChatQueryAdmin, promote_to_knowledge_base

        query = ChatQuery.objects.create(
            question="Do you support Windows Phone?",
            answer_given="No, but I cover Android and iOS.",
            needs_answer=True,
        )

        request = RequestFactory().get("/admin/chatbot/chatquery/")
        request.user = get_user_model().objects.create_superuser(
            "admintest", "admintest@example.com", "password123"
        )
        request.session = self.client.session
        request._messages = FallbackStorage(request)

        admin_instance = ChatQueryAdmin(ChatQuery, AdminSite())
        promote_to_knowledge_base(admin_instance, request, ChatQuery.objects.filter(pk=query.pk))

        self.assertTrue(KnowledgeBase.objects.filter(question="Do you support Windows Phone?").exists())
        query.refresh_from_db()
        self.assertFalse(query.needs_answer)
