from django.urls import path
from .views import (
    OrderCreateView, OrderListView, MainOrderListView, VendorOrderListView, 
    VendorOrderStatusUpdateView, VendorPaymentListView, UserOrderCancelView, OrderDeleteView, VendorDashboardView,
    InitiatePaymentView, VerifyPaymentView
)

urlpatterns = [
    path('', OrderCreateView.as_view(), name='order-create'),
    path('list/', OrderListView.as_view(), name='order-list'),
    path('history/', MainOrderListView.as_view(), name='main-order-history'),
    path('<int:pk>/cancel/', UserOrderCancelView.as_view(), name='user-order-cancel'),
    path('<int:pk>/', OrderDeleteView.as_view(), name='order-delete'),
    path('vendor/', VendorOrderListView.as_view(), name='vendor-order-list'),
    path('vendor/dashboard/', VendorDashboardView.as_view(), name='vendor-dashboard'),
    path('vendor/payments/', VendorPaymentListView.as_view(), name='vendor-payment-list'),
    path('vendor/<int:pk>/status/', VendorOrderStatusUpdateView.as_view(), name='vendor-order-status'),
    
    # Razorpay Payments
    path('payments/initiate/', InitiatePaymentView.as_view(), name='payment-initiate'),
    path('payments/verify/', VerifyPaymentView.as_view(), name='payment-verify'),
]
