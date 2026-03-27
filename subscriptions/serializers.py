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
            'id', 'subscription_type', 'plan_name', 'description', 
            'product_name', 'image', 'frequency_localized', 
            'slot_localized', 'status_localized', 'status', 
            'slot', 'frequency', 'quantity_litres', 
            'plan_subscribed_date', 'subscription_end_date'
        ] if hasattr(MonthlySubscriber, 'subscription_type') else [
            'id', 'plan_name', 'description', 
            'product_name', 'image', 'frequency_localized', 
            'slot_localized', 'status_localized', 'status', 
            'slot', 'frequency', 'quantity_litres', 
            'plan_subscribed_date', 'subscription_end_date'
        ]
    
    # Actually subscription_type is added in the view's data, so we don't need it in fields if not in model
    # I'll just list the model fields + method fields
    class Meta:
        model = MonthlySubscriber
        fields = [
            'id', 'plan_name', 'description', 
            'product_name', 'image', 'frequency_localized', 
            'slot_localized', 'status_localized', 'status', 
            'slot', 'frequency', 'quantity_litres', 
            'plan_subscribed_date', 'subscription_end_date'
        ]

class YearlySubscriberSerializer(BaseSubscriberSerializer):
    class Meta:
        model = YearlySubscriber
        fields = [
            'id', 'plan_name', 'description', 
            'product_name', 'image', 'frequency_localized', 
            'slot_localized', 'status_localized', 'status', 
            'slot', 'frequency', 'quantity_litres', 
            'plan_subscribed_date', 'subscription_end_date'
        ]
