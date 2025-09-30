from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ACCOUNT_TYPES = [
        ("freelancer","Freelancer"),
        ("company","Unternehmen"),
        ("freiberuflich","Freiberuflich"),
        ("other","Sonstiges"),
    ]
    account_type = models.CharField(max_length=30, choices=ACCOUNT_TYPES, default="freelancer")
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    # optional: fields like company name for company user
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)