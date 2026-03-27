from django.conf import settings
from django.db import models

# Create your models here.
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
    ]

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

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def order_number(self):
        return f"#ORD-{self.id}"

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