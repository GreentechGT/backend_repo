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


class VendorProductWriteSerializer(serializers.ModelSerializer):
    """Serializer for vendor to create/update their own products using simple field names."""
    name = serializers.CharField(write_only=True, required=True)
    description = serializers.CharField(write_only=True, required=False, allow_blank=True, default='')
    category = serializers.CharField(write_only=True, required=True)

    # Read-only display fields
    id = serializers.IntegerField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    image = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    stock_quantity = serializers.IntegerField(required=False, default=0)
    is_active = serializers.BooleanField(required=False, default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'price', 'image', 'stock_quantity', 'is_active', 'created_at', 'updated_at']

    def validate_category(self, value):
        try:
            return Category.objects.get(name_en__iexact=value)
        except Category.DoesNotExist:
            # Create category if it doesn't exist
            cat, _ = Category.objects.get_or_create(name_en=value)
            return cat

    def create(self, validated_data):
        category = validated_data.pop('category')
        name = validated_data.pop('name')
        description = validated_data.pop('description', '')
        shop_detail = validated_data.pop('shop_detail', None)
        return Product.objects.create(
            name_en=name,
            description_en=description,
            category=category,
            shop_detail=shop_detail,
            **validated_data
        )

    def update(self, instance, validated_data):
        if 'name' in validated_data:
            instance.name_en = validated_data.pop('name')
        if 'description' in validated_data:
            instance.description_en = validated_data.pop('description')
        if 'category' in validated_data:
            instance.category = validated_data.pop('category')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Return the full ProductSerializer representation after write."""
        return ProductSerializer(instance, context=self.context).data
