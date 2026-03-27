from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Product, ShopDetail, Nutrition

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'profile_image']

class CategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name']
    
    def get_name(self, obj):
        return {
            'en': obj.name_en,
            'hi': obj.name_hi
        }

class ShopDetailSerializer(serializers.ModelSerializer):
    shop_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = ShopDetail
        fields = ['id', 'shop_name', 'address', 'rating', 'opening_time', 'closing_time']
    
    def get_shop_name(self, obj):
        return {
            'en': obj.shop_name_en,
            'hi': obj.shop_name_hi
        }
    
    def get_address(self, obj):
        return {
            'en': obj.address_en,
            'hi': obj.address_hi
        }

class NutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrition
        fields = ['calories', 'protein', 'fat', 'carbs', 'per_unit']

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    category_name = serializers.CharField(source='category.name_en', read_only=True)
    shop_detail = ShopDetailSerializer(read_only=True)
    nutrition = NutritionSerializer(read_only=True)
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    defaultQuantity = serializers.CharField(source='default_quantity', read_only=True)
    vendor_id = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'vendor_id', 'price', 'image',
            'defaultQuantity', 'discount', 'name', 'description', 'shop_detail', 'nutrition',
            'stock_quantity', 'is_active', 'created_at', 'updated_at',
        ]

    def get_vendor_id(self, obj):
        if obj.shop_detail and obj.shop_detail.vendor:
            return obj.shop_detail.vendor.vendor_id
        return None
    
    def get_name(self, obj):
        return {
            'en': obj.name_en,
            'hi': obj.name_hi
        }
    
    def get_description(self, obj):
        return {
            'en': obj.description_en,
            'hi': obj.description_hi
        }
