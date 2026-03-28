from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
import random
from datetime import timedelta
from django.db.models import Q
from .serializers import RegisterSerializer, UserSerializer, MyTokenObtainPairSerializer, AddressSerializer, VendorSerializer, VendorProfileSerializer
from .utils import send_otp_via_email
from .models import User, Address, Vendor, Customer

import logging

logger = logging.getLogger(__name__)

class BecomePartnerView(generics.CreateAPIView):
    serializer_class = VendorSerializer
    permission_classes = [permissions.AllowAny]

class RegisterView(generics.CreateAPIView):
    queryset = Customer.objects.all() # Now registers customers
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = RegisterSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class VendorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # The vendor's vendor_id matches the logged-in user's user_id
        vendor_id = self.request.user.user_id
        vendor = Vendor.objects.filter(vendor_id=vendor_id).first()
        if not vendor:
            from rest_framework.exceptions import NotFound
            raise NotFound(detail="Vendor profile not found for this user.")
        return vendor

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
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
                
                # Now create the actual User account for login
                q_objects = Q()
                if customer.email:
                    q_objects |= Q(email=customer.email)
                if customer.phone:
                    q_objects |= Q(phone=customer.phone)
                    
                if not User.objects.filter(q_objects).exists():
                    User.objects.create_user(
                        email=customer.email if customer.email else None,
                        password=customer.password, # create_user will hash this
                        phone=customer.phone if customer.phone else None,
                        full_name=customer.name,
                        role='customer',
                        user_id=customer.cust_id
                    )
                    return Response({"detail": "Account verified and created successfully. You can now login."}, status=status.HTTP_200_OK)
                else:
                    return Response({"detail": "User already exists."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"detail": f"Error creating user: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
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
