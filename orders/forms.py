from django import forms
from .models import Order, Application, Message



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

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["text"]
        widgets = {
            "text": forms.TextInput(attrs={
                "class": "flex-1 rounded-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500 px-4 py-2",
                "placeholder": "Schreibe eine Nachricht..."
            })
        }