from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'full_name', 'total_amount', 'payment_method', 'status', 'address', 'city', 'pincode', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('full_name', 'phone', 'city')
    inlines = [OrderItemInline]
    raw_id_fields = ('user', 'shipping_address')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
