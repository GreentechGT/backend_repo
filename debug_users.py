import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'milk_delivery_backend.settings')
django.setup()

from users.models import User

users = User.objects.all()
print(f"Total users: {users.count()}")
for user in users:
    print(f"User: {user.username}, email: {user.email}, user_id: {user.user_id}")

# If duplicates exist, fix them
seen_ids = set()
for user in users:
    if user.user_id in seen_ids or user.user_id is None:
        new_id = uuid.uuid4()
        print(f"Fixing user {user.username}: {user.user_id} -> {new_id}")
        user.user_id = new_id
        user.save()
    seen_ids.add(user.user_id)
