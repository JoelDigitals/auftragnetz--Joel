from django.db import models
from django.conf import settings
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