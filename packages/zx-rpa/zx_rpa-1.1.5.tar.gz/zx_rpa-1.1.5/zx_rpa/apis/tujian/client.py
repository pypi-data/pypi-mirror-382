"""
图鉴验证码识别平台客户端
基于官方HTTP API接口封装，提供简洁易用的验证码识别服务
"""

import requests
from typing import Dict, Any, Optional
from loguru import logger
from ...system.image import ImageHandler


class TujianClient:
    """图鉴验证码识别客户端"""

    # API 接口地址
    PREDICT_URL = "http://api.ttshitu.com/predict"
    REPORT_ERROR_URL = "http://api.ttshitu.com/reporterror.json"
    QUERY_BALANCE_URL = "http://api.ttshitu.com/queryAccountInfo.json"

    # 验证码类型映射
    CAPTCHA_TYPES = {
        1: "纯数字",
        1001: "纯数字2",
        2: "纯英文", 
        1002: "纯英文2",
        3: "数英混合",
        1003: "数英混合2",
        4: "闪动GIF",
        7: "无感学习(独家)",
        66: "问答题",
        11: "计算题",
        1005: "快速计算题",
        5: "快速计算题2",
        16: "汉字",
        32: "通用文字识别(证件、单据)",
        29: "旋转类型",
        1029: "背景匹配旋转类型",
        2029: "背景匹配双旋转类型",
        19: "点选1个坐标",
        20: "点选3个坐标",
        21: "点选3-5个坐标",
        22: "点选5-8个坐标",
        27: "点选1-4个坐标",
        48: "轨迹类型",
        18: "缺口识别（2张图）",
        33: "单缺口识别（返回X轴坐标）",
        34: "缺口识别2（返回X轴坐标）",
        3400: "缺口识别（返回缺口左上角X,Y坐标）",
        53: "拼图识别"
    }

    def __init__(self, username: str, password: str, timeout: int = 60):
        """
        初始化图鉴客户端

        Args:
            username (str): 图鉴用户名
            password (str): 图鉴密码
            timeout (int, optional): 请求超时时间，单位秒. Defaults to 60.

        Raises:
            ValueError: 当用户名或密码为空时
        """
        logger.debug("初始化图鉴验证码客户端，用户: {}", username)
        
        if not username or not password:
            logger.debug("图鉴用户名和密码不能为空")
            raise ValueError("图鉴用户名和密码不能为空")

        self.username = username
        self.password = password
        self.timeout = timeout
        self._image_handler = ImageHandler()
        
        # 设置请求头
        self._headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def recognize_captcha(self, image: str, type_id: int = 3, **kwargs) -> Dict[str, Any]:
        """
        识别验证码

        Args:
            image (str): 图片数据（base64编码/文件路径/URL）
            type_id (int, optional): 验证码类型ID，默认3为数英混合. Defaults to 3.
            **kwargs: 其他可选参数
                - angle (str): 旋转角度，当typeid为14时使用，默认90
                - step (str): 每次旋转角度，旋转类型时使用，默认10
                - typename (str): 无感学习子类型名称，最多30字符
                - remark (str): 备注字段
                - imageback (str): 背景图片（缺口识别等需要）
                - content (str): 标题内容（快速点选需要）
                - title_image (str): 标题图片（快速点选需要）

        Returns:
            Dict[str, Any]: 识别结果
                - success (bool): 是否成功
                - result (str): 识别结果文本（成功时）
                - id (str): 识别ID（成功时，用于报错）
                - message (str): 错误信息（失败时）

        Raises:
            Exception: 当网络请求失败或参数错误时

        Example:
            >>> client = TujianClient("username", "password")
            >>> result = client.recognize_captcha("base64_image_data", type_id=3)
            >>> if result['success']:
            >>>     print(f"识别结果: {result['result']}")
            >>> else:
            >>>     print(f"识别失败: {result['message']}")
        """
        logger.debug("图鉴识别验证码，类型: {} ({})", type_id, self.CAPTCHA_TYPES.get(type_id, "未知类型"))

        try:
            # 处理图片格式，转换为base64
            base64_image = self._image_handler.process_image_to_base64(image)
            logger.debug("图片预处理完成，base64长度: {}", len(base64_image))

            # 构建请求数据
            request_data = {
                "username": self.username,
                "password": self.password,
                "typeid": str(type_id),
                "image": base64_image
            }

            # 添加可选参数
            optional_params = ['angle', 'step', 'typename', 'remark', 'content']
            for param in optional_params:
                if param in kwargs and kwargs[param] is not None:
                    request_data[param] = str(kwargs[param])

            # 处理附加图片参数
            if 'imageback' in kwargs and kwargs['imageback']:
                imageback_base64 = self._image_handler.process_image_to_base64(kwargs['imageback'])
                request_data['imageback'] = imageback_base64

            if 'title_image' in kwargs and kwargs['title_image']:
                title_image_base64 = self._image_handler.process_image_to_base64(kwargs['title_image'])
                request_data['title_image'] = title_image_base64

            logger.debug("发送识别请求到图鉴API")
            
            # 发送请求
            response = requests.post(
                self.PREDICT_URL,
                json=request_data,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            # 解析响应
            result = response.json()
            logger.debug("图鉴API响应状态: {}, 成功: {}", response.status_code, result.get('success'))

            if result.get('success'):
                logger.debug("验证码识别成功，结果: {}, ID: {}", result['data']['result'], result['data']['id'])
                return {
                    'success': True,
                    'result': result['data']['result'],
                    'id': result['data']['id']
                }
            else:
                logger.debug("验证码识别失败: {}", result.get('message'))
                return {
                    'success': False,
                    'message': result.get('message', '未知错误')
                }

        except requests.RequestException as e:
            logger.debug("图鉴网络请求失败: {}", str(e))
            raise Exception(f"图鉴网络请求失败: {e}")
        except Exception as e:
            logger.debug("图鉴验证码识别异常: {}", str(e))
            raise Exception(f"图鉴验证码识别异常: {e}")

    def get_balance(self) -> Dict[str, Any]:
        """
        查询账户余额

        Returns:
            Dict[str, Any]: 账户信息
                - success (bool): 是否成功
                - balance (str): 账户余额（成功时）
                - consumed (str): 总消费（成功时）
                - success_num (str): 成功识别次数（成功时）
                - fail_num (str): 失败识别次数（成功时）
                - message (str): 错误信息（失败时）

        Raises:
            Exception: 当网络请求失败时

        Example:
            >>> client = TujianClient("username", "password")
            >>> balance_info = client.get_balance()
            >>> if balance_info['success']:
            >>>     print(f"账户余额: {balance_info['balance']}")
            >>> else:
            >>>     print(f"查询失败: {balance_info['message']}")
        """
        logger.debug("查询图鉴账户余额")

        try:
            # 构建请求参数
            params = {
                'username': self.username,
                'password': self.password
            }

            logger.debug("发送余额查询请求到图鉴API")
            
            # 发送GET请求
            response = requests.get(
                self.QUERY_BALANCE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            # 解析响应
            result = response.json()
            logger.debug("余额查询响应状态: {}, 成功: {}", response.status_code, result.get('success'))

            if result.get('success'):
                data = result['data']
                logger.debug("余额查询成功，余额: {}", data['balance'])
                return {
                    'success': True,
                    'balance': data['balance'],
                    'consumed': data['consumed'],
                    'success_num': data['successNum'],
                    'fail_num': data['failNum']
                }
            else:
                logger.debug("余额查询失败: {}", result.get('message'))
                return {
                    'success': False,
                    'message': result.get('message', '未知错误')
                }

        except requests.RequestException as e:
            logger.debug("图鉴余额查询网络请求失败: {}", str(e))
            raise Exception(f"图鉴余额查询网络请求失败: {e}")
        except Exception as e:
            logger.debug("图鉴余额查询异常: {}", str(e))
            raise Exception(f"图鉴余额查询异常: {e}")

    def report_error(self, result_id: str) -> Dict[str, Any]:
        """
        报错处理，识别错误时可以调用此方法

        Args:
            result_id (str): 识别成功时返回的ID

        Returns:
            Dict[str, Any]: 报错结果
                - success (bool): 是否成功
                - message (str): 结果信息

        Raises:
            Exception: 当网络请求失败时

        Example:
            >>> client = TujianClient("username", "password")
            >>> # 先识别验证码
            >>> result = client.recognize_captcha("image_data")
            >>> if result['success']:
            >>>     # 如果识别结果错误，可以报错
            >>>     error_result = client.report_error(result['id'])
            >>>     print(f"报错结果: {error_result}")
        """
        logger.debug("图鉴验证码报错，ID: {}", result_id)

        try:
            # 构建请求数据
            request_data = {"id": result_id}

            logger.debug("发送报错请求到图鉴API")
            
            # 发送POST请求
            response = requests.post(
                self.REPORT_ERROR_URL,
                json=request_data,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            # 解析响应
            result = response.json()
            logger.debug("报错请求响应状态: {}, 成功: {}", response.status_code, result.get('success'))

            if result.get('success'):
                logger.debug("图鉴验证码报错成功")
                return {
                    'success': True,
                    'message': result['data']['result']
                }
            else:
                logger.debug("图鉴验证码报错失败: {}", result.get('message'))
                return {
                    'success': False,
                    'message': result.get('message', '未知错误')
                }

        except requests.RequestException as e:
            logger.debug("图鉴报错网络请求失败: {}", str(e))
            raise Exception(f"图鉴报错网络请求失败: {e}")
        except Exception as e:
            logger.debug("图鉴报错处理异常: {}", str(e))
            raise Exception(f"图鉴报错处理异常: {e}")

    def get_supported_types(self) -> Dict[int, str]:
        """
        获取支持的验证码类型

        Returns:
            Dict[int, str]: 验证码类型映射，key为类型ID，value为类型描述

        Example:
            >>> client = TujianClient("username", "password")
            >>> types = client.get_supported_types()
            >>> for type_id, description in types.items():
            >>>     print(f"{type_id}: {description}")
        """
        logger.debug("获取图鉴支持的验证码类型")
        return self.CAPTCHA_TYPES.copy()

    def validate_image(self, image: str) -> bool:
        """
        验证图片格式是否有效

        Args:
            image (str): 图片来源

        Returns:
            bool: 是否为有效图片

        Example:
            >>> client = TujianClient("username", "password")
            >>> is_valid = client.validate_image("./photo.jpg")
            >>> print(is_valid)  # True or False
        """
        logger.debug("验证图片格式")
        return self._image_handler.validate_image_format(image)
