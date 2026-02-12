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

import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login
from .models import User
import secrets


def register(request):
    """Normale Registrierungsseite mit SSO-Option"""
    
    # Prüfe ob SSO-Daten vorhanden sind
    sso_data = request.session.get('sso_user_data')
    
    if request.method == 'POST':
        # Normale Registrierung ODER Registrierung mit SSO-Daten
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Validierung
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': 'Diese Email ist bereits registriert',
                'sso_data': sso_data,
            })
        
        # User erstellen
        user = User.objects.create_user(
            username=email.split('@')[0] + '_' + secrets.token_hex(3),
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        
        # Einloggen
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # SSO-Daten aus Session löschen
        if 'sso_user_data' in request.session:
            del request.session['sso_user_data']
        if 'sso_state' in request.session:
            del request.session['sso_state']
        
        return redirect('/')  # Oder Dashboard
    
    # GET Request - Zeige Formular
    return render(request, 'accounts/register.html', {
        'sso_data': sso_data,
    })

import secrets
from django.shortcuts import redirect
from django.conf import settings


def sso_connect(request):
    """Startet SSO-Connect zu Joel Digitals"""
    print("\n" + "🟢" * 40)
    print("FUNCTION: sso_connect - AUFTRAGNETZ")
    print("🟢" * 40)
    
    # State generieren
    state = secrets.token_urlsafe(32)
    
    print(f"📝 State generiert: {state}")
    print(f"🌐 Session Key vorher: {request.session.session_key}")
    print(f"🌐 Session Keys vorher: {list(request.session.keys())}")
    
    # !!! WICHTIG: Session muss existieren BEVOR wir speichern !!!
    if not request.session.session_key:
        # Force Django to create a session
        request.session.create()
        print(f"✨ Neue Session erstellt: {request.session.session_key}")
    
    # State speichern
    request.session['sso_state'] = state
    request.session.modified = True
    request.session.save()
    
    print(f"💾 Session Key nachher: {request.session.session_key}")
    print(f"💾 State gespeichert: {request.session.get('sso_state')}")
    print(f"💾 Alle Session Keys: {list(request.session.keys())}")
    
    # Redirect URL
    sso_url = (
        f"{settings.SSO_PROVIDER_URL}/auth/sso/connect/"
        f"?client_id={settings.SSO_CLIENT_ID}"
        f"&redirect_uri={settings.SSO_CALLBACK_URL}"
        f"&state={state}"
    )
    
    print(f"↗️  Redirect zu: {sso_url}")
    print("🟢" * 40 + "\n")
    
    response = redirect(sso_url)
    
    # !!! WICHTIG: Session-Cookie muss gesetzt werden !!!
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=request.session.session_key,
        max_age=settings.SESSION_COOKIE_AGE,
        httponly=True,
        samesite='Lax',
    )
    
    return response

