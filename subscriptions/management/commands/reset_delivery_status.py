from django.core.management.base import BaseCommand
from subscriptions.models import MonthlySubscriber, YearlySubscriber

class Command(BaseCommand):
    help = 'Resets daily_delivery_status to confirmed for all subscribers'

    def handle(self, *args, **options):
        # Update all active monthly subscribers
        updated_monthly = MonthlySubscriber.objects.filter(status='active').update(
            daily_delivery_status='confirmed',
            daily_delivery_status_en='Confirmed',
            daily_delivery_status_hi='पुष्टी केली'
        )
        
        # Update all active yearly subscribers
        updated_yearly = YearlySubscriber.objects.filter(status='active').update(
            daily_delivery_status='confirmed',
            daily_delivery_status_en='Confirmed',
            daily_delivery_status_hi='पुष्टी केली'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully reset {updated_monthly} monthly and {updated_yearly} yearly subscribers.')
        )
