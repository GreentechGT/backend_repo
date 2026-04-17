from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import random
from datetime import timedelta
from django.db.models import Q
from .serializers import RegisterSerializer, UserSerializer, MyTokenObtainPairSerializer, AddressSerializer, VendorSerializer, VendorProfileSerializer
from .utils import send_otp_via_email
from .models import User, Address, Vendor, Customer

import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def become_partner(request):
    serializer = VendorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@authentication_classes([])
def register_customer(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    user = request.user
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = UserSerializer(user, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def vendor_profile(request):
    vendor_id = request.user.user_id
    vendor = Vendor.objects.filter(vendor_id=vendor_id).first()
    if not vendor:
        from rest_framework.exceptions import NotFound
        raise NotFound(detail="Vendor profile not found for this user.")
        
    if request.method == 'GET':
        serializer = VendorProfileSerializer(vendor)
        return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = VendorProfileSerializer(vendor, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp(request):
    identifier = request.data.get('identifier')
    otp_code = request.data.get('otp_code')

    if not identifier or not otp_code:
        return Response({"detail": "Identifier and OTP code are required."}, status=status.HTTP_400_BAD_REQUEST)

    customer = Customer.objects.filter(Q(email=identifier) | Q(phone=identifier)).first()

    if not customer:
        return Response({"detail": "Registration not found."}, status=status.HTTP_404_NOT_FOUND)

    if customer.is_verified:
        return Response({"detail": "Customer is already verified."}, status=status.HTTP_400_BAD_REQUEST)

    if customer.otp_code == otp_code and customer.otp_expiry > timezone.now():
        try:
            # Mark customer as verified
            customer.is_verified = True
            customer.save()
            
            # Determine if registration was via phone or email based on identifier used
            has_at_symbol = "@" in identifier
            is_phone_verification = not has_at_symbol
            is_email_verification = has_at_symbol

            # Now create the actual User account for login
            q_objects = Q()
            if customer.email:
                q_objects |= Q(email=customer.email)
            if customer.phone:
                q_objects |= Q(phone=customer.phone)
                
            if not User.objects.filter(q_objects).exists():
                user = User.objects.create_user(
                    email=customer.email if customer.email else None,
                    password=customer.password, # create_user will hash this
                    phone=customer.phone if customer.phone else None,
                    full_name=customer.name,
                    role='customer',
                    user_id=customer.cust_id,
                    # Set verified status based on what was actually verified via OTP
                    phone_verified=is_phone_verification,
                    email_verified=is_email_verification,
                )
                
                # Generate tokens for immediate login
                refresh = RefreshToken.for_user(user)
                return Response({
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserSerializer(user).data,
                    "detail": "Account verified and created successfully."
                }, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "User already exists."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Error creating user: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resend_otp(request):
    identifier = request.data.get('identifier')

    if not identifier:
        return Response({"detail": "Identifier is required."}, status=status.HTTP_400_BAD_REQUEST)

    customer = Customer.objects.filter(Q(email=identifier) | Q(phone=identifier)).first()

    if not customer:
        return Response({"detail": "Registration not found."}, status=status.HTTP_404_NOT_FOUND)

    if customer.is_verified:
        return Response({"detail": "Customer is already verified."}, status=status.HTTP_400_BAD_REQUEST)

    # Generate new OTP (Hardcoded to 1234)
    otp = "1234"
    customer.otp_code = otp
    customer.otp_expiry = timezone.now() + timedelta(minutes=10)
    customer.save()

    return Response({"detail": "OTP resent successfully."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_email_otp(request):
    """
    Allows an already-authenticated user to verify a new email address.
    The frontend sends the new email + OTP; on success the user's email is
    updated, fake @noemail.local address is replaced, and email_verified=True.
    """
    new_email = request.data.get('identifier')  # the new email to verify
    otp_code = request.data.get('otp_code')

    if not new_email or not otp_code:
        return Response({"detail": "Email and OTP code are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate the OTP — for now it's hardcoded as "1234"
    if otp_code != "1234":
        return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

    # Check the email isn't already taken by another user
    existing = User.objects.filter(email=new_email).exclude(pk=request.user.pk).first()
    if existing:
        return Response({"detail": "This email is already in use by another account."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = request.user
        user.email = new_email
        user.email_verified = True
        user.save(update_fields=['email', 'email_verified'])
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": f"Error updating email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_phone_otp(request):
    """
    Allows an already-authenticated user to verify a new or existing phone number.
    The frontend sends the phone number + OTP; on success the user's phone is
    updated and phone_verified=True.
    """
    new_phone = request.data.get('identifier')
    otp_code = request.data.get('otp_code')

    if not new_phone or not otp_code:
        return Response({"detail": "Phone and OTP code are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate the OTP — for now it's hardcoded as "1234"
    if otp_code != "1234":
        return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

    # Check the phone isn't already taken by another user
    existing = User.objects.filter(phone=new_phone).exclude(pk=request.user.pk).first()
    if existing:
        return Response({"detail": "This phone number is already in use by another account."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = request.user
        user.phone = new_phone
        user.phone_verified = True
        user.save(update_fields=['phone', 'phone_verified'])
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": f"Error updating phone: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

