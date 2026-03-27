import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'milk_delivery_backend.settings')
django.setup()

from users.models import User

def create_verified_user(username, password, email, phone, role='customer'):
    try:
        user = User.objects.filter(username=username).first()
        if user:
            user.set_password(password)
            user.email = email
            user.phone = phone
            user.role = role
            user.is_verified = True
            user.save()
            print(f"User {username} updated and verified.")
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                phone=phone,
                role=role,
                is_verified=True
            )
            print(f"User {username} created and verified.")
        return user
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Credentials that pass frontend validation (10-digit phone)
    create_verified_user(
        username="9999999999",
        password="password123",
        email="test_customer@example.com",
        phone="9999999999",
        role="customer"
    )
