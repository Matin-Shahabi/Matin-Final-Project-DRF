# reviews/serializers.py
from rest_framework import serializers
from .models import StoreReview,Review as ProductReview
from products.models import Product
from stores.models import Store

class UnifiedReviewSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.ChoiceField(choices=['product', 'store'], write_only=True)
    target_id = serializers.IntegerField(write_only=True)  # id محصول یا فروشگاه
    rating = serializers.FloatField(min_value=0.5, max_value=5.0)
    comment = serializers.CharField(max_length=1000, allow_blank=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)

    # فیلدهای نمایشی
    target_name = serializers.CharField(read_only=True)
    target_image = serializers.ImageField(read_only=True, allow_null=True)

    def validate(self, data):
        type_ = data.get('type')
        target_id = data.get('target_id')

        if type_ == 'product':
            if not Product.objects.filter(id=target_id, is_active=True).exists():
                raise serializers.ValidationError("محصول یافت نشد.")
        elif type_ == 'store':
            if not Store.objects.filter(id=target_id, is_active=True).exists():
                raise serializers.Validation("فروشگاه یافت نشد.")
        else:
            raise serializers.ValidationError("نوع نظر باید product یا store باشد.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
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
        # نمایش یکپارچه برای هر دو نوع نظر
        data = {
            'id': instance.id,
            'rating': instance.rating,
            'comment': instance.comment,
            'created_at': instance.created_at,
        }

        if hasattr(instance, 'product'):  # نظر محصول
            data['type'] = 'product'
            data['target_id'] = instance.product.id
            data['target_name'] = instance.product.name
            first_image = instance.product.images.first()
            data['target_image'] = first_image.image.url if first_image else None

        elif hasattr(instance, 'store'):  # نظر فروشگاه
            data['type'] = 'store'
            data['target_id'] = instance.store.id
            data['target_name'] = instance.store.name
            data['target_image'] = instance.store.logo.url if instance.store.logo else None

        return data