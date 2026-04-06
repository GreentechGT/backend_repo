import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def send_push_message(token, message, extra=None):
    # Push notifications are temporarily disabled
    pass

def notify_order_status_change(order):
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{order.user.user_id}",
                {
                    "type": "status_update",
                    "data": {
                        "type": "order_status",
                        "order_id": order.id,
                        "status": order.status,
                        "message": f"Your order {order.order_number} is now {order.status}.",
                    }
                }
            )
    except Exception as e:
        print(f"WS Notification Error (Order Status): {e}")

def notify_subscription_status_change(subscription):
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{subscription.user.user_id}",
                {
                    "type": "status_update",
                    "data": {
                        "type": "status_update",
                        "data": {
                            "type": "subscription_status",
                            "subscription_id": subscription.id,
                            "status": subscription.daily_delivery_status,
                            "message": f"Your delivery for {subscription.plan.name_en} is now {subscription.daily_delivery_status}.",
                        }
                    }
                }
            )
    except Exception as e:
        print(f"WS Notification Error (Subscription Status): {e}")

def notify_vendor_dashboard_refresh(vendor_id):
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{vendor_id}",
                {
                    "type": "status_update",
                    "data": {
                        "type": "vendor_dashboard_refresh",
                        "message": "New order or status update. Refreshing dashboard...",
                    }
                }
            )
    except Exception as e:
        print(f"WS Notification Error (Vendor Refresh): {e}")


