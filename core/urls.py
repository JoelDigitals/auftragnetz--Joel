from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from products.sitemaps import ProductSitemap

sitemaps = {
    "products": ProductSitemap,
}

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/register/step1/", views.registration_step1, name="registration_step1"),
    path("accounts/register/step2/", views.registration_step2, name="registration_step2"),
    path("accounts/register/done/", views.registration_done, name="registration_done"),
    path("orders/create/", views.create_order, name="create_order"),
    path("company/dashboard/", views.company_dashboard, name="company_dashboard"),
    path("leads/settings/", views.lead_preferences, name="lead_preferences"),
    path('auth/joel/callback/', views.joel_callback, name='joel_callback'),

    
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}),
]
