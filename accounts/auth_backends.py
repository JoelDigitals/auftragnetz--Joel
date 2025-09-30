from django.contrib.auth.backends import ModelBackend
from .models import User

class EmailConfirmedBackend(ModelBackend):
    def user_can_authenticate(self, user):
        is_active = super().user_can_authenticate(user)
        return is_active and user.email_confirmed
