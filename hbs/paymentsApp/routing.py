
# routing.py
from django.urls import re_path
from .consumers import TransactionConsumer

websocket_urlpatterns = [
    re_path(r'ws/transactions/(?P<order_id>[0-9a-f-]+)/$', TransactionConsumer.as_asgi()),
]
