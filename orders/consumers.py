import json
from channels.generic.websocket import AsyncWebsocketConsumer


class OrderStatusConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer that allows a customer to receive 
    real-time order/subscription status updates.

    URL pattern: ws/orders/<user_id>/
    Group name:  user_<user_id>
    """

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.user_id}"

        # Join user-specific group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print(f"[WebSocket] Client connected: {self.group_name}")

    async def disconnect(self, close_code):
        # Leave user-specific group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print(f"[WebSocket] Client disconnected: {self.group_name} (code={close_code})")

    async def receive(self, text_data):
        # Client can send a ping or any message; we just echo/ack
        try:
            data = json.loads(text_data)
            print(f"[WebSocket] Received from {self.group_name}: {data}")
        except json.JSONDecodeError:
            pass

    # ── Handler for group_send messages ────────────────────────────────
    async def status_update(self, event):
        """
        Called when `notify_order_status_change` or 
        `notify_subscription_status_change` does a group_send
        with type='status_update'.
        """
        await self.send(text_data=json.dumps(event["data"]))
