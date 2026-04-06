from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscriptions'

    def ready(self):
        import os
        # Only start scheduler once when running with runserver
        if os.environ.get('RUN_MAIN', None) != 'true':
            return
            
        from subscriptions import updater
        updater.start()
