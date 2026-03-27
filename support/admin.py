from django.contrib import admin
from .models import FAQ, SupportMessage

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question_en', 'created_at')
    search_fields = ('question_en', 'answer_en', 'question_hi', 'answer_hi')

@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('name', 'phone', 'message')
    readonly_fields = ('created_at',)
