"""
ZX_RPA统一消息通知模块
整合企业微信、钉钉、飞书等平台的消息通知功能

从 zx_rpa/notifications.py 迁移而来，保持完整功能并添加统一接口类
"""

import requests
import time
import hmac
import hashlib
import base64
from urllib.parse import quote_plus
from typing import Dict, Optional
from loguru import logger


"""
通知推送工厂类和专用客户端
"""

class WecomClient:
    """企业微信通知客户端"""

    def __init__(self, webhook_url: str):
        """
        初始化企业微信客户端

        Args:
            webhook_url: 企业微信群机器人webhook地址
        """
        logger.debug("初始化企业微信通知客户端")

        if not webhook_url:
            logger.error("企业微信webhook地址不能为空")
            raise ValueError("企业微信webhook地址不能为空")

        self.webhook_url = webhook_url

    def send(self, content: str) -> Dict:
        """
        发送企业微信消息

        Args:
            content: 消息内容

        Returns:
            Dict: 接口返回结果
        """
        logger.debug("发送企业微信消息")

        try:
            response = requests.post(
                self.webhook_url,
                json={
                    "msgtype": "text",
                    "text": {
                        "content": content
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            response.raise_for_status()
            result = response.json()

            if result.get("errcode") != 0:
                logger.error("企业微信API错误: {}", result.get('errmsg', '未知错误'))
                raise ValueError(f"企业微信API错误: {result.get('errmsg', '未知错误')}")

            logger.debug("企业微信通知发送成功")
            return result

        except requests.RequestException as e:
            logger.error("企业微信通知网络请求失败: {}", str(e))
            raise
        except Exception as e:
            logger.error("企业微信通知发送失败: {}", str(e))
            raise


class DingtalkClient:
    """钉钉通知客户端"""

    def __init__(self, webhook_url: str, secret: Optional[str] = None):
        """
        初始化钉钉客户端

        Args:
            webhook_url: 钉钉群机器人webhook地址
            secret: 机器人密钥（可选）
        """
        logger.debug("初始化钉钉通知客户端")

        if not webhook_url:
            logger.error("钉钉webhook地址不能为空")
            raise ValueError("钉钉webhook地址不能为空")

        self.webhook_url = webhook_url
        self.secret = secret

    def send(self, content: str) -> Dict:
        """
        发送钉钉消息

        Args:
            content: 消息内容

        Returns:
            Dict: 接口返回结果
        """
        logger.debug("发送钉钉消息")

        try:
            webhook_url = self.webhook_url

            # 如果有密钥，生成签名
            if self.secret:
                timestamp = str(round(time.time() * 1000))
                string_to_sign = f"{timestamp}\n{self.secret}"
                hmac_code = hmac.new(
                    self.secret.encode('utf-8'),
                    string_to_sign.encode('utf-8'),
                    digestmod=hashlib.sha256
                ).digest()
                sign = quote_plus(base64.b64encode(hmac_code))
                webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"

            response = requests.post(
                webhook_url,
                json={
                    "msgtype": "text",
                    "text": {
                        "content": content
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            response.raise_for_status()
            result = response.json()

            if result.get("errcode") != 0:
                logger.error("钉钉API错误: {}", result.get('errmsg', '未知错误'))
                raise ValueError(f"钉钉API错误: {result.get('errmsg', '未知错误')}")

            logger.debug("钉钉通知发送成功")
            return result

        except requests.RequestException as e:
            logger.error("钉钉通知网络请求失败: {}", str(e))
            raise
        except Exception as e:
            logger.error("钉钉通知发送失败: {}", str(e))
            raise


class FeishuClient:
    """飞书通知客户端"""

    def __init__(self, webhook_url: str):
        """
        初始化飞书客户端

        Args:
            webhook_url: 飞书群机器人webhook地址
        """
        logger.debug("初始化飞书通知客户端")

        if not webhook_url:
            logger.error("飞书webhook地址不能为空")
            raise ValueError("飞书webhook地址不能为空")

        self.webhook_url = webhook_url

    def send(self, content: str) -> Dict:
        """
        发送飞书消息

        Args:
            content: 消息内容

        Returns:
            Dict: 接口返回结果
        """
        logger.debug("发送飞书消息")

        try:
            response = requests.post(
                self.webhook_url,
                json={
                    "msg_type": "text",
                    "content": {
                        "text": content
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            response.raise_for_status()
            result = response.json()

            if result.get("code") != 0:
                logger.error("飞书API错误: {}", result.get('msg', '未知错误'))
                raise ValueError(f"飞书API错误: {result.get('msg', '未知错误')}")

            logger.debug("飞书通知发送成功")
            return result

        except requests.RequestException as e:
            logger.error("飞书通知网络请求失败: {}", str(e))
            raise
        except Exception as e:
            logger.error("飞书通知发送失败: {}", str(e))
            raise


class NotificationSender:
    """通知发送器工厂类"""

    @classmethod
    def wecom(cls, webhook_url: str) -> WecomClient:
        """
        创建企业微信通知客户端

        Args:
            webhook_url: 企业微信群机器人webhook地址

        Returns:
            WecomClient: 企业微信客户端实例
        """
        logger.debug("创建企业微信通知客户端")
        return WecomClient(webhook_url)

    @classmethod
    def dingtalk(cls, webhook_url: str, secret: Optional[str] = None) -> DingtalkClient:
        """
        创建钉钉通知客户端

        Args:
            webhook_url: 钉钉群机器人webhook地址
            secret: 机器人密钥（可选）

        Returns:
            DingtalkClient: 钉钉客户端实例
        """
        logger.debug("创建钉钉通知客户端")
        return DingtalkClient(webhook_url, secret)

    @classmethod
    def feishu(cls, webhook_url: str) -> FeishuClient:
        """
        创建飞书通知客户端

        Args:
            webhook_url: 飞书群机器人webhook地址

        Returns:
            FeishuClient: 飞书客户端实例
        """
        logger.debug("创建飞书通知客户端")
        return FeishuClient(webhook_url)