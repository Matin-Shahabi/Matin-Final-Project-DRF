from django.urls import path
from .views import CartItemsView

urlpatterns = [
    path('items/', CartItemsView.as_view(), name='cart-items'),
]

