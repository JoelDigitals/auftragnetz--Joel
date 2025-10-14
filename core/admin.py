from django.contrib import admin
from .models import TwoFactorCode, Lead

# Register your models here.
admin.site.register(TwoFactorCode)
admin.site.register(Lead)