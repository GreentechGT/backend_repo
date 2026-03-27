import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'milk_delivery_backend.settings')
django.setup()

from users.models import User

users = User.objects.all()
print(f"Total users: {users.count()}")
for user in users:
    print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Phone: {user.phone}, Full Name: {user.full_name}")

# Check for duplicate detection logic
def check_duplicate(emailOrPhone):
    user = User.objects.filter(models.Q(username=emailOrPhone) | models.Q(email=emailOrPhone) | models.Q(phone=emailOrPhone)).first()
    return user is not None

from django.db import models
import django.db.models as dr_models
