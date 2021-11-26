from datetime import datetime

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication
from django.db.models import Q
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .serializers import RegistrationSerializer, LoginSerializer
from .serializers import MessageSerializer, UserSerializer
from .models import MessageModel, User
from BorisDoes_test import settings


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to access this url
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.data

        serializer = RegistrationSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'username': serializer.data.get('username', None),
                'email': serializer.data.get('email', None),
                'token': serializer.data.get('token', None),
            },
            status=status.HTTP_201_CREATED
        )


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        response = {
            'success' : 'True',
            'status code' : status.HTTP_200_OK,
            'message': 'User logged in  successfully',
            'token' : serializer.data['token'],
            }

        return Response(
            {
                'success': 'True',
                'message': 'User logged in  successfully',
                'name': serializer.data.get('username', None),
                'email': serializer.data.get('email', None),
                'token': serializer.data.get('token', None),
            },
            status=status.HTTP_200_OK
        )


# class CsrfExemptSessionAuthentication(SessionAuthentication):
#     """
#     SessionAuthentication scheme used by DRF. DRF's SessionAuthentication uses
#     Django's session framework for authentication which requires CSRF to be
#     checked. In this case we are going to disable CSRF tokens for the API.
#     """
#
#     def enforce_csrf(self, request):
#         return


class MessagePagination(PageNumberPagination):
    """
    Limit message prefetch to one page.
    """
    page_size = settings.MESSAGES_TO_LOAD


class MessageModelViewSet(ModelViewSet):

    queryset = MessageModel.objects.all()
    serializer_class = MessageSerializer
    allowed_methods = ('GET', 'POST', 'HEAD', 'OPTIONS')
    permission_classes = (IsAuthenticated,)
    pagination_class = MessagePagination

    def send_msg(self, request, channel, *args, **kwargs):

        async_to_sync(channel.group_send)(
            f'{request.get("author", None)}\n{request.get("body")}\n{request.get("timestamp")}'
        )
        # async_to_sync(channel.group_send)("{}".format(self.chat_id), notification)

    def write_msg(self, request, *args, **kwargs):

        channel_layer = get_channel_layer()
        # group = async_to_sync(channel_layer.group_add('sda'))
        msg = request.data
        serializer = self.serializer_class(data=msg)
        serializer.is_valid(raise_exception=True)

        if not serializer.data.anonymus:
            author = None
        else:
            author = serializer.data.user

        response = {
            'body': serializer.data.get('body', '[Empty massage]'),
            'author': author,
            'timestamp': serializer.data.get('datetime', datetime.now()),
            'chat_id': channel_layer,
        }

        self.send_msg(response, channel_layer)
        serializer.create(response)
        return Response(response, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(
            Q(recipient=request.user) | Q(user=request.user)
        )
        target = self.request.query_params.get(
            'target',
            None,
        )
        if target is not None:
            self.queryset = self.queryset.filter(
                Q(recipient=request.user, user__username=target) |
                Q(recipient__username=target, user=request.user),
            )

        return super(MessageModelViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        msg = get_object_or_404(
            self.queryset.filter(
                Q(recipient=request.user) |
                Q(user=request.user),
                Q(pk=kwargs['pk']),
            )
        )
        serializer = self.get_serializer(msg)

        return Response(serializer.data)


class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    allowed_methods = ('GET', 'HEAD', 'OPTIONS')
    pagination_class = None  # Get all user

    def list(self, request, *args, **kwargs):
        # Get all users except yourself
        self.queryset = self.queryset.exclude(id=request.user.id)
        return super(UserModelViewSet, self).list(request, *args, **kwargs)



