from rest_framework.generics import ListAPIView,RetrieveAPIView,CreateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Product
from .serializers import ProductListSerializer,ProductDetailSerializer
from rest_framework.permissions import AllowAny
from reviews.models import Review
from reviews.serializers import ReviewCreateSerializer




class ProductListAPI(ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    
    filterset_fields = {
        "category__id": ["exact"],
        "price": ["gte", "lte"],
        "name": ["icontains"],
    }
    ordering_fields = ["price", "rating"]
    ordering = ["-rating", "-price"]



class ProductDetailAPIView(RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer


