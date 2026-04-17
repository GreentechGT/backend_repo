from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    register_customer, MyTokenObtainPairView, user_profile, AddressViewSet, 
    verify_otp, resend_otp, become_partner, vendor_profile, verify_email_otp, verify_phone_otp
)

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_customer, name='auth_register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('become-partner/', become_partner, name='become_partner'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('resend-otp/', resend_otp, name='resend_otp'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', user_profile, name='user_profile'),
    path('verify-email-otp/', verify_email_otp, name='verify_email_otp'),
    path('verify-phone-otp/', verify_phone_otp, name='verify_phone_otp'),
    path('vendor/profile/', vendor_profile, name='vendor_profile'),
]
