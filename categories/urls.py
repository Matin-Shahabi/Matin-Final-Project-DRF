from django.urls import path
from .views import CategoryListAPIView, CategoryDetailAPIView

urlpatterns = [
    path("", CategoryListAPIView.as_view(), name="category-list"),
    path("<int:pk>/", CategoryDetailAPIView.as_view(), name="category-detail"),
]