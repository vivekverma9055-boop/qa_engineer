from django.db import models


class ContactMessage(models.Model):
    class ServiceType(models.TextChoices):
        MANUAL = "manual", "Manual Testing"
        AUTOMATION_WEB = "automation_web", "Web Automation (Selenium)"
        AUTOMATION_MOBILE = "automation_mobile", "Mobile Automation (Appium)"
        API = "api", "API Testing"
        DEVICE = "device", "Device / IoT / VoIP Testing"
        FRAMEWORK = "framework", "Automation Framework Setup"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        IN_DISCUSSION = "in_discussion", "In Discussion"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=120)
    email = models.EmailField()
    company = models.CharField(max_length=150, blank=True)
    country = models.CharField(max_length=100, blank=True)
    service_needed = models.CharField(
        max_length=30, choices=ServiceType.choices, default=ServiceType.OTHER
    )
    budget = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> - {self.get_service_needed_display()}"
