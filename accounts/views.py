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
    CLIENT_ID = "JYQgmcexNerZk2KqvFdhCpwtZIA5ljGaM60qiS1Y"
    CLIENT_SECRET = "pbkdf2_sha256$1000000$4L8DGdVkw3sW5h3cvWE8iT$oYdRIQGjPyjrnOMw3E9RdgjfF0gbG3RKoUDOiocDAA0="
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

    return render(request, "accounts/login.html", {"CLIENT_ID": CLIENT_ID, "CLIENT_SECRET": CLIENT_SECRET})


def user_logout(request):
    logout(request)
    messages.success(request, _("Du wurdest ausgeloggt."))
    return redirect("home")

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError

from .models import User
from .forms import RegisterForm


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = True
                user.email_confirmed = True
                user.save()

                #uid = urlsafe_base64_encode(force_bytes(user.pk))
                #token = default_token_generator.make_token(user)
                #current_site = get_current_site(request)
#
                #subject = _("Bitte bestätige deine E-Mail-Adresse")
                #html_content = render_to_string("accounts/activation_email.html", {
                #    "user": user,
                #    "domain": current_site.domain,
                #    "uidb64": uid,
                #    "token": token,
                #})
#
                #email = EmailMultiAlternatives(
                #    subject,
                #    "",
                #    settings.DEFAULT_FROM_EMAIL,
                #    [user.email],
                #)
                #email.attach_alternative(html_content, "text/html")
                #email.send(fail_silently=False)
#
                messages.success(request, _("Registrierung erfolgreich! Bitte bestätige deine E-Mail-Adresse."))
                return redirect("login")

            except IntegrityError:
                messages.error(request, _("Dieser Benutzer existiert bereits."))
        else:
            messages.error(request, _("Bitte überprüfe deine Eingaben."))
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.email_confirmed = True
        user.is_active = True
        user.save()
        messages.success(request, _("E-Mail bestätigt! Du kannst dich jetzt anmelden."))
        return redirect("login")
    else:
        messages.error(request, _("Der Verifizierungslink ist ungültig oder abgelaufen."))
        return redirect("home")

from django.shortcuts import redirect
from django.conf import settings
from .utils import generate_pkce

def joel_login(request):
    verifier, challenge = generate_pkce()
    request.session["pkce_verifier"] = verifier

    url = (
        "https://joel-digitals.de/o/authorize/"
        "?response_type=code"
        f"&client_id={settings.JOEL_CLIENT_ID}"
        f"&redirect_uri={settings.JOEL_REDIRECT_URI}"
        "&scope=read"
        f"&code_challenge={challenge}"
        "&code_challenge_method=S256"
    )

    return redirect(url)
