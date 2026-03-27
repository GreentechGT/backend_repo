from rest_framework import generics, permissions
from django.utils import timezone
from .models import Promotion, Banner, Offer
from .serializers import PromotionSerializer, BannerSerializer, OfferSerializer

class BannerListView(generics.ListAPIView):
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer
    permission_classes = [permissions.AllowAny]

class BannerDetailView(generics.RetrieveAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [permissions.AllowAny]

class OfferListView(generics.ListAPIView):
    serializer_class = OfferSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Offer.objects.filter(is_active=True)

class OfferDetailView(generics.RetrieveAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [permissions.AllowAny]

class PromotionListView(generics.ListAPIView):
    serializer_class = PromotionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return Promotion.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        )

class PromotionDetailView(generics.RetrieveAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [permissions.AllowAny]
