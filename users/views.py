from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
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


def generate_otp():
    return str(random.randint(100000, 999999))


class RequestOTPView(APIView):
    """
    POST /api/accounts/request-otp/
    قبول می‌کنه:
    - {"phone": "09121111111"}
    - {"username": "09121111111"}
    - حتی {"mobile": "09121111111"} اگر فرانت اشتباه کرد
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # همه کلیدهای ممکن رو چک کن
        phone = (
            request.data.get('phone') or
            request.data.get('username') or
            request.data.get('mobile') or
            request.data.get('Phone') or
            request.data.get('Username')
        )

        if not phone:
            return Response(
                {"detail": "شماره موبایل الزامی است. (phone یا username)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # اعتبارسنجی شماره
        phone = str(phone).strip()
        if not phone.isdigit() or len(phone) < 10:
            return Response(
                {"detail": "شماره موبایل معتبر نیست."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # شروع با 0 یا 09 رو قبول کن، ولی ذخیره با 09
        if phone.startswith('9'):
            phone = '0' + phone
        elif not phone.startswith('0'):
            phone = '0' + phone

        # ساخت کاربر و OTP
        user, created = CustomUser.objects.get_or_create(
            phone=phone,
            defaults={'username': phone}
        )

        otp_obj, _ = OTP.objects.update_or_create(
            user=user,
            defaults={
                'code': generate_otp(),
                'expires_at': timezone.now() + timedelta(minutes=5),
                'is_used': False
            }
        )

        print(f"OTP برای {phone}: {otp_obj.code}")  # تست

        return Response({"detail": "کد OTP ارسال شد."}, status=status.HTTP_200_OK)

class LoginView(APIView):
    """
    POST /api/accounts/login/
    body: {
        "username": "09123456789",   // شماره موبایل
        "password": "123456"         // کد OTP
    }
    این اندپوینت اصلی ورود هست که فرانت استفاده می‌کنه
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']  # شماره موبایل
        otp_code = serializer.validated_data['password']  # کد OTP

        try:
            # کاربر باید با username = phone وجود داشته باشه
            user = CustomUser.objects.get(username=username, phone=username)

            # چک کردن OTP
            otp = OTP.objects.filter(
                user=user,
                code=otp_code,
                is_used=False,
                expires_at__gt=timezone.now()
            ).latest('created_at')

            # علامت‌گذاری OTP به عنوان استفاده‌شده
            otp.is_used = True
            otp.save()

            # تولید توکن JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'phone': user.phone,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                }
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "شماره موبایل ثبت‌نام نشده است."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except OTP.DoesNotExist:
            return Response(
                {"detail": "کد OTP اشتباه یا منقضی شده است."},
                status=status.HTTP_400_BAD_REQUEST
            )


# این رو می‌تونی نگه داری برای سازگاری قدیمی، یا حذف کنی
class VerifyOTPView(APIView):
    """
    POST /api/accounts/verify-otp/
    فقط برای سازگاری با نسخه‌های قدیمی (اگر لازم بود)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # دقیقاً همون منطق LoginView
        return LoginView.post(self, request)


class RegisterView(APIView):
    """
    POST /api/accounts/register/
    body: {
        "username": "09123456789",
        "userType": true,  // true = فروشنده
        "birth_date": "1990-01-01",
        "gender": "male"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "detail": "ثبت‌نام با موفقیت انجام شد. حالا می‌توانید وارد شوید.",
                "user_id": user.id,
                "role": user.role
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- بقیه ویوها بدون تغییر (کامل حفظ شدن) ---
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