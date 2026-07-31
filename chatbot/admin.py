from django.contrib import admin

from .models import ChatQuery, KnowledgeBase


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ("question", "is_published", "times_matched", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("question", "keywords", "answer")
    list_editable = ("is_published",)


@admin.action(description="Add selected queries to the Knowledge Base")
def promote_to_knowledge_base(modeladmin, request, queryset):
    created = 0
    for query in queryset:
        if not query.answer_given or query.matched_kb_id:
            continue
        KnowledgeBase.objects.create(
            question=query.question,
            answer=query.answer_given,
            is_published=True,
        )
        query.needs_answer = False
        query.save(update_fields=["needs_answer"])
        created += 1
    modeladmin.message_user(request, f"Added {created} new knowledge base entr{'y' if created == 1 else 'ies'}.")


@admin.register(ChatQuery)
class ChatQueryAdmin(admin.ModelAdmin):
    list_display = ("question", "needs_answer", "confidence", "matched_kb", "created_at")
    list_filter = ("needs_answer", "created_at")
    search_fields = ("question", "answer_given", "visitor_email")
    readonly_fields = ("question", "matched_kb", "confidence", "created_at")
    actions = [promote_to_knowledge_base]
