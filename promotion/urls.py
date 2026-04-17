from django.urls import path
from .views import (
    promotion_list, promotion_detail,
    banner_list, banner_detail,
    offer_list, offer_detail
)

urlpatterns = [
    path('', promotion_list, name='promotion-list'),
    path('<int:pk>/', promotion_detail, name='promotion-detail'),
    path('banners/', banner_list, name='banner-list'),
    path('banners/<int:pk>/', banner_detail, name='banner-detail'),
    path('offers/', offer_list, name='offer-list'),
    path('offers/<int:pk>/', offer_detail, name='offer-detail'),
]
