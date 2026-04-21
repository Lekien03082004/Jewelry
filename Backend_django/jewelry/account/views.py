from django.shortcuts import render
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.permissions import AllowAny

from .models import CustomerUser
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from .services.auth_service import Authentication

import logging
import ipaddress
# Create your views here.

logger = logging.getLogger(__name__)


class Register(CreateAPIView):
    serializer_class = RegisterSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        return Response({
            "message": "Register successfully",
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            },
            },
            status=status.HTTP_201_CREATED
        )
    

class AuthThrottle(UserRateThrottle):
    scope = 'logout'

# class LoginView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         print(username, password)
#         if not username or not password:
#             return Response({'error': 'Username and password are required.'}, status=400)
        
#         try:
#             user = authenticate(request, username=username, password=password)
#             print(type(user))
#             if user is not None:
#                 refresh = RefreshToken.for_user(user)
#                 response = Response(
#                     {
#                     'user': {
#                         'id': user.id,
#                         'username': user.username,
#                         'email': user.email,
#                         'first_name': user.first_name,
#                         'last_name': user.last_name,
#                         'phone_number': user.phone_number,
#                         'address': user.address,
#                         'role': user.role,
#                     },
#                     'message': 'Login successful.',
#                 },
#                 status=status.HTTP_200_OK,
#                 )
#                 response.set_cookie(key='access_token', value=str(refresh.access_token), httponly=True, secure=True, path='/', samesite='Lax')
#                 response.set_cookie(key='refresh_token', value=str(refresh), httponly=True, secure=True, )
#                 return response
#             else:
#                 return Response({'error': 'Invalid credentials.'}, status=401)
#         except Exception as e:
#             logger.error(f"System error during login for {user.username}: {e}", exc_info=True)
#             return Response({'error': 'An unexpected error occurred. Please contact support.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AuthThrottle]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = Authentication()
        
    def post(self, request):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        
        result = self.auth_service.authenticate_user(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
            request=request
        )
        
        if not result.success:
            return Response(
                {
                    "message": result.message, 
                    "error": result.error
                },
                status=status.HTTP_404_NOT_FOUND
            )
            
        response = Response({
            "success": result.success,
            "message": result.message,
            "user": {
                "first_name": result.user.first_name,
                "last_name": result.user.last_name,
                "email": result.user.email
            }
        })
        
        response.set_cookie(
            key="access_token",
            value=result.tokens['access'],
            httponly=True,
            secure=False, #khi nào deploy thì mới bật
            path='/',
            samesite="Lax"
        )
        response.set_cookie(
            key="refresh_token",
            value=result.tokens['refresh'],
            httponly=True,
            secure=False, #khi nào deploy thì mới bật
            path="/auth/token/refresh/",
            samesite="Strict"
        )
        return response
        
        
    
class Logout(APIView):
    
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthThrottle]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        user_id = request.user.id
        response = Response({
            
                "success": True,
                "message": "Logged out sucessfully."
            
        },
        status=status.HTTP_200_OK,
        )
        
        self._clear_auth_cookie(response)
        
        if not refresh_token:
            logger.info("Logout attempt without refresh token",
                        extra={
                            "user_id": user_id,
                            "ip": self._get_client_ip(request),
                            "event": "logout_no_token"
                        }
            )
            
            self._audit_logout(request, success=True, reason='no_refresh_token')
            
            return response
            
        try:
            token = RefreshToken(refresh_token)
            
            if token.get("token_type")!='refresh':
                logger.warning("Attempt to use access token as refresh token",
                    extra={
                        "user_id": user_id,
                        "ip": self._get_client_ip(request),
                        "event": "invalid_token_type"
                    })
            
                self._audit_logout(request, success=True, reason="invalid_token_type")
                return response
            
            # Verify token belongs to authenticated user
            if token.get("user_id") != user_id:
                logger.error(
                    "Token user_id mismatch",
                    extra={
                        "token_user_id": token.get("user_id"),
                        "request_user_id": user_id,
                        "ip": self._get_client_ip(request),
                        "event": "token_user_mismatch"
                    }
                )
                self._audit_logout(request, success=True, reason="token_mismatch")
                return response
            
             # Attempt to blacklist token
            try:
                token.blacklist()
                logger.info(
                    "Refresh token blacklisted successfully",
                    extra={
                        "user_id": user_id,
                        "token_jti": token.get("jti"),
                        "event": "token_blacklisted"
                    }
                )
                self._audit_logout(request, success=True, reason="token_blacklisted")
                
            except Exception as blacklist_error:
                if "already blacklisted" in str(blacklist_error).lower():
                    logger.info(
                        "Token already blacklisted",
                        extra={"user_id": user_id, "event": "token_already_blacklisted"}
                    )
                else:
                    raise  # Re-raise for outer exception handler
        except TokenError as e:
            # Token expired or already invalid - this is fine
            logger.info(
                "Expired or invalid token during logout",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "event": "token_expired_or_invalid"
                }
            )
            self._audit_logout(request, success=True, reason="token_expired")
            
        except InvalidToken as e:
            # Malformed token - but client is already logged out
            logger.warning(
                "Malformed refresh token received",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "ip": self._get_client_ip(request),
                    "event": "malformed_token"
                }
            )
            # Still return success - fail-safe principle
            self._audit_logout(request, success=True, reason="malformed_token")
            
        except Exception as e:
            # Unexpected server error - but client is logged out
            logger.error(
                "Unexpected error during token processing",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "event": "logout_error"
                },
                exc_info=True
            )
            # Update response message but keep success=True
            response.data.update({
                "message": "Logged out with server warnings.",
                "warning": "Some cleanup tasks failed, but you are logged out.",
                "code": "LOGOUT_PARTIAL"
            })
            self._audit_logout(request, success=True, reason="partial_error")
        
        return response     
            
    def _clear_auth_cookie(self, response):
        cookie_config = {
            "path": "/",
            "domain": getattr(settings, "SESSION_COOKIE_DOMAIN", None),
        }

        response.delete_cookie(
            key=getattr(settings, "JWT_AUTH_COOKIE", "access_token"),
            **cookie_config
        )
        response.delete_cookie(
            key=getattr(settings, "JWT_REFRESH_COOKIE", "refresh_token"),
            **cookie_config
        )

        csrf_cookie_name = getattr(settings, "CSRF_COOKIE_NAME", None)
        if csrf_cookie_name:
            response.delete_cookie(
                key=csrf_cookie_name,
                **cookie_config
            )
            
        logger.debug("Auth cookies cleared")

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in the list (client IP)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Validate IP address format
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            return "invalid_ip"
        
    
    def _audit_logout(self, request, success, reason=None):
        audit_data = {
            "event_type": "user_logout",
            "user_id": request.user.id,
            "username": request.user.username,
            "ip_address": self._get_client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "success": success,
            "reason": reason,
            "timestamp": timezone.now().isoformat(),
        }
        
        if not success:
            logger.warning(f"SECURITY_AUDIT: {audit_data}")
        else:
            logger.info(f"SECURITY_AUDIT: {audit_data}")
        
        
class ListUserApi(ListAPIView):
    queryset = CustomerUser.objects.all()
    serializer_class = UserSerializer
    
