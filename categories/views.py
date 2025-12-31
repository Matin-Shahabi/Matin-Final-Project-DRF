# api/views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny
from categories.models import Category
from .serializers import CategoryListSerializer, CategoryDetailSerializer

class CategoryListView(generics.ListAPIView):
    """
    GET /api/categories/
    لیست همه دسته‌بندی‌های فعال (بدون حذف شده‌ها)
    """
    permission_classes = [AllowAny]
    queryset = Category.objects.filter(is_active=True, deleted_at__isnull=True, parent__isnull=True)  # فقط والدها
    serializer_class = CategoryListSerializer

    # اگر می‌خوای همه دسته‌ها (با زیرمجموعه) رو بفرستی، این خط رو کامنت کن:
    # queryset = Category.objects.filter(is_active=True, deleted_at__isnull=True)


class CategoryDetailView(generics.RetrieveAPIView):
    """
    GET /api/categories/5/
    جزئیات یک دسته‌بندی به همراه زیر دسته‌هاش
    """
    permission_classes = [AllowAny]
    queryset = Category.objects.filter(is_active=True, deleted_at__isnull=True)
    serializer_class = CategoryDetailSerializer