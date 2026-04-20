# authentication/services/auth_policy_service.py

from django.conf import settings
from django.utils import timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AuthPolicyService:

    def __init__(self):
        self.redis = settings.REDIS_CLIENT

        # config
        self.max_attempts = 5
        self.lock_time = 15 * 60  # 15 phút
        
    def is_locked(self, username: str) -> bool:
        key = f"lock:{username}"
        return self.redis.exists(key)
    
    def register_failure(self, username: str) -> None:
        key = f"fail:{username}"

        attempts = self.redis.incr(key)

        # set expiry nếu lần đầu
        if attempts == 1:
            self.redis.expire(key, self.lock_time)

        if attempts >= self.max_attempts:
            self._lock_account(username)
        
    def _lock_account(self, username: str):
        lock_key = f"lock:{username}"
        self.redis.setex(lock_key, self.lock_time, "1")

        logger.warning(f"Account locked: {username}")
        
    def reset_attempts(self, username: str):
        self.redis.delete(f"fail:{username}")
        self.redis.delete(f"lock:{username}")
        
    def check_policy(self, username: str) -> Optional[str]:
        if self.is_locked(username):
            return "Account temporarily locked. Try again later."
        return None