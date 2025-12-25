from rest_framework import serializers
from .models import Product, ProductStore
from categories.serializers import CategorySerializer




class ProductListSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    best_price = serializers.SerializerMethodField()
    best_seller = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ["id", "name", "description", "categories", "rating", "images", "stock", "best_price", "best_seller"]

    def get_categories(self, obj):
        # در اینجا فرض بر اینه که Product فقط یک category داره، اما می‌توانیم همه children را هم اضافه کنیم
        return [CategorySerializer(obj.category).data]

    def get_best_price(self, obj):
        store_item = obj.product_stores.filter(is_active=True).order_by("store_price").first()
        return store_item.discount_price if store_item else None

    def get_best_seller(self, obj):
        store_item = obj.product_stores.filter(is_active=True).order_by("store_price").first()
        return store_item.store.name if store_item else None




class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    store = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'image',
            'price',
            'discount_price',
            'category',
            'store',
            'description',
            'rating',
            'created_at',
        ]