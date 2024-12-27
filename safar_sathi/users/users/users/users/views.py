from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import create_user, create_otp, verify_otp, generate_token

@csrf_exempt
def send_otp_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        phone_number = data.get("phone_number")
        if not phone_number:
            return JsonResponse({"error": "Phone number is required"}, status=400)

        user = create_user(phone_number)
        otp_code = create_otp(user)

        # Simulate sending OTP (you can integrate Twilio here)
        print(f"Sending OTP {otp_code} to {phone_number}")
        return JsonResponse({"message": "OTP sent successfully", "user_id": user.id})

@csrf_exempt
def verify_otp_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        phone_number = data.get("phone_number")
        otp_code = data.get("otp_code")

        if not phone_number or not otp_code:
            return JsonResponse({"error": "Phone number and OTP code are required"}, status=400)

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        if verify_otp(user, otp_code):
            token = generate_token(user.id)
            return JsonResponse({"message": "OTP verified successfully", "token": token})
        return JsonResponse({"error": "Invalid or expired OTP"}, status=400)
