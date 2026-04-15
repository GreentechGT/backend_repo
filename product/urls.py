from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CategoryViewSet, ProductViewSet, VendorProductsView, VendorProductDetailView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('vendor-products/', VendorProductsView.as_view(), name='vendor_products'),
    path('vendor-products/<int:pk>/', VendorProductDetailView.as_view(), name='vendor_product_detail'),
    path('', include(router.urls)),
]
