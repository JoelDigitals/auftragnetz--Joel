from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.utils import timezone
from products.models import Product
from profiles.models import ProfileVisit
from core.models import Lead
from orders.models import Order, Category
from .models import LeadPreference
from plans.models import UserPlan
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, "main/home.html")

def registration_step1(request):
    if request.method == "POST":
        # Rolle speichern (Freelancer, Unternehmen, etc.)
        role = request.POST.get("role")
        request.session["role"] = role
        return redirect("registration_step2")
    return render(request, "accounts/registration_step1.html")

def registration_step2(request):
    if request.method == "POST":
        # Daten speichern
        # z.B. Account anlegen
        return redirect("registration_done")
    return render(request, "accounts/registration_step2.html")

def registration_done(request):
    return render(request, "accounts/registration_done.html")
    

def create_order(request):
    if request.method == "POST":
        # Auftrag speichern
        pass
    return render(request, "main/create_order.html")

def company_dashboard(request):
    active_plan = UserPlan.objects.filter(user=request.user, expires_at__gte=timezone.now()).first()
    profile_visits_count = 0
    profile = getattr(request.user, "companyprofile", None) or getattr(request.user, "freelancerprofile", None)
    if profile:
        profile_visits_count = getattr(profile, "visitor_count", 0)

    leads = []
    if active_plan:
        pref = getattr(request.user, "lead_preference", None)
        if pref and pref.categories.exists():
            leads = Lead.objects.filter(category__in=pref.categories.all()).distinct().order_by('-created_at')
        else:
            leads = Lead.objects.all().order_by('-created_at')
    else:
        leads = []


    products = Product.objects.filter(owner=request.user)
    jobs = Order.objects.filter(user=request.user)

    context = {
        "profile_visits_count": profile_visits_count,
        "leads_count": len(leads) if active_plan else 0,
        "leads": leads,
        "products_count": products.count(),
        "products": products,
        "jobs": jobs,
        "active_plan": bool(active_plan),
    }

    return render(request, "main/company_dashboard.html", context)

@login_required
def lead_preferences(request):
    categories = Category.objects.all()

    # Vorhandene Einstellungen laden oder neu anlegen
    pref, created = LeadPreference.objects.get_or_create(company=request.user)

    if request.method == "POST":
        selected = request.POST.getlist("categories")
        pref.categories.set(selected)
        return redirect("company_dashboard")

    return render(request, "main/lead_preferences.html", {
        "categories": categories,
        "selected_categories": pref.categories.all()
    })

import requests
from django.contrib.auth import login
from django.shortcuts import redirect
from django.conf import settings
import base64
from accounts.models import User

def joel_callback(request):
    code = request.GET.get("code")

    if not code:
        return redirect("/accounts/login/")

    # Client Credentials als Basic Auth
    credentials = f"{settings.JOEL_CLIENT_ID}:{settings.JOEL_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    token_response = requests.post(
        "https://joel-digitals.de/en/o/token/",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.JOEL_REDIRECT_URI,
        },
        headers={
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=10,
    )

    print(f"=== TOKEN RESPONSE ===")
    print(f"Status Code: {token_response.status_code}")
    print(f"Response Text: {token_response.text}")

    if token_response.status_code != 200:
        return redirect("/accounts/login/")

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return redirect("/accounts/login/")

    user_response = requests.get(
        "https://joel-digitals.de/en/api/user/",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )

    data = user_response.json()

    user, _ = User.objects.get_or_create(
        email=data["email"],
        defaults={
            "username": data["email"],
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "is_active": True,
        },
    )

    login(request, user)
    return redirect("/")

import requests
from django.contrib.auth import login
from django.shortcuts import redirect
from django.conf import settings
from accounts.models import User
import secrets


