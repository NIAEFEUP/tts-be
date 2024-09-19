from django.urls import path
from .websocket import TestConsumer

websocket_urlpatterns = [
    path('ws/chat/<int:room_name>/', TestConsumer.as_asgi()),
]