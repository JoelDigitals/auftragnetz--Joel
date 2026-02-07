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
from django.contrib.auth.models import User
from django.shortcuts import redirect

def joel_callback(request):
    code = request.GET.get('code')

    # 1️⃣ Code → Access Token tauschen
    token_response = requests.post(
        'https://joel-digital.de/o/token/',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'https://auftragsnetz.de/auth/joel/callback/',
            'client_id': 'JYQgmcexNerZk2KqvFdhCpwtZIA5ljGaM60qiS1Y',
            'client_secret': 'pbkdf2_sha256$1000000$4L8DGdVkw3sW5h3cvWE8iT$oYdRIQGjPyjrnOMw3E9RdgjfF0gbG3RKoUDOiocDAA0=',
        }
    )

    token = token_response.json()['access_token']

    # 2️⃣ User-Daten holen
    user_response = requests.get(
        'https://joel-digital.de/api/user/',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = user_response.json()

    # 3️⃣ User lokal anlegen oder holen
    user, created = User.objects.get_or_create(
        username=data['email'],
        defaults={
            'email': data['email'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
        }
    )

    # 4️⃣ Login
    login(request, user)

    return redirect('/')
