from django.db import models
from users.models import CustomUser,BaseModel
from products.models import Product
from stores.models import Store

class Review(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.FloatField()
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.user.username if self.user else 'Anonymous'} for {self.product.name} - {self.rating}/5"
    


class StoreReview(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="reviews")
    rating = models.FloatField()
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.user.username if self.user else 'Anonymous'} for {self.store.name} - {self.rating}/5"
