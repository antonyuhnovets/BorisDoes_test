from django.conf.urls import url, re_path

from chat import consumers

websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    url(r'^ws$', consumers.ChatConsumer),
]