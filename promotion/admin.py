from django.contrib import admin
from .models import Promotion, Banner, Offer

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_hi', 'subtitle_en', 'is_active', 'order', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title_en', 'title_hi')
    filter_horizontal = ('products',)

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'type', 'code', 'discount_value', 'discount_type', 'is_active')
    list_filter = ('type', 'discount_type', 'is_active')
    search_fields = ('title_en', 'code', 'category')

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'discount_code', 'discount_percentage', 'is_active', 'valid_until')
    list_filter = ('is_active',)
    search_fields = ('title_en', 'discount_code')
