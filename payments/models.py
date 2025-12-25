from django.db import models
from django.utils import timezone


class Payment(models.Model):
    PAYMENT_TYPES = (
        ("card", "Card"),
        ("cash", "Cash"),
        ("online", "Online"),
    )
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    )
    reference_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )  # ref_id درگاه

    transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )  # authority / gateway tx id

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payment"
    )    
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    type = models.CharField(max_length=10, choices=PAYMENT_TYPES,default="online")
    paid_date = models.DateField(default=timezone.now)
    paid_time = models.TimeField(default=timezone.now)
    # transaction id 
    def __str__(self):
        return f"{self.type} payment of {self.amount} for Order #{self.order.id}"
    


class Transaction(models.Model):
    STATUS_CHOICES = (
        ("initiated", "Initiated"),
        ("success", "Success"),
        ("failed", "Failed"),
    )

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    gateway = models.CharField(
        max_length=50
    )  # مثلا zarinpal, stripe

    reference_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,default="initiated"
    )

    raw_response = models.JSONField(
        null=True,
        blank=True
    )  # جواب کامل درگاه (خیلی مهم)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction #{self.id} - {self.status}"