import jwt
import random
from django.utils.timezone import now, timedelta
from .models import User, OTP
from django.conf import settings

def generate_token(user_id):
    return jwt.encode({"user_id": user_id, "exp": now() + timedelta(hours=1000)}, settings.SECRET_KEY, algorithm="HS256")

def create_user(phone_number):
    user, created = User.objects.get_or_create(phone_number=phone_number)
    return user

def create_otp(user, expires_in_minutes=5):
    otp_code = str(random.randint(100000, 999999))
    expires_at = now() + timedelta(minutes=expires_in_minutes)
    OTP.objects.create(user=user, otp_code=otp_code, expires_at=expires_at)
    return otp_code

def verify_otp(user, otp_code):
    otp = OTP.objects.filter(user=user, otp_code=otp_code, expires_at__gt=now()).order_by('-created_at').first()
    return otp is not None
