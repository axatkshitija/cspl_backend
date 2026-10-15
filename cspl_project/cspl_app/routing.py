from django.urls import re_path
from cspl_app import consumers

websocket_urlpatterns = [
    re_path(r'^ws/live-match/(?P<match_id>\w+)/?$', consumers.LiveMatchConsumer.as_asgi()),
]