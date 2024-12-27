from django.utils.timezone import now, timedelta
from django.db import transaction
from django.http import JsonResponse
from twilio.rest import Client
from django.conf import settings
import jwt
import random
import logging
from .models import User, OTP

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Twilio client
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

# Generate JWT Token
def generate_token(user_id):
    try:
        token = jwt.encode({"user_id": user_id, "exp": now() + timedelta(hours=1000)}, settings.JWT_SECRET_KEY, algorithm="HS256")
        return token
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        return None

# Normalize Phone Number
def normalize_phone_number(phone_number):
    if not phone_number.startswith("+"):
        return f"+91{phone_number}"  # Assuming India as default country code
    return phone_number

# Send OTP
def send_otp(phone_number):
    try:
        normalized_phone_number = normalize_phone_number(phone_number)

        # Check if user exists or create a new user
        user, created = User.objects.get_or_create(phone_number=normalized_phone_number)

        # Generate a 6-digit OTP
        otp_code = str(random.randint(100000, 999999))

        # Set OTP expiration (5 minutes)
        expires_at = now() + timedelta(minutes=5)

        # Insert OTP into the database
        OTP.objects.create(phone_number=user.phone_number, otp_code=otp_code, created_at=now())

        # Send OTP via Twilio
        twilio_client.messages.create(
            body=f"Your OTP code is: {otp_code}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=normalized_phone_number,
        )

        return {"message": "OTP sent successfully", "user_id": user.id}
    except Exception as e:
        logger.error(f"Error sending OTP: {e}")
        return {"error": "Failed to send OTP"}

# Verify OTP
def verify_otp_handler(phone_number, otp_code):
    try:
        normalized_phone_number = normalize_phone_number(phone_number)

        # Check if user exists
        try:
            user = User.objects.get(phone_number=normalized_phone_number)
        except User.DoesNotExist:
            return {"error": "User not found"}

        # Verify OTP
        otp_record = OTP.objects.filter(phone_number=normalized_phone_number, otp_code=otp_code).order_by('-created_at').first()
        if otp_record and otp_record.created_at > now() - timedelta(minutes=5):
            token = generate_token(user.id)
            return {"message": "OTP verified successfully", "token": token}
        else:
            return {"error": "Invalid or expired OTP"}
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        return {"error": "Failed to verify OTP"}

# Example usage in views
from django.views.decorators.csrf import csrf_exempt
import json

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

        response = verify_otp_handler(phone_number, otp_code)
        return JsonResponse(response)
