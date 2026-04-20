from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

import secrets
import logging


logger = logging.getLogger(__name__)
User = get_user_model()

class TokenService:
    
    """
    Dịch vụ JWT Token chuẩn sản xuất

    Trách nhiệm:
    - Tạo cặp token
    - Làm mới access token
    - Xoay vòng refresh token một cách an toàn
    - Thu hồi token (đăng xuất)
    """
    
    
    def __init__(self):
        jwt_settings = getattr(settings, "SIMPLE_JWT", {})
        
        self.access_lifetime = jwt_settings.get("ACCESS_TOKEN_LIFETIME")
        self.refresh_lifetime = jwt_settings.get("REFRESH_TOKEN_LIFETIME")
        
    def _generate_session_id(self)->str:
        # Định danh phiên duy nhất để theo dõi thiết bị/phiên
        return secrets.token_hex(16)
    
    def _is_blacklisted(self, token: RefreshToken) -> bool:
        try:
            return BlacklistedToken.objects.filter(token__jti=token["jti"]).exists()
        except Exception:
            return False
    
    def _should_rotate(self, token: RefreshToken)->bool:
        # Rotate refresh token when near expiration
        
        exp = token.payload.get('exp')
        
        if not exp:
            return False
        
        remaining_seconds = exp - timezone.now().timestamp()
        # rotate if less than 1 day remaining
        return remaining_seconds < 24 * 60 * 60
    
    def _revoke_token(self, token: RefreshToken)->None:
        # Safe revoke old refresh token
        try:
            token.blacklist()
            
        except Exception as e:
            logger.warning(f"Failed to revoke token: {str(e)}")
            
    def _to_seconds(self, timedelta_obj)->int:
        
        # Convert timedelta to seconds safely
        if not timedelta_obj:
            return 0
        
        return int(timedelta_obj.total_seconds())
        
    def create_tokens(self, user: "User")->Dict[str, Any]:
        refresh = RefreshToken.for_user(user)
        session_id = self._generate_session_id()
        
        refresh["session_id"]=session_id
        refresh["user_id"]=user.id 
        
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "token_type": "Bearer",
            "access_expires_in": self._to_seconds(self.access_lifetime),
            "refresh_expires_in": self._to_seconds(self.refresh_lifetime),
            "session_id": session_id
        }
        
    def refresh_tokens(self, refresh_token: str)->Dict[str, Any]:
        # Làm mới token truy cập an toàn Tùy chọn xoay token làm mới (được khuyến nghị)
        
        try:
            old_refresh = RefreshToken(refresh_token)
            
            if self._is_blacklisted(old_refresh):
                raise TokenError("Token has been revoked.")
            
            user_id = old_refresh.get('user_id')
            session_id = old_refresh.get('session_id')
            
            new_access = str(old_refresh.access_token)
            
            response = {
                "access": new_access,
                "access_expires_in": self._to_seconds(self.access_lifetime)
            }
            
            # Xoay vòng an toàn: tạo token làm mới hoàn toàn mới
            
            if self._should_rotate(old_refresh):
                user = User.objects.get(id=user_id)
                
                new_refresh = RefreshToken.for_user(user)
                new_session_id = self._generate_session_id()
                
                response.update({
                    "refresh": str(new_refresh),
                    "refresh_expires_in": self._to_seconds(self.refresh_lifetime),
                    "session_id": new_session_id
                })
                self._revoke_token(old_refresh)
            return response
        except TokenError as e:
            logger.warning(f"Invalid refresh token: {e}")
            raise ValueError("Invalid or expired refresh token.")


