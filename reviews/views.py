from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import StoreReview, Review as ProductReview
from .serializers import UnifiedReviewSerializer


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class MyReviewsListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/reviews/              → لیست همه نظرات کاربر (با pagination)
    POST /api/reviews/              → ثبت نظر جدید (به محصول یا فروشگاه)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UnifiedReviewSerializer
    pagination_class = StandardPagination  # اضافه شد — pagination استاندارد

    def get_queryset(self):
        user = self.request.user
        # ترکیب نظرات محصول و فروشگاه
        product_reviews = ProductReview.objects.filter(
            user=user,
            is_active=True,
            deleted_at__isnull=True
        )
        store_reviews = StoreReview.objects.filter(
            user=user,
            is_active=True,
            deleted_at__isnull=True
        )
        # ترکیب و مرتب‌سازی بر اساس جدیدترین
        combined = list(product_reviews) + list(store_reviews)
        combined.sort(key=lambda x: x.created_at, reverse=True)
        return combined

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        })

    def perform_create(self, serializer):
        # کاربر از request گرفته می‌شه
        serializer.save()


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/reviews/<id>/     → جزئیات یک نظر
    PUT    /api/reviews/<id>/     → ویرایش کامل
    PATCH  /api/reviews/<id>/     → ویرایش جزئی
    DELETE /api/reviews/<id>/     → حذف نرم
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UnifiedReviewSerializer
    pagination_class = None  # نیازی به pagination نداره
    http_method_names = ['get', 'put', 'patch', 'delete']

    def get_queryset(self):
        # فقط نظرات کاربر فعلی
        user = self.request.user
        return ProductReview.objects.filter(user=user) | StoreReview.objects.filter(user=user)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs['pk']
        review = get_object_or_404(queryset, pk=pk, is_active=True, deleted_at__isnull=True)
        return review

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_destroy(self, instance):
        instance.soft_delete()
        return Response({"detail": "نظر با موفقیت حذف شد."}, status=status.HTTP_200_OK)