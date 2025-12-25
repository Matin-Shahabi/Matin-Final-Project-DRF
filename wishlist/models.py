from django.db import models
from users.models import CustomUser
from products.models import Product

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="wishlists")

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.username}'s wishlist"