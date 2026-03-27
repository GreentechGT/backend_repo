from django.db import connection
from django.utils import timezone
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'milk_delivery_backend.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("INSERT INTO django_migrations (app, name, applied) VALUES ('users', '0001_initial', %s)", [timezone.now()])
    print('Successfully recorded users.0001_initial as applied')
