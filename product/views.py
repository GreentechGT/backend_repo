from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Category, Product, ShopDetail
from .serializers import UserSerializer, CategorySerializer, ProductSerializer

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


class VendorProductsView(generics.ListAPIView):
    """Returns products belonging to the currently logged-in vendor."""
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        vendor_id = getattr(user, 'user_id', None)
        
        if not vendor_id:
            return Product.objects.none()

        try:
            # Using filter().first() instead of get() to be safer against DB inconsistencies
            shop_detail = ShopDetail.objects.filter(vendor__vendor_id=vendor_id).first()
            if not shop_detail:
                return Product.objects.none()
            return Product.objects.filter(shop_detail=shop_detail).select_related('category', 'shop_detail')
        except Exception:
            return Product.objects.none()
