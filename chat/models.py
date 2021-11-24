import jwt

from datetime import datetime, timedelta

from django.core import validators
from django.db import models
# from django.conf import settings
from BorisDoes_test import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)


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

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    """
    email = models.EmailField(max_length=40, unique=True, validators=[validators.validate_email])
    username = models.CharField(db_index=True, max_length=255, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def token(self):
        """
        Позволяет получить токен пользователя путем вызова user.token, вместо
        user._generate_jwt_token().
        """
        return self._generate_jwt_token()

    def get_name(self):
        """
        Этот метод требуется Django для таких вещей, как обработка электронной
        почты.
        """
        return self.username

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=1)
        payload = {
            'id': self.pk,
            'exp': int(dt.strftime('%S'))
        }

        token = jwt.encode(payload, key=settings.SECRET_KEY, algorithm='HS256')

        return token
        #     jwt.decode(
        #     jwt=token,
        #     key=settings.SECRET_KEY,
        #     algorithms=['HS256'],
        #     options={'verify_signature': False},
        # )


class Message(models.Model):

    title = models.CharField(max_length=60)
    body = models.TextField('Message body')
    author = models.ForeignKey('User', on_delete=models.DO_NOTHING)
    date_time = models.DateTimeField('Date and time', auto_now=True, editable=False, db_index=True)
