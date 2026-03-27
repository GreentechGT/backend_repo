from rest_framework import serializers
from .models import Promotion, Banner, Offer

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'

class BannerSerializer(serializers.ModelSerializer):
    product_ids = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='products')

    class Meta:
        model = Banner
        fields = '__all__'

class OfferSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name_en', read_only=True)

    class Meta:
        model = Offer
        fields = '__all__'
