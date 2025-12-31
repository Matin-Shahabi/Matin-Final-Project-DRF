# reviews/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import StoreReview, Review as ProductReview
from .serializers import UnifiedReviewSerializer

class MyReviewsListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/reviews/     → لیست همه نظرات کاربر
    POST /api/reviews/     → ثبت نظر جدید (به محصول یا فروشگاه)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UnifiedReviewSerializer

    def get_queryset(self):
        user = self.request.user
        # ترکیب نظرات محصول و فروشگاه
        product_reviews = ProductReview.objects.filter(user=user, is_active=True, deleted_at__isnull=True)
        store_reviews = StoreReview.objects.filter(user=user, is_active=True, deleted_at__isnull=True)
        return list(product_reviews) + list(store_reviews)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # مرتب‌سازی بر اساس جدیدترین
        queryset.sort(key=lambda x: x.created_at, reverse=True)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        })

    def perform_create(self, serializer):
        serializer.save()


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/reviews/12/
    PUT    /api/reviews/12/
    PATCH  /api/reviews/12/
    DELETE /api/reviews/12/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UnifiedReviewSerializer
    http_method_names = ['get', 'put', 'patch', 'delete']

    def get_object(self):
        pk = self.kwargs['pk']
        user = self.request.user

        try:
            review = ProductReview.objects.get(pk=pk, user=user, is_active=True, deleted_at__isnull=True)
            return review
        except ProductReview.DoesNotExist:
            pass

        review = get_object_or_404(StoreReview, pk=pk, user=user, is_active=True, deleted_at__isnull=True)
        return review

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_destroy(self, instance):
        instance.soft_delete()
        return Response({"detail": "نظر با موفقیت حذف شد."}, status=status.HTTP_200_OK)