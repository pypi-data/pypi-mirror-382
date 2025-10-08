"""
DeepSeek AI客户端
专注于DeepSeek平台的对话API调用
"""

import requests
from loguru import logger
from typing import Union, Tuple


class DeepSeekClient:
    """DeepSeek AI客户端"""

    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: str = ''):
        """
        初始化DeepSeek客户端

        Args:
            api_key: DeepSeek API密钥
            model: 默认模型名称
            base_url: API基础URL（可选）
        """
        logger.debug("初始化DeepSeek客户端，模型: {}", model)
        
        if not api_key:
            logger.debug("DeepSeek API密钥不能为空")
            raise ValueError("DeepSeek API密钥不能为空")

        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.deepseek.com"

    def chat(self, message: str, model: str = '', system_content: str = '', 
             temperature: float = 0.7) -> Union[str, Tuple[str, str]]:
        """
        DeepSeek对话

        Args:
            message: 对话消息内容
            model: 模型名称（可选，覆盖默认模型）
            system_content: 系统提示词（可选）
            temperature: 温度参数（可选，默认0.7）

        Returns:
            对于 deepseek-chat: 返回 str (AI回复内容)
            对于 deepseek-reasoner: 返回 tuple (content, reasoning_content)
        """
        actual_model = model or self.model
        logger.debug("DeepSeek对话，模型: {}，消息长度: {}", actual_model, len(message))

        if not message.strip():
            logger.debug("对话消息不能为空")
            raise ValueError("对话消息不能为空")

        url = f"{self.base_url}/chat/completions"
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
            logger.debug("发送请求到DeepSeek API")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            response_data = response.json()
            logger.debug("DeepSeek API响应成功")

            if "choices" in response_data and len(response_data["choices"]) > 0:
                choice = response_data["choices"][0]
                message_data = choice["message"]

                if actual_model == "deepseek-reasoner":
                    reasoning_content = message_data.get("reasoning_content", "")
                    content = message_data.get("content", "")
                    # 记录AI返回结果（截取前200字符避免日志过长）
                    content_preview = content[:200] + "..." if len(content) > 200 else content
                    reasoning_preview = reasoning_content[:200] + "..." if len(reasoning_content) > 200 else reasoning_content
                    logger.debug("DeepSeek推理模型响应完成，内容长度: {}，推理长度: {}，内容预览: {}，推理预览: {}",
                               len(content), len(reasoning_content), content_preview, reasoning_preview)
                    return content, reasoning_content
                else:
                    content = message_data.get("content", "")
                    # 记录AI返回结果（截取前200字符避免日志过长）
                    content_preview = content[:200] + "..." if len(content) > 200 else content
                    logger.debug("DeepSeek对话完成，回复长度: {}，AI返回内容: {}", len(content), content_preview)
                    return content
            else:
                logger.debug("DeepSeek API响应格式异常")
                raise Exception("DeepSeek API响应格式异常")

        except requests.RequestException as e:
            logger.debug("DeepSeek API请求失败: {}", str(e))
            raise Exception(f"DeepSeek API请求失败: {e}")
        except Exception as e:
            logger.debug("DeepSeek对话异常: {}", str(e))
            raise
