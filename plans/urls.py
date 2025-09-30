
from django.urls import path
from . import views

urlpatterns = [
    path("", views.plans_overview, name="plans"),
    path("redeem/", views.redeem_code, name="redeem_code"),
]