def sso_login(request):
    """Startet SSO Login Flow"""
    print("\n" + "=" * 80)
    print("🚀 SSO LOGIN FLOW - START")
    print("=" * 80)
    
    # Zeige Request-Info
    print(f"\n🌐 Request Info:")
    print(f"   Path: {request.path}")
    print(f"   Method: {request.method}")
    print(f"   User: {request.user}")
    print(f"   Session Key (vorher): {request.session.session_key}")
    
    # State generieren
    state = secrets.token_urlsafe(32)
    
    print(f"\n📝 State generiert: {state}")
    
    # Session-Status VORHER
    print(f"\n💾 Session VORHER:")
    print(f"   Session Key: {request.session.session_key}")
    print(f"   Session Keys: {list(request.session.keys())}")
    print(f"   Session ist leer: {request.session.is_empty()}")
    
    # State speichern
    request.session['sso_state'] = state
    request.session.modified = True
    request.session.save()
    
    # Session-Status NACHHER
    print(f"\n💾 Session NACHHER:")
    print(f"   Session Key: {request.session.session_key}")
    print(f"   sso_state: {request.session.get('sso_state')}")
    print(f"   Alle Keys: {list(request.session.keys())}")
    print(f"   Session wurde gespeichert: {request.session.get('sso_state') == state}")
    
    # Redirect URL
    sso_url = (
        f"{settings.SSO_PROVIDER_URL}/auth/sso/connect/"
        f"?client_id={settings.SSO_CLIENT_ID}"
        f"&redirect_uri={settings.SSO_CALLBACK_URL}"
        f"&state={state}"
    )
    
    print(f"\n↗️  Redirect zu: {sso_url}")
    print("=" * 80 + "\n")
    
    return redirect(sso_url)


def sso_callback(request):
    """Empfängt SSO Token und erstellt/logged User ein"""
    print("\n" + "=" * 80)
    print("🔙 SSO CALLBACK - START")
    print("=" * 80)
    
    # Zeige Request-Info
    print(f"\n🌐 Request Info:")
    print(f"   Path: {request.path}")
    print(f"   Method: {request.method}")
    print(f"   User: {request.user}")
    
    # GET-Parameter
    token = request.GET.get('token')
    state = request.GET.get('state')
    
    print(f"\n📥 GET-Parameter:")
    print(f"   token: {token[:30] if token else 'None'}...")
    print(f"   state: {state}")
    
    # Session-Info
    print(f"\n💾 Session Info:")
    print(f"   Session Key: {request.session.session_key}")
    print(f"   Session ist leer: {request.session.is_empty()}")
    print(f"   Session Keys: {list(request.session.keys())}")
    
    # Alle Session-Werte ausgeben
    if not request.session.is_empty():
        print(f"   Session Inhalt:")
        for key in request.session.keys():
            print(f"      {key}: {request.session.get(key)}")
    
    # Cookie-Info
    print(f"\n🍪 Cookies:")
    for key, value in request.COOKIES.items():
        if 'session' in key.lower():
            print(f"   {key}: {value}")
    
    # State-Vergleich
    stored_state = request.session.get('sso_state')
    
    print(f"\n🔍 State-Vergleich:")
    print(f"   State aus URL:     '{state}'")
    print(f"   State aus Session: '{stored_state}'")
    print(f"   Sind identisch:    {state == stored_state}")
    
    # Fehleranalyse
    if not state:
        print("\n❌ FEHLER: Kein State in URL!")
        return redirect('/accounts/register/?error=no_state')
    
    if not stored_state:
        print("\n❌ FEHLER: Session hat keinen gespeicherten State!")
        print("   MÖGLICHE URSACHEN:")
        print("   1. Session-Cookie wurde nicht vom Browser gesendet")
        print("   2. Session ist abgelaufen")
        print("   3. Browser hat Cookies blockiert")
        print("   4. Andere Session (anderer Session-Key)")
        print(f"\n   Aktueller Session-Key: {request.session.session_key}")
        print(f"   Session hat diese Keys: {list(request.session.keys())}")
        return redirect('/accounts/register/?error=session_lost')
    
    if state != stored_state:
        print("\n❌ FEHLER: State Mismatch!")
        return redirect('/accounts/register/?error=invalid_state')
    
    print("\n✅ State erfolgreich validiert!")
    
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
        
        # Prüfe ob User bereits existiert
        existing_user = User.objects.filter(email=user_data['email']).first()
        
        if existing_user:
            print(f"✅ User existiert bereits → Einloggen")
            login(request, existing_user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Cleanup
            if 'sso_state' in request.session:
                del request.session['sso_state']
            
            print("=" * 80 + "\n")
            return redirect('/')
        
        # User existiert noch nicht → Daten in Session speichern
        print(f"📝 Neuer User → Speichere Daten in Session für Registrierung")
        request.session['sso_user_data'] = user_data
        
        print("=" * 80 + "\n")
        return redirect('/accounts/register/')
        
    except requests.RequestException as e:
        print(f"❌ SSO Request Error: {e}")
        print("=" * 80 + "\n")
        return redirect('/accounts/register/?error=connection_failed')