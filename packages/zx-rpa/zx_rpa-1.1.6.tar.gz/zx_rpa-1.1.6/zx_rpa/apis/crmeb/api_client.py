#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB API客户端模块

提供CRMEB平台的基础HTTP请求服务，包括token管理和请求封装。
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional
from loguru import logger


class CrmebApiClient:
    """CRMEB API客户端 - 提供基础HTTP请求服务"""

    def __init__(self, main_url: str, appid: str, appsecret: str, timeout: int = 30):
        """初始化API客户端
        
        Args:
            main_url: CRMEB主域名
            appid: 应用ID
            appsecret: 应用密钥
            timeout: 请求超时时间（秒）
        """
        logger.debug("初始化CRMEB API客户端，URL: {}", main_url)
        
        if not all([main_url, appid, appsecret]):
            logger.debug("CRMEB配置不完整，缺少必要参数")
            raise ValueError("CRMEB配置不完整，缺少main_url、appid或appsecret")
        
        self._main_url = main_url.rstrip('/')
        self._appid = appid
        self._appsecret = appsecret
        self._timeout = timeout
        self._token = None
        self._token_expire_time = None
        
        # 创建会话
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'zx-rpa/CrmebClient',
            'Content-Type': 'application/json'
        })
        
        logger.debug("CRMEB API客户端初始化完成，超时: {}秒", timeout)

    def get_token(self) -> str:
        """获取访问令牌"""
        if self._is_token_valid():
            logger.debug("使用缓存的token")
            return self._token
        
        logger.debug("获取新的访问token")
        return self._fetch_new_token()

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None) -> Dict:
        """发起HTTP请求
        
        Args:
            method: HTTP方法（GET/POST/PUT等）
            endpoint: API端点
            data: 请求数据
            headers: 自定义请求头
            
        Returns:
            API响应数据
        """
        url = f"{self._main_url}{endpoint}"
        logger.debug("发起{}请求: {}", method.upper(), endpoint)
        
        try:
            request_headers = self._build_headers(headers)
            
            if method.upper() == 'GET':
                response = self._session.get(url, headers=request_headers, 
                                           params=data, timeout=self._timeout)
            elif method.upper() == 'POST':
                response = self._session.post(url, headers=request_headers,
                                            json=data, timeout=self._timeout)
            elif method.upper() == 'PUT':
                response = self._session.put(url, headers=request_headers,
                                           json=data, timeout=self._timeout)
            else:
                logger.debug("不支持的HTTP方法: {}", method)
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            result = self._handle_response(response)
            logger.debug("请求成功，返回数据字段数量: {}", len(result.get('data', {})) if isinstance(result.get('data'), dict) else 0)
            return result
            
        except requests.RequestException as e:
            logger.debug("HTTP请求失败: {}", str(e))
            raise RuntimeError(f"HTTP请求失败: {e}")

    def _is_token_valid(self) -> bool:
        """检查token是否有效"""
        if not self._token or not self._token_expire_time:
            return False
        
        current_timestamp = int(datetime.now().timestamp())
        # 提前1小时刷新token
        return current_timestamp + 3600 < self._token_expire_time

    def _fetch_new_token(self) -> str:
        """获取新的访问令牌"""
        url = f"{self._main_url}/outapi/get_token"
        data = {
            "appid": self._appid,
            "appsecret": self._appsecret
        }
        
        try:
            # 获取token时不使用JSON头，使用form-data格式
            headers = {'User-Agent': 'zx-rpa/CrmebClient'}
            response = requests.post(url, data=data, headers=headers, timeout=self._timeout)
            response.raise_for_status()
            
            response_data = response.json()
            if response_data.get('status') != 200:
                error_msg = response_data.get('msg', '未知错误')
                logger.debug("获取token失败: {}", error_msg)
                raise RuntimeError(f"获取token失败: {error_msg}")
            
            self._token = response_data['data']['token']
            self._token_expire_time = response_data['data']['exp_time']
            
            logger.debug("token获取成功，过期时间: {}", self._token_expire_time)
            return self._token
            
        except requests.RequestException as e:
            logger.debug("获取token请求失败: {}", str(e))
            raise RuntimeError(f"获取token请求失败: {e}")
        except (KeyError, TypeError) as e:
            logger.debug("token响应数据格式错误: {}", str(e))
            raise RuntimeError(f"token响应数据格式错误: {e}")

    def _build_headers(self, custom_headers: Optional[Dict] = None) -> Dict:
        """构建请求头"""
        token = self.get_token()
        headers = {
            'authori-zation': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        if custom_headers:
            headers.update(custom_headers)
        
        return headers

    def _handle_response(self, response: requests.Response) -> Dict:
        """处理HTTP响应"""
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get('msg', '未知错误')
            except json.JSONDecodeError:
                error_msg = response.text[:200]
            
            logger.debug("HTTP错误 {}: {}", response.status_code, error_msg)
            raise RuntimeError(f"HTTP {response.status_code}: {error_msg}")

        try:
            result = response.json()
        except json.JSONDecodeError as e:
            logger.debug("响应JSON解析失败: {}", str(e))
            raise RuntimeError(f"响应JSON解析失败: {e}")

        if result.get('status') != 200:
            error_msg = result.get('msg', '未知业务错误')
            logger.debug("API业务错误: {}", error_msg)
            raise RuntimeError(f"API业务错误: {error_msg}")
        
        return result

    def close(self):
        """关闭会话"""
        if hasattr(self, '_session'):
            self._session.close()
            logger.debug("CRMEB API客户端会话已关闭")

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        self.close()
