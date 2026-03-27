from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Category, Product, ShopDetail, Nutrition

User = get_user_model()

# Register your models here.



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en','name_hi',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_en','name_hi', 'price', 'category', 'default_quantity', 'discount', 'shop_detail')
    list_filter = ('category', 'shop_detail')
    search_fields = ('name_en', 'description_en')

@admin.register(ShopDetail)
class ShopDetailAdmin(admin.ModelAdmin):
    list_display = ('shop_name_en', 'shop_name_hi', 'address_en', 'address_hi', 'rating')
    search_fields = ('shop_name_en', 'shop_name_hi', 'address_en', 'address_hi')

@admin.register(Nutrition)
class NutritionAdmin(admin.ModelAdmin):
    list_display = ('product', 'calories', 'protein', 'fat', 'carbs')
    search_fields = ('product__name_en',)
