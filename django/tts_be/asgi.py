"""
ASGI config for tts_be project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from university.routing import websocket_urlpatterns
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

import socketio
from university.socket.views import sio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tts_be.settings')

django_app = get_asgi_application()

application = socketio.ASGIApp(sio, django_app)
