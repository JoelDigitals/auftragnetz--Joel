from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

from .models import User
from .forms import RegisterForm
from .utils import email_verification_token


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active or not user.email_confirmed:
                messages.error(request, _("Bitte bestätige zuerst deine E-Mail-Adresse."))
                return render(request, "accounts/login.html")

            login(request, user)
            messages.success(request, _("Willkommen zurück, ") + user.username + "!")
            return redirect("home")
        else:
            messages.error(request, _("Ungültiger Benutzername oder Passwort."))

    return render(request, "accounts/login.html")


def user_logout(request):
    logout(request)
    messages.success(request, _("Du wurdest ausgeloggt."))
    return redirect("home")

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # User speichern, aber noch nicht aktiv
            user = form.save(commit=False)
            user.is_active = False
            user.email_confirmed = False
            user.save()  # unbedingt speichern, sonst keine PK

            # UID und Token erstellen
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Aktiverungs-Mail rendern
            current_site = get_current_site(request)
            subject = "Bitte bestätige deine E-Mail-Adresse"
            html_content = render_to_string("accounts/activation_email.html", {
                "user": user,
                "domain": current_site.domain,
                "uidb64": uid,
                "token": token,
                "current_year": 2025,
            })

            # HTML-Mail versenden
            email = EmailMultiAlternatives(
                subject,
                "",  # Textversion leer oder alternativ kurze Textversion
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            messages.success(request, "Registrierung erfolgreich! Bitte bestätige deine E-Mail-Adresse.")
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and email_verification_token.check_token(user, token):
        user.email_confirmed = True
        user.is_active = True
        user.save()
        messages.success(request, "Deine E-Mail wurde bestätigt. Du kannst dich nun anmelden.")
        return redirect("login")
    else:
        messages.error(request, "Der Verifizierungslink ist ungültig oder abgelaufen.")
        return redirect("home")
