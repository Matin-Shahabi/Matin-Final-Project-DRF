# api/views.py
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Min,Count,F, ExpressionWrapper, DecimalField

from products.models import Product
from reviews.models import Review
from .serializers import (
    ProductListSerializer, ProductDetailSerializer,
    ReviewSerializer
)

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class ProductListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'price', 'discount']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True, deleted_at__isnull=True)

        # جستجو و فیلترهای پایه
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)

        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')

        # محاسبه قیمت نهایی با تخفیف در سطح دیتابیس
        discount_calc = ExpressionWrapper(
            F('product_stores__store_price') * (1 - F('product_stores__store_discount') / 100),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )

        queryset = queryset.annotate(
            min_store_price=Min(discount_calc),  # کمترین قیمت با تخفیف در همه فروشگاه‌ها
            avg_rating=Avg('reviews__rating'),   # میانگین امتیاز
            review_count=Count('reviews')
        )

        # فیلتر قیمت بر اساس قیمت با تخفیف
        if price_min:
            queryset = queryset.filter(min_store_price__gte=price_min)
        if price_max:
            queryset = queryset.filter(min_store_price__lte=price_max)

        # مرتب‌سازی بر اساس امتیاز
        ordering = self.request.query_params.get('ordering')
        if ordering == '-rating':
            queryset = queryset.order_by('-avg_rating')
        elif ordering == 'rating':
            queryset = queryset.order_by('avg_rating')

        return queryset
    

class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_active=True, deleted_at__isnull=True)
    serializer_class = ProductDetailSerializer

    def get_object(self):
        obj = super().get_object()

        # محاسبه sellers
        product_stores = obj.product_stores.filter(stock__gt=0).select_related('store')

        sellers = []
        for ps in product_stores:
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
                "discount_price": float(ps.discount_price) if ps.discount_price else None
            })

        obj.sellers = sellers
        obj.best_price = min([s["discount_price"] or s["price"] for s in sellers], default=obj.price)
        obj.avg_rating = obj.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        return obj


class ReviewCreateView(generics.CreateAPIView):
    """
    POST /api/products/5/review_create/
    بدون لاگین هم اجازه می‌ده (طبق نیاز پارت اول)
    body: { "rating": 4.5, "comment": "عالی بود" }
    """
    permission_classes = [AllowAny]  # بعداً می‌تونی IsAuthenticated کنی
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        product = Product.objects.get(pk=self.kwargs['pk'], is_active=True)
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(product=product, user=user)


class ReviewListView(generics.ListAPIView):
    """
    GET /api/products/5/review_list/?page=1&page_size=5
    """
    permission_classes = [AllowAny]
    serializer_class = ReviewSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        product_id = self.kwargs['pk']
        return Review.objects.filter(
            product_id=product_id,
            is_active=True,
            deleted_at__isnull=True
        ).order_by('-created_at')