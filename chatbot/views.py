import json

from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .matching import FALLBACK_ANSWER, find_answer
from .models import ChatQuery, KnowledgeBase

MAX_QUESTION_LENGTH = 500


@require_POST
def chat_api(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid request."}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({"error": "Invalid request."}, status=400)

    raw_message = payload.get("message")
    if not isinstance(raw_message, str):
        return JsonResponse({"error": "Please type a question."}, status=400)

    question = raw_message.strip()[:MAX_QUESTION_LENGTH]
    if not question:
        return JsonResponse({"error": "Please type a question."}, status=400)

    kb_entry, confidence = find_answer(question)

    if kb_entry:
        answer = kb_entry.answer
        KnowledgeBase.objects.filter(pk=kb_entry.pk).update(times_matched=F("times_matched") + 1)
        needs_answer = False
    else:
        answer = FALLBACK_ANSWER
        needs_answer = True

    ChatQuery.objects.create(
        question=question,
        matched_kb=kb_entry,
        confidence=confidence,
        answer_given=answer,
        needs_answer=needs_answer,
    )

    return JsonResponse({"reply": answer, "matched": kb_entry is not None})
