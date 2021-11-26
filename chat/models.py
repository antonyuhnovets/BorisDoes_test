import jwt

from datetime import datetime, timedelta

from django.core import validators
from django.db import models
from BorisDoes_test import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db.models import (Model, TextField, DateTimeField, ForeignKey, CASCADE)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class UserManager(BaseUserManager):

    def _create_user(self, username, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email,and password.

        """
        if not email:
            raise ValueError('The given email must be set')

        if not username:
            raise ValueError('The given username must be set')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(username, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    """
    username = models.CharField(
        db_index=True,
        max_length=255,
        unique=True
    )
    email = models.EmailField(
        max_length=40,
        unique=True,
        validators=[validators.validate_email]
    )
    first_name = models.CharField(
        max_length=30,
        blank=True
    )
    last_name = models.CharField(
        max_length=30,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    @property
    def token(self):
        return self._generate_jwt_token()

    def get_name(self):
        return self.username

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=1)
        payload = {
            'id': self.pk,
            'exp': int(dt.strftime('%S'))
        }
        token = jwt.encode(payload, key=settings.SECRET_KEY, algorithm='HS256')

        return token


class MessageModel(Model):
    """
    This class represents a chat message. It has a owner (user), timestamp and
    the message body.

    """
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name='user',
        related_name='from_user',
        db_index=True,
    )
    chat_id = models.CharField(
        max_length=256,
        verbose_name='chat',
        db_index=True,
    )
    timestamp = DateTimeField(
        name='timestamp',
        default=datetime.now(),
        editable=True,
        db_index=True,
    )
    body = TextField('Message body')

    def __str__(self):
        return str(self.body)

    def notify_ws_clients(self):
        """
        Inform client there is a new message.
        """
        notification = {
            'type': 'recieve_group_message',
            'message': f'{self.pk}',
            'datetime': f'{self.timestamp}'
        }

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)("{}".format(self.author), notification)
        async_to_sync(channel_layer.group_send)("{}".format(self.chat_id), notification)

    def save(self, *args, **kwargs):

        self.notify_ws_clients()

    class Meta:
        app_label = 'chat'
        verbose_name = 'message'
        verbose_name_plural = 'messages'
        ordering = ('-timestamp',)

