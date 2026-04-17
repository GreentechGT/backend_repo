from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CategoryViewSet, ProductViewSet, vendor_products_list, vendor_product_detail

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('vendor-products/', vendor_products_list, name='vendor_products'),
    path('vendor-products/<int:pk>/', vendor_product_detail, name='vendor_product_detail'),
    path('', include(router.urls)),
]
