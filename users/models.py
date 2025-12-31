from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone



class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)   
    updated_at = models.DateTimeField(auto_now=True)      
    deleted_at = models.DateTimeField(null=True, blank=True)  
    is_active = models.BooleanField(default=True)         
    
    class Meta:
        abstract = True  # هیچ جدول مستقیمی ساخته نمیشه، فقط ارث بری

    def soft_delete(self):
        """حذف نرم: فقط تاریخ حذف رو می‌ذاره و رکورد غیر فعال می‌کنه"""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        """بازگرداندن رکورد حذف شده"""
        self.deleted_at = None
        self.is_active = True
        self.save()



class CustomUser(AbstractUser,BaseModel):
    ROLE_CHOICES = (
        ("guest", "Guest"),
        ("customer", "Customer"),
        ("seller", "Seller"),
        ("admin", "Admin"),
    )
    username = models.CharField(max_length=20, unique=True)  # شماره موبایل
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    avatar = models.ImageField(
        upload_to="users/avatars/",
        null=True,
        blank=True
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="guest")

    def __str__(self):
        return f"{self.username} ({self.email})"

class Address(BaseModel):
    LABEL_CHOICES = (
        ("home", "Home"),
        ("work", "Work"),
        ("office", "Office"),
        ("other", "Other"),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(
        max_length=20,
        choices=LABEL_CHOICES,
        default="home"
    )
    country = models.CharField(
        max_length=100,
        default="Iran"
    )
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.city}, {self.province}"


class OTP(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=10)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP {self.code} for {self.user.username} ({'Used' if self.is_used else 'Unused'})"