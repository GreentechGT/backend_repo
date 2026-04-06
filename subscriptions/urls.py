from django.urls import path
from .views import SubscriptionListView, SubscribeView, UserSubscriptionListView, SubscriptionUpdateView, VendorSubscriptionListView, VendorSubscriptionUpdateView

urlpatterns = [
    path('', SubscriptionListView.as_view(), name='subscription-list'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('user/list/', UserSubscriptionListView.as_view(), name='user-subscriptions'),
    path('update-subscription/<str:type>/<int:pk>/', SubscriptionUpdateView.as_view(), name='subscription-update'),
    path('vendor/list/', VendorSubscriptionListView.as_view(), name='vendor-subscriptions'),
    path('vendor/update/<str:type>/<int:pk>/', VendorSubscriptionUpdateView.as_view(), name='vendor-subscription-update'),
]
