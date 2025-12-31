from rest_framework import permissions
# stores/serializers.py
from rest_framework import serializers
from stores.models import Store
from reviews.models import StoreReview
from products.models import ProductStore, Product, ProductImage




class IsStoreOwner(permissions.BasePermission):
    """فقط صاحب فروشگاه اجازه ویرایش داره"""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    



# --- فروشگاه عمومی ---
class StoreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'logo', 'rating', 'sales_count', 'total_product']

class StoreDetailSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'logo', 'rating', 'avg_rating',
                  'review_count', 'sales_count', 'total_product']

class StoreUpdateSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Store
        fields = ['name', 'address', 'logo']

# --- محصولات فروشگاه (عمومی) ---
class StoreProductPublicSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_description = serializers.CharField(source='product.description', read_only=True)
    product_images = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = ProductStore
        fields = ['id', 'product', 'product_name', 'product_description', 'product_images',
                  'store_price', 'store_discount', 'final_price', 'stock']

    def get_product_images(self, obj):
        images = obj.product.images.all()[:4]
        return [image.image.url for image in images if image.image]

    def get_final_price(self, obj):
        return obj.discount_price

# --- مدیریت محصولات توسط فروشنده ---
class StoreItemManageSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductStore
        fields = ['id', 'product', 'product_name', 'store_price',
                  'store_discount', 'stock']

    def validate_product(self, product):
        if not product.is_active or product.deleted_at:
            raise serializers.ValidationError("این محصول غیرفعال است و نمی‌توان اضافه کرد.")
        return product

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("موجودی نمی‌تواند منفی باشد.")
        return value

# --- نظرات فروشگاه ---
class StoreReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True, default="ناشناس")
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)

    class Meta:
        model = StoreReview
        fields = ['id', 'user_name', 'user_avatar', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']