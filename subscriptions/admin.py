from django.contrib import admin
from .models import Subscription, MonthlySubscriber, YearlySubscriber

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('plan_name_en', 'product', 'frequency_en', 'slot_en', 'status_en', 'total_amount')
    list_filter = ('frequency', 'slot', 'status')
    search_fields = ('plan_name_en', 'product__name_en')

@admin.register(MonthlySubscriber)
class MonthlySubscriberAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_name_en', 'status_en', 'slot_en', 'frequency_en', 'quantity_litres', 'plan_subscribed_date', 'subscription_end_date')
    list_filter = ('status', 'slot', 'frequency', 'plan_subscribed_date')
    search_fields = ('user__username', 'plan_name_en', 'plan__name_en')

@admin.register(YearlySubscriber)
class YearlySubscriberAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_name_en', 'status_en', 'slot_en', 'frequency_en', 'quantity_litres', 'plan_subscribed_date', 'subscription_end_date')
    list_filter = ('status', 'slot', 'frequency', 'plan_subscribed_date')
    search_fields = ('user__username', 'plan_name_en', 'plan__name_en')
