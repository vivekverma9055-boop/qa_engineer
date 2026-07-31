from django.db import models


class KnowledgeBase(models.Model):
    """A single Q&A the chatbot (and the on-page FAQ) can answer from.

    This is the bot's "brain" — add an entry here and every future visitor
    who asks something similar gets answered instantly.
    """

    question = models.CharField(
        max_length=255, help_text="The question visitors typically ask, e.g. 'Do you test iOS apps?'"
    )
    keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional comma-separated synonyms/keywords to widen matching, e.g. 'ios, iphone, apple, xcode'",
    )
    answer = models.TextField()
    is_published = models.BooleanField(
        default=True, help_text="Uncheck to keep a draft answer out of the live bot/FAQ."
    )
    times_matched = models.PositiveIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-times_matched", "question"]
        verbose_name_plural = "Knowledge base"

    def __str__(self):
        return self.question


class ChatQuery(models.Model):
    """Every question a visitor asked the chatbot.

    Confidently-matched questions are logged for analytics. Questions the bot
    couldn't confidently answer land in the "needs answer" queue — answering
    one here (or promoting it into the KnowledgeBase) is literally how the
    bot gets smarter over time.
    """

    question = models.TextField()
    matched_kb = models.ForeignKey(
        KnowledgeBase, null=True, blank=True, on_delete=models.SET_NULL, related_name="matches"
    )
    confidence = models.FloatField(default=0.0)
    answer_given = models.TextField(blank=True)
    needs_answer = models.BooleanField(default=True)
    visitor_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Chat queries"

    def __str__(self):
        return self.question[:80]
