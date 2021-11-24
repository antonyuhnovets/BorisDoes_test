from django.conf.urls import url
from .views import RegistrationAPIView, LoginAPIView

app_name = 'chat'
urlpatterns = [
    url(r'^registration/$', RegistrationAPIView.as_view()),
    url(r'^login/$', LoginAPIView.as_view()),
]