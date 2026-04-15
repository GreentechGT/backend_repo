from django.urls import path
from .views import (
    SubscriptionListView, SubscribeView, UserSubscriptionListView, 
    SubscriptionUpdateView, VendorSubscriptionListView, VendorSubscriptionUpdateView,
    VendorSubscriptionPlanView, VendorSubscriptionPlanDetailView
)

urlpatterns = [
    path('', SubscriptionListView.as_view(), name='subscription-list'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('user/list/', UserSubscriptionListView.as_view(), name='user-subscriptions'),
    path('update-subscription/<str:type>/<int:pk>/', SubscriptionUpdateView.as_view(), name='subscription-update'),
    path('vendor/list/', VendorSubscriptionListView.as_view(), name='vendor-subscriptions'),
    path('vendor/update/<str:type>/<int:pk>/', VendorSubscriptionUpdateView.as_view(), name='vendor-subscription-update'),
    path('vendor/plans/', VendorSubscriptionPlanView.as_view(), name='vendor-subscription-plans'),
    path('vendor/plans/<int:pk>/', VendorSubscriptionPlanDetailView.as_view(), name='vendor-subscription-plan-detail'),
]
