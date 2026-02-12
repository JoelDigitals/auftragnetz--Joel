from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg, Case, When, Value, FloatField, F
from django.utils import timezone
from datetime import datetime
from .models import Order, Application, Category, Chat, Message
from accounts.models import User
from .forms import ApplicationForm, MessageForm, OrderStatusForm
from plans.models import UserPlan
from products.models import Product
import calendar
from datetime import timedelta
from django.utils.dateparse import parse_date
from core.models import Lead
from django.core.paginator import Paginator

def order_list(request):
    qs = Order.objects.filter(status__in=["open", "in_progress"]).order_by("-created_at")

    # Suche
    search = request.GET.get("q")
    if search:
        qs = qs.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    # Mehrere Kategorien (z. B. ?categories=1&categories=5)
    categories_filter = request.GET.getlist("categories")
    if categories_filter:
        qs = qs.filter(category__id__in=categories_filter).distinct()

    # Datumsfilter (z. B. ?date_from=2025-09-01&date_to=2025-09-29)
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if date_from:
        qs = qs.filter(created_at__gte=parse_date(date_from))
    if date_to:
        qs = qs.filter(created_at__lte=parse_date(date_to))

    categories = Category.objects.all().order_by("name")

    return render(request, "orders/order_list.html", {
        "orders": qs,
        "categories": categories,
        "selected_categories": categories_filter,
        "search": search,
        "date_from": date_from,
        "date_to": date_to,
    })

def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    applications = order.applications.select_related("applicant").all()

    # Status-Update nur für den Ersteller
    if request.user == order.created_by:
        if request.method == "POST":
            form = OrderStatusForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect("order_detail", pk=order.pk)
        else:
            form = OrderStatusForm(instance=order)
    else:
        form = None

    return render(request, "orders/order_detail.html", {
        "order": order,
        "applications": applications,
        "form": form,
    })



@login_required
def order_create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        budget = request.POST.get('budget')
        deadline = request.POST.get('deadline')
        categories = request.POST.getlist('categories')
        status = request.POST.get('status')

        order = Order.objects.create(
            title=title,
            description=description,
            budget=budget,
            deadline=deadline,
            status=status,
            created_by=request.user
        )

        order.categories.set(categories)  # Set ManyToMany relation

        return redirect("orders:order_detail", pk=order.pk)
    else:
        categories = Category.objects.all()
        status_choices = Order.STATUS_CHOICES
        return render(request, "orders/create_order.html", {
            "categories": categories,
            "status_choices": status_choices,
            "title": "",
            "description": "",
            "budget": "",
            "deadline": "",
            "status": "",
            "selected_categories": []
        })
    
