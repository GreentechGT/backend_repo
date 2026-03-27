from django.db import models

class Category(models.Model):
    name_en = models.CharField(max_length=255, unique=True)
    name_hi = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    @property
    def name(self):
        return self.name_en

    def __str__(self):
        return self.name_en

class ShopDetail(models.Model):
    vendor = models.OneToOneField('users.Vendor', to_field='vendor_id', on_delete=models.CASCADE, related_name='shop_detail', null=True, blank=True)
    shop_name_en = models.CharField(max_length=255)
    shop_name_hi = models.CharField(max_length=255, null=True, blank=True)
    address_en = models.TextField()
    address_hi = models.TextField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    opening_time = models.CharField(max_length=50, default='6:00 AM')
    closing_time = models.CharField(max_length=50, default='9:00 PM')

    def __str__(self):
        return self.shop_name_en

class Nutrition(models.Model):
    product = models.OneToOneField('Product', related_name='nutrition', on_delete=models.CASCADE)
    calories = models.CharField(max_length=50)
    protein = models.CharField(max_length=50)
    fat = models.CharField(max_length=50)
    carbs = models.CharField(max_length=50)
    per_unit = models.CharField(max_length=50, default='100ml')

    def __str__(self):
        return f"Nutrition for {self.product.name_en}"

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    shop_detail = models.ForeignKey(ShopDetail, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)

    name_en = models.CharField(max_length=255)
    name_hi = models.CharField(max_length=255, null=True, blank=True)

    description_en = models.TextField(blank=True, null=True)
    description_hi = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField(blank=True, null=True)
    default_quantity = models.CharField(max_length=50, blank=True, null=True)
    discount = models.CharField(max_length=50, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    vendor_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        # Synchronize vendor_id from shop_detail before saving
        if self.shop_detail and self.shop_detail.vendor:
            self.vendor_id = self.shop_detail.vendor.vendor_id
        super().save(*args, **kwargs)

    @property
    def name(self):
        return self.name_en

    @property
    def description(self):
        return self.description_en

    def __str__(self):
        return self.name_en
