from rest_framework import serializers
from .models import Subscription
from product.models import Product

class SubscriptionProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name_en', 'name_hi', 'price', 'image', 'default_quantity']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Match frontend mock data structure
        return {
            'id': data['id'],
            'name': {
                'en': data['name_en'],
                'hi': data['name_hi']
            },
            'quantity': 1, # Default quantity for subscription item
            'unit': 'L',   # Default unit for subscription item
            'price': float(data['price']),
            'image': data['image']
        }

class SubscriptionSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    price = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2)

    isBestValue = serializers.BooleanField(source='is_best_value', read_only=True)
    originalPrice = serializers.DecimalField(source='original_price', max_digits=10, decimal_places=2, allow_null=True, read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'title', 'description', 'price', 'unit', 'image', 
            'category', 'isBestValue', 'frequency', 'discount', 
            'originalPrice', 'products'
        ]

    def get_title(self, obj):
        return {
            'en': obj.plan_name_en,
            'hi': obj.plan_name_hi
        }

    def get_description(self, obj):
        return {
            'en': obj.desc_en,
            'hi': obj.desc_hi
        }

    def get_products(self, obj):
        return [SubscriptionProductSerializer(obj.product).data]

from .models import MonthlySubscriber, YearlySubscriber

class BaseSubscriberSerializer(serializers.ModelSerializer):
    plan_name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    image = serializers.URLField(source='plan.image', read_only=True)
    frequency_localized = serializers.SerializerMethodField()
    slot_localized = serializers.SerializerMethodField()
    status_localized = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    address_details = serializers.CharField(source='address.address', read_only=True)
    city = serializers.CharField(source='address.city', read_only=True)
    pincode = serializers.CharField(source='address.pincode', read_only=True)
    plan_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    def get_plan_name(self, obj):
        return {'en': obj.plan_name_en, 'hi': obj.plan_name_hi}

    def get_description(self, obj):
        return {'en': obj.desc_en, 'hi': obj.desc_hi}

    def get_product_name(self, obj):
        return {'en': obj.plan.name_en, 'hi': obj.plan.name_hi}

    def get_frequency_localized(self, obj):
        return {'en': obj.frequency_en, 'hi': obj.frequency_hi}

    def get_slot_localized(self, obj):
        return {'en': obj.slot_en, 'hi': obj.slot_hi}

    def get_status_localized(self, obj):
        return {'en': obj.status_en, 'hi': obj.status_hi}

class MonthlySubscriberSerializer(BaseSubscriberSerializer):
    class Meta:
        model = MonthlySubscriber
        fields = [
            'id', 'plan_name', 'description', 
            'product_name', 'image', 'frequency_localized', 
            'slot_localized', 'status_localized', 'status', 
            'slot', 'frequency', 'quantity_litres', 
            'plan_subscribed_date', 'subscription_end_date',
            'is_paused', 'is_paused_days', 'original_subscription_end_date', 'paused_at',
            'daily_delivery_status', 'daily_delivery_status_en', 'daily_delivery_status_hi', 'user_name', 'plan_price',
            'status_confirmed_at', 'status_ontheway_at', 'status_delivered_at'
        ]

class YearlySubscriberSerializer(BaseSubscriberSerializer):
    class Meta:
        model = YearlySubscriber
        fields = [
            'id', 'plan_name', 'description', 
            'product_name', 'image', 'frequency_localized', 
            'slot_localized', 'status_localized', 'status', 
            'slot', 'frequency', 'quantity_litres', 
            'plan_subscribed_date', 'subscription_end_date',
            'is_paused', 'is_paused_days', 'original_subscription_end_date', 'paused_at',
            'daily_delivery_status', 'daily_delivery_status_en', 'daily_delivery_status_hi', 'user_name', 'plan_price',
            'status_confirmed_at', 'status_ontheway_at', 'status_delivered_at'
        ]


class VendorSubscriptionWriteSerializer(serializers.ModelSerializer):
    subscription_name = serializers.CharField(write_only=True)
    product_name = serializers.CharField(write_only=True)
    amount = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2)
    delivery_slot = serializers.CharField(source='slot', write_only=True, required=False, default='morning')
    # CharField instead of URLField: accepts local file:// URIs from ImagePicker
    image = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Subscription
        fields = ['id', 'subscription_name', 'product_name', 'frequency', 'amount', 'delivery_slot', 'image']

    def create(self, validated_data):
        subscription_name = validated_data.pop('subscription_name')
        product_name = validated_data.pop('product_name')
        
        # Find the product by name for this vendor
        request = self.context.get('request')
        vendor_id = request.user.user_id
        
        try:
            product = Product.objects.get(
                name_en=product_name,
                shop_detail__vendor__vendor_id=vendor_id
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_name": f"Product '{product_name}' not found for your shop."})

        return Subscription.objects.create(
            plan_name_en=subscription_name,
            plan_name_hi=subscription_name, # Default same as EN for now
            desc_en=f"Subscription for {product_name}",
            desc_hi=f"{product_name} के लिए सदस्यता",
            product=product,
            **validated_data
        )

    def update(self, instance, validated_data):
        if 'subscription_name' in validated_data:
            name = validated_data.pop('subscription_name')
            instance.plan_name_en = name
            instance.plan_name_hi = name
        
        if 'product_name' in validated_data:
            p_name = validated_data.pop('product_name')
            request = self.context.get('request')
            vendor_id = request.user.user_id
            try:
                product = Product.objects.get(
                    name_en=p_name,
                    shop_detail__vendor__vendor_id=vendor_id
                )
                instance.product = product
                instance.desc_en = f"Subscription for {p_name}"
            except Product.DoesNotExist:
                raise serializers.ValidationError({"product_name": f"Product '{p_name}' not found for your shop."})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'subscription_name': instance.plan_name_en,
            'product_name': instance.product.name_en,
            'frequency': instance.frequency,
            'amount': float(instance.total_amount),
            'image': instance.image
        }
