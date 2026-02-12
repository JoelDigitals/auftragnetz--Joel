from django.urls import path
from . import views

urlpatterns = [
    path("edit/", views.edit_profile, name="edit_profile"),
    path("<str:username>/", views.profile_detail, name="profile_detail"),
    path('<str:username>/review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('api/<str:username>/review-status/', views.check_review_status, name='check_review_status'),
]
