from django import forms
from .models import Order, Application, Category



class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Schreibe hier deine Bewerbung..."}),
        }
        labels = {
            "message": "Deine Bewerbung",
        }