
from rest_framework import serializers
from .models import ProductStore
from products.models import Product
from categories.models import Category
from stores.models import Store

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name="category-detail",
        lookup_field="pk"
    )
    class Meta:
        model = Category
        fields = ["id", "name", "description", "image", "is_active", "detail_url"]

# Product Serializer
class ProductNestedSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, source="category_set")
    class Meta:
        model = Product
        fields = ["id", "name", "description", "rating", "categories", "images"]

# Store Serializer
class StoreNestedSerializer(serializers.ModelSerializer):
    seller = serializers.HyperlinkedIdentityField(
        view_name="user-detail",
        lookup_field="user_id"
    )
    class Meta:
        model = Store
        fields = ["id", "name", "description", "seller"]

# ProductStore Serializer
class ProductStoreSerializer(serializers.ModelSerializer):
    product = ProductNestedSerializer(read_only=True)
    store = StoreNestedSerializer(read_only=True)
    discount_price = serializers.DecimalField(
        source="discount_price", max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = ProductStore
        fields = [
            "id", "created_at", "updated_at", "price", "discount_price",
            "stock", "is_active", "product", "store"
        ]



class ProductStoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStore
        fields = ["product", "store", "store_price", "store_discount", "created_at"]
        read_only_fields = ["created_at"]
