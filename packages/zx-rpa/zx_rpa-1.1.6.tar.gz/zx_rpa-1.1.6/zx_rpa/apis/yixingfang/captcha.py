"""
伊性坊平台验证码处理模块

使用新的图鉴API客户端，提供验证码识别功能。
遵循ZX_RPA规范，避免重复实现。
"""

from typing import Dict
from loguru import logger
from ..tujian import TujianClient

# 限制对外暴露的类
__all__ = ['CaptchaHandler']


class CaptchaHandler:
    """
    验证码处理器

    使用新的统一验证码模块，提供伊性坊平台专用的验证码处理功能。
    """

    def __init__(self, tujian_username: str, tujian_password: str):
        """
        初始化验证码处理器

        Args:
            tujian_username: 图鉴平台用户名
            tujian_password: 图鉴平台密码
        """
        logger.debug("初始化验证码处理器，图鉴用户: {}", tujian_username)

        if not tujian_username or not tujian_password:
            logger.debug("图鉴用户名和密码不能为空")
            raise ValueError("图鉴用户名和密码不能为空")

        try:
            # 使用新的图鉴API客户端
            self._tujian_client = TujianClient(tujian_username, tujian_password)
            logger.debug("验证码处理器初始化成功")
        except Exception as e:
            logger.debug("初始化验证码处理器失败: {}", str(e))
            raise

    def recognize_captcha(self, image_source: str, type_id: int = 1) -> str:
        """
        识别验证码

        Args:
            image_source: 图片来源，支持base64编码、本地文件路径、网络URL
            type_id: 验证码类型ID，默认为1（普通英数字验证码）

        Returns:
            str: 识别结果

        Raises:
            Exception: 识别失败时抛出异常
        """
        logger.debug("开始识别验证码，类型ID: {}", type_id)

        try:
            # 使用新的图鉴API客户端
            result = self._tujian_client.recognize_captcha(image_source, type_id)
            if result['success']:
                logger.debug("验证码识别成功，结果: {}", result['result'])
                return result['result']
            else:
                logger.debug("验证码识别失败: {}", result['message'])
                raise Exception(f"验证码识别失败: {result['message']}")
        except Exception as e:
            logger.debug("验证码识别异常: {}", str(e))
            raise Exception(f"验证码识别异常: {str(e)}")

    def recognize_with_retry(self, image_source: str, type_id: int = 1, max_retries: int = 3) -> str:
        """
        带重试机制的验证码识别
        
        Args:
            image_source: 图片来源
            type_id: 验证码类型ID
            max_retries: 最大重试次数
            
        Returns:
            str: 识别结果
            
        Raises:
            Exception: 所有重试都失败时抛出异常
        """
        logger.debug("开始验证码识别，最大重试次数: {}", max_retries)
        
        last_error = None
        for attempt in range(max_retries):
            try:
                result = self.recognize_captcha(image_source, type_id)
                if result and result.strip():
                    logger.debug("第{}次尝试识别成功", attempt + 1)
                    return result.strip()
                else:
                    logger.debug("第{}次尝试识别结果为空", attempt + 1)
                    continue
            except Exception as e:
                last_error = e
                logger.debug("第{}次尝试识别失败: {}", attempt + 1, str(e))
                if attempt < max_retries - 1:
                    continue
                    
        logger.debug("验证码识别重试全部失败，重试次数: {}", max_retries)
        raise Exception(f"验证码识别重试全部失败: {str(last_error)}")

    def check_balance(self) -> Dict[str, str]:
        """
        查询图鉴账户余额

        Returns:
            dict: 余额信息

        Raises:
            Exception: 查询失败时抛出异常
        """
        logger.debug("查询图鉴账户余额")

        try:
            # 使用新的图鉴API客户端
            balance_info = self._tujian_client.get_balance()
            if balance_info['success']:
                logger.debug("余额查询成功，余额: {}", balance_info['balance'])
                return balance_info
            else:
                logger.debug("查询余额失败: {}", balance_info['message'])
                raise Exception(f"查询余额失败: {balance_info['message']}")
        except Exception as e:
            logger.debug("查询余额异常: {}", str(e))
            raise Exception(f"查询余额异常: {str(e)}")

    def validate_image(self, image_source: str) -> bool:
        """
        验证图片格式是否有效

        Args:
            image_source: 图片来源

        Returns:
            bool: 图片格式是否有效
        """
        logger.debug("验证图片格式")

        try:
            return self._tujian_client.validate_image(image_source)
        except Exception as e:
            logger.debug("图片格式验证失败: {}", str(e))
            return False
