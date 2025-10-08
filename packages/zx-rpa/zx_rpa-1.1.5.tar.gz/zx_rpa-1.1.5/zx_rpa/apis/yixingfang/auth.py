"""
伊性坊平台认证管理模块

提供Authorization令牌的管理功能，支持缓存和过期检查。
遵循ZX_RPA规范，避免全局单例，使用实例级别的认证管理。
"""

import threading
from datetime import datetime, timedelta
from typing import Optional, Dict
from loguru import logger

# 限制对外暴露的类
__all__ = ['AuthManager']


class AuthManager:
    """
    认证管理器 - 实例级别的Authorization管理
    
    不使用全局单例模式，每个客户端实例独立管理自己的认证状态。
    这样可以避免多实例使用时的冲突问题。
    """

    def __init__(self):
        """初始化认证管理器"""
        logger.debug("初始化认证管理器")
        
        self._authorization = None
        self._expire_time = None
        self._last_update = None
        self._update_lock = threading.Lock()

    def set_authorization(self, authorization: str, expire_minutes: int = 30):
        """
        设置Authorization令牌
        
        Args:
            authorization: Authorization令牌
            expire_minutes: 过期时间（分钟），默认30分钟
        """
        if not authorization:
            logger.debug("Authorization不能为空")
            raise ValueError("Authorization不能为空")
            
        with self._update_lock:
            self._authorization = authorization
            self._expire_time = datetime.now() + timedelta(minutes=expire_minutes)
            self._last_update = datetime.now()
            
            # 脱敏显示Authorization
            masked_auth = authorization[:20] + "..." if len(authorization) > 20 else authorization
            expire_time_str = self._expire_time.strftime('%H:%M:%S')
            logger.debug("Authorization已更新: {}，有效期至: {}", masked_auth, expire_time_str)

    def get_authorization(self) -> Optional[str]:
        """
        获取有效的Authorization令牌
        
        Returns:
            str: 有效的Authorization令牌，如果过期或不存在返回None
        """
        with self._update_lock:
            if self._authorization and self._expire_time and datetime.now() < self._expire_time:
                return self._authorization
            elif self._authorization and self._expire_time:
                expire_time_str = self._expire_time.strftime('%H:%M:%S')
                logger.debug("Authorization已过期，过期时间: {}", expire_time_str)
            return None

    def is_expired(self) -> bool:
        """
        检查Authorization是否过期
        
        Returns:
            bool: 如果过期或不存在返回True
        """
        if not self._expire_time:
            return True
        return datetime.now() >= self._expire_time

    def clear(self):
        """清除Authorization令牌"""
        with self._update_lock:
            self._authorization = None
            self._expire_time = None
            self._last_update = None
            logger.debug("Authorization已清除")

    def get_status(self) -> Dict[str, Optional[str]]:
        """
        获取认证状态信息
        
        Returns:
            dict: 包含认证状态的字典
        """
        with self._update_lock:
            return {
                "has_auth": bool(self._authorization),
                "is_expired": self.is_expired(),
                "expire_time": self._expire_time.strftime('%H:%M:%S') if self._expire_time else None,
                "last_update": self._last_update.strftime('%H:%M:%S') if self._last_update else None
            }

    def is_valid(self) -> bool:
        """
        检查Authorization是否有效（存在且未过期）
        
        Returns:
            bool: 如果有效返回True
        """
        return bool(self.get_authorization())

    def get_remaining_time(self) -> Optional[int]:
        """
        获取剩余有效时间（秒）
        
        Returns:
            int: 剩余秒数，如果已过期或不存在返回None
        """
        with self._update_lock:
            if not self._expire_time:
                return None
                
            remaining = (self._expire_time - datetime.now()).total_seconds()
            return max(0, int(remaining)) if remaining > 0 else None
