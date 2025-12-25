from django.db import models
from users.models import CustomUser
from products.models import Product

class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.FloatField()
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.user.username if self.user else 'Anonymous'} for {self.product.name} - {self.rating}/5"