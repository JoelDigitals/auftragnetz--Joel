from django.contrib import admin
from .models import FreelancerProfile, CompanyProfile, Sonstiges

# Register your models here.
admin.site.register(FreelancerProfile)
admin.site.register(CompanyProfile)
admin.site.register(Sonstiges)