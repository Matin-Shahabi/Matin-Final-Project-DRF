# api/serializers.py
from rest_framework import serializers
from products.models import Product, ProductImage
from reviews.models import Review
from categories.models import Category

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

# products/serializers.py
class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    min_price = serializers.DecimalField(source='min_store_price', max_digits=12, decimal_places=2, read_only=True)
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_name', 'price', 'discount',
                  'description', 'images', 'min_price', 'avg_rating', 'created_at']

# سریالایزر نظرات محصول
class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True, default='ناشناس')
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user_name', 'user_avatar', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at', 'user_name', 'user_avatar']



# سریالایزر کامل برای جزئیات محصول
class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(source='reviews.count', read_only=True)
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'price', 'description',
            'discount', 'final_price', 'stock', 'start_date', 'end_date',
            'images', 'reviews', 'review_count', 'avg_rating'
        ]

    def get_final_price(self, obj):
        return obj.price * (1 - obj.discount / 100)

    def get_avg_rating(self, obj):
        if hasattr(obj, 'avg_rating'):
            return round(obj.avg_rating, 1)
        return 0