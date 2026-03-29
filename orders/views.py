from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, VendorOrderSerializer


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            print(f">>> Processing Order for User: {self.request.user}")
            serializer.save(user=self.request.user)
            print(">>> Order Created Successfully!")
        except Exception as e:
            print(f">>> ERROR during Order Creation: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


# ─── Vendor Views ──────────────────────────────────────────────────────────────

class VendorOrderListView(generics.ListAPIView):
    """
    Returns all orders that contain at least one item belonging to the
    currently authenticated vendor (matched by user.user_id == OrderItem.vendor_id).
    Each order's 'items' list is filtered to only include that vendor's products.
    """
    serializer_class = VendorOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        vendor_id = self.request.user.user_id
        if not vendor_id:
            return Order.objects.none()
        return (
            Order.objects
            .filter(items__vendor_id=vendor_id)
            .distinct()
            .prefetch_related('items', 'items__product')
            .order_by('-created_at')
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['vendor_id'] = self.request.user.user_id
        return context


class VendorOrderStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/orders/vendor/<pk>/status/
    Allows the vendor to update the status of an order that contains their items.
    Accepts body: { "status": "on_the_way" }
    """
    serializer_class = VendorOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    VALID_STATUSES = ['confirmed', 'on_the_way', 'delivered', 'cancelled']

    def get_queryset(self):
        vendor_id = self.request.user.user_id
        if not vendor_id:
            return Order.objects.none()
        return Order.objects.filter(items__vendor_id=vendor_id).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['vendor_id'] = self.request.user.user_id
        return context

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {'error': 'status field is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in self.VALID_STATUSES:
            return Response(
                {'error': f'Invalid status. Valid choices: {self.VALID_STATUSES}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save(update_fields=['status'])

        serializer = self.get_serializer(order)
        return Response(serializer.data)
 
 
class UserOrderCancelView(generics.UpdateAPIView):
    """
    PATCH /api/orders/<pk>/cancel/
    Allows the customer to cancel their own order if it's still 'pending' or 'confirmed'.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']
 
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
 
    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        allowed_statuses = ['pending', 'confirmed']
        
        if order.status.lower() not in allowed_statuses:
            return Response(
                {'error': f'Order cannot be cancelled in its current state ({order.status}).'},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        order.status = 'cancelled'
        order.save(update_fields=['status'])
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
 
 
class OrderDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/orders/<pk>/
    Allows the customer to delete their own order if it's 'cancelled' or 'delivered'.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
 
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
 
    def perform_destroy(self, instance):
        allowed_statuses = ['cancelled', 'delivered']
        if instance.status.lower() not in allowed_statuses:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f'Order can only be deleted if it is cancelled or delivered.')
        instance.delete()
