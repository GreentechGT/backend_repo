from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import MainOrder, Order, OrderItem, Payment, VendorSettlement
from .serializers import MainOrderSerializer, OrderSerializer, VendorOrderSerializer, VendorSettlementSerializer
from .notifications import notify_order_status_change
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F
from rest_framework.exceptions import ValidationError
import razorpay
from django.conf import settings
from .serializers import RazorpayOrderSerializer, PaymentVerificationSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def order_create(request):
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        try:
            print(f">>> Processing Order for User: {request.user}")
            serializer.save(user=request.user)
            print(">>> Order Created Successfully!")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f">>> ERROR during Order Creation: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_list(request):
    queryset = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def main_order_list(request):
    """
    Returns a list of Main Orders (checkouts) with nested vendor-specific orders.
    Useful for 'Order History' grouped view.
    """
    queryset = MainOrder.objects.filter(user=request.user).order_by('-created_at')
    serializer = MainOrderSerializer(queryset, many=True)
    return Response(serializer.data)

# ─── Vendor Views ──────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def vendor_order_list(request):
    """
    Returns all orders that contain at least one item belonging to the
    currently authenticated vendor (matched by user.user_id == OrderItem.vendor_id).
    Each order's 'items' list is filtered to only include that vendor's products.
    """
    vendor_id = request.user.user_id
    if not vendor_id:
        return Response([])

    queryset = (
        Order.objects
        .filter(items__vendor_id=vendor_id)
        .distinct()
        .prefetch_related('items', 'items__product')
        .order_by('-created_at')
    )
    context = {'vendor_id': vendor_id, 'request': request}
    serializer = VendorOrderSerializer(queryset, many=True, context=context)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def vendor_payment_list(request):
    """
    Returns a list of successful payments/settlements for the vendor.
    Used for the 'Payments' screen in the vendor app.
    """
    vendor_id = request.user.user_id
    if not vendor_id:
        return Response([])
    
    queryset = (
        VendorSettlement.objects
        .filter(vendor_id=vendor_id)
        .select_related('payment', 'vendor_order')
        .order_by('-created_at')
    )
    serializer = VendorSettlementSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def vendor_order_status_update(request, pk):
    """
    PATCH /api/orders/vendor/<pk>/status/
    Allows the vendor to update the status of an order that contains their items.
    Accepts body: { "status": "on_the_way" }
    """
    VALID_STATUSES = ['confirmed', 'on_the_way', 'delivered', 'cancelled']
    
    vendor_id = request.user.user_id
    if not vendor_id:
        return Response({'error': 'Vendor ID missing'}, status=status.HTTP_403_FORBIDDEN)
        
    try:
        order = Order.objects.get(pk=pk, items__vendor_id=vendor_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')

    if not new_status:
        return Response(
            {'error': 'status field is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if new_status not in VALID_STATUSES:
        return Response(
            {'error': f'Invalid status. Valid choices: {VALID_STATUSES}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    order.status = new_status
    order.save() # Call full save to trigger timestamp logic

    # Trigger settlement and payment status sync (Discrete Success Event for COD)
    if new_status == 'delivered':
        try:
            # Create a NEW Success record for the delivery event
            timestamp = int(timezone.now().timestamp())
            new_payment = Payment.objects.create(
                user=order.user,
                main_order=order.main_order,
                order=order if not order.main_order else None,
                vendor_id=order.vendor_id,
                amount=order.total_amount,
                status='success',
                payment_method='cod_collection',
                razorpay_order_id=f"SUCCESS-{order.id}-{timestamp}"
            )
            
            # Create a NEW Settlement record for the successful collection
            VendorSettlement.objects.create(
                payment=new_payment,
                vendor_order=order,
                vendor_id=order.vendor_id,
                amount=order.total_amount,
                status='settled'
            )
            print(f">>> DISCRETE SUCCESS EVENT: Created new success record for COD order {order.id}")
        except Exception as e:
            print(f"Error creating discrete success event: {e}")

    # Trigger WebSocket Notification (wrapped to avoid 500 if channels offline)
    try:
        notify_order_status_change(order)
    except Exception as e:
        print(f"WS Notification Error (Vendor Status Update): {e}")

    context = {'vendor_id': vendor_id, 'request': request}
    serializer = VendorOrderSerializer(order, context=context)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def user_order_cancel(request, pk):
    """
    PATCH /api/orders/<pk>/cancel/
    Allows the customer to cancel their own order if it's still 'pending' or 'confirmed'.
    """
    try:
        order = Order.objects.get(pk=pk, user=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    allowed_statuses = ['pending', 'confirmed']
    
    if order.status.lower() not in allowed_statuses:
        return Response(
            {'error': f'Order cannot be cancelled in its current state ({order.status}).'},
            status=status.HTTP_400_BAD_REQUEST
        )

    order.status = 'cancelled'
    order.save() # Call full save to trigger timestamp logic
    
    # Trigger WebSocket Notification (wrapped to avoid 500 if channels offline)
    try:
        notify_order_status_change(order)
    except Exception as e:
        print(f"WS Notification Error (User Cancel): {e}")
    
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def order_delete(request, pk):
    """
    DELETE /api/orders/<pk>/
    Allows the customer to delete their own order if it's 'cancelled' or 'delivered'.
    """
    try:
        instance = Order.objects.get(pk=pk, user=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    allowed_statuses = ['cancelled', 'delivered']
    if instance.status.lower() not in allowed_statuses:
        raise ValidationError(f'Order can only be deleted if it is cancelled or delivered.')
        
    instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def vendor_dashboard(request):
    """
    GET /api/orders/vendor/dashboard/
    Aggregates metrics for the Vendor HomeScreen.
    """
    vendor_id = request.user.user_id
    if not vendor_id:
        return Response({'error': 'Vendor ID not found for user.'}, status=400)
        
    today = timezone.now().date()
    from subscriptions.models import MonthlySubscriber, YearlySubscriber
    from subscriptions.serializers import MonthlySubscriberSerializer, YearlySubscriberSerializer
    
    # Deliveries & Progress
    active_monthly_subs = MonthlySubscriber.objects.filter(
        plan__vendor_id=vendor_id, status='active', is_paused=False
    )
    active_yearly_subs = YearlySubscriber.objects.filter(
        plan__vendor_id=vendor_id, status='active', is_paused=False
    )
    
    subs_delivery_count = active_monthly_subs.count() + active_yearly_subs.count()
    today_orders = Order.objects.filter(items__vendor_id=vendor_id, delivery_date=today).distinct()
    orders_delivery_count = today_orders.count()
    total_deliveries = subs_delivery_count + orders_delivery_count
    
    delivered_subs = (
        active_monthly_subs.filter(daily_delivery_status='delivered').count() +
        active_yearly_subs.filter(daily_delivery_status='delivered').count()
    )
    delivered_orders = today_orders.filter(status='delivered').count()
    
    delivered_total = delivered_subs + delivered_orders
    pending_total = total_deliveries - delivered_total
    percentage = (delivered_total / total_deliveries) if total_deliveries > 0 else 0
    
    # Financials (ONLY deliveries made today)
    delivered_order_items = OrderItem.objects.filter(
        vendor_id=vendor_id, 
        order__status='delivered', 
        order__status_delivered_at__date=today
    )
    product_revenue_today = delivered_order_items.aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0
    
    # Subscription revenue for today based on deliveries made
    delivered_monthly = MonthlySubscriber.objects.filter(
        plan__vendor_id=vendor_id, 
        daily_delivery_status='delivered', 
        status_delivered_at__date=today
    )
    delivered_yearly = YearlySubscriber.objects.filter(
        plan__vendor_id=vendor_id, 
        daily_delivery_status='delivered', 
        status_delivered_at__date=today
    )
    
    sub_revenue_today = 0
    for sub in list(delivered_monthly) + list(delivered_yearly):
        # sub.plan is Product, use its current price * quantity
        sub_revenue_today += float(sub.quantity_litres * sub.plan.price)
    
    total_revenue_today = float(sub_revenue_today) + float(product_revenue_today)
    
    # Growth Calculation
    yesterday = today - timedelta(days=1)
    yest_monthly_subs = MonthlySubscriber.objects.filter(plan__vendor_id=vendor_id, created_at__date=yesterday)
    yest_yearly_subs = YearlySubscriber.objects.filter(plan__vendor_id=vendor_id, created_at__date=yesterday)
    yest_sub_rev = (
        (yest_monthly_subs.aggregate(total=Sum('plan_price'))['total'] or 0) +
        (yest_yearly_subs.aggregate(total=Sum('plan_price'))['total'] or 0)
    )
    yest_order_items = OrderItem.objects.filter(vendor_id=vendor_id, order__created_at__date=yesterday)
    yest_prod_rev = yest_order_items.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
    yest_total_rev = yest_sub_rev + yest_prod_rev
    
    if float(yest_total_rev) == 0:
        growth = "+100%" if total_revenue_today > 0 else "0%"
    else:
        pct = ((total_revenue_today - float(yest_total_rev)) / float(yest_total_rev)) * 100
        growth = f"+{pct:.1f}%" if pct > 0 else f"{pct:.1f}%"
        
    # Subscription Stats
    all_monthly = MonthlySubscriber.objects.filter(plan__vendor_id=vendor_id)
    all_yearly = YearlySubscriber.objects.filter(plan__vendor_id=vendor_id)
    
    active_count = all_monthly.filter(status='active', is_paused=False).count() + all_yearly.filter(status='active', is_paused=False).count()
    paused_count = all_monthly.filter(status='active', is_paused=True).count() + all_yearly.filter(status='active', is_paused=True).count()
    
    new_monthly_subs = MonthlySubscriber.objects.filter(plan__vendor_id=vendor_id, created_at__date=today)
    new_yearly_subs = YearlySubscriber.objects.filter(plan__vendor_id=vendor_id, created_at__date=today)
    new_today_count = new_monthly_subs.count() + new_yearly_subs.count()
    
    sub_liters = (
        (active_monthly_subs.aggregate(total=Sum('quantity_litres'))['total'] or 0) +
        (active_yearly_subs.aggregate(total=Sum('quantity_litres'))['total'] or 0)
    )
    
    # Weekly Chart Data
    chartData = {'subscriptions': [], 'products': []}
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        ms = MonthlySubscriber.objects.filter(plan__vendor_id=vendor_id, created_at__date=d)
        ys = YearlySubscriber.objects.filter(plan__vendor_id=vendor_id, created_at__date=d)
        s_rev = (ms.aggregate(t=Sum('plan_price'))['t'] or 0) + (ys.aggregate(t=Sum('plan_price'))['t'] or 0)
        
        ois = OrderItem.objects.filter(vendor_id=vendor_id, order__created_at__date=d)
        p_rev = ois.aggregate(t=Sum(F('price') * F('quantity')))['t'] or 0
        
        chartData['subscriptions'].append(float(s_rev))
        chartData['products'].append(float(p_rev))
    
    # Build product sales summary for today
    products_dict = {}
    today_order_items = OrderItem.objects.filter(vendor_id=vendor_id, order__created_at__date=today)
    for item in today_order_items.select_related('product'):
        pname = item.product.name_en if hasattr(item.product, 'name_en') else item.product.name
        qty = item.quantity
        rev = item.price * qty
        if pname not in products_dict:
            products_dict[pname] = {'name': pname, 'sold': 0, 'revenue': 0.0, 'unit': getattr(item.product, 'unit', 'unit')}
        products_dict[pname]['sold'] += qty
        products_dict[pname]['revenue'] += float(rev)
        
    product_list = []
    for v in products_dict.values():
        v['trend'] = 'up'
        v['revenue'] = f"{v['revenue']:,.2f}"
        product_list.append(v)
        
    # Recent Orders
    recent_orders_qs = Order.objects.filter(items__vendor_id=vendor_id).distinct().prefetch_related('items', 'items__product').order_by('-created_at')[:4]
    serializer_context = {'vendor_id': vendor_id, 'request': request}
    recent_orders_serialized = VendorOrderSerializer(recent_orders_qs, many=True, context=serializer_context).data

    payload = {
        'revenue': {
            'total': f"{total_revenue_today:,.2f}",
            'subscriptions': f"{sub_revenue_today:,.2f}",
            'products': f"{product_revenue_today:,.2f}",
            'growth': growth
        },
        'deliveries': {
            'subscriptionDeliveries': subs_delivery_count,
            'productOrders': orders_delivery_count,
            'total': total_deliveries
        },
        'progress': {
            'delivered': delivered_total,
            'pending': pending_total,
            'percentage': percentage
        },
        'subscriptions': {
            'active': active_count,
            'paused': paused_count,
            'newToday': new_today_count,
            'milkLiters': sub_liters
        },
        'products': product_list,
        'recentOrders': recent_orders_serialized,
        'recentSubscriptions': (
            MonthlySubscriberSerializer(active_monthly_subs.order_by('-created_at')[:5], many=True).data +
            YearlySubscriberSerializer(active_yearly_subs.order_by('-created_at')[:5], many=True).data
        ),
        'chartData': chartData
    }
    
    return Response(payload)


# Initialize Razorpay Client (Cleaning keys for extra safety)
RAZORPAY_KEY_ID = settings.RAZORPAY_KEY_ID.strip() if settings.RAZORPAY_KEY_ID else ""
RAZORPAY_KEY_SECRET = settings.RAZORPAY_KEY_SECRET.strip() if settings.RAZORPAY_KEY_SECRET else ""

# Try/except block because RAZORPAY_KEY_ID might be empty during generic check
try:
    razorpay_client = razorpay.Client(
        auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
    )
except:
    razorpay_client = None

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initiate_payment(request):
    """
    POST /api/orders/payments/initiate/
    Creates a Razorpay order and returns order_id for frontend checkout.
    """
    serializer = RazorpayOrderSerializer(data=request.data)
    if serializer.is_valid():
        amount = int(serializer.validated_data['amount'] * 100) # Paise
        main_order_id = serializer.validated_data.get('order_id')
        
        try:
            print(f">>> Attempting Razorpay Order: Amount={amount}, ProvidedID={main_order_id}")
            
            # Robustly find the MainOrder
            main_order = None
            if main_order_id:
                # Try finding as MainOrder first
                main_order = MainOrder.objects.filter(id=main_order_id).first()
                
                # If not found, try finding as SubOrder (Order) and get its main_order
                if not main_order:
                    sub_order = Order.objects.filter(id=main_order_id).first()
                    if sub_order:
                        main_order = sub_order.main_order
            
            if main_order and main_order.is_multi_vendor:
                return Response({"error": "Multi-vendor orders follow internal settlement flow and skip Razorpay."}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Check if keys are actually present
            if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET or not razorpay_client:
                return Response({"error": "Razorpay keys are missing in .env"}, status=status.HTTP_400_BAD_REQUEST)

            razorpay_order = razorpay_client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1"
            })
            
            print(f">>> SUCCESS: Razorpay Order Created: {razorpay_order['id']}")
            
            # Create payment linked to MainOrder if found, otherwise keep standard linked order
            payment_params = {
                'user': request.user,
                'amount': serializer.validated_data['amount'],
                'razorpay_order_id': razorpay_order['id'],
                'status': 'pending'
            }
            
            # Identify the vendor for this payment (for single-vendor checkout)
            # If it's single-vendor, it will have at least one sub-order
            payment_vendor_id = None
            if main_order:
                payment_params['main_order'] = main_order
                # Try to get vendor from first sub-order
                first_sub = main_order.vendor_orders.first()
                if first_sub:
                    payment_vendor_id = first_sub.vendor_id
            else:
                # Fallback for manual order_id passed from frontend
                payment_params['order_id'] = main_order_id
                sub_order = Order.objects.filter(id=main_order_id).first()
                if sub_order:
                    payment_vendor_id = sub_order.vendor_id

            if payment_vendor_id:
                payment_params['vendor_id'] = payment_vendor_id
            
            Payment.objects.create(**payment_params)
            
            return Response(razorpay_order, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            error_msg = str(e)
            print(f">>> RAZORPAY CRITICAL ERROR: {error_msg}")
            # Log traceback for exact network failure point
            import traceback
            traceback.print_exc()
            
            if "Remote end closed connection" in error_msg or "Connection aborted" in error_msg:
                return Response({
                    "error": "Razorpay Connection Failed. This is often an SSL/TLS issue on local development machines.",
                    "detail": error_msg
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"error": f"Payment initiation failed: {error_msg}"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_payment(request):
    """
    POST /api/orders/payments/verify/
    Verifies the Razorpay signature and updates payment status.
    """
    if not razorpay_client:
        return Response({"error": "Razorpay keys are missing in .env"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = PaymentVerificationSerializer(data=request.data)
    if serializer.is_valid():
        razorpay_order_id = serializer.validated_data['razorpay_order_id']
        razorpay_payment_id = serializer.validated_data['razorpay_payment_id']
        razorpay_signature = serializer.validated_data['razorpay_signature']
        
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'success'
            
            try:
                payment_details = razorpay_client.payment.fetch(razorpay_payment_id)
                payment.payment_method = payment_details.get('method')
            except:
                pass
            
            payment.save()
            
            # Update statuses for all associated orders
            if payment.main_order:
                payment.main_order.status = 'placed'
                payment.main_order.save()
                
                for sub_order in payment.main_order.vendor_orders.all():
                    sub_order.status = 'confirmed'
                    sub_order.save()
                    
                    VendorSettlement.objects.create(
                        payment=payment,
                        vendor_order=sub_order,
                        vendor_id=sub_order.vendor_id,
                        amount=sub_order.total_amount,
                        status='pending'
                    )
            
            elif payment.order:
                payment.order.status = 'confirmed'
                payment.order.save()
                
                # Also create settlement for standalone order
                VendorSettlement.objects.create(
                    payment=payment,
                    vendor_order=payment.order,
                    vendor_id=payment.order.vendor_id,
                    amount=payment.order.total_amount,
                    status='pending'
                )
            
            return Response({"status": "Payment Verified Successfully"}, status=status.HTTP_200_OK)
        except razorpay.errors.SignatureVerificationError:
            payment = Payment.objects.filter(razorpay_order_id=razorpay_order_id).first()
            if payment:
                payment.status = 'failed'
                payment.save()
            return Response({"error": "Invalid Payment Signature"}, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({"error": "Payment Record Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
