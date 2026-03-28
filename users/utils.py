import os
from django.core.mail import send_mail
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

def send_otp_via_email(email, otp):
    """Sends a verification OTP to the user's email address."""
    subject = "Verify your Milk Delivery Account"
    message = f"Your verification code is: {otp}. It expires in 10 minutes."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
