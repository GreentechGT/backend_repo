from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Promotion, Banner, Offer
from .serializers import PromotionSerializer, BannerSerializer, OfferSerializer

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def banner_list(request):
    queryset = Banner.objects.filter(is_active=True)
    serializer = BannerSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def banner_detail(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    serializer = BannerSerializer(banner)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def offer_list(request):
    queryset = Offer.objects.filter(is_active=True)
    serializer = OfferSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def offer_detail(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    serializer = OfferSerializer(offer)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def promotion_list(request):
    now = timezone.now()
    queryset = Promotion.objects.filter(
        is_active=True,
        valid_from__lte=now,
        valid_until__gte=now
    )
    serializer = PromotionSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def promotion_detail(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)
    serializer = PromotionSerializer(promotion)
    return Response(serializer.data)
