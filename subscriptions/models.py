from django.db import models
from django.conf import settings

def sync_localized_fields(obj):
    # Translations Mapping
    translations = {
        'frequency': {
            'daily': {'en': 'Daily', 'hi': 'दैनिक'},
            'monthly': {'en': 'Monthly', 'hi': 'मासिक'},
        },
        'slot': {
            'morning': {'en': 'Morning', 'hi': 'सुबह'},
            'evening': {'en': 'Evening', 'hi': 'शाम'},
            'both': {'en': 'Both', 'hi': 'दोनों'},
        },
        'status': {
            'active': {'en': 'Active', 'hi': 'सक्रिय'},
            'paused': {'en': 'Paused', 'hi': 'थांबवले'},
        },
        'delivery_status': {
            'confirmed': {'en': 'Confirmed', 'hi': 'पुष्टी केली'},
            'on_the_way': {'en': 'On the Way', 'hi': 'रास्त्यावर'},
            'delivered': {'en': 'Delivered', 'hi': 'वितरित'},
        }
    }

    # Sync Frequency
    if hasattr(obj, 'frequency') and obj.frequency in translations['frequency']:
        t = translations['frequency'][obj.frequency]
        obj.frequency_en = t['en']
        obj.frequency_hi = t['hi']

    # Sync Slot
    if hasattr(obj, 'slot') and obj.slot in translations['slot']:
        t = translations['slot'][obj.slot]
        obj.slot_en = t['en']
        obj.slot_hi = t['hi']

    # Sync Status
    if hasattr(obj, 'status') and obj.status in translations['status']:
        t = translations['status'][obj.status]
        obj.status_en = t['en']
        obj.status_hi = t['hi']

    # Sync Delivery Status
    if hasattr(obj, 'daily_delivery_status') and obj.daily_delivery_status in translations['delivery_status']:
        t = translations['delivery_status'][obj.daily_delivery_status]
        obj.daily_delivery_status_en = t['en']
        obj.daily_delivery_status_hi = t['hi']

class Subscription(models.Model):
    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    SLOT_CHOICES = [
        ('morning', 'Morning'),
        ('evening', 'Evening'),
        ('both', 'Both'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
    ]
    DELIVERY_STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('on_the_way', 'On the Way'),
        ('delivered', 'Delivered'),
    ]
    CATEGORY_CHOICES = [
        ('Monthly Essentials', 'Monthly Essentials'),
        ('Monthly Organic', 'Monthly Organic'),
        ('Yearly Family Packs', 'Yearly Family Packs'),
        ('Yearly Organic', 'Yearly Organic'),
    ]

    image = models.URLField(blank=True, null=True)
    plan_name_en = models.CharField(max_length=255)
    plan_name_hi = models.CharField(max_length=255)
    
    desc_en = models.CharField(max_length=255)
    desc_hi = models.CharField(max_length=255)

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Monthly Essentials')
    is_best_value = models.BooleanField(default=False)
    discount = models.CharField(max_length=50, blank=True, null=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=50, default='Monthly')

    frequency_en = models.CharField(max_length=255, default='Daily')
    frequency_hi = models.CharField(max_length=255, default='दैनिक')

    slot_en = models.CharField(max_length=255, default='Morning')
    slot_hi = models.CharField(max_length=255, default='सुबह')

    status_en = models.CharField(max_length=255, default='Active')
    status_hi = models.CharField(max_length=255, default='सक्रिय')
    
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, related_name='subscriptions')
    
    quantity_litres = models.PositiveIntegerField(default=1)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    slot = models.CharField(max_length=20, choices=SLOT_CHOICES, default='morning')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        sync_localized_fields(self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plan_name_en} - {self.product.name_en} ({self.frequency})"


