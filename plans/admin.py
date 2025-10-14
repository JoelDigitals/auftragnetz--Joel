from django.contrib import admin
from .models import Plan, Code, UserPlan

# Register your models here.
admin.site.register(Plan)
admin.site.register(Code)
admin.site.register(UserPlan)