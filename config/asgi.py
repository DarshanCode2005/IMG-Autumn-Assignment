"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

# Set up Django BEFORE any other imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django first
import django
django.setup()

# Now we can safely import Django-dependent modules
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from config.authentication import TokenAuthMiddlewareStack

django_asgi_app = get_asgi_application()

from social.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
