from django.urls import path
from .views import (
    order_create, order_list, main_order_list, vendor_order_list, 
    vendor_order_status_update, vendor_payment_list, user_order_cancel, order_delete, vendor_dashboard,
    initiate_payment, verify_payment
)

urlpatterns = [
    path('', order_create, name='order-create'),
    path('list/', order_list, name='order-list'),
    path('history/', main_order_list, name='main-order-history'),
    path('<int:pk>/cancel/', user_order_cancel, name='user-order-cancel'),
    path('<int:pk>/', order_delete, name='order-delete'),
    path('vendor/', vendor_order_list, name='vendor-order-list'),
    path('vendor/dashboard/', vendor_dashboard, name='vendor-dashboard'),
    path('vendor/payments/', vendor_payment_list, name='vendor-payment-list'),
    path('vendor/<int:pk>/status/', vendor_order_status_update, name='vendor-order-status'),
    
    # Razorpay Payments
    path('payments/initiate/', initiate_payment, name='payment-initiate'),
    path('payments/verify/', verify_payment, name='payment-verify'),
]
