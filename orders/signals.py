from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order
from .notifications import notify_order_status_change

@receiver(pre_save, sender=Order)
def store_previous_status(sender, instance, **kwargs):
    if instance.id:
        try:
            instance._previous_status = Order.objects.get(id=instance.id).status
        except Order.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    # If the order is newly created, it's 'confirmed' by default
    if created:
        notify_order_status_change(instance)
    else:
        # Check if status has changed
        previous_status = getattr(instance, '_previous_status', None)
        if previous_status and previous_status != instance.status:
            notify_order_status_change(instance)
