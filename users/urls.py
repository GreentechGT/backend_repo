from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, MyTokenObtainPairView, UserProfileView, AddressViewSet, VerifyOTPView, ResendOTPView, BecomePartnerView, VendorProfileView, VerifyEmailOTPView, VerifyPhoneOTPView

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('become-partner/', BecomePartnerView.as_view(), name='become_partner'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('verify-email-otp/', VerifyEmailOTPView.as_view(), name='verify_email_otp'),
    path('verify-phone-otp/', VerifyPhoneOTPView.as_view(), name='verify_phone_otp'),
    path('vendor/profile/', VendorProfileView.as_view(), name='vendor_profile'),
]
