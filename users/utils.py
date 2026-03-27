import os
from twilio.rest import Client
from django.core.mail import send_mail
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

def send_otp_via_twilio(phone, otp):
    # Ensure phone number is in E.164 format (e.g., +919209494261)
    if not phone.startswith('+'):
        if len(phone) == 10:
            phone = f"+91{phone}"
        else:
            phone = f"+{phone}"

    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    
    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"Your Milk Delivery verification code is: {otp}. It expires in 10 minutes.",
            from_=twilio_phone,
            to=phone
        )
        return message.sid
    except Exception as e:
        print(f"TWILIO ERROR: {str(e)}")
        if "is not a verified phone number" in str(e):
            print("TRIAL ACCOUNT RESTRICTION: You can only send SMS to verified numbers in your Twilio Console.")
        raise e

def send_otp_via_email(email, otp):
    subject = "Verify your Milk Delivery Account"
    message = f"Your verification code is: {otp}. It expires in 10 minutes."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
