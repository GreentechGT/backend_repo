import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from .models import MonthlySubscriber, YearlySubscriber

logger = logging.getLogger(__name__)

def reset_morning_subscriptions():
    """Reset daily delivery status for morning and both slots."""
    logger.info("Running scheduled task: reset_morning_subscriptions")
    updated_monthly = MonthlySubscriber.objects.filter(
        status='active', slot__in=['morning', 'both']
    ).update(
        daily_delivery_status='confirmed',
        daily_delivery_status_en='Confirmed',
        daily_delivery_status_hi='पुष्टी केली'
    )
    
    updated_yearly = YearlySubscriber.objects.filter(
        status='active', slot__in=['morning', 'both']
    ).update(
        daily_delivery_status='confirmed',
        daily_delivery_status_en='Confirmed',
        daily_delivery_status_hi='पुष्टी केली'
    )
    logger.info(f"Reset morning status for {updated_monthly} monthly and {updated_yearly} yearly subs.")

def reset_evening_subscriptions():
    """Reset daily delivery status for evening and both slots."""
    logger.info("Running scheduled task: reset_evening_subscriptions")
    updated_monthly = MonthlySubscriber.objects.filter(
        status='active', slot__in=['evening', 'both']
    ).update(
        daily_delivery_status='confirmed',
        daily_delivery_status_en='Confirmed',
        daily_delivery_status_hi='पुष्टी केली'
    )
    
    updated_yearly = YearlySubscriber.objects.filter(
        status='active', slot__in=['evening', 'both']
    ).update(
        daily_delivery_status='confirmed',
        daily_delivery_status_en='Confirmed',
        daily_delivery_status_hi='पुष्टी केली'
    )
    logger.info(f"Reset evening status for {updated_monthly} monthly and {updated_yearly} yearly subs.")

def start():
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # Run at 12:00 AM (Midnight)
    scheduler.add_job(
        reset_morning_subscriptions,
        'cron',
        hour=0,
        minute=0,
        id='reset_morning_subscriptions_job',
        max_instances=1,
        replace_existing=True,
    )
    
    # Run at 12:00 PM (Noon)
    scheduler.add_job(
        reset_evening_subscriptions,
        'cron',
        hour=12,
        minute=0,
        id='reset_evening_subscriptions_job',
        max_instances=1,
        replace_existing=True,
    )

    register_events(scheduler)
    scheduler.start()
    logger.info("APScheduler started successfully.")
