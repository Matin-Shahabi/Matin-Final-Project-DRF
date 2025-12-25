from django.db import models
from django.utils import timezone

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ("percent", "Percent"),
        ("fixed", "Fixed"),
    )

    code = models.CharField(
        max_length=50,
        unique=True
    )

    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,default="percent"
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,default=0.00
    )

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True,blank=True)

    is_active = models.BooleanField(default=True)

    usage_limit = models.PositiveIntegerField()
    usage_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code} ({self.discount_type})"