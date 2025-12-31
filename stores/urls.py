
from django.urls import path
from .views import *

urlpatterns = [
    # عمومی
    path('', StoreListView.as_view(), name='store-list'),
    path('<int:pk>/', StoreDetailView.as_view(), name='store-detail'),
    path('<int:pk>/products/', StoreProductsPublicView.as_view(), name='store-products'),
    path('<int:pk>/review_list/', StoreReviewListView.as_view(), name='store-review-list'),
    path('<int:pk>/review_create/', StoreReviewCreateView.as_view(), name='store-review-create'),

    # مدیریت توسط فروشنده
    path('items/', MyStoreItemsListCreateView.as_view(), name='my-store-items'),
    path('items/<int:pk>/', MyStoreItemDetailView.as_view(), name='my-store-item-detail'),
]

