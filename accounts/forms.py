from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class AccountTypeForm(forms.Form):
    account_type = forms.ChoiceField(choices=User.ACCOUNT_TYPES, label="Account Typ")

class UserSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ("username","email","phone_number","password1","password2")

class TwoFactorForm(forms.Form):
    code = forms.CharField(max_length=10)
    remember_device = forms.BooleanField(required=False, initial=False)


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "phone_number", "account_type", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "w-full px-4 py-2 border rounded-lg"}),
            "email": forms.EmailInput(attrs={"class": "w-full px-4 py-2 border rounded-lg"}),
            "phone_number": forms.TextInput(attrs={"class": "w-full px-4 py-2 border rounded-lg"}),
            "account_type": forms.Select(attrs={"class": "w-full px-4 py-2 border rounded-lg"}),
        }


