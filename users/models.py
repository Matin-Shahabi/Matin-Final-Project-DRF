from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("guest", "Guest"),
        ("customer", "Customer"),
        ("seller", "Seller"),
        ("admin", "Admin"),
    )

    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="guest")

    def _str_(self):
        return f"{self.username} ({self.email})"

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="addresses")
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)

    def _str_(self):
        return f"{self.user.username} - {self.city}, {self.province}"

class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=10)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def _str_(self):
        return f"OTP {self.code} for {self.user.username} ({'Used' if self.is_used else 'Unused'})"