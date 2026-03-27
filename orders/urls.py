from django.urls import path
from .views import OrderCreateView, OrderListView, VendorOrderListView, VendorOrderStatusUpdateView

urlpatterns = [
    path('', OrderCreateView.as_view(), name='order-create'),
    path('list/', OrderListView.as_view(), name='order-list'),
    path('vendor/', VendorOrderListView.as_view(), name='vendor-order-list'),
    path('vendor/<int:pk>/status/', VendorOrderStatusUpdateView.as_view(), name='vendor-order-status'),
]
