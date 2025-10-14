from django import forms
from .models import Order, Application, Message

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={
                "class": (
                    "w-full px-4 py-3 rounded-2xl "
                    "bg-gray-100/80 dark:bg-gray-700/70 "
                    "border border-gray-300 dark:border-gray-600 "
                    "shadow-inner text-gray-900 dark:text-white "
                    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 "
                    "transition"
                )
            })
        }

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