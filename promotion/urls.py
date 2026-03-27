from django.urls import path
from .views import (
    PromotionListView, PromotionDetailView,
    BannerListView, BannerDetailView,
    OfferListView, OfferDetailView
)

urlpatterns = [
    path('', PromotionListView.as_view(), name='promotion-list'),
    path('<int:pk>/', PromotionDetailView.as_view(), name='promotion-detail'),
    path('banners/', BannerListView.as_view(), name='banner-list'),
    path('banners/<int:pk>/', BannerDetailView.as_view(), name='banner-detail'),
    path('offers/', OfferListView.as_view(), name='offer-list'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
]
