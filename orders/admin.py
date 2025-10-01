from django.contrib import admin
from .models import Category, Order, Application, Chat, Message

# Register your models here.
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Application)
admin.site.register(Chat)
admin.site.register(Message)