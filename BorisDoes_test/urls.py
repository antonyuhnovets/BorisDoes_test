from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
import chat.views as views

import chat.urls

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include(chat.urls)),

    # path('login/', views.LoginAPIView.as_view(), name='login'),
    path('login/', auth_views.LoginView.as_view(), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/', views.RegistrationAPIView.as_view(), name='register'),
]