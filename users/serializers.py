from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from users.models import CustomUser, Address
from stores.models import Store


class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20, write_only=True)

    def validate_phone(self, value):
        value = value.strip()
        # حذف خط فاصله یا + اگر باشه
        value = value.replace(' ', '').replace('+', '')
        # اگر با ۰۹ شروع شده یا ۹، تبدیل به فرمت استاندارد
        if value.startswith('09'):
            value = value[1:]  # به 9 تبدیل می‌شه
        elif value.startswith('9'):
            value = '0' + value
        # چک نهایی
        if not value.isdigit() or len(value) != 11 or not value.startswith('09'):
            raise serializers.ValidationError("شماره موبایل معتبر نیست (باید ۰۹ شروع شود و ۱۱ رقم باشد).")
        return value


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20)  # شماره موبایل
    userType = serializers.BooleanField()  # True = فروشنده، False = مشتری
    birth_date = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(max_length=10, required=False, allow_blank=True)

    def validate_username(self, value):
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("شماره موبایل معتبر نیست.")
        return value

    def create(self, validated_data):
        phone = validated_data['username']
        user_type = validated_data.pop('userType')

        role = "seller" if user_type else "customer"

        user = CustomUser.objects.create_user(
            username=phone,
            phone=phone,
            role=role,
            **validated_data
        )
        user.set_unusable_password()
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20)  # شماره موبایل
    password = serializers.CharField(max_length=10)  # کد OTP


# myuser 
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'label', 'country', 'province', 'city', 'address', 'postal_code']
        read_only_fields = ['id']

    def validate(self, data):
        # کشور پیش‌فرض ایران
        if not data.get('country'):
            data['country'] = 'Iran'
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'phone', 'email', 'first_name', 'last_name',
            'birth_date', 'gender', 'avatar', 'role', 'addresses'
        ]
        read_only_fields = ['id', 'username', 'phone', 'role']


class UserUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'birth_date', 'gender', 'avatar']


class RegisterAsSellerSerializer(serializers.Serializer):
    store_name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=500)
    logo = serializers.ImageField(required=False)