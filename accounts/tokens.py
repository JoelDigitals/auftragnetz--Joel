# Platzhalter — du kannst Django's signing oder django-allauth verwenden
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
