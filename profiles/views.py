from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from accounts.models import User
from products.models import Product
from .models import CompanyProfile, FreelancerProfile, Sonstiges, ProfileVisit, Review
from .forms import CompanyProfileForm, FreelancerProfileForm, SonstigesForm


@login_required
def edit_profile(request):
    user = request.user

    # passendes Profil holen oder erstellen
    if user.account_type == "company":
        profile, _ = CompanyProfile.objects.get_or_create(user=user)
        form_class = CompanyProfileForm
    elif user.account_type == "freelancer":
        profile, _ = FreelancerProfile.objects.get_or_create(user=user)
        form_class = FreelancerProfileForm
    else:  # "freiberuflich" oder "other"
        profile, _ = Sonstiges.objects.get_or_create(user=user)
        form_class = SonstigesForm

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil erfolgreich aktualisiert!")
            return redirect("profile_detail", username=user.username)
    else:
        form = form_class(instance=profile)

    return render(request, "profiles/edit_profile.html", {"form": form, "profile": profile})


def profile_detail(request, username):
    """Öffentliche Profilansicht mit Produkten und Bewertungen"""
    user = get_object_or_404(User, username=username)

    # Profil finden
    profile = None
    profile_type = None
    
    if hasattr(user, "companyprofile"):
        profile = user.companyprofile
        profile_type = "company"
    elif hasattr(user, "freelancerprofile"):
        profile = user.freelancerprofile
        profile_type = "freelancer"
    elif hasattr(user, "sonstiges"):
        profile = user.sonstiges
        profile_type = "sonstiges"

    if not profile:
        return render(request, "profiles/no_profile.html", {"user": user})

    # Besucher zählen (aber nicht sich selbst)
    if request.user.is_authenticated and request.user != user:
        # Prüfen ob heute schon gezählt wurde (optional, verhindert Spam)
        from datetime import datetime, timedelta
        today = datetime.now().date()
        already_visited = ProfileVisit.objects.filter(
            profile=user, 
            visitor=request.user,
            visited_at__date=today
        ).exists()
        
        if not already_visited:
            profile.visitor_count += 1
            profile.save(update_fields=["visitor_count"])
            ProfileVisit.objects.create(profile=user, visitor=request.user)

    # === PRODUKTE LADEN ===
    products = Product.objects.filter(
        owner=user, 
        is_active=True
    ).order_by('-is_boosted', '-created_at')

    # === BEWERTUNGEN LADEN & PAGINIEREN ===
    reviews_list = Review.objects.filter(
        profile_user=user,
        is_approved=True
    ).select_related('reviewer').order_by('-created_at')
    
    # Pagination: 5 Reviews pro Seite
    paginator = Paginator(reviews_list, 5)
    page_number = request.GET.get('page')
    reviews = paginator.get_page(page_number)

    # === BEWERTUNGSSTATISTIK BERECHNEN ===
    reviews_count = reviews_list.count()
    average_rating = reviews_list.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Stern-Verteilung für Balkendiagramm
    rating_counts = {}
    rating_percentages = {}
    
    for star in range(1, 6):
        count = reviews_list.filter(rating=star).count()
        rating_counts[star] = count
        rating_percentages[star] = (count / reviews_count * 100) if reviews_count > 0 else 0

    # Prüfen ob aktueller User schon bewertet hat
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(
            profile_user=user,
            reviewer=request.user
        ).exists()

    context = {
        "profile": profile,
        "profile_user": user,
        "profile_type": profile_type,
        "products": products,
        "reviews": reviews,
        "reviews_count": reviews_count,
        "average_rating": round(average_rating, 1),
        "rating_counts": rating_counts,
        "rating_percentages": rating_percentages,
        "user_has_reviewed": user_has_reviewed,
    }
    
    return render(request, "profiles/profile_detail.html", context)


@login_required
@require_POST
def add_review(request, username):
    """Neue Bewertung hinzufügen"""
    profile_user = get_object_or_404(User, username=username)
    
    # Verhindern dass man sich selbst bewertet
    if request.user == profile_user:
        messages.error(request, "Du kannst dich nicht selbst bewerten!")
        return redirect("profile_detail", username=username)
    
    # Prüfen ob schon bewertet
    existing_review = Review.objects.filter(
        profile_user=profile_user,
        reviewer=request.user
    ).first()
    
    rating = request.POST.get('rating')
    title = request.POST.get('title', '').strip()
    comment = request.POST.get('comment', '').strip()
    
    if not rating or not comment:
        messages.error(request, "Bitte gib eine Bewertung und einen Kommentar ein.")
        return redirect("profile_detail", username=username)
    
    try:
        rating = int(rating)
        if not 1 <= rating <= 5:
            raise ValueError
    except ValueError:
        messages.error(request, "Ungültige Bewertung.")
        return redirect("profile_detail", username=username)
    
    if existing_review:
        # Update existing review
        existing_review.rating = rating
        existing_review.title = title
        existing_review.comment = comment
        existing_review.save()
        messages.success(request, "Deine Bewertung wurde aktualisiert!")
    else:
        # Create new review
        Review.objects.create(
            profile_user=profile_user,
            reviewer=request.user,
            rating=rating,
            title=title,
            comment=comment
        )
        messages.success(request, "Deine Bewertung wurde hinzugefügt!")
    
    # Zurück zum Reviews-Tab
    return redirect(f"{request.build_absolute_uri('/')}profiles/{username}/?tab=reviews")


@login_required
def delete_review(request, review_id):
    """Eigene Bewertung löschen"""
    review = get_object_or_404(Review, id=review_id, reviewer=request.user)
    username = review.profile_user.username
    review.delete()
    messages.success(request, "Bewertung gelöscht.")
    return redirect("profile_detail", username=username)


# API Endpoint für AJAX (optional)
@login_required
def check_review_status(request, username):
    """Prüft ob User schon bewertet hat (für AJAX)"""
    user = get_object_or_404(User, username=username)
    has_reviewed = Review.objects.filter(
        profile_user=user,
        reviewer=request.user
    ).exists()
    return JsonResponse({'has_reviewed': has_reviewed})