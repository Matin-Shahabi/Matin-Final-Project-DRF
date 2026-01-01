# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import random
from users.models import CustomUser, Address, OTP
from stores.models import Store
from .serializers import (
    RequestOTPSerializer, RegisterSerializer, LoginSerializer,
    UserProfileSerializer, UserUpdateSerializer,
    AddressSerializer, RegisterAsSellerSerializer
)
from .sms import send_otp_pattern


# accounts/views.py - فقط این کلاس رو جایگزین کن

class RequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = (
            request.data.get('phone') or
            request.data.get('username') or
            request.data.get('mobile')
        )

        if not phone:
            return Response({"detail": "شماره موبایل الزامی است."}, status=400)

        phone = str(phone).strip()

        if not phone.isdigit() or len(phone) < 10:
            return Response({"detail": "شماره موبایل معتبر نیست."}, status=400)

        if phone.startswith('9') and len(phone) == 10:
            phone = '0' + phone

        # فقط اگر کاربر وجود داشت کد بفرست
        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            return Response({
                "detail": "این شماره موبایل ثبت‌نام نشده است. لطفاً ابتدا ثبت‌نام کنید."
            }, status=400)

        code = ''.join(random.choices('0123456789', k=6))

        OTP.objects.update_or_create(
            user=user,
            defaults={
                'code': code,
                'expires_at': timezone.now() + timedelta(minutes=5),
                'is_used': False
            }
        )

        success = send_otp_pattern(phone, code)

        if success:
            return Response({"detail": "کد تایید به شماره شما ارسال شد."}, status=200)
        else:
            print(f"تست محلی - کد OTP برای لاگین {phone}: {code}")
            return Response({
                "detail": "خطا در ارسال پیامک. کد در کنسول چاپ شد.",
                "test_code": code
            }, status=200)
        

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        otp_code = serializer.validated_data['password']

        # استاندارد کردن شماره برای جستجو
        normalized = username.strip().replace(' ', '').replace('+', '').replace('-', '')
        if normalized.startswith('989'):
            normalized = '0' + normalized[2:]
        elif normalized.startswith('9') and len(normalized) == 10:
            normalized = '0' + normalized

        try:
            user = CustomUser.objects.get(username=normalized, phone=normalized)

            otp = OTP.objects.filter(
                user=user,
                code=otp_code,
                is_used=False,
                expires_at__gt=timezone.now()
            ).latest('created_at')

            otp.is_used = True
            otp.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'phone': user.phone,
                    'role': user.role,
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'email': user.email or '',
                }
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"detail": "شماره موبایل ثبت‌نام نشده است."}, status=400)
        except OTP.DoesNotExist:
            return Response({"detail": "کد OTP اشتباه یا منقضی شده است."}, status=400)


# accounts/views.py - فقط این کلاس رو جایگزین کن
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # کپی از دیتا برای تغییر
        data = request.data.copy()

        # تبدیل کلیدهای ممکن به فرمت مورد انتظار LoginSerializer
        if 'phone' in data and 'username' not in data:
            data['username'] = data.pop('phone')
        if 'mobile' in data and 'username' not in data:
            data['username'] = data.pop('mobile')
        if 'code' in data and 'password' not in data:
            data['password'] = data.pop('code')
        if 'otp' in data and 'password' not in data:
            data['password'] = data.pop('otp')

        # حالا مستقیم به LoginSerializer پاس بده
        serializer = LoginSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        otp_code = serializer.validated_data['password']

        # استاندارد کردن شماره
        if username.startswith('9') and len(username) == 10:
            username = '0' + username

        try:
            user = CustomUser.objects.get(username=username, phone=username)

            otp = OTP.objects.filter(
                user=user,
                code=otp_code,
                is_used=False,
                expires_at__gt=timezone.now()
            ).latest('created_at')

            otp.is_used = True
            otp.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'phone': user.phone,
                    'role': user.role,
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'email': user.email or '',
                }
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"detail": "شماره موبایل ثبت‌نام نشده است."}, status=400)
        except OTP.DoesNotExist:
            return Response({"detail": "کد OTP اشتباه یا منقضی شده است."}, status=400)
        

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['username']

        # چک تکراری بودن
        if CustomUser.objects.filter(phone=phone).exists():
            return Response({
                "detail": "این شماره موبایل قبلاً ثبت‌نام شده است. لطفاً وارد شوید."
            }, status=status.HTTP_400_BAD_REQUEST)

        # ساخت کاربر
        user = serializer.save()

        # ارسال کد OTP
        code = ''.join(random.choices('0123456789', k=6))
        OTP.objects.update_or_create(
            user=user,
            defaults={
                'code': code,
                'expires_at': timezone.now() + timedelta(minutes=5),
                'is_used': False
            }
        )

        success = send_otp_pattern(phone, code)

        if success:
            message = "ثبت‌نام با موفقیت انجام شد و کد تایید ارسال شد."
        else:
            print(f"تست - کد OTP ثبت‌نام {phone}: {code}")
            message = "ثبت‌نام موفق بود اما خطا در ارسال پیامک."

        return Response({
            "detail": message,
            "user_id": user.id,
            "role": user.role
        }, status=status.HTTP_201_CREATED)
    
# بقیه ویوها دقیقاً همون قبلی — بدون تغییر
class MyUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(request.user).data)
        return Response(serializer.errors, status=400)


class AddressListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    pagination_class = None


    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_active=True, deleted_at__isnull=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_active=True, deleted_at__isnull=True)

    def perform_destroy(self, instance):
        instance.soft_delete()
        return Response({"detail": "آدرس با موفقیت حذف شد."}, status=200)


class RegisterAsSellerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role == "seller" and Store.objects.filter(user=request.user, is_active=True).exists():
            return Response({"detail": "شما قبلاً فروشنده هستید."}, status=400)

        serializer = RegisterAsSellerSerializer(data=request.data)
        if serializer.is_valid():
            store_name = serializer.validated_data['store_name']
            address = serializer.validated_data['address']
            logo = serializer.validated_data.get('logo')

            request.user.role = "seller"
            request.user.save()

            Store.objects.create(
                user=request.user,
                name=store_name,
                address=address,
                logo=logo
            )

            return Response({
                "detail": "فروشگاه با موفقیت ایجاد شد.",
                "role": "seller"
            }, status=201)

        return Response(serializer.errors, status=400)