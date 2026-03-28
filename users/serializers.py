from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import models
import uuid
import random
from datetime import timedelta
from django.utils import timezone
from .models import User, Address, Vendor, Customer
from .utils import send_otp_via_email

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'full_name', 'phone', 'address', 'city', 'pincode', 'address_type', 'is_default']
        read_only_fields = ['user']

class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'user_id', 'full_name', 'email', 'role', 'phone', 'addresses', 'push_token')

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['cust_id', 'name', 'email', 'phone', 'password']
        read_only_fields = ['cust_id']

class RegisterSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        
        email = email if email else None
        phone = phone if phone else None
        
        attrs['email'] = email
        attrs['phone'] = phone

        if not email and not phone:
            raise serializers.ValidationError({"detail": "Either email or phone number is required."})

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "User with this email already exists."})
        
        if phone and User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({"phone": "User with this phone number already exists."})

        return attrs

    def create(self, validated_data):
        # Create a Customer record first (for registration/OTP)
        try:
            email = validated_data.get('email')
            phone = validated_data.get('phone')
            
            # Prefer finding by email if available, else phone
            if email:
                customer, created = Customer.objects.update_or_create(
                    email=email,
                    defaults={
                        'name': validated_data.get('full_name'),
                        'phone': phone,
                        'password': validated_data.get('password'),
                        'is_verified': False
                    }
                )
            else:
                customer, created = Customer.objects.update_or_create(
                    phone=phone,
                    defaults={
                        'name': validated_data.get('full_name'),
                        'email': email,
                        'password': validated_data.get('password'),
                        'is_verified': False
                    }
                )
            
            # Generate OTP
            otp = "1234"
            customer.otp_code = otp
            customer.otp_expiry = timezone.now() + timedelta(minutes=10)
            customer.save()
            
            return customer
        except Exception as e:
            raise serializers.ValidationError({"detail": str(e)})

    def to_representation(self, instance):
        return {
            "full_name": getattr(instance, 'name', ''),
            "email": getattr(instance, 'email', ''),
            "phone": getattr(instance, 'phone', '')
        }

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['user_uuid'] = str(user.user_id)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        # The custom backend EmailOrPhoneBackend will handle the 'username' 
        # which might be an email or a phone number.
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            'vendor_id', 'name', 'phone', 'email', 'password', 'personal_id_proof',
            'shop_name', 'shop_address', 'shop_location', 'shop_id_proof',
            'tagline', 'description', 'website', 'instagram', 'facebook',
            'banner_image', 'logo_image',
            'business_name', 'gst_number', 'pan_number', 'fssai_license',
            'bank_name', 'account_holder_name', 'account_number', 'ifsc_code',
            'account_type', 'bank_branch',
        ]
        read_only_fields = ['vendor_id']

    def create(self, validated_data):
        return Vendor.objects.create(**validated_data)


class VendorProfileSerializer(serializers.ModelSerializer):
    """Serializer for authenticated vendor to view and update their own profile."""
    class Meta:
        model = Vendor
        fields = [
            'vendor_id', 'name', 'phone', 'email',
            # Shop Profile
            'shop_name', 'shop_address', 'shop_location',
            'tagline', 'description', 'website', 'instagram', 'facebook',
            'banner_image', 'logo_image',
            # Business
            'business_name', 'gst_number', 'pan_number', 'fssai_license',
            # Bank
            'bank_name', 'account_holder_name', 'account_number', 'ifsc_code',
            'account_type', 'bank_branch',
            # Meta
            'verified', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['vendor_id', 'verified', 'is_active', 'created_at', 'updated_at']

