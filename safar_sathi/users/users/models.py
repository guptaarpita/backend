from django.db import models
from django.utils.timezone import now

class User(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    jwt_token = models.TextField(default="")
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    religion = models.CharField(max_length=100, null=True, blank=True)
    drinking = models.BooleanField(default=False)
    smoking = models.BooleanField(default=False)
    preferred_gender = models.CharField(max_length=10, null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_location = models.CharField(max_length=100, null=True, blank=True)
    prompt = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=now)

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=now)
