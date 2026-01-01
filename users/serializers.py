# accounts/serializers.py
from rest_framework import serializers
from users.models import CustomUser, Address
from stores.models import Store

class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20, write_only=True)

    def validate_phone(self, value):
        value = value.strip().replace(' ', '').replace('+', '').replace('-', '')
        
        # تبدیل به فرمت استاندارد 09xxxxxxxxx
        if value.startswith('989'):
            value = '0' + value[2:]
        elif value.startswith('9'):
            value = '0' + value
        elif value.startswith('09'):
            pass  # خوبه
        else:
            raise serializers.ValidationError("شماره موبایل باید با ۰۹ شروع شود.")

        if not value.isdigit() or len(value) != 11 or not value.startswith('09'):
            raise serializers.ValidationError("شماره موبایل معتبر نیست (باید ۱۱ رقم و با ۰۹ شروع شود).")
        
        return value


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20)  # شماره موبایل
    userType = serializers.BooleanField()
    birth_date = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(max_length=10, required=False, allow_blank=True)

    def validate_username(self, value):
        # تمیز کردن و استاندارد کردن شماره
        phone = value.strip().replace(' ', '').replace('+', '').replace('-', '')
        if phone.startswith('989'):
            phone = '0' + phone[2:]
        elif phone.startswith('9') and len(phone) == 10:
            phone = '0' + phone
        elif phone.startswith('09'):
            pass
        else:
            raise serializers.ValidationError("شماره موبایل باید با ۰۹ شروع شود.")

        if not phone.isdigit() or len(phone) != 11:
            raise serializers.ValidationError("شماره موبایل معتبر نیست (باید ۱۱ رقم باشد).")

        # چک تکراری بودن با فرمت استاندارد
        if CustomUser.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("این شماره موبایل قبلاً ثبت‌نام شده است. لطفاً وارد شوید.")

        return phone

    def create(self, validated_data):
        phone = validated_data['username']
        user_type = validated_data.pop('userType')
        role = "seller" if user_type else "customer"

        # چک نهایی تکراری بودن قبل از ساخت
        if CustomUser.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({"username": ["این شماره موبایل قبلاً ثبت‌نام شده است."]})

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
    username = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=10)  # کد OTP


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'label', 'country', 'province', 'city', 'address', 'postal_code']
        read_only_fields = ['id']

    def validate(self, data):
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