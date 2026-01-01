from rest_framework import serializers
from products.models import Product, ProductImage
from reviews.models import Review
from categories.models import Category
from users.models import CustomUser


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    min_price = serializers.SerializerMethodField()  # تغییر به method برای امنیت
    avg_rating = serializers.FloatField(read_only=True)
    sellers = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'price', 'discount',
            'description', 'images', 'min_price', 'avg_rating', 'created_at', 'sellers'
        ]

    def get_min_price(self, obj):
        # اگر min_store_price None بود، قیمت پایه با تخفیف محصول
        if hasattr(obj, 'min_store_price') and obj.min_store_price is not None:
            return float(obj.min_store_price)
        # قیمت پایه محصول با تخفیف خودش
        return float(obj.price * (1 - obj.discount / 100))

    def get_sellers(self, obj):
        sellers = []
        # فقط فروشگاه‌های با موجودی
        for ps in obj.product_stores.filter(stock__gt=0):
            discount_price = ps.discount_price if ps.discount_price is not None else ps.store_price
            sellers.append({
                "id": ps.id,
                "price": float(ps.store_price),
                "stock": ps.stock,
                "store": {
                    "id": ps.store.id,
                    "name": ps.store.name,
                    "seller": ps.store.user.id,
                    "description": ps.store.address or ""
                },
                "discount_price": float(discount_price)
            })
        return sellers


class ReviewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'avatar']


class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']



class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(source='reviews.count', read_only=True)
    avg_rating = serializers.SerializerMethodField()

    # فیلدهای مورد انتظار فرانت
    sellers = serializers.SerializerMethodField()
    best_price = serializers.SerializerMethodField()
    best_seller = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'price', 'description',
            'discount', 'final_price', 'stock', 'start_date', 'end_date',
            'images', 'reviews', 'review_count', 'avg_rating',
            'sellers', 'best_price', 'best_seller', 'created_at'
        ]

    def get_final_price(self, obj):
        return float(obj.price * (1 - obj.discount / 100))

    def get_avg_rating(self, obj):
        if hasattr(obj, 'avg_rating') and obj.avg_rating is not None:
            return round(obj.avg_rating, 1)
        return 0.0

    def get_sellers(self, obj):
        sellers = getattr(obj, 'sellers', [])
        # اگر sellers تو ویو پر نشده بود، اینجا پر کن
        if not sellers:
            sellers = []
            for ps in obj.product_stores.filter(stock__gt=0):
                discount_price = ps.discount_price if ps.discount_price is not None else ps.store_price
                sellers.append({
                    "id": ps.id,
                    "price": float(ps.store_price),
                    "stock": ps.stock,
                    "store": {
                        "id": ps.store.id,
                        "name": ps.store.name,
                        "seller": ps.store.user.id,
                        "description": ps.store.address or ""
                    },
                    "discount_price": float(discount_price)
                })
        return sellers

    def get_best_price(self, obj):
        if hasattr(obj, 'best_price') and obj.best_price is not None:
            return obj.best_price
        # fallback به قیمت پایه
        return float(obj.price * (1 - obj.discount / 100))

    def get_best_seller(self, obj):
        if hasattr(obj, 'best_seller') and obj.best_seller is not None:
            return obj.best_seller
        # اگر نبود، اولین فروشنده با موجودی رو برگردون
        ps = obj.product_stores.filter(stock__gt=0).first()
        if ps:
            discount_price = ps.discount_price if ps.discount_price is not None else ps.store_price
            return {
                "id": ps.id,
                "price": float(ps.store_price),
                "stock": ps.stock,
                "store": {
                    "id": ps.store.id,
                    "name": ps.store.name,
                    "seller": ps.store.user.id,
                    "description": ps.store.address or ""
                },
                "discount_price": float(discount_price)
            }
        return None