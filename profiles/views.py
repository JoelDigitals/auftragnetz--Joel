from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import User
from .models import CompanyProfile, FreelancerProfile, Sonstiges, ProfileVisit
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
            return redirect("profile_dashboard")  # Dashboard-Ansicht
    else:
        form = form_class(instance=profile)

    return render(request, "profiles/edit_profile.html", {"form": form, "profile": profile})

@login_required
def profile_detail(request, username):
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
    if request.user != user:
        profile.visitor_count = profile.visitor_count + 1
        profile.save(update_fields=["visitor_count"])
        # Optional: verhindern, dass mehrere Visits am selben Tag von demselben User gezählt werden
        ProfileVisit.objects.create(profile=user, visitor=request.user)

    return render(
        request,
        "profiles/profile_detail.html",
        {
            "profile": profile,
            "profile_user": user,
            "profile_type": profile_type,
        },
    )
