from django.db import connection
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'milk_delivery_backend.settings')
django.setup()

with open('users_sql.txt', 'r', encoding='utf-16') as f:
    sql = f.read()

# Strip potential BOM
sql = sql.lstrip('\ufeff')

# Remove BEGIN and COMMIT if present to execute manually
sql = sql.replace('BEGIN;', '').replace('COMMIT;', '')

with connection.cursor() as cursor:
    for statement in sql.split(';'):
        if statement.strip():
            print(f"Executing: {statement[:50]}...")
            cursor.execute(statement)

print('Successfully created missing tables')
