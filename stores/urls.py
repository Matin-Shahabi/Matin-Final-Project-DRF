
from django.urls import path
from .views import ProductStoreListCreateAPIView

urlpatterns = [
    path("items/", ProductStoreListCreateAPIView.as_view(), name="store-items-list"),
]
