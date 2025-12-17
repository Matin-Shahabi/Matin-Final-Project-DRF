from django.db import models
from users.models import CustomUser
from products.models import Product

class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.FloatField()
    comment = models.TextField()

    def _str_(self):
        return f"Review by {self.user.username} for {self.product.name} - {self.rating}/5"