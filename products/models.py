from django.db import models
from categories.models import Category
from stores.models import Store
from users.models import BaseModel

class Product(BaseModel):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # discount model / one to many
    
    def __str__(self):
        return self.name
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    
    def __str__(self):
        return f"Image for {self.product.name}"
    


class ProductStore(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_stores")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="product_stores")
    store_price = models.DecimalField(max_digits=10, decimal_places=2)
    store_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.product.name} in {self.store.name}"
    
    @property
    def discount_price(self):
        return self.store_price * (1 - self.store_discount / 100)