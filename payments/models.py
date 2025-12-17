from django.db import models
from orders.models import Order

class Payment(models.Model):
    PAYMENT_TYPES = (
        ("card", "Card"),
        ("cash", "Cash"),
        ("online", "Online"),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=PAYMENT_TYPES)
    paid_date = models.DateField()
    paid_time = models.TimeField()

    def _str_(self):
        return f"{self.type} payment of {self.amount} for Order #{self.order.id}"