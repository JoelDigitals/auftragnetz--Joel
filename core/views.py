from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.utils import timezone
from products.models import Product
from profiles.models import ProfileVisit
from core.models import Lead
from orders.models import Order
from plans.models import UserPlan


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
    # Aktiver Plan prüfen
    active_plan = UserPlan.objects.filter(user=request.user, expires_at__gte=timezone.now()).first()
    
    # Besucherzählung (angenommen als Integer)
    profile_visits_count = 123  # Dummy, hier deine echte Logik einsetzen

    # Leads nur wenn Plan aktiv
    leads = Lead.objects.filter(company=request.user) if active_plan else []

    # Produkte des Unternehmens
    products = Product.objects.filter(owner=request.user)

    # Jobangebote
    jobs = Order.objects.filter(user=request.user)

    context = {
        "profile_visits_count": profile_visits_count,
        "leads_count": leads.count() if active_plan else 0,
        "leads": leads,
        "products_count": products.count(),
        "products": products,
        "jobs": jobs,
        "active_plan": bool(active_plan),
    }

    return render(request, "main/company_dashboard.html", context)