@login_required
def create_order(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        budget = request.POST.get('budget') or None
        deadline = request.POST.get('deadline') or None
        categories = request.POST.getlist('categories')
        status = request.POST.get('status')

        order = Order.objects.create(
            title=title,
            description=description,
            budget=budget,
            deadline=deadline,
            status=status,
            created_by=request.user
        )

        if categories:
            order.category.set(categories)  # funktioniert jetzt mit ManyToMany
        return redirect("order_detail", pk=order.pk)
    else:
        categories = Category.objects.all()
        status_choices = Order.STATUS_CHOICES
        return render(request, "orders/order_create.html", {
            "categories": categories,
            "status_choices": status_choices
        })
    
@login_required
def apply_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    now = timezone.now()

    # Aktiver Plan prüfen
    userplan = UserPlan.objects.filter(user=request.user, expires_at__gte=now).first()

    # Monatslimit berechnen
    month_start = datetime(now.year, now.month, 1)
    month_end = datetime(
        now.year, now.month,
        calendar.monthrange(now.year, now.month)[1], 23, 59, 59
    )

    count_apps = Application.objects.filter(
        applicant=request.user,
        created_at__range=(month_start, month_end)
    ).count()

    if userplan:
        limit = userplan.plan.applications_limit_per_month or 10
    else:
        limit = 10  # Free User Limit

    if count_apps >= limit:
        return redirect("order_detail", pk=order.pk)

    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.order = order
            a.applicant = request.user
            a.phone = getattr(request.user, "phone_number", "")
            a.email = request.user.email
            a.save()

            # Chat erstellen
            chat = Chat.objects.create()
            chat.participants.add(request.user, order.created_by)
            a.chat = chat
            a.save(update_fields=["chat"])

            # Erste Nachricht = Bewerbungstext + Kontaktdaten
            msg_text = (
                f"📌 Bewerbung auf {order.title}\n\n"
                f"{a.message}\n\n"
                f"Kontaktdaten:\n📞 {a.phone or '-'}\n📧 {a.email or '-'}"
            )
            Message.objects.create(chat=chat, sender=request.user, text=msg_text)

            return redirect("order_detail", pk=order.pk)
    else:
        form = ApplicationForm()

    return render(request, "orders/apply_order.html", {
        "order": order,
        "form": form
    })

def freelancer_list(request):
    # 🔹 Alle relevanten User laden mit select_related für Performance
    qs = User.objects.filter(
        account_type__in=["freelancer", "company", "sonstiges"]
    ).select_related(
        'freelancerprofile', 'companyprofile', 'sonstiges'
    ).annotate(
        app_count=Count("application")
    )

    # 🔹 Filterparameter auslesen
    search_query = request.GET.get("q", "").strip()
    category_search = request.GET.get("cat_q", "").strip()
    user_type = request.GET.get("type", "").strip()
    location = request.GET.get("location", "").strip()
    category_id = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "").strip()

    # 🔹 TYP-FILTER
    if user_type == "freelancer":
        qs = qs.filter(account_type="freelancer")
    elif user_type == "company":
        qs = qs.filter(account_type="company")
    elif user_type == "other":
        qs = qs.filter(account_type="sonstiges")

    # 🔹 KATEGORIE-SUCHE (korrigiert) + LEAD ERSTELLUNG
    if category_search:
        # Lead erstellen wenn nach Kategorie gesucht wird
        if request.user.is_authenticated:
            Lead.objects.create(
                company=request.user,
                name=f"Kategorie-Suche: {category_search}",
                email=request.user.email,
                phone=request.user.freelancerprofile.phone_number if hasattr(request.user, "freelancerprofile") else "",

                source="category_search",
                message=f"Benutzer hat nach Kategorie gesucht: '{category_search}'"
            )
        
        qs = qs.filter(
            Q(freelancerprofile__isnull=False, freelancerprofile__Categorys__name__icontains=category_search) |
            Q(companyprofile__isnull=False, companyprofile__Categorys__name__icontains=category_search) |
            Q(sonstiges__isnull=False, sonstiges__Categorys__name__icontains=category_search)
        ).distinct()

    # 🔹 KATEGORIE-FILTER (Dropdown) + LEAD ERSTELLUNG
    if category_id and category_id.isdigit():
        cat_id = int(category_id)
        
        # Lead erstellen wenn Kategorie aus Dropdown gewählt wurde
        try:
            selected_cat = Category.objects.get(id=cat_id)
            if request.user.is_authenticated:
                Lead.objects.create(
                    company=request.user,
                    name=f"Kategorie-Suche: {category_search}",
                    email=request.user.email,
                    phone=request.user.freelancerprofile.phone_number if hasattr(request.user, "freelancerprofile") else "",
                    
                    source="category_search",
                    message=f"Benutzer hat nach Kategorie gesucht: '{category_search}'"
                )
            selected_cat.lead_set.add(Lead.objects.latest('id'))  # Optional: Kategorie verknüpfen
        except Category.DoesNotExist:
            pass
        
        qs = qs.filter(
            Q(freelancerprofile__isnull=False, freelancerprofile__Categorys__id=cat_id) |
            Q(companyprofile__isnull=False, companyprofile__Categorys__id=cat_id) |
            Q(sonstiges__isnull=False, sonstiges__Categorys__id=cat_id)
        ).distinct()

    # 🔹 STANDORT-FILTER (korrigiert)
    if location:
        qs = qs.filter(
            Q(freelancerprofile__isnull=False, freelancerprofile__location__icontains=location) |
            Q(companyprofile__isnull=False, companyprofile__location__icontains=location) |
            Q(sonstiges__isnull=False, sonstiges__location__icontains=location)
        )

    # 🔹 HAUPT-SUCHFUNKTION (korrigiert - ohne bio__icontains)
    if search_query:
        search_terms = search_query.split()
        
        for term in search_terms:
            # Basis-Suche auf User-Ebene
            user_filter = Q(
                Q(username__icontains=term) |
                Q(email__icontains=term) |
                Q(first_name__icontains=term) |
                Q(last_name__icontains=term)
            )
            
            # Kategorie-Suche (sicher)
            category_filter = Q(
                Q(freelancerprofile__isnull=False, freelancerprofile__Categorys__name__icontains=term) |
                Q(companyprofile__isnull=False, companyprofile__Categorys__name__icontains=term) |
                Q(sonstiges__isnull=False, sonstiges__Categorys__name__icontains=term)
            )
            
            qs = qs.filter(user_filter | category_filter).distinct()

    # 🔹 SORTIERUNG
    if sort == "applications":
        qs = qs.order_by("-app_count")
    elif sort == "newest":
        qs = qs.order_by("-date_joined")
    elif sort == "name":
        qs = qs.order_by("username")
    else:
        qs = qs.order_by("-app_count", "-date_joined")

    # 🔹 PAGINATION
    paginator = Paginator(qs.distinct(), 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # 🔹 KATEGORIEN
    categories = Category.objects.all().order_by("name")
    
    # Für popular_categories - prüfe zuerst dein Modell
    try:
        popular_categories = Category.objects.annotate(
            user_count=Count('freelancerprofile', distinct=True) + 
                      Count('companyprofile', distinct=True) + 
                      Count('sonstiges', distinct=True)
        ).order_by('-user_count')[:5]
    except:
        # Fallback falls related_names anders sind
        popular_categories = Category.objects.all().order_by('name')[:5]

    # 🔹 AKTIVE KATEGORIE
    selected_category_obj = None
    if category_id and category_id.isdigit():
        try:
            selected_category_obj = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            pass

    return render(
        request,
        "orders/freelancer_list.html",
        {
            "freelancers": page_obj,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
            "categories": categories,
            "popular_categories": popular_categories,
            "selected_category": int(category_id) if category_id and category_id.isdigit() else None,
            "selected_category_name": selected_category_obj.name if selected_category_obj else "",
            "location": location,
            "q": search_query,
            "cat_q": category_search,
            "user_type": user_type,
            "sort": sort,
        },
    )

@login_required
def start_chat(request, username):
    other_user = get_object_or_404(User, username=username)
    chat = Chat.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(request.user, other_user)
    return redirect("chat_detail", pk=chat.pk)

@login_required
def chat_detail(request, pk):
    chat = get_object_or_404(Chat, pk=pk, participants=request.user)

    # Den anderen Teilnehmer bestimmen
    other_user = chat.participants.exclude(id=request.user.id).first()

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.chat = chat
            msg.sender = request.user
            msg.save()
            return redirect("chat_detail", pk=chat.pk)
    else:
        form = MessageForm()

    messages = chat.messages.order_by("created_at")
    return render(request, "chats/chat_detail.html", {
        "chat": chat,
        "messages": messages,
        "form": form,
        "other_user": other_user,   # 👈 für Template
    })

@login_required
def chat_list(request):
    chats = Chat.objects.filter(participants=request.user).order_by("-created_at")
    return render(request, "chats/chat_list.html", {"chats": chats})