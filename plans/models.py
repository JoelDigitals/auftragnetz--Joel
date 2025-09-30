from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

class Plan(models.Model):
    name = models.CharField(max_length=50)
    applications_limit_per_month = models.IntegerField(null=True, blank=True)  # None = unlimited
    product_limit = models.IntegerField(null=True, blank=True)
    booster_limit = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2)  # e.g., 9999.99
    description = models.TextField(blank=True)
    discount_percent = models.IntegerField(default=0)  # e.g., 20 for 20% discount
    is_active = models.BooleanField(default=True)

    def discounted_price(self):
        if self.discount_percent > 0:
            discount_amount = (self.discount_percent / 100) * float(self.price)
            return float(self.price) - discount_amount
        return float(self.price)
    
    def __str__(self):
        return self.name

class Code(models.Model):
    code = models.CharField(max_length=50, unique=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.code

class UserPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    activated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    @classmethod
    def activate_code(cls, user, code_obj):
        if code_obj.is_used:
            return False, "Code bereits eingelöst"
        expires = timezone.now() + timedelta(days=365)
        up = cls.objects.create(user=user, plan=code_obj.plan, expires_at=expires)
        code_obj.is_used = True
        code_obj.save()
        return True, up

    def __str__(self):
        return super().__str__() + f" - {self.user.username} ({self.plan.name})"
    
