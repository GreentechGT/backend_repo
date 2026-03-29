from django.core.management import call_command
from django.db import connection
from django.apps import apps
from io import StringIO

def run():
    print(">>> Starting Database Sequence Reset...")
    for app_config in apps.get_app_configs():
        # Only reset our custom apps to avoid system table issues
        if app_config.label in ['orders', 'product', 'users', 'subscriptions', 'support', 'promotion']:
            output = StringIO()
            try:
                call_command('sqlsequencereset', app_config.label, stdout=output)
                sql = output.getvalue()
                if sql:
                    with connection.cursor() as cursor:
                        cursor.execute(sql)
                    print(f">>> Reset sequences for app: {app_config.label}")
            except Exception as e:
                print(f">>> Skipping {app_config.label} due to: {str(e)}")
    print(">>> Database Sequence Reset Complete!")

if __name__ == "__main__":
    run()