"""
Nâng cấp
class TokenService:

    def __init__(self):
        jwt_settings = getattr(settings, "SIMPLE_JWT", {})

        self.access_lifetime = jwt_settings.get("ACCESS_TOKEN_LIFETIME")
        self.refresh_lifetime = jwt_settings.get("REFRESH_TOKEN_LIFETIME")

        # Redis (inject in real system)
        self.redis = settings.REDIS_CLIENT

    # =========================
    # CREATE TOKENS
    # =========================
    def create_tokens(self, user) -> Dict[str, Any]:

        refresh = RefreshToken.for_user(user)

        session_id = self._generate_session_id()
        device_id = self._generate_device_fingerprint(user)

        refresh["user_id"] = user.id
        refresh["session_id"] = session_id
        refresh["device_id"] = device_id

        # store session in Redis (IMPORTANT)
        self._store_session(session_id, user.id, device_id)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "token_type": "Bearer",
            "access_expires_in": self._to_seconds(self.access_lifetime),
            "refresh_expires_in": self._to_seconds(self.refresh_lifetime),
            "session_id": session_id,
        }

    # =========================
    # REFRESH FLOW (ENTERPRISE SAFE)
    # =========================
    def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:

        try:
            token = RefreshToken(refresh_token)

            jti = token.payload.get("jti")
            session_id = token.payload.get("session_id")
            user_id = token.payload.get("user_id")

            # 1. REUSE DETECTION (CRITICAL SECURITY)
            if self._is_reused(jti):
                self._revoke_all_sessions(user_id)
                raise TokenError("Token reuse detected (possible theft)")

            # 2. BLACKLIST CHECK (Redis O(1))
            if self._is_blacklisted(jti):
                raise TokenError("Token revoked")

            # 3. VALID SESSION CHECK
            if not self._validate_session(session_id, user_id):
                raise TokenError("Invalid session")

            user = User.objects.get(id=user_id)

            # 4. ISSUE NEW ACCESS TOKEN
            new_access = str(token.access_token)

            response = {
                "access": new_access,
                "access_expires_in": self._to_seconds(self.access_lifetime),
            }

            # 5. ROTATION (ALWAYS SAFE ROTATION)
            new_refresh = RefreshToken.for_user(user)

            new_session_id = self._generate_session_id()
            new_refresh["user_id"] = user.id
            new_refresh["session_id"] = new_session_id

            # 6. invalidate old token
            self._blacklist(jti)
            self._store_session(new_session_id, user.id, token.payload.get("device_id"))

            response.update({
                "refresh": str(new_refresh),
                "refresh_expires_in": self._to_seconds(self.refresh_lifetime),
                "session_id": new_session_id,
            })

            return response

        except TokenError as e:
            logger.warning(f"Token error: {str(e)}")
            raise ValueError("Authentication failed")

        except Exception as e:
            logger.exception("Unexpected token error")
            raise ValueError("Token processing failed")

    # =========================
    # SESSION MANAGEMENT (NEW)
    # =========================
    def _store_session(self, session_id, user_id, device_id):
        key = f"session:{session_id}"
        self.redis.setex(
            key,
            int(self._to_seconds(self.refresh_lifetime)),
            f"{user_id}:{device_id}"
        )

    def _validate_session(self, session_id, user_id):
        key = f"session:{session_id}"
        data = self.redis.get(key)

        if not data:
            return False

        stored_user_id = data.decode().split(":")[0]
        return str(stored_user_id) == str(user_id)

    # =========================
    # BLACKLIST (REDIS)
    # =========================
    def _blacklist(self, jti):
        self.redis.setex(f"blacklist:{jti}", 86400, "1")

    def _is_blacklisted(self, jti):
        return self.redis.exists(f"blacklist:{jti}")

    # =========================
    # REUSE DETECTION (VERY IMPORTANT)
    # =========================
    def _is_reused(self, jti):
        key = f"used:{jti}"
        if self.redis.exists(key):
            return True

        self.redis.setex(key, 86400, "1")
        return False

    # =========================
    # DEVICE FINGERPRINT
    # =========================
    def _generate_device_fingerprint(self, user):
        raw = f"{user.id}:{timezone.now().timestamp()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    # =========================
    # HELPERS
    # =========================
    def _generate_session_id(self):
        return secrets.token_hex(16)

    def _to_seconds(self, td):
        if not td:
            return 0
        return int(td.total_seconds())
"""
