from django.db import models
from django.conf import settings
from orders.models import Category

class TwoFactorCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    purpose = models.CharField(max_length=30, default="2fa")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

class Lead(models.Model):
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="company_leads", null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    message = models.TextField(blank=True)
    source = models.CharField(max_length=255, blank=True)
    category = models.ManyToManyField(Category, blank=True)
    status = models.CharField(max_length=50, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.source})"
    
class LeadPreference(models.Model):
    company = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lead_preference"
    )
    categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return f"Lead Preferences for {self.company.username}"