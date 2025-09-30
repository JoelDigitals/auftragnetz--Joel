from django.urls import path
from . import views

urlpatterns = [
    path("edit/", views.edit_profile, name="edit_profile"),
    path("<str:username>/", views.profile_detail, name="profile_detail"),
]
