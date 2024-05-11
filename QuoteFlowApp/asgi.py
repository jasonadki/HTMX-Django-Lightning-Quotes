# asgi.py
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuoteFlowApp.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter
from QuoteFlowApp.routing import application as channels_applications

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # If you're using http and websocket
    "websocket": channels_applications,
})
