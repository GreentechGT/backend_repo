from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Order, OrderItem
from product.models import Product
from users.models import Address


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField(source='product.name_en', read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product_id', 'product_name', 'product_image', 'quantity', 'price']

    def get_product_image(self, obj):
        if obj.product.image:
            return obj.product.image
        return 'https://cdn-icons-png.flaticon.com/512/3119/3119338.png'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    shipping_address = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'shipping_address', 'full_name', 'phone',
            'address', 'city', 'pincode', 'total_amount',
            'payment_method', 'status', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'user', 'created_at']

    def validate_shipping_address(self, value):
        if value and not Address.objects.filter(id=value).exists():
            return None
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        user = validated_data.pop('user', None)
        if not user:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                user = request.user

        if not user or user.is_anonymous:
            raise serializers.ValidationError({"user": "Authentication required to place an order."})

        shipping_address_id = validated_data.pop('shipping_address', None)
        if shipping_address_id:
            validated_data['shipping_address'] = Address.objects.filter(id=shipping_address_id).first()

        order = Order.objects.create(user=user, **validated_data)

        for item_data in items_data:
            product_id = item_data.pop('product_id')
            product = Product.objects.filter(id=product_id).first()
            if not product:
                raise serializers.ValidationError({"items": f"Product with id {product_id} not found."})
            OrderItem.objects.create(order=order, product=product, **item_data)

        return order

    def to_representation(self, instance):
        try:
            data = super().to_representation(instance)
            # Ensure shipping_address returns the ID as an integer in the response
            if instance.shipping_address:
                data['shipping_address'] = instance.shipping_address.id
            return data
        except Exception as e:
            print(f">>> ERROR during Order Serialization: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return a basic version if full serialization fails to avoid 500
            return {
                "id": instance.id,
                "order_number": f"#ORD-{instance.id}",
                "status": instance.status,
                "total_amount": str(instance.total_amount),
                "message": "Order created, but response serialization had a minor issue."
            }


# ─── Vendor-specific serializers ───────────────────────────────────────────────

class VendorOrderItemSerializer(serializers.ModelSerializer):
    """Serializes an order item for the vendor — product name, image, qty, unit price."""
    name = serializers.CharField(source='product.name_en', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'name', 'image', 'quantity', 'price']

    def get_image(self, obj):
        if obj.product.image:
            return obj.product.image
        return 'https://cdn-icons-png.flaticon.com/512/3119/3119338.png'


class VendorOrderSerializer(serializers.ModelSerializer):
    """
    Serializes an Order for the vendor dashboard.

    Key behaviours:
    - 'items' only contains the OrderItems that belong to the requesting vendor
      (filtered by vendor_id passed via serializer context).
    - Exposes customer name, phone, full address as a flat string.
    - Converts snake_case status and payment_method to human-readable display values.
    """

    PAYMENT_LABELS = {
        'cod': 'Cash on Delivery',
        'online': 'Online Payment',
    }

    STATUS_DISPLAY = {
        'confirmed': 'Confirmed',
        'on_the_way': 'On the way',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled',
    }

    order_number = serializers.ReadOnlyField()
    items = serializers.SerializerMethodField()
    customer_name = serializers.CharField(source='full_name', read_only=True)
    customer_phone = serializers.CharField(source='phone', read_only=True)
    customer_address = serializers.SerializerMethodField()
    payment_method_label = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'total_amount', 'payment_method', 'payment_method_label',
            'customer_name', 'customer_phone', 'customer_address',
            'items', 'created_at',
        ]
        read_only_fields = ['id', 'order_number', 'created_at']

    def get_items(self, obj):
        vendor_id = self.context.get('vendor_id')
        qs = obj.items.filter(vendor_id=vendor_id) if vendor_id else obj.items.all()
        return VendorOrderItemSerializer(qs, many=True).data

    def get_customer_address(self, obj):
        parts = [p for p in [obj.address, obj.city, obj.pincode] if p]
        return ', '.join(parts)

    def get_payment_method_label(self, obj):
        return self.PAYMENT_LABELS.get(obj.payment_method, obj.payment_method)

    def get_status_display(self, obj):
        return self.STATUS_DISPLAY.get(obj.status, obj.status.replace('_', ' ').title())
