
from django.urls import path
from .views import RequestOTPView, VerifyOTPView, RegisterView, LoginView,MyUserView, AddressListCreateView,AddressDetailView, RegisterAsSellerView
from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView


urlpatterns = [
    path('accounts/request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('accounts/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('accounts/token/', TokenObtainPairView.as_view()),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/login/', LoginView.as_view(), name='login'),  # alias برای verify-otp
    path('myuser/', MyUserView.as_view(), name='myuser'),
    path('myuser/address/', AddressListCreateView.as_view(), name='address-list-create'),
    path('myuser/address/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('myuser/register_as_seller/', RegisterAsSellerView.as_view(), name='register-as-seller'),
]


