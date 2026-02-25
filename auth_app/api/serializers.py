from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from ..models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """
    User Serializer for User data representation
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for User Registration
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirmed_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirmed_password')
        extra_kwargs = {
            'username': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError(
                {'confirmed_password': 'Passwörter stimmen nicht überein.'}
            )
        
        # Trim whitespace
        username = data['username'].strip()
        email = data['email'].strip()
        
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'username': 'Benutzername existiert bereits.'}
            )
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'E-Mail existiert bereits.'}
            )
        
        data['username'] = username
        data['email'] = email
        
        return data

    def create(self, validated_data):
        validated_data.pop('confirmed_password')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        UserProfile.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for User Login
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, data):
        from django.contrib.auth import authenticate
        
        # Trim whitespace from username and password
        username = data['username'].strip()
        password = data['password'].strip()
        
        user = authenticate(
            username=username,
            password=password
        )
        
        if not user:
            raise serializers.ValidationError(
                'Ungültige Anmeldedaten. Benutzer oder Passwort nicht korrekt.'
            )
        
        data['user'] = user
        
        return data
