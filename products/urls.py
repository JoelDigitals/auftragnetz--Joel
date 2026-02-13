from django.urls import path
from . import views

urlpatterns = [
    path("products/create/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("products/image/<int:pk>/delete/", views.product_image_delete, name="product_image_delete"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("", views.product_list, name="product_list"),
]
