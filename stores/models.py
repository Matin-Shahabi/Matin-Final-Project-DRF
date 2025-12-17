from django.db import models
from users.models import CustomUser

class Store(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=255)
    address = models.TextField()
    logo = models.ImageField(upload_to="store_logos/")
    rating = models.FloatField(default=0)
    sales_count = models.IntegerField(default=0)
    total_product = models.IntegerField(default=0)

    def _str_(self):
        return self.name