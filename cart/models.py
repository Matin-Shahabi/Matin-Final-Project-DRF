from django.db import models
from users.models import CustomUser
from products.models import ProductStore

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="carts")

    def _str_(self):
        return f"{self.user.username}'s Cart"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_store = models.ForeignKey(ProductStore, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def _str_(self):
        return f"{self.quantity} x {self.product_store.product.name} from {self.product_store.store.name}"