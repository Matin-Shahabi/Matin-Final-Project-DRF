from django.urls import path
from .views import ProductListAPI,ProductDetailAPIView

urlpatterns = [
    path("", ProductListAPI.as_view(), name="product-list"),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),

]

