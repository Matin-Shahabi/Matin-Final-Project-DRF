from django.db import models
from categories.models import Category
from stores.models import Store

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to="products/")
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def _str_(self):
        return self.name

class ProductStore(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_stores")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="product_stores")
    store_price = models.DecimalField(max_digits=10, decimal_places=2)
    store_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateField(auto_now_add=True)

    def _str_(self):
        return f"{self.product.name} in {self.store.name}"