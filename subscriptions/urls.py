from django.urls import path
from .views import (
    subscription_list, subscribe, user_subscription_list, 
    subscription_update, vendor_subscription_list, vendor_subscription_update,
    vendor_subscription_plans, vendor_subscription_plan_detail
)

urlpatterns = [
    path('', subscription_list, name='subscription-list'),
    path('subscribe/', subscribe, name='subscribe'),
    path('user/list/', user_subscription_list, name='user-subscriptions'),
    path('update-subscription/<str:type>/<int:pk>/', subscription_update, name='subscription-update'),
    path('vendor/list/', vendor_subscription_list, name='vendor-subscriptions'),
    path('vendor/update/<str:type>/<int:pk>/', vendor_subscription_update, name='vendor-subscription-update'),
    path('vendor/plans/', vendor_subscription_plans, name='vendor-subscription-plans'),
    path('vendor/plans/<int:pk>/', vendor_subscription_plan_detail, name='vendor-subscription-plan-detail'),
]
