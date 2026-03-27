from rest_framework import serializers
from .models import FAQ, SupportMessage

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ['id', 'name', 'phone', 'message', 'is_resolved', 'created_at']
        read_only_fields = ['is_resolved', 'created_at']
