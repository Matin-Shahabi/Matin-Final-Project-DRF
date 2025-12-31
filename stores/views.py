# stores/views.py
from rest_framework import generics, permissions, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from stores.models import Store
from reviews.models import StoreReview
from products.models import ProductStore
from .serializers import StoreDetailSerializer,StoreItemManageSerializer,StoreListSerializer,StoreProductPublicSerializer,StoreReviewSerializer,StoreUpdateSerializer,IsStoreOwner

# pagination استاندارد
class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

# --- عمومی ---
class StoreListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Store.objects.filter(is_active=True, deleted_at__isnull=True)
    serializer_class = StoreListSerializer
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['rating', 'sales_count', 'total_product']
    ordering = ['-rating']

class StoreDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Store.objects.filter(is_active=True, deleted_at__isnull=True)
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsStoreOwner]
            return StoreUpdateSerializer
        return StoreDetailSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [IsStoreOwner()]
        return [permissions.AllowAny()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        agg = instance.reviews.aggregate(avg=Avg('rating'), count=Count('id'))
        serializer = StoreDetailSerializer(instance)
        data = serializer.data
        data['avg_rating'] = round(agg['avg'] or 0, 1)
        data['review_count'] = agg['count'] or 0
        return Response(data)

class StoreProductsPublicView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = StoreProductPublicSerializer
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name', 'product__description']
    ordering_fields = ['store_price', 'store_discount', 'product__created_at']
    ordering = ['-product__created_at']

    def get_queryset(self):
        store_id = self.kwargs['pk']
        return ProductStore.objects.filter(
            store_id=store_id,
            store__is_active=True,
            product__is_active=True,
            stock__gt=0
        ).select_related('product')

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        if price_min:
            queryset = queryset.filter(store_price__gte=price_min)
        if price_max:
            queryset = queryset.filter(store_price__lte=price_max)
        return queryset

class StoreReviewListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = StoreReviewSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        store_id = self.kwargs['pk']
        return StoreReview.objects.filter(
            store_id=store_id,
            is_active=True,
            deleted_at__isnull=True
        ).order_by('-created_at')

class StoreReviewCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # پارت اول بدون لاگین
    serializer_class = StoreReviewSerializer

    def perform_create(self, serializer):
        store = get_object_or_404(Store, pk=self.kwargs['pk'], is_active=True)
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(store=store, user=user)

# --- مدیریت توسط فروشنده ---
class MyStoreItemsListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StoreItemManageSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return ProductStore.objects.filter(store__user=self.request.user).select_related('product')

    def perform_create(self, serializer):
        store = get_object_or_404(Store, user=self.request.user, is_active=True)
        serializer.save(store=store)

class MyStoreItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StoreItemManageSerializer

    def get_queryset(self):
        return ProductStore.objects.filter(store__user=self.request.user)

    def perform_destroy(self, instance):
        instance.stock = 0
        instance.is_active = False
        instance.save()
        # یا اگر بخوای حذف نرم از BaseModel استفاده کن
        # instance.soft_delete()
        return Response({"detail": "محصول از فروشگاه حذف شد."}, status=status.HTTP_200_OK)