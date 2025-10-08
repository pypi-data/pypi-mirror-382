"""
AI助手
提供简洁易用的AI服务接口
"""

from loguru import logger
from .deepseek_client import DeepSeekClient
from .doubao_client import DoubaoClient


class AIAssistant:
    """AI助手工厂类"""

    @classmethod
    def deepseek(cls, api_key: str, model: str = "deepseek-chat", base_url: str = '') -> DeepSeekClient:
        """
        创建DeepSeek客户端

        Args:
            api_key: DeepSeek API密钥
            model: 默认模型名称
            base_url: API基础URL（可选）

        Returns:
            DeepSeekClient: DeepSeek客户端实例
        """
        logger.debug("创建DeepSeek客户端")
        return DeepSeekClient(api_key, model, base_url)

    @classmethod
    def doubao(cls, api_key: str, model: str, base_url: str = '') -> DoubaoClient:
        """
        创建豆包客户端

        Args:
            api_key: 豆包API密钥
            model: 智能体模型ID
            base_url: API基础URL（可选）

        Returns:
            DoubaoClient: 豆包客户端实例
        """
        logger.debug("创建豆包客户端")
        return DoubaoClient(api_key, model, base_url)
