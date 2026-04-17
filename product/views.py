from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Category, Product, ShopDetail
from .serializers import UserSerializer, CategorySerializer, ProductSerializer, VendorProductWriteSerializer
from rest_framework.exceptions import NotFound

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

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def vendor_products_list(request):
    """
    GET  /api/vendor-products/  → list products for the logged-in vendor
    POST /api/vendor-products/  → create a new product linked to the vendor's shop
    """
    user = request.user
    vendor_id = getattr(user, 'user_id', None)

    if not vendor_id:
        if request.method == 'GET':
            return Response([])
        return Response({'error': 'Not an authenticated vendor'}, status=status.HTTP_403_FORBIDDEN)

    try:
        shop_detail = ShopDetail.objects.filter(vendor__vendor_id=vendor_id).first()
    except Exception:
        shop_detail = None

    if request.method == 'GET':
        if not shop_detail:
            return Response([])
        products = Product.objects.filter(shop_detail=shop_detail).select_related('category', 'shop_detail')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = VendorProductWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(shop_detail=shop_detail)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def vendor_product_detail(request, pk):
    """
    GET    /api/vendor-products/<id>/  → retrieve a specific product
    PATCH  /api/vendor-products/<id>/  → update a vendor's product
    DELETE /api/vendor-products/<id>/  → delete a vendor's product
    """
    user = request.user
    vendor_id = getattr(user, 'user_id', None)

    if not vendor_id:
        return Response({'error': 'Not an authenticated vendor'}, status=status.HTTP_403_FORBIDDEN)

    try:
        shop_detail = ShopDetail.objects.filter(vendor__vendor_id=vendor_id).first()
        if not shop_detail:
            raise NotFound(detail="Product not found or you do not have permission.")
        product = Product.objects.get(pk=pk, shop_detail=shop_detail)
    except (Product.DoesNotExist, Exception):
        raise NotFound(detail="Product not found or you do not have permission.")

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        serializer = VendorProductWriteSerializer(product, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
