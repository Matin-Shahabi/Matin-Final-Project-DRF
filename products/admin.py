from django.contrib import admin
from .models import Product, ProductStore,ProductImage

admin.site.register(Product)
admin.site.register(ProductStore)
admin.site.register(ProductImage)