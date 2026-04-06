from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^/?ws/orders/(?P<user_id>[a-zA-Z0-9\-_]+)/$', consumers.OrderStatusConsumer.as_asgi()),
]

