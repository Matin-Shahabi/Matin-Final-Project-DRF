from django.urls import path
from .views import MyReviewsListCreateView, ReviewDetailView

urlpatterns = [
    path('reviews/', MyReviewsListCreateView.as_view(), name='my-reviews-list-create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
]