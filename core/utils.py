import random, string
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from django.utils import timezone
from datetime import timedelta
from .models import TwoFactorCode

def random_code(n=6):
    return "".join(random.choices("0123456789", k=n))

def send_email_code(email, purpose="2fa", user=None):
    code = random_code()
    # store code in model
    TwoFactorCode.objects.create(user=user, code=code, purpose=purpose, expires_at=timezone.now()+timedelta(minutes=10))
    send_mail(subject=f"Dein {purpose} Code", message=f"Code: {code}", from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email])

def send_sms_code(phone, purpose="2fa", user=None):
    code = random_code()
    TwoFactorCode.objects.create(user=user, code=code, purpose=purpose, expires_at=timezone.now()+timedelta(minutes=10))
    if settings.TWILIO_ACCOUNT_SID:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(body=f"Dein {purpose} Code: {code}", from_=settings.TWILIO_FROM, to=phone)

def verify_twofa_code(user, code, purpose="2fa"):
    qs = TwoFactorCode.objects.filter(user=user, code=code, purpose=purpose, used=False, expires_at__gte=timezone.now()).order_by("-created_at")
    if qs.exists():
        t = qs.first()
        t.used = True
        t.save()
        return True
    return False
