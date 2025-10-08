#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB前端客户端

基于JWT认证的管理后台API客户端，用于处理前端管理界面的API请求。
"""

import requests
from typing import Dict, Any, Optional
from loguru import logger


class CrmebFrontendClient:
    """CRMEB前端API客户端"""

    def __init__(self, main_url: str, username: str, password: str, timeout: int = 30):
        """初始化前端客户端并自动登录

        Args:
            main_url: 完整的主域名URL（如：https://shop.shikejk.com 或 http://shop.example.com）
            username: 管理员用户名
            password: 管理员密码
            timeout: 请求超时时间（秒）

        Raises:
            Exception: 登录失败时抛出异常
        """
        logger.debug("初始化CRMEB前端客户端，主URL: {}", main_url)

        # 确保URL格式正确
        if not main_url.startswith(('http://', 'https://')):
            raise ValueError("main_url必须包含协议（http://或https://）")

        self.main_url = main_url.rstrip('/')  # 移除末尾的斜杠
        self.base_url = self.main_url
        self.timeout = timeout
        self.session = requests.Session()
        self.token = None

        # 设置默认请求头（基于您提供的请求信息）
        self._setup_default_headers()

        # 自动登录获取JWT Token
        self._auto_login(username, password)
        
        logger.debug("CRMEB前端客户端初始化完成")

    def _setup_default_headers(self):
        """设置默认请求头"""
        self.session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Sec-Ch-Ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=1, i',
            'Referer': f'{self.base_url}/admin/product/product_brand'
        })

    def _auto_login(self, username: str, password: str):
        """自动登录获取JWT认证令牌

        Args:
            username: 用户名
            password: 密码

        Raises:
            Exception: 登录失败时抛出异常
        """
        logger.debug("开始自动登录，账号: {}", username)
        
        url = f"{self.base_url}/adminapi/login"

        # 设置登录请求的特殊请求头
        login_headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/admin/login'
        }

        # 请求数据
        login_data = {
            "account": username,
            "pwd": password,
            "captchaType": "",
            "captchaVerification": ""
        }

        try:
            response = self.session.post(
                url, 
                json=login_data, 
                headers=login_headers, 
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.debug("登录响应状态: {}", result.get('status'))

            # 检查登录结果
            if result.get('status') == 200 and 'data' in result:
                data = result['data']
                if 'token' in data:
                    # 设置认证令牌（注意特殊的拼写：Authori-zation）
                    self.token = data['token']
                    self.session.headers['Authori-zation'] = f'Bearer {self.token}'
                    logger.debug("JWT Token设置成功")
                else:
                    raise Exception("登录响应中未找到token")
            else:
                error_msg = result.get('msg', '未知错误')
                raise Exception(f"登录失败: {error_msg}")

        except requests.RequestException as e:
            logger.debug("登录请求异常: {}", str(e))
            raise Exception(f"登录请求失败: {e}")

    def make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                    data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """发起API请求

        Args:
            method: HTTP方法（GET, POST, PUT, DELETE等）
            endpoint: API端点路径（如：/adminapi/product/brand）
            params: URL查询参数
            data: 表单数据
            json_data: JSON数据

        Returns:
            API响应的JSON数据

        Raises:
            Exception: 请求失败时抛出异常
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug("发起API请求: {} {}", method, url)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.debug("API响应状态: {}", result.get('status'))
            
            return result

        except requests.RequestException as e:
            logger.debug("API请求异常: {}", str(e))
            raise Exception(f"API请求失败: {e}")



    def close(self):
        """关闭客户端连接"""
        logger.debug("关闭CRMEB前端客户端")
        if hasattr(self, 'session'):
            self.session.close()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        self.close()
