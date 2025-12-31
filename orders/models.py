from django.db import models
from users.models import CustomUser,BaseModel
from stores.models import Store
from products.models import ProductStore
from coupons.models import Coupon

class Order(BaseModel):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders")
    shipping_address = models.ForeignKey("users.Address", on_delete=models.SET_NULL, null=True, related_name="shipping_orders")
    billing_address = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product_id_snapshot = models.IntegerField()
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    discount_snapshot = models.DecimalField(max_digits=5, decimal_places=2)
    final_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.quantity} x ProductID {self.product_id_snapshot} in Order #{self.order.id}"

class OrderStatusHistory(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.order} -> {self.status} at {self.changed_at}"