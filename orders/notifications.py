from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
import requests


def send_push_message(token, message, extra=None):
    try:
        response = PushClient().publish(
            PushMessage(to=token,
                        body=message,
                        data=extra))
    except PushServerError as exc:
        # Encountered some cases where Expo server returned a 5xx error
        print(f"PushServerError: {exc.errors}, {exc.response_data}, {exc.message}")
        raise
    except (PushTicketError, DeviceNotRegisteredError) as exc:
        # Device is no longer registered or token is invalid
        print(f"PushTicketError: {exc.push_message}, {exc.errors}, {exc.response_data}")
        # Here you might want to remove the token from the user profile
        pass
    except requests.exceptions.ConnectionError:
        print("ConnectionError: Failed to connect to Expo push server")
        pass
    except Exception as exc:
        print(f"Error sending push message: {exc}")
        pass

def notify_order_status_change(order):
    if not order.user.push_token:
        return

    status = order.status.lower()
    message = ""
    
    if status == 'confirmed':
        message = f"Your order {order.order_number} has been confirmed!"
    elif status == 'on_the_way':
        message = "Our delivery partner is on the way with your order!"
    elif status == 'delivered':
        message = "Your order has been delivered. Enjoy your fresh products!"
    elif status == 'cancelled':
        message = f"Your order {order.order_number} has been cancelled."

    if message:
        send_push_message(
            order.user.push_token, 
            message, 
            extra={'orderId': order.id, 'status': status}
        )
