"""
Serializers for accounts app.
"""
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework import exceptions, serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'username')
        read_only_fields = ('id', 'email')


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate_email(self, value):
        """Store emails in a canonical form and reject duplicates regardless of case."""
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return email

    def validate_username(self, value):
        """Reject blank and look-alike usernames."""
        username = value.strip()
        if not username:
            raise serializers.ValidationError('Username cannot be blank.')
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return username

    def validate(self, data):
        """
        Validate that passwords match and satisfy Django's password validators.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        candidate = User(
            email=data.get('email', ''),
            username=data.get('username', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
        )
        try:
            validate_password(data['password'], user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)}) from exc
        return data

    def create(self, validated_data):
        """
        Create a new user with a hashed password and no staff privileges.
        """
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        for privileged in ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions'):
            validated_data.pop(privileged, None)
        try:
            with transaction.atomic():
                user = User.objects.create_user(password=password, **validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError({
                'email': 'A user with this email already exists.',
            }) from exc
        if user.is_staff or user.is_superuser:
            user.is_staff = False
            user.is_superuser = False
            user.save(update_fields=['is_staff', 'is_superuser'])
        return user


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    """
    Custom user details serializer for dj-rest-auth.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')
        read_only_fields = ('id', 'email')


class EmailLoginSerializer(LoginSerializer):
    """Authenticate by email without revealing which part of the credentials failed."""

    def get_auth_user_using_orm(self, username, email, password):
        looked_up = False
        if email:
            try:
                username = User.objects.get(email__iexact=email).get_username()
                looked_up = True
            except User.DoesNotExist:
                username = None

        user = None
        if username and password:
            user = self.authenticate(username=username, password=password)
        if user is None and password and not looked_up:
            # Spend the same password-hash cost when the account does not exist.
            User().set_password(password)
        return user

    @staticmethod
    def validate_auth_user_status(user):
        if not user.is_active:
            raise exceptions.ValidationError('Unable to log in with provided credentials.')
