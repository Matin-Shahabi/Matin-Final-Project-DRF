
from rest_framework.generics import ListCreateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import ProductStore
from .serializers import ProductStoreSerializer, ProductStoreCreateSerializer
from rest_framework.pagination import PageNumberPagination

# Pagination class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# List and Create API
class ProductStoreListCreateAPIView(ListCreateAPIView):
    queryset = ProductStore.objects.all().order_by("-created_at")
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "created_at": ["gte", "lte"],
        "is_active": ["exact"],
        "stock": ["gte", "lte"],
        "store__id": ["exact"],
        "store__name": ["icontains"],
        "product__name": ["icontains"],
    }
    ordering_fields = ["store__name", "discount_price"]
    ordering = ["-store__name", "discount_price"]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductStoreCreateSerializer
        return ProductStoreSerializer
