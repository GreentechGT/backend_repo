from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Category, Product, ShopDetail
from .serializers import UserSerializer, CategorySerializer, ProductSerializer, VendorProductWriteSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_update(self, serializer):
        print(f"\n--- DEBUG UPDATE ---")
        print(f"Product ID: {self.get_object().id}")
        print(f"Request Data: {self.request.data}")
        print(f"Validated Data: {serializer.validated_data}")
        serializer.save()
        print(f"--- END DEBUG ---\n")


class VendorProductsView(generics.ListCreateAPIView):
    """
    GET  /api/vendor-products/  → list products for the logged-in vendor
    POST /api/vendor-products/  → create a new product linked to the vendor's shop
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VendorProductWriteSerializer
        return ProductSerializer

    def get_queryset(self):
        user = self.request.user
        vendor_id = getattr(user, 'user_id', None)

        if not vendor_id:
            return Product.objects.none()

        try:
            shop_detail = ShopDetail.objects.filter(vendor__vendor_id=vendor_id).first()
            if not shop_detail:
                return Product.objects.none()
            return Product.objects.filter(shop_detail=shop_detail).select_related('category', 'shop_detail')
        except Exception:
            return Product.objects.none()

    def perform_create(self, serializer):
        """Auto-link the product to the vendor's ShopDetail."""
        user = self.request.user
        vendor_id = getattr(user, 'user_id', None)

        shop_detail = None
        if vendor_id:
            shop_detail = ShopDetail.objects.filter(vendor__vendor_id=vendor_id).first()

        serializer.save(shop_detail=shop_detail)


class VendorProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/vendor-products/<id>/  → retrieve a specific product
    PATCH  /api/vendor-products/<id>/  → update a vendor's product
    DELETE /api/vendor-products/<id>/  → delete a vendor's product
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return VendorProductWriteSerializer
        return ProductSerializer

    def get_queryset(self):
        user = self.request.user
        vendor_id = getattr(user, 'user_id', None)

        if not vendor_id:
            return Product.objects.none()

        try:
            shop_detail = ShopDetail.objects.filter(vendor__vendor_id=vendor_id).first()
            if not shop_detail:
                return Product.objects.none()
            return Product.objects.filter(shop_detail=shop_detail).select_related('category', 'shop_detail')
        except Exception:
            return Product.objects.none()
