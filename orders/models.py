from django.db import models
from django.conf import settings
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    STATUS_CHOICES = [
        ("open", "Offen"),
        ("in_progress", "In Arbeit"),
        ("closed", "Vergeben"),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_orders")
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="open")
    category = models.ManyToManyField(Category, blank=True)  # <-- hier ändern

    def __str__(self):
        return self.title


# models.py
class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Application(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    chat = models.OneToOneField(Chat, on_delete=models.SET_NULL, null=True, blank=True)  # <---

