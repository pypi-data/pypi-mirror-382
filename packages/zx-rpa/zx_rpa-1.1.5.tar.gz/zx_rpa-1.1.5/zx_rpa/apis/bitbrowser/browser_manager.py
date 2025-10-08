"""
比特浏览器窗口管理器

提供浏览器窗口的创建、更新、打开、关闭、删除等功能
"""

import requests
import json
import time
from typing import Dict, List, Optional, Union, Any
from loguru import logger


class BrowserManager:
    """比特浏览器窗口管理器"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:54345", cache_ttl: int = 600):
        """初始化浏览器管理器

        Args:
            base_url (str): 比特浏览器本地服务地址，默认为 http://127.0.0.1:54345
            cache_ttl (int): 缓存过期时间（秒），默认600秒
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {'Content-Type': 'application/json'}

        # 缓存相关
        self._browser_cache: Dict[str, Dict[str, Any]] = {}  # name -> browser_info
        self._cache_timestamp: float = 0
        self._cache_ttl: int = cache_ttl

        logger.debug("初始化比特浏览器窗口管理器，服务地址: {}, 缓存TTL: {}秒", base_url, cache_ttl)
    
    def create_browser(self, name: str, remark: str = "", proxy_method: int = 2, 
                      proxy_type: str = "noproxy", host: str = "", port: str = "",
                      proxy_username: str = "", proxy_password: str = "",
                      browser_fingerprint: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """创建浏览器窗口
        
        Args:
            name (str): 窗口名称
            remark (str, optional): 备注信息. Defaults to "".
            proxy_method (int, optional): 代理方式，2为自定义，3为提取IP. Defaults to 2.
            proxy_type (str, optional): 代理类型，支持 noproxy/http/https/socks5/ssh. Defaults to "noproxy".
            host (str, optional): 代理主机. Defaults to "".
            port (str, optional): 代理端口. Defaults to "".
            proxy_username (str, optional): 代理用户名. Defaults to "".
            proxy_password (str, optional): 代理密码. Defaults to "".
            browser_fingerprint (Dict, optional): 浏览器指纹配置. Defaults to None.
            **kwargs: 其他窗口配置参数
            
        Returns:
            Dict[str, Any]: 创建结果，包含窗口ID等信息
            
        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当参数格式不正确时
        """
        logger.debug("开始创建浏览器窗口，名称: {}", name)
        
        # 构建请求数据
        json_data = {
            'name': name,
            'remark': remark,
            'proxyMethod': proxy_method,
            'proxyType': proxy_type,
            'host': host,
            'port': port,
            'proxyUserName': proxy_username,
            'proxyPassword': proxy_password,
            'browserFingerPrint': browser_fingerprint or {'coreVersion': '124'}
        }
        
        # 添加其他参数
        json_data.update(kwargs)
        
        try:
            response = requests.post(
                f"{self.base_url}/browser/update",
                data=json.dumps(json_data),
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()

            browser_id = result.get('data', {}).get('id')
            logger.debug("浏览器窗口创建完成，窗口ID: {}", browser_id)

            # 同步缓存：添加新创建的浏览器
            if result.get('success') and browser_id:
                browser_info = {
                    'id': browser_id,
                    'name': name,
                    'remark': remark,
                    'proxyMethod': proxy_method,
                    'proxyType': proxy_type,
                    'host': host,
                    'port': port,
                    'proxyUserName': proxy_username,
                    'proxyPassword': proxy_password
                }
                # 添加其他传入的参数
                browser_info.update(kwargs)
                self._add_to_cache(browser_info)

            return result
            
        except requests.RequestException as e:
            logger.debug("创建浏览器窗口异常: {}", str(e))
            raise
    
    def update_browser_partial(self, browser_ids: List[str], **update_fields) -> Dict[str, Any]:
        """批量更新浏览器窗口信息
        
        Args:
            browser_ids (List[str]): 要更新的窗口ID列表
            **update_fields: 要更新的字段，如 name, remark, browserFingerPrint 等
            
        Returns:
            Dict[str, Any]: 更新结果
            
        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当参数格式不正确时
        """
        logger.debug("开始批量更新浏览器窗口，数量: {}", len(browser_ids))
        
        json_data = {'ids': browser_ids}
        json_data.update(update_fields)
        
        try:
            response = requests.post(
                f"{self.base_url}/browser/update/partial",
                data=json.dumps(json_data),
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()

            logger.debug("批量更新浏览器窗口完成")

            # 同步缓存：批量更新后刷新缓存（因为可能涉及多个浏览器的名称等信息变更）
            if result.get('success'):
                self._refresh_cache()
                logger.debug("批量更新后刷新缓存")

            return result
            
        except requests.RequestException as e:
            logger.debug("批量更新浏览器窗口异常: {}", str(e))
            raise
    
    def open_browser(self, name_or_id: str) -> Dict[str, Any]:
        """打开浏览器窗口

        Args:
            name_or_id (str): 浏览器窗口名称或ID

        Returns:
            Dict[str, Any]: 打开结果，包含调试端口等信息

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当找不到对应的浏览器时
        """
        # 解析为浏览器ID
        browser_id = self._resolve_browser_id(name_or_id)
        logger.debug("开始打开浏览器窗口，ID: {}", browser_id)

        json_data = {"id": browser_id}
        
        try:
            response = requests.post(
                f"{self.base_url}/browser/open",
                data=json.dumps(json_data),
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            logger.debug("浏览器窗口打开完成，调试端口: {}", result.get('data', {}).get('http'))
            return result
            
        except requests.RequestException as e:
            logger.debug("打开浏览器窗口异常: {}", str(e))
            raise
    
    def close_browser(self, name_or_id: str) -> Dict[str, Any]:
        """关闭浏览器窗口

        Args:
            name_or_id (str): 浏览器窗口名称或ID

        Returns:
            Dict[str, Any]: 关闭结果

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当找不到对应的浏览器时
        """
        # 解析为浏览器ID
        browser_id = self._resolve_browser_id(name_or_id)
        logger.debug("开始关闭浏览器窗口，ID: {}", browser_id)

        json_data = {'id': browser_id}
        
        try:
            response = requests.post(
                f"{self.base_url}/browser/close",
                data=json.dumps(json_data),
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            logger.debug("浏览器窗口关闭完成")
            return result
            
        except requests.RequestException as e:
            logger.debug("关闭浏览器窗口异常: {}", str(e))
            raise
    
    def delete_browser(self, name_or_id: str) -> Dict[str, Any]:
        """删除浏览器窗口

        Args:
            name_or_id (str): 浏览器窗口名称或ID

        Returns:
            Dict[str, Any]: 删除结果

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当找不到对应的浏览器时
        """
        # 解析为浏览器ID
        browser_id = self._resolve_browser_id(name_or_id)
        logger.debug("开始删除浏览器窗口，ID: {}", browser_id)

        json_data = {'id': browser_id}
        
        try:
            response = requests.post(
                f"{self.base_url}/browser/delete",
                data=json.dumps(json_data),
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()

            logger.debug("浏览器窗口删除完成")

            # 同步缓存：移除已删除的浏览器
            if result.get('success'):
                self._remove_from_cache(name_or_id)

            return result
            
        except requests.RequestException as e:
            logger.debug("删除浏览器窗口异常: {}", str(e))
            raise
    
    def list_browsers(self, page: int = 0, page_size: int = 10, group_name_or_id: str = "",
                     get_all: bool = False, **filters) -> Dict[str, Any]:
        """查询浏览器窗口列表

        Args:
            page (int, optional): 页码，从0开始. Defaults to 0.
            page_size (int, optional): 每页数量，最大100. Defaults to 10.
            group_name_or_id (str, optional): 分组名称或ID，用于筛选特定分组的窗口. Defaults to "".
            get_all (bool, optional): 是否获取所有浏览器，忽略分页参数. Defaults to False.
            **filters: 其他筛选条件

        Returns:
            Dict[str, Any]: 窗口列表数据

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当找不到对应的分组时
        """
        # 解析分组名称或ID为分组ID
        group_id = ""
        if group_name_or_id and group_name_or_id.strip():
            from .group_manager import GroupManager
            group_manager = GroupManager(self.base_url)
            group_id = group_manager._resolve_group_id(group_name_or_id)

        if get_all:
            return self._get_all_browsers(group_id, **filters)

        logger.debug("开始查询浏览器窗口列表，页码: {}, 每页: {}", page, page_size)

        json_data = {
            'page': page,
            'pageSize': min(page_size, 100),  # 限制最大100条
            'groupId': group_id
        }
        json_data.update(filters)

        try:
            response = requests.post(
                f"{self.base_url}/browser/list",
                data=json.dumps(json_data),
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()

            # 获取实际的浏览器列表数量
            data = result.get('data', [])
            if isinstance(data, list):
                total_count = len(data)
            elif isinstance(data, dict):
                total_count = data.get('total', len(data.get('list', [])))
            else:
                total_count = 0

            logger.debug("浏览器窗口列表查询完成，总数: {}", total_count)
            return result

        except requests.RequestException as e:
            logger.debug("查询浏览器窗口列表异常: {}", str(e))
            raise

    def _get_all_browsers(self, group_id: str = "", **filters) -> Dict[str, Any]:
        """获取所有浏览器窗口（内部方法）

        Args:
            group_id (str, optional): 分组ID. Defaults to "".
            **filters: 其他筛选条件

        Returns:
            Dict[str, Any]: 包含所有浏览器的结果

        Raises:
            requests.RequestException: 当网络请求失败时
        """
        logger.debug("开始获取所有浏览器窗口")

        all_browsers = []
        page = 0
        page_size = 100  # 使用较大的页面大小减少API调用

        while True:
            json_data = {
                'page': page,
                'pageSize': page_size,
                'groupId': group_id
            }
            json_data.update(filters)

            try:
                response = requests.post(
                    f"{self.base_url}/browser/list",
                    data=json.dumps(json_data),
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()

                data = result.get('data', [])
                if isinstance(data, list):
                    browsers = data
                elif isinstance(data, dict):
                    browsers = data.get('list', [])
                else:
                    browsers = []

                if not browsers:
                    break

                all_browsers.extend(browsers)

                # 如果返回的数量少于页面大小，说明已经是最后一页
                if len(browsers) < page_size:
                    break

                page += 1

            except requests.RequestException as e:
                logger.debug("获取所有浏览器窗口异常: {}", str(e))
                raise

        logger.debug("获取所有浏览器窗口完成，总数: {}", len(all_browsers))

        # 返回与原API相同的格式
        return {
            'success': True,
            'data': all_browsers
        }

    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self._browser_cache:
            return False
        return time.time() - self._cache_timestamp < self._cache_ttl

    def _refresh_cache(self) -> None:
        """刷新浏览器缓存"""
        logger.debug("开始刷新浏览器缓存")

        try:
            result = self._get_all_browsers()
            browsers = result.get('data', [])

            # 重建缓存
            self._browser_cache.clear()
            for browser in browsers:
                name = browser.get('name', '')
                if name:  # 只缓存有名称的浏览器
                    self._browser_cache[name] = browser

            self._cache_timestamp = time.time()
            logger.debug("浏览器缓存刷新完成，缓存数量: {}", len(self._browser_cache))

        except Exception as e:
            logger.debug("刷新浏览器缓存异常: {}", str(e))
            # 不抛出异常，保持旧缓存

    def clear_cache(self) -> None:
        """清空浏览器缓存"""
        logger.debug("清空浏览器缓存")
        self._browser_cache.clear()
        self._cache_timestamp = 0

    def refresh_cache(self) -> None:
        """强制刷新浏览器缓存"""
        self._refresh_cache()

    def _add_to_cache(self, browser_info: Dict[str, Any]) -> None:
        """添加浏览器到缓存

        Args:
            browser_info (Dict[str, Any]): 浏览器信息
        """
        name = browser_info.get('name', '').strip()
        if not name:
            return  # 没有名称的浏览器不缓存

        # 如果缓存无效，先初始化缓存
        if not self._is_cache_valid():
            self._refresh_cache()

        # 添加到缓存
        self._browser_cache[name] = browser_info
        logger.debug("添加浏览器到缓存: {}", name)

    def _remove_from_cache(self, name_or_id: str) -> None:
        """从缓存中移除浏览器

        Args:
            name_or_id (str): 浏览器名称或ID
        """
        if not self._is_cache_valid():
            return  # 缓存无效时不处理

        name_or_id = name_or_id.strip()

        # 如果是ID，需要找到对应的名称
        if len(name_or_id) == 32 and all(c in '0123456789abcdefABCDEF' for c in name_or_id):
            # 通过ID查找名称
            for name, browser_info in list(self._browser_cache.items()):
                if browser_info.get('id') == name_or_id:
                    del self._browser_cache[name]
                    logger.debug("从缓存中移除浏览器(通过ID): {} -> {}", name_or_id[:8], name)
                    break
        else:
            # 直接通过名称移除
            if name_or_id in self._browser_cache:
                del self._browser_cache[name_or_id]
                logger.debug("从缓存中移除浏览器(通过名称): {}", name_or_id)

    def _update_cache(self, browser_info: Dict[str, Any]) -> None:
        """更新缓存中的浏览器信息

        Args:
            browser_info (Dict[str, Any]): 新的浏览器信息
        """
        if not self._is_cache_valid():
            return  # 缓存无效时不更新

        name = browser_info.get('name', '').strip()
        browser_id = browser_info.get('id', '')

        if not name or not browser_id:
            return

        # 先移除旧的缓存项（可能名称已更改）
        for cached_name, cached_info in list(self._browser_cache.items()):
            if cached_info.get('id') == browser_id:
                if cached_name != name:  # 名称已更改
                    del self._browser_cache[cached_name]
                    logger.debug("移除旧缓存项(名称已更改): {} -> {}", cached_name, name)
                break

        # 添加新的缓存项
        self._browser_cache[name] = browser_info
        logger.debug("更新缓存中的浏览器: {}", name)

    def get_all_browsers(self, group_name_or_id: str = "", **filters) -> List[Dict[str, Any]]:
        """获取所有浏览器窗口（便捷方法）

        Args:
            group_name_or_id (str, optional): 分组名称或ID. Defaults to "".
            **filters: 其他筛选条件

        Returns:
            List[Dict[str, Any]]: 所有浏览器窗口列表

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当找不到对应的分组时
        """
        # 解析分组名称或ID为分组ID
        group_id = ""
        if group_name_or_id and group_name_or_id.strip():
            from .group_manager import GroupManager
            group_manager = GroupManager(self.base_url)
            group_id = group_manager._resolve_group_id(group_name_or_id)

        result = self._get_all_browsers(group_id, **filters)
        return result.get('data', [])

    def close_all_browsers(self) -> Dict[str, Any]:
        """关闭所有浏览器窗口
        
        Returns:
            Dict[str, Any]: 关闭结果
            
        Raises:
            requests.RequestException: 当网络请求失败时
        """
        logger.debug("开始关闭所有浏览器窗口")
        
        try:
            response = requests.post(
                f"{self.base_url}/browser/close/all",
                data=json.dumps({}),
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            logger.debug("所有浏览器窗口关闭完成")
            return result
            
        except requests.RequestException as e:
            logger.debug("关闭所有浏览器窗口异常: {}", str(e))
            raise

    def find_browser_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称查找浏览器窗口（使用缓存优化）

        Args:
            name (str): 浏览器窗口名称

        Returns:
            Optional[Dict[str, Any]]: 找到的浏览器信息，未找到返回None

        Raises:
            requests.RequestException: 当网络请求失败时
        """
        if not name or not name.strip():
            return None

        target_name = name.strip()
        logger.debug("开始根据名称查找浏览器窗口: {}", target_name)

        # 检查缓存是否有效
        if not self._is_cache_valid():
            logger.debug("缓存无效，刷新缓存")
            self._refresh_cache()

        # 从缓存中查找
        browser = self._browser_cache.get(target_name)
        if browser:
            logger.debug("从缓存中找到浏览器窗口，ID: {}", browser.get('id'))
            return browser

        # 缓存中没有找到，尝试刷新缓存再查找一次
        logger.debug("缓存中未找到，刷新缓存后重试")
        self._refresh_cache()
        browser = self._browser_cache.get(target_name)

        if browser:
            logger.debug("刷新缓存后找到浏览器窗口，ID: {}", browser.get('id'))
            return browser
        else:
            logger.debug("未找到名称为 {} 的浏览器窗口", target_name)
            return None

    def _resolve_browser_id(self, name_or_id: str) -> str:
        """解析浏览器标识符（名称或ID）为ID

        Args:
            name_or_id (str): 浏览器名称或ID

        Returns:
            str: 浏览器ID

        Raises:
            ValueError: 当找不到对应的浏览器时
            requests.RequestException: 当网络请求失败时
        """
        if not name_or_id or not name_or_id.strip():
            raise ValueError("浏览器名称或ID不能为空")

        name_or_id = name_or_id.strip()

        # 如果看起来像ID（32位十六进制字符），直接返回
        if len(name_or_id) == 32 and all(c in '0123456789abcdefABCDEF' for c in name_or_id):
            logger.debug("识别为浏览器ID: {}", name_or_id)
            return name_or_id

        # 否则当作名称处理，查找对应的ID
        logger.debug("识别为浏览器名称，开始查找ID: {}", name_or_id)
        browser = self.find_browser_by_name(name_or_id)
        if browser:
            browser_id = browser.get('id', '')
            logger.debug("找到浏览器ID: {}", browser_id)
            return browser_id
        else:
            raise ValueError(f"未找到名称为 '{name_or_id}' 的浏览器窗口")
