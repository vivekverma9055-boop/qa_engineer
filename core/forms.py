from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = [
            "name",
            "email",
            "company",
            "country",
            "service_needed",
            "budget",
            "message",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Your full name", "class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "you@company.com", "class": "form-control"}
            ),
            "company": forms.TextInput(
                attrs={"placeholder": "Company / Agency (optional)", "class": "form-control"}
            ),
            "country": forms.TextInput(
                attrs={"placeholder": "Country (e.g. USA, UK, Canada)", "class": "form-control"}
            ),
            "service_needed": forms.Select(attrs={"class": "form-control"}),
            "budget": forms.TextInput(
                attrs={"placeholder": "Estimated budget / hourly rate (optional)", "class": "form-control"}
            ),
            "message": forms.Textarea(
                attrs={
                    "placeholder": "Tell me about your project, timelines, and QA needs...",
                    "class": "form-control",
                    "rows": 5,
                }
            ),
        }