def sso_callback(request):
    """Empfängt SSO Token und erstellt/logged User ein"""
    print("\n" + "=" * 80)
    print("🔙 SSO CALLBACK - START")
    print("=" * 80)
    
    token = request.GET.get('token')
    state = request.GET.get('state')
    
    # State-Validierung
    stored_state = request.session.get('sso_state')
    
    if not stored_state and state:
        print("⚠️  WARNING: Session-State fehlt - akzeptiere State aus URL (DEV ONLY!)")
        request.session['sso_state'] = state
        stored_state = state
    
    if state != stored_state:
        print("❌ FEHLER: State Mismatch!")
        return redirect('/accounts/register/?error=invalid_state')
    
    print("✅ State validiert!")
    
    if not token:
        print("❌ FEHLER: Kein Token")
        return redirect('/accounts/register/?error=no_token')
    
    # Token validieren
    print(f"\n🔍 Validiere Token bei SSO Provider...")
    try:
        response = requests.post(
            f"{settings.SSO_PROVIDER_URL}/api/sso/validate/",
            data={
                'token': token,
                'client_id': settings.SSO_CLIENT_ID,
                'client_secret': settings.SSO_CLIENT_SECRET,
            },
            timeout=10,
        )
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Token Validation fehlgeschlagen: {response.text}")
            return redirect('/accounts/register/?error=validation_failed')
        
        user_data = response.json()
        print(f"✅ Token validiert, User-Daten erhalten:")
        print(f"   Email: {user_data.get('email')}")
        print(f"   Username: {user_data.get('username')}")
        print(f"   First Name: {user_data.get('first_name')}")
        print(f"   Last Name: {user_data.get('last_name')}")
        
        # Zuerst: Prüfe ob User mit dieser EMAIL bereits existiert
        try:
            user = User.objects.get(email=user_data['email'])
            print(f"✅ Bestehender User gefunden (via Email): {user.email}")
            
            # Update User-Daten falls sich was geändert hat
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.is_active = True
            user.email_confirmed = True
            user.save()
            print(f"📝 User-Daten aktualisiert")
            
        except User.DoesNotExist:
            # User existiert noch nicht → Erstellen
            print(f"📝 Erstelle neuen User...")
            
            # Generiere eindeutigen Username falls nötig
            base_username = user_data.get('username', user_data['email'].split('@')[0])
            username = base_username
            counter = 1
            
            # Prüfe ob Username bereits existiert
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
                print(f"   Username '{base_username}' existiert bereits, versuche '{username}'")
            
            user = User.objects.create(
                email=user_data['email'],
                username=username,
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                is_active=True,
                email_confirmed=True,
            )
            
            # Setze unbrauchbares Passwort (SSO-User)
            user.set_unusable_password()
            user.save()
            
            print(f"✨ Neuer SSO-User erstellt: {user.email} (Username: {user.username})")

            print(f"\n🔓 Logge User ein...")
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            print(f"✅ User eingeloggt: {user.email}")

            # Session cleanup
            if 'sso_state' in request.session:
                del request.session['sso_state']
            if 'sso_user_data' in request.session:
                del request.session['sso_user_data']

            print("\n" + "=" * 80)
            print("✅ SSO LOGIN - KOMPLETT ERFOLGREICH")
            print("=" * 80 + "\n")

            return redirect('/accounts/register/step1/')  # Zur Startseite oder Dashboard
        
        # User einloggen
        print(f"\n🔓 Logge User ein...")
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        print(f"✅ User eingeloggt: {user.email}")
        
        # Session cleanup
        if 'sso_state' in request.session:
            del request.session['sso_state']
        if 'sso_user_data' in request.session:
            del request.session['sso_user_data']
        
        print("\n" + "=" * 80)
        print("✅ SSO LOGIN - KOMPLETT ERFOLGREICH")
        print("=" * 80 + "\n")
        
        return redirect('/')  # Zur Startseite oder Dashboard
        
    except requests.RequestException as e:
        print(f"❌ SSO Request Error: {e}")
        print("=" * 80 + "\n")
        return redirect('/accounts/register/?error=connection_failed')
    
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
        "https://joel-digitals.de/en/o/authorize/"
        "?response_type=code"
        f"&client_id={settings.JOEL_CLIENT_ID}"
        f"&redirect_uri={settings.JOEL_REDIRECT_URI}"
        "&scope=read"
        f"&code_challenge={challenge}"
        "&code_challenge_method=S256"
    )

    return redirect(url)

import requests
from django.contrib.auth import login
from django.shortcuts import redirect
from django.conf import settings
from accounts.models import User

def joel_login(request):
    """Redirect zu joel-digitals Login-Seite"""
    # Redirect zur joel-digitals Login-Seite
    return redirect("https://joel-digitals.de/en/auth/sso-login/")


def joel_callback(request):
    """Empfängt SSO-Token und erstellt/logged User ein"""
    sso_token = request.GET.get('sso_token')
    
    if not sso_token:
        return redirect("/accounts/login/")
    
    # Validiere Token bei joel-digitals
    response = requests.post(
        "https://joel-digitals.de/en/api/sso/validate-token/",
        data={
            'sso_token': sso_token,
            'secret': settings.SSO_SHARED_SECRET,
        },
        timeout=10,
    )
    
    if response.status_code != 200:
        print(f"SSO Error: {response.status_code} - {response.text}")
        return redirect("/accounts/login/")
    
    user_data = response.json()
    
    # User erstellen oder abrufen
    user, created = User.objects.get_or_create(
        email=user_data['email'],
        defaults={
            'username': user_data.get('username', user_data['email']),
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'is_active': True,
        },
    )
    
    # User einloggen
    login(request, user)
    
    print(f"✅ User {user.email} erfolgreich eingeloggt!")
    return redirect("/")  # Oder wohin auch immer nach Login


from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect

@login_required
def password_change(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            
            # Wichtig! Sonst wird der User ausgeloggt
            update_session_auth_hash(request, user)

            messages.success(request, "Your password was successfully updated!")
            return redirect("profile")  # Passe URL an
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/password_change.html", {"form": form})

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.shortcuts import render, redirect

@login_required
def account_delete(request):
    if request.method == "POST":
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=request.user.username,
            password=password
        )

        if user is not None:
            request.user.delete()
            messages.success(request, "Your account has been deleted.")
            return redirect("home")  # Passe URL-Name an
        else:
            messages.error(request, "Incorrect password.")

    return render(request, "accounts/account_delete.html")
