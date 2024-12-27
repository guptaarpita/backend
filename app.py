from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
import json

# Models
class User(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)

class OTP(models.Model):
    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

# Helper functions for OTP
import random

def send_otp(phone_number):
    otp_code = str(random.randint(100000, 999999))
    OTP.objects.create(phone_number=phone_number, otp_code=otp_code)
    # Here, you can integrate with an SMS service to send the OTP.
    return {"message": "OTP sent successfully", "otp": otp_code}  # Remove 'otp' in production.

def verify_otp(phone_number, otp_code):
    try:
        otp_record = OTP.objects.filter(phone_number=phone_number, otp_code=otp_code).latest('created_at')
        return {"message": "OTP verified successfully"}
    except OTP.DoesNotExist:
        return {"error": "Invalid OTP or phone number"}

# Views
@csrf_exempt
def send_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phoneNumber')

        if not phone_number:
            return JsonResponse({"error": "Phone number is required"}, status=400)

        response = send_otp(phone_number)
        return JsonResponse(response)

@csrf_exempt
def verify_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phoneNumber')
        otp_code = data.get('otpCode')

        if not phone_number or not otp_code:
            return JsonResponse({"error": "Phone number and OTP code are required"}, status=400)

        response = verify_otp(phone_number, otp_code)
        return JsonResponse(response)

# URLs
from django.urls import path

urlpatterns = [
    path('auth/phone/send-code', send_code, name='send_code'),
    path('auth/phone/verify-code', verify_code, name='verify_code'),
]
