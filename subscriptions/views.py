from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Subscription, MonthlySubscriber, YearlySubscriber
from .serializers import SubscriptionSerializer, MonthlySubscriberSerializer, YearlySubscriberSerializer, VendorSubscriptionWriteSerializer
from django.utils import timezone
from datetime import timedelta
from product.models import Product

@api_view(['GET'])
def subscription_list(request):
    queryset = Subscription.objects.all()
    serializer = SubscriptionSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def subscribe(request):
    subscription_id = request.data.get('subscription_id')
    quantity = request.data.get('quantity', 1)
    slot = request.data.get('slot', 'morning')
    address_id = request.data.get('address_id')
    
    try:
        plan_obj = Subscription.objects.get(id=subscription_id)
    except Subscription.DoesNotExist:
        return Response({'error': 'Subscription plan not found'}, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if user.is_anonymous:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.first() # Default for demo/anonymous

    # Calculate end date
    now = timezone.now().date()
    if plan_obj.frequency == 'monthly':
        end_date = now + timedelta(days=30)
        subscriber_class = MonthlySubscriber
    else: # yearly or defaults
        end_date = now + timedelta(days=365)
        subscriber_class = YearlySubscriber

    subscriber = subscriber_class.objects.create(
        user=user,
        plan=plan_obj.product,
        plan_name_en=plan_obj.plan_name_en,
        plan_name_hi=plan_obj.plan_name_hi,
        desc_en=plan_obj.desc_en,
        desc_hi=plan_obj.desc_hi,
        frequency_en=plan_obj.frequency_en,
        frequency_hi=plan_obj.frequency_hi,
        slot_en=plan_obj.slot_en,
        slot_hi=plan_obj.slot_hi,
        status=plan_obj.status,
        address_id=address_id,
        slot=slot,
        frequency=plan_obj.frequency,
        quantity_litres=quantity,
        plan_price=plan_obj.total_amount,
        subscription_end_date=end_date
    )

    return Response({
        'message': 'Subscription activated successfully',
        'subscriber_id': subscriber.id,
        'frequency': plan_obj.frequency,
        'end_date': end_date
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def user_subscription_list(request):
    user = request.user
    if user.is_anonymous:
        # For demo/test purposes if not logged in
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.first()

    monthly = MonthlySubscriber.objects.filter(user=user)
    yearly = YearlySubscriber.objects.filter(user=user)
    
    monthly_data = MonthlySubscriberSerializer(monthly, many=True).data
    yearly_data = YearlySubscriberSerializer(yearly, many=True).data
    
    # Add a flag to distinguish between monthly and yearly in the frontend
    for item in monthly_data:
        item['subscription_type'] = 'monthly'
    for item in yearly_data:
        item['subscription_type'] = 'yearly'
        
    return Response({
        'monthly': monthly_data,
        'yearly': yearly_data,
        'all': monthly_data + yearly_data
    })

@api_view(['PATCH'])
def subscription_update(request, type, pk):
    user = request.user
    if user.is_anonymous:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.first()

    if type == 'monthly':
        model = MonthlySubscriber
        serializer_class = MonthlySubscriberSerializer
    elif type == 'yearly':
        model = YearlySubscriber
        serializer_class = YearlySubscriberSerializer
    else:
        return Response({'error': 'Invalid subscription type'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        subscription = model.objects.get(pk=pk, user=user)
    except model.DoesNotExist:
        return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = serializer_class(subscription, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def vendor_subscription_list(request):
    vendor_id = request.user.user_id
    if not vendor_id:
        return Response({'error': 'User is not a vendor'}, status=status.HTTP_403_FORBIDDEN)

    # Filter Monthly and Yearly subscribers by product's vendor
    monthly = MonthlySubscriber.objects.filter(plan__shop_detail__vendor__vendor_id=vendor_id).select_related('plan', 'user')
    yearly = YearlySubscriber.objects.filter(plan__shop_detail__vendor__vendor_id=vendor_id).select_related('plan', 'user')

    monthly_data = MonthlySubscriberSerializer(monthly, many=True).data
    yearly_data = YearlySubscriberSerializer(yearly, many=True).data

    # Add subscription_type flag
    for item in monthly_data: item['subscription_type'] = 'monthly'
    for item in yearly_data: item['subscription_type'] = 'yearly'

    all_subs = monthly_data + yearly_data

    # Grouping
    active = [s for s in all_subs if not s.get('is_paused')]
    paused = [s for s in all_subs if s.get('is_paused')]

    return Response({
        'active': active,
        'paused': paused,
        'count': len(all_subs)
    })

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def vendor_subscription_update(request, type, pk):
    vendor_id = request.user.user_id
    if not vendor_id:
        return Response({'error': 'User is not a vendor'}, status=status.HTTP_403_FORBIDDEN)

    if type == 'monthly':
        model = MonthlySubscriber
        serializer_class = MonthlySubscriberSerializer
    elif type == 'yearly':
        model = YearlySubscriber
        serializer_class = YearlySubscriberSerializer
    else:
        return Response({'error': 'Invalid subscription type'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        subscription = model.objects.get(pk=pk, plan__shop_detail__vendor__vendor_id=vendor_id)
    except model.DoesNotExist:
        return Response({'error': 'Subscription not found or you do not have permission'}, status=status.HTTP_404_NOT_FOUND)

    serializer = serializer_class(subscription, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def vendor_subscription_plans(request):
    vendor_id = request.user.user_id
    if not vendor_id:
        if request.method == 'GET':
            return Response([])
        return Response({'error': 'Not an authenticated vendor'}, status=status.HTTP_403_FORBIDDEN)
        
    if request.method == 'GET':
        queryset = Subscription.objects.filter(product__shop_detail__vendor__vendor_id=vendor_id)
        serializer = SubscriptionSerializer(queryset, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = VendorSubscriptionWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def vendor_subscription_plan_detail(request, pk):
    vendor_id = request.user.user_id
    if not vendor_id:
        return Response({'error': 'Not an authenticated vendor'}, status=status.HTTP_403_FORBIDDEN)

    try:
        plan = Subscription.objects.get(pk=pk, product__shop_detail__vendor__vendor_id=vendor_id)
    except Subscription.DoesNotExist:
        from rest_framework.exceptions import NotFound
        raise NotFound(detail="Subscription plan not found or you do not have permission.")

    if request.method == 'GET':
        serializer = SubscriptionSerializer(plan)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        serializer = VendorSubscriptionWriteSerializer(plan, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
