from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
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
    # 🔹 Alle relevanten User laden
    qs = User.objects.filter(account_type__in=["freelancer", "company", "sonstiges"]).annotate(
        app_count=Count("application")
    )

    # 🔹 Filterparameter auslesen
    search_categories = request.GET.getlist("category")  # mehrere möglich
    location = request.GET.get("location", "").strip()
    q = request.GET.get("q", "").strip()

    # 🔹 Suchtext (Name, E-Mail)
    if q:
        qs = qs.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(freelancerprofile__Categorys__name__icontains=q) |
            Q(companyprofile__Categorys__name__icontains=q) |
            Q(sonstiges__Categorys__name__icontains=q)
        ).distinct()

    # 🔹 Kategorie-/Skill-Filter
    if search_categories:
        qs = qs.filter(
            Q(freelancerprofile__Categorys__id__in=search_categories) |
            Q(companyprofile__Categorys__id__in=search_categories) |
            Q(sonstiges__Categorys__id__in=search_categories)
        ).distinct()

        # 💡 Lead automatisch erstellen
        if request.user.is_authenticated:
            cat_objs = Category.objects.filter(id__in=search_categories)
            lead = Lead.objects.create(
                company=request.user,
                name=f"Suchanfrage nach {', '.join(c.name for c in cat_objs)}",
                email=request.user.email,
                phone=getattr(request.user, "phone_number", ""),
                message=f"{request.user.username} hat nach Freelancern/Companys in {', '.join(c.name for c in cat_objs)} gesucht.",
                source="Freelancer Suche",
                status="new",
            )
            lead.category.set(cat_objs)
        

    # 🔹 Standortfilter
    if location:
        qs = qs.filter(
            Q(freelancerprofile__location__icontains=location) |
            Q(companyprofile__location__icontains=location) |
            Q(sonstiges__location__icontains=location)
        )

    # 🔹 Kategorien & Produkte laden
    categories = Category.objects.all()
    products = Product.objects.all()

    return render(
        request,
        "orders/freelancer_list.html",
        {
            "freelancers": qs.distinct(),
            "categories": categories,
            "products": products,
            "selected_categories": [int(c) for c in search_categories],
            "location": location,
            "q": q,
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