class MonthlySubscriber(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='monthly_subscriptions')
    plan = models.ForeignKey('product.Product', on_delete=models.CASCADE, related_name='monthly_subscribers')
    
    plan_name_en = models.CharField(max_length=255)
    plan_name_hi = models.CharField(max_length=255)
    
    desc_en = models.CharField(max_length=255)
    desc_hi = models.CharField(max_length=255)

    frequency_en = models.CharField(max_length=255, default='Daily')
    frequency_hi = models.CharField(max_length=255, default='दैनिक')

    slot_en = models.CharField(max_length=255, default='Morning')
    slot_hi = models.CharField(max_length=255, default='सुबह')

    status_en = models.CharField(max_length=255, default='Active')
    status_hi = models.CharField(max_length=255, default='सक्रिय')

    status = models.CharField(max_length=20, choices=Subscription.STATUS_CHOICES, default='active')
    address = models.ForeignKey('users.Address', on_delete=models.SET_NULL, null=True, related_name='monthly_subscriptions')
    
    slot = models.CharField(max_length=20, choices=Subscription.SLOT_CHOICES, default='morning')
    frequency = models.CharField(max_length=20, choices=Subscription.FREQUENCY_CHOICES, default='daily')
    quantity_litres = models.PositiveIntegerField(default=1)
    plan_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Paused Logic
    is_paused = models.BooleanField(default=False)
    is_paused_days = models.PositiveIntegerField(default=0)
    paused_at = models.DateTimeField(null=True, blank=True)
    original_subscription_end_date = models.DateField(null=True, blank=True)
    
    # Delivery logic
    daily_delivery_status = models.CharField(max_length=20, choices=Subscription.DELIVERY_STATUS_CHOICES, default='confirmed')
    daily_delivery_status_en = models.CharField(max_length=20, default='Confirmed')
    daily_delivery_status_hi = models.CharField(max_length=20, default='पुष्टी केली')

    plan_subscribed_date = models.DateField(auto_now_add=True)
    subscription_end_date = models.DateField()
    
    status_ontheway_at = models.DateTimeField(null=True, blank=True)

    status_delivered_at = models.DateTimeField(null=True, blank=True)
    status_confirmed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        from django.utils import timezone
        from datetime import timedelta
        
        # Logic to handle Pause/Resume automation
        if self.pk:
            old_instance = MonthlySubscriber.objects.get(pk=self.pk)
            # Case 1: Just Paused
            if self.is_paused and not old_instance.is_paused:
                self.paused_at = timezone.now()
            # Case 2: Just Resumed
            elif not self.is_paused and old_instance.is_paused:
                if self.paused_at:
                    delta = timezone.now().date() - self.paused_at.date()
                    # Add at least 1 day if it was paused and time has passed, or 0 if same day
                    self.is_paused_days += max(0, delta.days)
                    self.paused_at = None
            
            # Delivery Status Timestamps
            if self.daily_delivery_status != old_instance.daily_delivery_status:
                if self.daily_delivery_status == 'confirmed':
                    self.status_confirmed_at = timezone.now()
                elif self.daily_delivery_status == 'on_the_way':
                    self.status_ontheway_at = timezone.now()

                elif self.daily_delivery_status == 'delivered':
                    self.status_delivered_at = timezone.now()
        else:
            # New subscription
            if self.daily_delivery_status == 'confirmed':
                self.status_confirmed_at = timezone.now()
        
        # Ensure original end date is stored
        if not self.original_subscription_end_date and self.subscription_end_date:
            self.original_subscription_end_date = self.subscription_end_date
            
        # Update current end date based on original + was-paused days
        if self.original_subscription_end_date:
            self.subscription_end_date = self.original_subscription_end_date + timedelta(days=self.is_paused_days)

        sync_localized_fields(self)
        super().save(*args, **kwargs)
        
        # Trigger WebSocket Notification if status changed
        if self.pk:
            try:
                from orders.notifications import notify_subscription_status_change
                notify_subscription_status_change(self)
            except Exception as e:
                print(f"WS Notification Error: {e}")


    def __str__(self):
        return f"{self.user.username} - Monthly - {self.plan.name_en}"

