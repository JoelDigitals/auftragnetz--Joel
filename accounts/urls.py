from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path('register/', views.register, name='register'),
    path('register/sso/', views.sso_connect, name='sso_connect'),
    path('register/callback/', views.sso_callback, name='sso_callback'),
]