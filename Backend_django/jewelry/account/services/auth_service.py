from typing import TYPE_CHECKING,Optional
from dataclasses import dataclass
from enum import Enum

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from .token_service import TokenService
from .auth_policy_service import AuthPolicyService

import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class AuthError(Enum):
    INVALID_CREDENTIALS = 'invalid_credentials'
    ACCOUNT_DISABLED = 'account_disabled'
    ACCOUNT_LOCKED = 'account_locked'
    SYSTEM_ERROR = 'system_error'
    
@dataclass(frozen=True)
class AuthResult:
    success: bool
    user: Optional[User] = None
    tokens: Optional[dict] = None
    error: Optional[AuthError]= None
    message: Optional[str] = None

class Authentication:
    def __init__(self):
        self.token_service = TokenService()
        # self.policy = AuthPolicyService()
        
    def _fail(self, error: AuthError, message: str)->AuthResult:
        return AuthResult(
            success=False,
            error=error,
            message=message
        )
        
    def _is_valid_input(self, username: str, password: str)->bool:
        return bool(username and password)
    
    def _check_account_status(self, user: User)->Optional[AuthResult]:
        
        if not user.is_active:
            return self._fail(
                AuthError.ACCOUNT_DISABLED,
                "Account disabled"
            )

        return AuthResult(success=True)
    
    def _log_failed_attempt(self, username: str)->None:
        logger.warning("Failed login attempt", extra={"username":username})
        
    def _log_success(self, user: User)->None:
        logger.info("Successful login", extra={
            "id":user.id,
            "username":user.username
        } )
        
    def authenticate_user(self, username: str, password: str, request=None)->AuthResult:
        
        if not self._is_valid_input(username, password):
            return self._fail(AuthError.INVALID_CREDENTIALS, "Invalid credentials.")
        
        try:
            # policy_error = self.policy.check_policy(username)
            # if policy_error:
            #     return self._fail(AuthError.ACCOUNT_LOCKED, policy_error)
            user = authenticate(request, username=username, password=password)
            if not user:
                # self.policy.register_failure(username)
                self._log_failed_attempt(username)
                return self._fail(
                    AuthError.INVALID_CREDENTIALS,
                    "Invalid credentials."
                )

            account_check  =self._check_account_status(user)
            
            if not account_check.success:
                return account_check
            
            tokens = self.token_service.create_tokens(user)
            
            self._log_success(user)
            # self.policy.reset_attempts(username)
            
            return AuthResult(success=True,
                              user=user,
                              tokens=tokens,
                              message="Login Successfully!"
                              )
        except Exception as e:
            logger.exception(
                "Authentication system error.",
                extra={"username":username}
            )
            return self._fail(
                AuthError.SYSTEM_ERROR,
                "Authentication failed."
            )
            
    