from django.db import models

class Banner(models.Model):
    title_en = models.CharField(max_length=255)
    title_hi = models.CharField(max_length=255, blank=True, null=True)

    subtitle_en = models.CharField(max_length=255, blank=True, null=True)
    subtitle_hi = models.CharField(max_length=255, blank=True, null=True)

    color = models.CharField(max_length=50, blank=True, null=True)
    image = models.URLField()
    products = models.ManyToManyField('product.Product', related_name='banners', blank=True)
    link_url = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title_en

class Offer(models.Model):
    OFFER_TYPES = [
        ('Coupon', 'Coupon'),
        ('Bank', 'Bank'),
        ('Exclusive', 'Exclusive'),
    ]
    
    type = models.CharField(max_length=20, choices=OFFER_TYPES, default='Coupon')
    code = models.CharField(max_length=50, blank=True, null=True)
    
    title_en = models.CharField(max_length=255)
    title_hi = models.CharField(max_length=255, blank=True, null=True)
    
    description_en = models.TextField()
    description_hi = models.TextField(blank=True, null=True)
    
    expiry_text = models.CharField(max_length=100)
    color = models.CharField(max_length=50, default='#3b82f6')
    category = models.CharField(max_length=100, blank=True, null=True)
    
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=20, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    applicable_categories = models.JSONField(default=list, blank=True)
    
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, related_name='offers', null=True, blank=True)
    image = models.URLField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title_en

class Promotion(models.Model):
    title_en = models.CharField(max_length=255)
    title_hi = models.CharField(max_length=255, null=True, blank=True)

    description_en = models.TextField()
    description_hi = models.TextField(null=True, blank=True)

    discount_code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage discount")
    
    image = models.URLField(blank=True, null=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def title(self):
        return self.title_en

    @property
    def description(self):
        return self.description_en

    def __str__(self):
        return self.title_en
