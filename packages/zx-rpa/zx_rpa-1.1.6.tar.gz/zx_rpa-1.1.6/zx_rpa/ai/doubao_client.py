"""
豆包AI客户端
专注于豆包平台的对话API调用
"""

import requests
from loguru import logger


class DoubaoClient:
    """豆包AI客户端"""

    def __init__(self, api_key: str, model: str, base_url: str = None):
        """
        初始化豆包客户端

        Args:
            api_key: 豆包API密钥
            model: 智能体模型ID
            base_url: API基础URL（可选）
        """
        logger.debug("初始化豆包客户端，模型: {}", model)
        
        if not api_key:
            logger.debug("豆包API密钥不能为空")
            raise ValueError("豆包API密钥不能为空")

        if not model:
            logger.debug("豆包模型ID不能为空")
            raise ValueError("豆包模型ID不能为空")

        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://ark.cn-beijing.volces.com"

    def chat(self, message: str, model: str = None, system_content: str = None, 
             temperature: float = 0.7) -> str:
        """
        豆包对话

        Args:
            message: 对话消息内容
            model: 模型名称（可选，覆盖默认模型）
            system_content: 系统提示词（可选）
            temperature: 温度参数（可选，默认0.7）

        Returns:
            str: AI回复内容
        """
        actual_model = model or self.model
        logger.debug("豆包对话，模型: {}，消息长度: {}", actual_model, len(message))

        if not message.strip():
            logger.debug("对话消息不能为空")
            raise ValueError("对话消息不能为空")

        url = f"{self.base_url}/api/v3/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": system_content or "You are a helpful assistant"},
            {"role": "user", "content": message}
        ]

        data = {
            "model": actual_model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }

        try:
            logger.debug("发送请求到豆包API")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            response_data = response.json()
            logger.debug("豆包API响应成功")

            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                # 记录AI返回结果（截取前200字符避免日志过长）
                content_preview = content[:200] + "..." if len(content) > 200 else content
                logger.debug("豆包对话完成，回复长度: {}，AI返回内容: {}", len(content), content_preview)
                return content
            else:
                logger.debug("豆包API响应格式异常")
                raise Exception("豆包API响应格式异常")

        except requests.RequestException as e:
            logger.debug("豆包API请求失败: {}", str(e))
            raise Exception(f"豆包API请求失败: {e}")
        except Exception as e:
            logger.debug("豆包对话异常: {}", str(e))
            raise

    def chat_with_bot(self, message: str, model_id: str = None) -> str:
        """
        豆包智能体对话

        Args:
            message: 消息内容
            model_id: 智能体模型ID（可选，覆盖默认模型）

        Returns:
            str: 智能体回复内容，失败时返回None
        """
        actual_model_id = model_id or self.model
        logger.debug("豆包智能体对话，模型ID: {}，消息长度: {}", actual_model_id, len(message))

        if not message.strip():
            logger.debug("智能体对话消息不能为空")
            raise ValueError("智能体对话消息不能为空")

        url = f"{self.base_url}/api/v3/bots/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": actual_model_id,
            "stream": False,
            "stream_options": {"include_usage": True},
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        }

        try:
            logger.debug("发送请求到豆包智能体API")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            response_data = response.json()
            logger.debug("豆包智能体API响应成功")

            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                # 记录AI返回结果（截取前200字符避免日志过长）
                content_preview = content[:200] + "..." if len(content) > 200 else content
                logger.debug("豆包智能体对话完成，回复长度: {}，AI返回内容: {}", len(content), content_preview)
                return content
            else:
                logger.debug("豆包智能体API响应格式异常")
                return None

        except requests.RequestException as e:
            logger.debug("豆包智能体API请求失败: {}", str(e))
            return None
        except (KeyError, IndexError) as e:
            logger.debug("豆包智能体响应解析错误: {}", str(e))
            return None
        except Exception as e:
            logger.debug("豆包智能体对话异常: {}", str(e))
            return None
