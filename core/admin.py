from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "country", "service_needed", "status", "created_at")
    list_filter = ("status", "service_needed", "country", "created_at")
    search_fields = ("name", "email", "company", "message")
    list_editable = ("status",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
