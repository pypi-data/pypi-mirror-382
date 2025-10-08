"""
趣多推送客户端模块
提供微信消息推送功能，支持GET和POST两种请求方式
"""

import requests
import json
import time
from typing import Dict, Optional
from loguru import logger


class QuduoClient:
    """趣多推送客户端"""

    def __init__(self, token: str):
        """
        初始化趣多推送客户端

        Args:
            token: 趣多推送的TOKEN，关注公众号【趣多推送】获取
        """
        logger.debug("初始化趣多推送客户端")

        if not token:
            logger.warning("趣多推送TOKEN不能为空")
            raise ValueError("趣多推送TOKEN不能为空")

        self.token = token
        self.base_url = "http://api.ccqcc.cc/Handler/WeChat.ashx"
        self._last_request_time = 0

    def _check_rate_limit(self):
        """
        检查请求频率限制（6秒每次）
        """
        current_time = time.time()
        time_diff = current_time - self._last_request_time
        
        if time_diff < 6:
            wait_time = 6 - time_diff
            logger.debug("请求频率限制，等待 {:.2f} 秒", wait_time)
            time.sleep(wait_time)
        
        self._last_request_time = time.time()

    def _handle_response(self, response: requests.Response) -> Dict:
        """
        处理API响应

        Args:
            response: requests响应对象

        Returns:
            Dict: 处理后的响应数据
        """
        try:
            response.raise_for_status()

            # 记录原始响应内容用于调试
            response_text = response.text.strip()
            logger.trace("API原始响应: {}", response_text)

            # 检查响应是否为空
            if not response_text:
                logger.warning("API返回空响应")
                raise ValueError("API返回空响应")

            # 尝试解析JSON
            try:
                result = response.json()

                code = result.get("code")
                msg = result.get("msg", "")

                if code == "200":
                    logger.debug("趣多推送消息发送成功")
                    return result
                else:
                    # 处理错误码
                    error_messages = {
                        "9001": "微信服务器转发返回非成功标记",
                        "9002": "请求频繁限定6秒每次",
                        "9003": "消息包含常规违禁词",
                        "9004": "因违规永远封停账号"
                    }

                    error_msg = error_messages.get(code, f"未知错误码: {code}")
                    logger.warning("趣多推送API错误 [{}]: {} - {}", code, error_msg, msg)
                    raise ValueError(f"趣多推送API错误 [{code}]: {error_msg} - {msg}")

            except json.JSONDecodeError:
                # 如果不是JSON格式，可能是错误消息的纯文本
                logger.warning("API返回非JSON格式响应: {}", response_text)
                raise ValueError(f"API错误: {response_text}")

        except requests.RequestException as e:
            logger.warning("趣多推送网络请求失败: {}", str(e))
            raise
        except ValueError:
            # ValueError已经在上面处理过了，直接重新抛出
            raise
        except Exception as e:
            logger.warning("趣多推送请求处理失败: {}", str(e))
            raise

    def send_get(self, msg: str) -> Dict:
        """
        使用GET方式发送消息（简单文本消息，20字以内）

        Args:
            msg: 消息内容，20字以内

        Returns:
            Dict: 接口返回结果
        """
        logger.debug("使用GET方式发送趣多推送消息")

        if not msg:
            logger.warning("消息内容不能为空")
            raise ValueError("消息内容不能为空")

        if len(msg) > 20:
            logger.warning("GET方式消息内容不能超过20字")
            raise ValueError("GET方式消息内容不能超过20字")

        # 检查请求频率限制
        self._check_rate_limit()

        try:
            params = {
                "token": self.token,
                "msg": msg
            }

            response = requests.get(
                self.base_url,
                params=params,
                timeout=10
            )

            return self._handle_response(response)

        except Exception as e:
            logger.warning("GET方式发送趣多推送消息失败: {}", str(e))
            raise

    def send_post(self, title: str, content: str) -> Dict:
        """
        使用POST方式发送消息（支持长文本，最大4000字）

        Args:
            title: 消息标题，20字以内
            content: 消息内容，4000字以内

        Returns:
            Dict: 接口返回结果
        """
        logger.debug("使用POST方式发送趣多推送消息")

        if not title:
            logger.warning("消息标题不能为空")
            raise ValueError("消息标题不能为空")

        if not content:
            logger.warning("消息内容不能为空")
            raise ValueError("消息内容不能为空")

        # 注意：这里的20字是指字符数，中文字符也算1个字符
        if len(title) > 20:
            logger.warning("消息标题不能超过20字符")
            raise ValueError("消息标题不能超过20字符")

        if len(content) > 4000:
            logger.warning("消息内容不能超过4000字")
            raise ValueError("消息内容不能超过4000字")

        # 检查请求频率限制
        self._check_rate_limit()

        try:
            url = f"{self.base_url}?token={self.token}"
            
            payload = {
                "msg": title,
                "desc": content
            }

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload, ensure_ascii=False),
                timeout=10
            )

            return self._handle_response(response)

        except Exception as e:
            logger.warning("POST方式发送趣多推送消息失败: {}", str(e))
            raise

    def send(self, content: str, title: Optional[str] = None) -> Dict:
        """
        智能发送消息（根据内容长度自动选择GET或POST方式）

        Args:
            content: 消息内容
            title: 消息标题（可选，如果提供则使用POST方式）

        Returns:
            Dict: 接口返回结果
        """
        logger.debug("智能发送趣多推送消息")

        if title is not None:
            # 有标题，使用POST方式
            return self.send_post(title, content)
        elif len(content) <= 20:
            # 内容较短，使用GET方式
            return self.send_get(content)
        else:
            # 内容较长，使用POST方式，使用简单标题
            simple_title = "消息"
            return self.send_post(simple_title, content)
