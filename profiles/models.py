from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from orders.models import Category

class CompanyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    company_type = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    wages_info = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    social_links = models.TextField(blank=True)
    description = models.TextField(blank=True)
    visitor_count = models.PositiveIntegerField(default=0)
    Categorys = models.ManyToManyField(Category, blank=True, related_name="company_Categorys")

    def __str__(self):
        return self.company_name


class FreelancerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    Categorys = models.ManyToManyField(Category, blank=True, related_name="freelancer_Categorys")
    hourly_rate = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    availability = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    languages = models.CharField(max_length=255, blank=True)
    certifications = models.TextField(blank=True)
    social_links = models.TextField(blank=True)
    portfolio_link = models.URLField(blank=True)
    visitor_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}"


class Sonstiges(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    additional_info = models.TextField(blank=True)
    portfolio_link = models.URLField(blank=True)
    availability = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    languages = models.CharField(max_length=255, blank=True)
    certifications = models.TextField(blank=True)
    social_links = models.TextField(blank=True)
    resume = models.FileField(upload_to="resumes/", null=True, blank=True)
    visitor_count = models.PositiveIntegerField(default=0)
    Categorys = models.ManyToManyField(Category, blank=True, related_name="sonstiges_Categorys")

    def __str__(self):
        return f"{self.user.username}"


class ProfileVisit(models.Model):
    profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile_visits")
    visitor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="visited_profiles")
    visited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.visitor} visited {self.profile} on {self.visited_at}"


class Review(models.Model):
    """Bewertungen für Profile (Company, Freelancer, Sonstiges)"""
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    profile_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="received_reviews"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="given_reviews"
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    # Optional: Verknüpfung mit einem Projekt/Auftrag
    project = models.ForeignKey(
        'orders.Order', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)  # Für Moderation

    class Meta:
        unique_together = ['profile_user', 'reviewer']  # Ein Review pro User
        ordering = ['-created_at']
        verbose_name = "Bewertung"
        verbose_name_plural = "Bewertungen"

    def __str__(self):
        return f"{self.reviewer.username} → {self.profile_user.username}: {self.rating}★"

    @property
    def rating_stars(self):
        """Gibt Liste für Template-Loop zurück"""
        return range(self.rating)
    
    @property
    def empty_stars(self):
        """Gibt leere Sterne für Template zurück"""
        return range(5 - self.rating)