from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import permissions
from apps.core.base import BaseAPIView
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer

class UserRegistrationView(BaseAPIView):
    permission_classes= []
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            
            return self.success_response(
                message="User registered successfully", 
                data=response_data, 
                status_code=status.HTTP_201_CREATED
            )
        
        return self.error_response(
            message="Registration failed", 
            data=serializer.errors, 
            status_code=status.HTTP_400_BAD_REQUEST
        )


class UserLoginView(BaseAPIView):
    permission_classes= []
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return self.error_response(
                message="Login failed", 
                data={"error": "Username and password are required"}, 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            response_data = {
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return self.success_response(
                message="Login successful", 
                data=response_data
            )
        
        return self.error_response(
            message="Login failed", 
            data={"error": "Invalid credentials"}, 
            status_code=status.HTTP_401_UNAUTHORIZED
        )
        

class UserLogoutView(BaseAPIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return self.error_response(
                message="Logout failed",
                data={"error": "Refresh token is required"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # blacklist the refresh token
            return self.success_response(
                message="Logout successful",
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                message="Logout failed",
                data={"error": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )        


class UserProfileView(BaseAPIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required", 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        serializer = UserSerializer(request.user)
        return self.success_response(
            message="Profile retrieved successfully", 
            data=serializer.data
        )
    
    def put(self, request):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required", 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                message="Profile updated successfully", 
                data=serializer.data
            )
        
        return self.error_response(
            message="Profile update failed", 
            data=serializer.errors, 
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
