# QuoteFlowApp/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from quotes.consumers import QuoteConsumer

# Define your websocket routes
websocket_urlpatterns = [
    path('ws/quotes/', QuoteConsumer.as_asgi()),
]

# Define the application
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
