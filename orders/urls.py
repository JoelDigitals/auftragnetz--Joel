from django.urls import path
from . import views

urlpatterns = [
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("orders/create/", views.order_create, name="order_create"),
    path("orders/new/", views.create_order, name="create_order"),
    path("orders/<int:pk>/apply/", views.apply_order, name="apply_order"),
    path("freelancers/", views.freelancer_list, name="freelancer_list"),
    path("chats/<int:pk>/", views.chat_detail, name="chat_detail"),
    path("chats/", views.chat_list, name="chat_list"),
    path("start_chat/<str:username>/", views.start_chat, name="start_chat"),
]
