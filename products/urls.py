from django.urls import path
from .views import (
    ProductListView, ProductDetailView,
    ReviewCreateView, ReviewListView
)


urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/review_create/', ReviewCreateView.as_view(), name='product-review-create'),
    path('<int:pk>/review_list/', ReviewListView.as_view(), name='product-review-list'),
]