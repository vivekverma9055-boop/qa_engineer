import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from chatbot.models import KnowledgeBase

from .forms import ContactForm

logger = logging.getLogger(__name__)

RESEND_TIMEOUT_SECONDS = 10


@ensure_csrf_cookie
def home(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                contact = form.save()
            except Exception:
                logger.exception("Failed to save contact form submission")
                messages.error(
                    request,
                    "Something went wrong saving your message. Please email "
                    "vivkverma905@gmail.com directly and I'll get back to you.",
                )
            else:
                _notify_new_lead(contact)
                # No messages.success() here: the redirect target (contact_success)
                # renders its own confirmation and never displays the messages
                # queue, so a flashed message here would otherwise leak onto
                # whatever page the visitor views next.
                return redirect("core:home_success")
        else:
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

    if settings.RESEND_API_KEY:
        _send_via_resend(subject, body)
    else:
        _send_via_smtp(subject, body)


def _send_via_resend(subject, body):
    """Send over Resend's HTTPS API instead of raw SMTP.

    Hosts like Render's free tier can block outbound SMTP ports outright, in
    which case a socket connect attempt hangs until the WSGI worker's own
    timeout force-kills it with SystemExit -- which isn't a subclass of
    Exception, so no try/except here could ever catch it. A plain HTTPS POST
    doesn't have that failure mode, and still degrades gracefully (via the
    try/except below) for anything else that can go wrong.
    """
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
            json={
                "from": settings.RESEND_FROM_EMAIL,
                "to": [settings.CONTACT_RECEIVER_EMAIL],
                "subject": subject,
                "text": body,
            },
            timeout=RESEND_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except Exception:  # pragma: no cover - never break the request over email issues
        logger.exception("Failed to send contact-form notification email via Resend")


def _send_via_smtp(subject, body):
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            [settings.CONTACT_RECEIVER_EMAIL],
            fail_silently=True,
        )
    except Exception:  # pragma: no cover - never break the request over email issues
        logger.exception("Failed to send contact-form notification email via SMTP")
