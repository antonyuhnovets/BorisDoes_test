import datetime

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User, MessageModel


class RegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя и создания нового. """

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    token = serializers.CharField(
        max_length=255,
        read_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(
        max_length=40,
        read_only=True
    )
    username = serializers.CharField(
        max_length=255,
        write_only=False
    )
    password = serializers.CharField(
        max_length=128,
        write_only=True
    )
    token = serializers.CharField(
        max_length=255,
        read_only=True
    )

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)

        # Вызвать исключение, если не предоставлена почта.
        if username is None:
            raise serializers.ValidationError(
                'An username is required to log in.'
            )

        # Вызвать исключение, если не предоставлен пароль.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'email': user.email,
            'username': user.username,
            'token': user.token,
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'password', 'date_joined'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }


class MessageSerializer(serializers.ModelSerializer):
    body = serializers.CharField(
        max_length=3000,
        read_only=True,
    )
    author = serializers.CharField(
        max_length=30,
        read_only=True,
    )
    date_time = serializers.DateTimeField(
        default=datetime.datetime.now(),
        read_only=False,
    )
    chat = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    def create(self, validated_data):

        msg = MessageModel(
            chat_id=validated_data['chat'],
            body=validated_data['body'],
            user=validated_data['user'],
            timestamp=validated_data['timestamp'],
        )
        msg.save()

        return msg

    class Meta:
        model = MessageModel
        fields = ('body', 'author', 'timestamp', 'chat_id')




