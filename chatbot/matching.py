"""
Lightweight, dependency-free question matching for the help chatbot.

No external AI/API calls: this scores the visitor's question against every
published KnowledgeBase entry using word-overlap + fuzzy string similarity,
and returns the best match if it's confident enough. Anything below the
threshold is treated as "unknown" so it can be queued for a human answer --
that queue is how the bot's knowledge grows over time.
"""
import re
from difflib import SequenceMatcher

from .models import KnowledgeBase

MATCH_THRESHOLD = 0.42

STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "did", "can", "could",
    "will", "would", "should", "i", "you", "your", "my", "me", "to", "of",
    "for", "and", "or", "in", "on", "at", "with", "how", "what", "when",
    "where", "why", "which", "it", "this", "that", "be", "have", "has",
}


def _tokenize(text):
    words = re.findall(r"[a-z0-9']+", text.lower())
    tokens = set()
    for w in words:
        if w in STOPWORDS or len(w) <= 1:
            continue
        # naive stemming so "apps"/"app", "devices"/"device", "rates"/"rate" line up
        if w.endswith("s") and not w.endswith("ss") and len(w) > 4:
            w = w[:-1]
        tokens.add(w)
    return tokens


def _score(query_tokens, query_raw, kb):
    kb_text = f"{kb.question} {kb.keywords} {kb.answer}"
    kb_tokens = _tokenize(kb_text)

    if query_tokens and kb_tokens:
        # containment, not Jaccard: what fraction of the *query's* words show up
        # in this entry, so a short query isn't penalized against a long answer.
        overlap = len(query_tokens & kb_tokens) / len(query_tokens)
    else:
        overlap = 0.0

    fuzzy = SequenceMatcher(None, query_raw.lower(), kb.question.lower()).ratio()

    return (0.7 * overlap) + (0.3 * fuzzy)


def find_answer(question_text):
    """Return (kb_entry_or_None, confidence_float) for the given question."""
    candidates = KnowledgeBase.objects.filter(is_published=True)
    query_tokens = _tokenize(question_text)

    best_kb = None
    best_score = 0.0
    for kb in candidates:
        score = _score(query_tokens, question_text, kb)
        if score > best_score:
            best_score = score
            best_kb = kb

    if best_kb and best_score >= MATCH_THRESHOLD:
        return best_kb, round(best_score, 3)
    return None, round(best_score, 3)


FALLBACK_ANSWER = (
    "Good question — I don't have a ready answer for that yet, but I've noted it "
    "and Vivek will personally follow up by email. In the meantime, feel free to "
    "describe your project in the contact form below, or email "
    "vivkverma905@gmail.com directly."
)
