from django.contrib import admin
from .models import FreelancerProfile, CompanyProfile, Sonstiges, Review, ProfileVisit

# Register your models here.
admin.site.register(FreelancerProfile)
admin.site.register(CompanyProfile)
admin.site.register(Sonstiges)
admin.site.register(ProfileVisit)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['profile_user', 'reviewer', 'rating', 'created_at', 'is_approved']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['profile_user__username', 'reviewer__username', 'comment']