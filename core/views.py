import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from chatbot.models import KnowledgeBase

from .forms import ContactForm

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
def home(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            _notify_new_lead(contact)
            # No messages.success() here: the redirect target (contact_success)
            # renders its own confirmation and never displays the messages
            # queue, so a flashed message here would otherwise leak onto
            # whatever page the visitor views next.
            return redirect("core:home_success")
        messages.error(request, "Please correct the errors below and resubmit.")
    else:
        form = ContactForm()

    faqs = KnowledgeBase.objects.filter(is_published=True).order_by("question")
    return render(request, "core/home.html", {"form": form, "faqs": faqs})


@ensure_csrf_cookie
def contact_success(request):
    return render(request, "core/contact_success.html")


def _notify_new_lead(contact):
    subject = f"New QA/Automation project inquiry from {contact.name}"
    body = (
        f"Name: {contact.name}\n"
        f"Email: {contact.email}\n"
        f"Company: {contact.company or '-'}\n"
        f"Country: {contact.country or '-'}\n"
        f"Service needed: {contact.get_service_needed_display()}\n"
        f"Budget: {contact.budget or '-'}\n\n"
        f"Message:\n{contact.message}"
    )
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            [settings.CONTACT_RECEIVER_EMAIL],
            fail_silently=True,
        )
    except Exception:  # pragma: no cover - never break the request over email issues
        logger.exception("Failed to send contact-form notification email")
