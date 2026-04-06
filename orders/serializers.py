from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MainOrder, Order, OrderItem, Payment, VendorSettlement
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
    shipping_address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        required=False,
        allow_null=True
    )
    # Calculated server-side — frontend does NOT need to send these
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        required=False, default=0
    )
    status = serializers.CharField(required=False, default='confirmed')
    vendor_id = serializers.CharField(read_only=True)
    is_multi_vendor = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'main_order', 'vendor_id',
            'shipping_address', 'full_name', 'phone',
            'address', 'city', 'pincode', 'total_amount',
            'payment_method', 'status', 'items', 'created_at',
            'is_multi_vendor',
            'status_confirmed_at', 'status_ontheway_at', 'status_delivered_at', 'status_cancelled_at',
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'main_order', 'vendor_id', 'created_at',
            'status_confirmed_at', 'status_ontheway_at', 'status_delivered_at', 'status_cancelled_at',
        ]

    def get_is_multi_vendor(self, obj):
        if obj.main_order:
            return obj.main_order.is_multi_vendor
        return False

    def validate_shipping_address(self, value):
        if value and not Address.objects.filter(id=value.id).exists():
            return None
        return value

    def create(self, validated_data):
        try:
            items_data = validated_data.pop('items')

            user = validated_data.pop('user', None)
            if not user:
                request = self.context.get('request')
                if request and hasattr(request, 'user'):
                    user = request.user

            if not user or user.is_anonymous:
                raise serializers.ValidationError({"user": "Authentication required to place an order."})

            # 1. Group items by vendor
            vendor_items = {}
            total_amount = 0
            
            for item_data in items_data:
                product_id = item_data.get('product_id')
                product = Product.objects.filter(id=product_id).first()
                if not product:
                    raise serializers.ValidationError({"items": f"Product with id {product_id} not found."})
                
                v_id = product.vendor_id
                if not v_id:
                    v_id = "unknown" # Fallback
                
                if v_id not in vendor_items:
                    vendor_items[v_id] = []
                
                # Add product instance and data to group
                item_price = item_data.get('price', product.price)
                quantity = item_data.get('quantity', 1)
                line_total = item_price * quantity
                total_amount += line_total
                
                vendor_items[v_id].append({
                    'product': product,
                    'quantity': quantity,
                    'price': item_price
                })

            # 2. Create MainOrder
            is_multi_vendor = len(vendor_items) > 1
            main_order_status = 'placed' if is_multi_vendor else 'pending_payment'
            
            # Remove keys that we pass explicitly to avoid TypeError
            validated_data.pop('total_amount', None)
            validated_data.pop('status', None)

            main_order = MainOrder.objects.create(
                user=user,
                total_amount=total_amount,
                is_multi_vendor=is_multi_vendor,
                status=main_order_status,
                **validated_data
            )

            # 3. Create Vendor Orders (Sub-Orders)
            created_orders = []
            for v_id, items in vendor_items.items():
                vendor_total = sum(item['price'] * item['quantity'] for item in items)
                
                # Default status for multi-vendor is 'confirmed' (Place directly)
                # Single-vendor starts as 'confirmed' but MainOrder is 'pending_payment'
                # (Logic here depends on if COD or Online)
                sub_order_status = 'confirmed' 
                
                sub_order = Order.objects.create(
                    main_order=main_order,
                    vendor_id=v_id,
                    user=user,
                    status=sub_order_status,
                    total_amount=vendor_total,
                    **validated_data
                )
                
                for item in items:
                    OrderItem.objects.create(
                        order=sub_order,
                        product=item['product'],
                        quantity=item['quantity'],
                        price=item['price'],
                        vendor_id=v_id
                    )
                
                created_orders.append(sub_order)

            # 4. Handle Payment Recording (COD and Multi-Vendor)
            # Standard Online payments are handled separately in InitiatePaymentView.
            # Here we handle all other cases to ensure they appear in the history.
            should_create_payment = is_multi_vendor or validated_data.get('payment_method') == 'cod'
            
            if should_create_payment:
                try:
                    payment_method = 'internal_settlement' if is_multi_vendor else 'cod'
                    
                    # Determine vendor_id for single-vendor COD
                    payment_vendor_id = None
                    if not is_multi_vendor and len(created_orders) > 0:
                        payment_vendor_id = created_orders[0].vendor_id

                    payment = Payment.objects.create(
                        user=user,
                        main_order=main_order,
                        vendor_id=payment_vendor_id,
                        amount=total_amount,
                        status='pending',
                        payment_method=payment_method,
                        razorpay_order_id=f"{payment_method.upper()}-{main_order.id}-{int(main_order.created_at.timestamp())}"
                    )
                    
                    # Create settlements for each vendor involved
                    for sub in created_orders:
                        VendorSettlement.objects.create(
                            payment=payment,
                            vendor_order=sub,
                            vendor_id=sub.vendor_id,
                            amount=sub.total_amount,
                            status='pending'
                        )
                except Exception as pe:
                    print(f"Error creating payment/settlement record: {pe}")

            # Notify vendors
            try:
                from .notifications import notify_vendor_dashboard_refresh
                for v_id in vendor_items.keys():
                    if v_id and v_id != "unknown":
                        notify_vendor_dashboard_refresh(v_id)
            except Exception as e:
                print(f"WS Notification Error (Order Creation): {e}")

            # Return the first order (to satisfy Serializer return requirement)
            # We add main_order info to the returned object if needed
            return created_orders[0]
        except Exception as e:
            print(f"CRITICAL ERROR in OrderSerializer.create: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e


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
    is_multi_vendor = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'total_amount', 'payment_method', 'payment_method_label',
            'customer_name', 'customer_phone', 'customer_address',
            'items', 'created_at', 'is_multi_vendor'
        ]
        read_only_fields = ['id', 'order_number', 'created_at']

    def get_is_multi_vendor(self, obj):
        if obj.main_order:
            return obj.main_order.is_multi_vendor
        return False

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


class VendorSettlementSerializer(serializers.ModelSerializer):
    """
    Serializes a VendorSettlement for the vendor dashboard payment history.
    Provides customer info and payment method details.
    """
    customer_name = serializers.CharField(source='vendor_order.full_name', read_only=True)
    order_number = serializers.CharField(source='vendor_order.order_number', read_only=True)
    payment_method = serializers.CharField(source='payment.payment_method', read_only=True)
    payment_status = serializers.CharField(source='payment.status', read_only=True)
    date = serializers.DateTimeField(source='created_at', format="%b %d", read_only=True)
    time = serializers.DateTimeField(source='created_at', format="%I:%M %p", read_only=True)

    class Meta:
        model = VendorSettlement
        fields = [
            'id', 'customer_name', 'order_number', 'amount', 
            'status', 'payment_status', 'payment_method', 
            'date', 'time', 'created_at'
        ]


class MainOrderSerializer(serializers.ModelSerializer):
    vendor_orders = VendorOrderSerializer(many=True, read_only=True)

    class Meta:
        model = MainOrder
        fields = [
            'id', 'user', 'shipping_address', 'full_name', 'phone',
            'address', 'city', 'pincode', 'total_amount',
            'payment_method', 'status', 'razorpay_order_id',
            'is_multi_vendor', 'vendor_orders', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RazorpayOrderSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_id = serializers.IntegerField(required=False)

class PaymentVerificationSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
