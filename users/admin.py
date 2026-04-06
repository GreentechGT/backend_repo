from django.contrib import admin
from .models import User, Address, Vendor, Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('cust_id', 'name', 'email', 'phone', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('cust_id', 'name', 'email', 'phone')

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_id', 'shop_name', 'name', 'phone', 'verified', 'created_at')
    list_filter = ('verified', 'created_at')
    search_fields = ('vendor_id', 'shop_name', 'name', 'phone', 'gst_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_id', 'full_name', 'role', 'phone')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'user_id', 'full_name', 'phone')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('User Info', {'fields': ('user_id', 'full_name', 'phone', 'role', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'pincode', 'is_default')
    list_filter = ('city', 'is_default')
    search_fields = ('address', 'city', 'pincode')
