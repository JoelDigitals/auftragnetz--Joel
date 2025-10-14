from django import forms
from .models import CompanyProfile, FreelancerProfile, Sonstiges

# -------------------------------
# Einheitliches Styling für alle Felder
# -------------------------------
BASE_FIELD_CLASSES = (
    "w-full px-4 py-3 rounded-2xl "
    "bg-gray-100/80 dark:bg-gray-700/70 "
    "border border-gray-300 dark:border-gray-600 "
    "shadow-inner text-gray-900 dark:text-white "
    "placeholder-gray-400 dark:placeholder-gray-300 "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 "
    "transition"
)

TEXTAREA_CLASSES = BASE_FIELD_CLASSES + " resize-none appearance-none"

FILE_INPUT_CLASSES = (
    "w-full py-2 px-4 rounded-2xl border border-gray-300 dark:border-gray-600 "
    "bg-gray-100/80 dark:bg-gray-700/70 shadow-inner text-gray-900 dark:text-white "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
)

# -------------------------------
# CompanyProfileForm
# -------------------------------
class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        exclude = ("user", "visitor_count")
        widgets = {
            "company_name": forms.TextInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Unternehmensname"}),
            "employee_count": forms.NumberInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Mitarbeiterzahl"}),
            "company_type": forms.TextInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Unternehmensart"}),
            "phone": forms.TextInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Telefonnummer"}),
            "website": forms.URLInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Website"}),
            "wages_info": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 4, "placeholder": "Beschreibung / Gehaltsinformationen"}),
            "address": forms.TextInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Adresse"}),
            "location": forms.TextInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Ort"}),
            "social_links": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 2, "placeholder": "Social Media Links"}),
            "description": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 3, "placeholder": "Beschreibung des Unternehmens"}),
            "Categorys": forms.SelectMultiple(attrs={"class": BASE_FIELD_CLASSES}),
        }

# -------------------------------
# FreelancerProfileForm
# -------------------------------
class FreelancerProfileForm(forms.ModelForm):
    skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 3, "placeholder": "Fähigkeiten / Skills"})
    )

    class Meta:
        model = FreelancerProfile
        exclude = ("user", "visitor_count")
        widgets = {
            "Categorys": forms.SelectMultiple(attrs={"class": BASE_FIELD_CLASSES}),
            "hourly_rate": forms.NumberInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Stundensatz in €"}),
            "phone": forms.TextInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Telefonnummer"}),
            "website": forms.URLInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Website"}),
            "availability": forms.TextInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Verfügbarkeit"}),
            "location": forms.TextInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Ort"}),
            "languages": forms.TextInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Sprachen"}),
            "certifications": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 2, "placeholder": "Zertifikate"}),
            "social_links": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 2, "placeholder": "Social Media Links"}),
            "portfolio_link": forms.URLInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Portfolio Link"}),
        }

# -------------------------------
# SonstigesForm
# -------------------------------
class SonstigesForm(forms.ModelForm):
    class Meta:
        model = Sonstiges
        exclude = ("user", "visitor_count")
        widgets = {
            "additional_info": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 3, "placeholder": "Zusätzliche Informationen"}),
            "portfolio_link": forms.URLInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Portfolio Link"}),
            "availability": forms.TextInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Verfügbarkeit"}),
            "location": forms.TextInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Ort"}),
            "languages": forms.TextInput(attrs={"class": BASE_FIELD_CLASSES, "placeholder": "Sprachen"}),
            "certifications": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 2, "placeholder": "Zertifikate"}),
            "social_links": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 2, "placeholder": "Social Media Links"}),
            "resume": forms.ClearableFileInput(attrs={"class": FILE_INPUT_CLASSES}),
            "Categorys": forms.SelectMultiple(attrs={"class": BASE_FIELD_CLASSES}),
        }
