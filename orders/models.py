from django.conf import settings
from django.db import models
from django.utils import timezone

# Create your models here.
class MainOrder(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('placed', 'Placed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey('users.Address', on_delete=models.SET_NULL, null=True, blank=True)

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, default='online')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    is_multi_vendor = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MainOrder #{self.id} ({self.status})"

class Order(models.Model):

    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('on_the_way', 'On the Way'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
    ]

    main_order = models.ForeignKey(MainOrder, on_delete=models.CASCADE, related_name='vendor_orders', null=True, blank=True)
    vendor_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey('users.Address', on_delete=models.SET_NULL, null=True, blank=True)

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cod'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed'
    )

    # Status Timestamps
    status_confirmed_at = models.DateTimeField(null=True, blank=True)
    status_ontheway_at = models.DateTimeField(null=True, blank=True)
    status_delivered_at = models.DateTimeField(null=True, blank=True)
    status_cancelled_at = models.DateTimeField(null=True, blank=True)


    # Legacy subscription-link fields (kept for DB compatibility – migration 0011)
    is_subscription_order = models.BooleanField(default=False)
    subscriber_id = models.IntegerField(null=True, blank=True)
    subscription_type = models.CharField(
        max_length=20,
        choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')],
        null=True,
        blank=True,
    )

    delivery_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def order_number(self):
        return f"#ORD-{self.id}"

    def save(self, *args, **kwargs):
        is_existing_order = self.pk is not None
        if is_existing_order:
            old_instance = Order.objects.get(pk=self.pk)
            if self.status != old_instance.status:
                if self.status == 'confirmed':
                    self.status_confirmed_at = timezone.now()
                elif self.status == 'on_the_way':
                    self.status_ontheway_at = timezone.now()
                elif self.status == 'delivered':
                    self.status_delivered_at = timezone.now()
                elif self.status == 'cancelled':
                    self.status_cancelled_at = timezone.now()
        else:
            # Set initials for new order
            if self.status == 'confirmed':
                self.status_confirmed_at = timezone.now()

        super().save(*args, **kwargs)

        # Notify relevant vendors only on status updates for existing orders
        # (New orders are handled by the Serializer)
        if is_existing_order:
            try:
                from .notifications import notify_vendor_dashboard_refresh
                vendor_ids = self.items.values_list('vendor_id', flat=True).distinct()
                for v_id in vendor_ids:
                    if v_id:
                        notify_vendor_dashboard_refresh(v_id)
            except Exception as e:
                print(f"WS Notification Error (Order Status Update): {e}")

    def __str__(self):
        return self.order_number

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        "product.Product",
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField(default=1)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    vendor_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        # Always synchronize vendor_id from the product to ensure data integrity
        if self.product_id:
            self.vendor_id = self.product.vendor_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name_en} - {self.quantity}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    main_order = models.ForeignKey(MainOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    vendor_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=200, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.razorpay_order_id} - {self.status}"

class VendorSettlement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('settled', 'Settled'),
        ('failed', 'Failed'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='settlements')
    vendor_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='settlements')
    vendor_id = models.CharField(max_length=50, db_index=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    razorpay_transfer_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settlement {self.vendor_id} - {self.amount} ({self.status})"