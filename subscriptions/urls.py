from django.urls import path
from .views import SubscriptionListView, SubscribeView, UserSubscriptionListView, SubscriptionUpdateView

urlpatterns = [
    path('', SubscriptionListView.as_view(), name='subscription-list'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('user-subscriptions/', UserSubscriptionListView.as_view(), name='user-subscriptions'),
    path('update-subscription/<str:type>/<int:pk>/', SubscriptionUpdateView.as_view(), name='subscription-update'),
]
