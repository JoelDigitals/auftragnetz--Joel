from django import forms
from .models import CompanyProfile, FreelancerProfile, Sonstiges

# Basis-Styling für alle Felder
IOS_FIELD_CLASSES = (
    "w-full px-4 py-3 rounded-2xl "
    "bg-gray-100/80 dark:bg-gray-700/70 "
    "border border-gray-300 dark:border-gray-600 "
    "shadow-inner text-gray-900 dark:text-white "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 "
    "transition"
)

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        exclude = ("user",)
        widgets = {
            "company_name": forms.TextInput(attrs={"class": IOS_FIELD_CLASSES, "placeholder": "Unternehmensname"}),
            "employee_count": forms.NumberInput(attrs={"class": IOS_FIELD_CLASSES, "placeholder": "Mitarbeiterzahl"}),
            "company_type": forms.TextInput(attrs={"class": IOS_FIELD_CLASSES}),
            "phone": forms.TextInput(attrs={"class": IOS_FIELD_CLASSES}),
            "website": forms.URLInput(attrs={"class": IOS_FIELD_CLASSES}),
            "wages_info": forms.Textarea(attrs={"class": IOS_FIELD_CLASSES, "rows": 3}),
            "address": forms.TextInput(attrs={"class": IOS_FIELD_CLASSES}),
            "location": forms.TextInput(attrs={"class": IOS_FIELD_CLASSES}),
            "social_links": forms.Textarea(attrs={"class": IOS_FIELD_CLASSES, "rows": 2}),
        }

class FreelancerProfileForm(forms.ModelForm):
    class Meta:
        model = FreelancerProfile
        exclude = ("user",)
        widgets = {
            "skills": forms.Textarea(attrs={"class": IOS_FIELD_CLASSES, "rows": 3}),
            "hourly_rate": forms.NumberInput(attrs={"class": IOS_FIELD_CLASSES}),
            "phone": forms.TextInput(attrs={"class": IOS_FIELD_CLASSES}),
            "website": forms.URLInput(attrs={"class": IOS_FIELD_CLASSES}),
            "availability": forms.TextInput(attrs={"class": IOS_FIELD_CLASSES}),
            "location": forms.TextInput(attrs={"class": IOS_FIELD_CLASSES}),
            "languages": forms.TextInput(attrs={"class": IOS_FIELD_CLASSES}),
            "certifications": forms.Textarea(attrs={"class": IOS_FIELD_CLASSES, "rows": 2}),
            "social_links": forms.Textarea(attrs={"class": IOS_FIELD_CLASSES, "rows": 2}),
        }

class SonstigesForm(forms.ModelForm):
    class Meta:
        model = Sonstiges
        exclude = ("user",)
        widgets = {
            "additional_info": forms.Textarea(attrs={"class": IOS_FIELD_CLASSES, "rows": 3}),
            "portfolio_link": forms.URLInput(attrs={"class": IOS_FIELD_CLASSES}),
            "availability": forms.TextInput(attrs={"class": IOS_FIELD_CLASSES}),
            "location": forms.TextInput(attrs={"class": IOS_FIELD_CLASSES}),
            "languages": forms.TextInput(attrs={"class": IOS_FIELD_CLASSES}),
            "certifications": forms.Textarea(attrs={"class": IOS_FIELD_CLASSES, "rows": 2}),
            "social_links": forms.Textarea(attrs={"class": IOS_FIELD_CLASSES, "rows": 2}),
            "resume": forms.ClearableFileInput(attrs={"class": IOS_FIELD_CLASSES}),
        }
