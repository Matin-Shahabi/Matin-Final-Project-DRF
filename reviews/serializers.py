from rest_framework import serializers
from .models import StoreReview, Review as ProductReview
from products.models import Product
from stores.models import Store


class UnifiedReviewSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.ChoiceField(choices=['product', 'store'], write_only=True)
    target_id = serializers.IntegerField(write_only=True)  # id محصول یا فروشگاه
    rating = serializers.FloatField(min_value=0.5, max_value=5.0)
    comment = serializers.CharField(max_length=1000, allow_blank=True, required=False, default="")
    created_at = serializers.DateTimeField(read_only=True)

    # فیلدهای نمایشی
    target_name = serializers.CharField(read_only=True)
    target_image = serializers.SerializerMethodField()  # بهتره method باشه تا null رو درست هندل کنه

    # فیلدهای اضافی برای فرانت (اختیاری ولی خیلی خوبه)
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()

    class Meta:
        # Meta اختیاریه ولی برای وضوح خوبه
        pass

    def get_target_image(self, obj):
        if hasattr(obj, 'product') and obj.product:
            first_image = obj.product.images.first()
            return first_image.image.url if first_image and first_image.image else None
        elif hasattr(obj, 'store') and obj.store:
            return obj.store.logo.url if obj.store.logo else None
        return None

    def get_user_name(self, obj):
        if obj.user:
            # اگر first_name یا last_name داشت، نشون بده
            full_name = f"{obj.user.first_name or ''} {obj.user.last_name or ''}".strip()
            if full_name:
                return full_name
            return obj.user.username or "ناشناس"
        return "ناشناس"

    def get_user_avatar(self, obj):
        if obj.user and obj.user.avatar:
            return obj.user.avatar.url
        return None

    def validate(self, data):
        type_ = data.get('type')
        target_id = data.get('target_id')

        if type_ == 'product':
            if not Product.objects.filter(id=target_id, is_active=True, deleted_at__isnull=True).exists():
                raise serializers.ValidationError("محصول یافت نشد یا غیرفعال است.")
        elif type_ == 'store':
            if not Store.objects.filter(id=target_id, is_active=True, deleted_at__isnull=True).exists():
                raise serializers.ValidationError("فروشگاه یافت نشد یا غیرفعال است.")
        else:
            raise serializers.ValidationError("نوع نظر باید 'product' یا 'store' باشد.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user  # کاربر لاگین شده
        type_ = validated_data.pop('type')
        target_id = validated_data.pop('target_id')

        if type_ == 'product':
            product = Product.objects.get(id=target_id)
            review = ProductReview.objects.create(user=user, product=product, **validated_data)
        else:
            store = Store.objects.get(id=target_id)
            review = StoreReview.objects.create(user=user, store=store, **validated_data)

        return review

    def update(self, instance, validated_data):
        rating = validated_data.get('rating')
        comment = validated_data.get('comment')

        if rating is not None:
            instance.rating = rating
        if comment is not None:
            instance.comment = comment

        instance.save()
        return instance

    def to_representation(self, instance):
        data = {
            'id': instance.id,
            'type': 'product' if hasattr(instance, 'product') else 'store',
            'target_id': instance.product.id if hasattr(instance, 'product') else instance.store.id,
            'target_name': instance.product.name if hasattr(instance, 'product') else instance.store.name,
            'rating': instance.rating,
            'comment': instance.comment or "",
            'created_at': instance.created_at,
            'user_name': self.get_user_name(instance),
            'user_avatar': self.get_user_avatar(instance),
        }

        # target_image با method
        data['target_image'] = self.get_target_image(instance)

        return data