class YearlySubscriber(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='yearly_subscriptions')
    plan = models.ForeignKey('product.Product', on_delete=models.CASCADE, related_name='yearly_subscribers')
    
    plan_name_en = models.CharField(max_length=255)
    plan_name_hi = models.CharField(max_length=255)
    
    desc_en = models.CharField(max_length=255)
    desc_hi = models.CharField(max_length=255)

    frequency_en = models.CharField(max_length=255, default='Daily')
    frequency_hi = models.CharField(max_length=255, default='दैनिक')

    slot_en = models.CharField(max_length=255, default='Morning')
    slot_hi = models.CharField(max_length=255, default='सुबह')

    status_en = models.CharField(max_length=255, default='Active')
    status_hi = models.CharField(max_length=255, default='सक्रिय')

    status = models.CharField(max_length=20, choices=Subscription.STATUS_CHOICES, default='active')
    address = models.ForeignKey('users.Address', on_delete=models.SET_NULL, null=True, related_name='yearly_subscriptions')
    
    slot = models.CharField(max_length=20, choices=Subscription.SLOT_CHOICES, default='morning')
    frequency = models.CharField(max_length=20, choices=Subscription.FREQUENCY_CHOICES, default='daily')
    quantity_litres = models.PositiveIntegerField(default=1)
    plan_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Paused Logic
    is_paused = models.BooleanField(default=False)
    is_paused_days = models.PositiveIntegerField(default=0)
    paused_at = models.DateTimeField(null=True, blank=True)
    original_subscription_end_date = models.DateField(null=True, blank=True)
    
    # Delivery logic
    daily_delivery_status = models.CharField(max_length=20, choices=Subscription.DELIVERY_STATUS_CHOICES, default='confirmed')
    daily_delivery_status_en = models.CharField(max_length=20, default='Confirmed')
    daily_delivery_status_hi = models.CharField(max_length=20, default='पुष्टी केली')

    plan_subscribed_date = models.DateField(auto_now_add=True)
    subscription_end_date = models.DateField()
    
    status_ontheway_at = models.DateTimeField(null=True, blank=True)

    status_delivered_at = models.DateTimeField(null=True, blank=True)
    status_confirmed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        from django.utils import timezone
        from datetime import timedelta

        if self.pk:
            old_instance = YearlySubscriber.objects.get(pk=self.pk)
            if self.is_paused and not old_instance.is_paused:
                self.paused_at = timezone.now()
            elif not self.is_paused and old_instance.is_paused:
                if self.paused_at:
                    delta = timezone.now().date() - self.paused_at.date()
                    self.is_paused_days += max(0, delta.days)
                    self.paused_at = None
            
            # Delivery Status Timestamps
            if self.daily_delivery_status != old_instance.daily_delivery_status:
                if self.daily_delivery_status == 'confirmed':
                    self.status_confirmed_at = timezone.now()
                elif self.daily_delivery_status == 'on_the_way':
                    self.status_ontheway_at = timezone.now()

                elif self.daily_delivery_status == 'delivered':
                    self.status_delivered_at = timezone.now()
        else:
            # New subscription
            if self.daily_delivery_status == 'confirmed':
                self.status_confirmed_at = timezone.now()

        if not self.original_subscription_end_date and self.subscription_end_date:
            self.original_subscription_end_date = self.subscription_end_date
            
        if self.original_subscription_end_date:
            self.subscription_end_date = self.original_subscription_end_date + timedelta(days=self.is_paused_days)

        sync_localized_fields(self)
        super().save(*args, **kwargs)

        # Trigger WebSocket Notification if status changed
        if self.pk:
            try:
                from orders.notifications import notify_subscription_status_change
                notify_subscription_status_change(self)
            except Exception as e:
                print(f"WS Notification Error: {e}")


    def __str__(self):
        return f"{self.user.username} - Yearly - {self.plan.name_en}"
