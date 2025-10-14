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
        if pref:
            leads = Lead.objects.filter(source__in=pref.categories.values_list("name", flat=True))
        else:
            leads = Lead.objects.all()

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