from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user
    
    POST /api/register/
    Request Body:
    {
        "username": "your_username",
        "password": "your_password",
        "confirmed_password": "your_confirmed_password",
        "email": "your_email@example.com"
    }
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {'detail': 'User created successfully!'},
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login a user and set auth cookies
    
    POST /api/login/
    Request Body:
    {
        "username": "your_username",
        "password": "your_password"
    }
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        
        response = Response(
            {
                'detail': 'Login successfully!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            },
            status=status.HTTP_200_OK
        )
        
        response.set_cookie(
            'access_token',
            tokens['access'],
            max_age=15 * 60,
            httponly=True,
            secure=False,
            samesite='Lax'
        )
        response.set_cookie(
            'refresh_token',
            tokens['refresh'],
            max_age=7 * 24 * 60 * 60,
            httponly=True,
            secure=False,
            samesite='Lax'
        )
        
        return response
    
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout a user and delete all tokens
    
    POST /api/logout/
    """
    response = Response(
        {
            'detail': 'Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid.'
        },
        status=status.HTTP_200_OK
    )
    
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token(request):
    """
    Refresh the access token using the refresh token
    
    POST /api/token/refresh/
    """
    refresh = request.COOKIES.get('refresh_token')
    
    if not refresh:
        return Response(
            {'detail': 'Refresh token not found.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        refresh_token_obj = RefreshToken(refresh)
        access_token = str(refresh_token_obj.access_token)
        
        response = Response(
            {'detail': 'Token refreshed'},
            status=status.HTTP_200_OK
        )
        
        response.set_cookie(
            'access_token',
            access_token,
            max_age=15 * 60,
            httponly=True,
            secure=False,
            samesite='Lax'
        )
        
        return response
    except Exception as e:
        return Response(
            {'detail': 'Refresh token is invalid or expired.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
