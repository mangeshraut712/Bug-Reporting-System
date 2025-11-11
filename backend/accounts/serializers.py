"""
Serializers for accounts app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'username')
        read_only_fields = ('id',)


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate(self, data):
        """
        Validate that passwords match.
        """
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        """
        Create a new user with hashed password.
        """
        user = User.objects.create_user(**validated_data)
        return user


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    """
    Custom user details serializer for dj-rest-auth.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')
        read_only_fields = ('id',)
