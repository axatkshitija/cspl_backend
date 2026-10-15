import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cspl_project.settings')

# 1. Initialize Django ASGI application pehle karein
django_asgi_app = get_asgi_application()

# 2. Imports ko django_asgi_app ke BAAD karein
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import cspl_app.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            cspl_app.routing.websocket_urlpatterns
        )
    ),
})