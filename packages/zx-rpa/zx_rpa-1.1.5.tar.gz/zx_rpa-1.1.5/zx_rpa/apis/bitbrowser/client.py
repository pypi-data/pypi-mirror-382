"""
比特浏览器统一客户端

整合浏览器窗口管理和分组管理功能，提供简洁的对外API
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from .browser_manager import BrowserManager
from .group_manager import GroupManager


class BitBrowserClient:
    """比特浏览器统一客户端"""

    def __init__(self, base_url: str = "http://127.0.0.1:54345"):
        """初始化比特浏览器客户端

        Args:
            base_url (str): 比特浏览器本地服务地址，默认为 http://127.0.0.1:54345
        """
        self.base_url = base_url
        self.browser_manager = BrowserManager(base_url)
        self.group_manager = GroupManager(base_url)
        logger.debug("初始化比特浏览器客户端，服务地址: {}", base_url)

    # ==================== 浏览器窗口管理方法 ====================

    def create_browser(self, name: str, remark: str = "", proxy_method: int = 2,
                      proxy_type: str = "noproxy", host: str = "", port: str = "",
                      proxy_username: str = "", proxy_password: str = "",
                      browser_fingerprint: Optional[Dict] = None, **kwargs) -> str:
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
            str: 创建的浏览器窗口ID

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当参数格式不正确时
        """
        result = self.browser_manager.create_browser(
            name=name, remark=remark, proxy_method=proxy_method,
            proxy_type=proxy_type, host=host, port=port,
            proxy_username=proxy_username, proxy_password=proxy_password,
            browser_fingerprint=browser_fingerprint, **kwargs
        )
        return result.get('data', {}).get('id', '')

    def update_browsers(self, browser_ids: List[str], **update_fields) -> bool:
        """批量更新浏览器窗口信息

        Args:
            browser_ids (List[str]): 要更新的窗口ID列表
            **update_fields: 要更新的字段，如 name, remark, browserFingerPrint 等

        Returns:
            bool: 更新是否成功

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当参数格式不正确时
        """
        result = self.browser_manager.update_browser_partial(browser_ids, **update_fields)
        return result.get('success', False)

    def open_browser(self, name_or_id: str) -> Dict[str, Any]:
        """打开浏览器窗口

        Args:
            name_or_id (str): 浏览器窗口名称或ID

        Returns:
            Dict[str, Any]: 打开结果，包含浏览器调试信息的字典，包含以下字段：
                - ws (str): WebSocket调试地址，用于DevTools协议连接
                - http (str): HTTP调试端口，格式为"IP:端口"
                - port (int): 调试端口号（从http字段提取）
                - coreVersion (str): 浏览器内核版本号
                - driver (str): ChromeDriver可执行文件的完整路径
                - seq (int): 窗口序列号
                - name (str): 窗口名称
                - remark (str): 窗口备注信息
                - pid (int): 浏览器进程ID

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当找不到对应的浏览器时
        """
        result = self.browser_manager.open_browser(name_or_id)
        data = result.get('data', {})

        # 从http字段提取端口号并添加到返回数据中
        if 'http' in data and data['http']:
            try:
                # 从 "127.0.0.1:53325" 格式中提取端口号
                http_str = str(data['http'])
                if ':' in http_str:
                    port = int(http_str.split(':')[-1])
                    data['port'] = port
            except (ValueError, IndexError):
                # 如果提取失败，不添加port字段
                pass

        return data

    def close_browser(self, name_or_id: str) -> bool:
        """关闭浏览器窗口

        Args:
            name_or_id (str): 浏览器窗口名称或ID

        Returns:
            bool: 关闭是否成功

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当找不到对应的浏览器时
        """
        result = self.browser_manager.close_browser(name_or_id)
        return result.get('success', False)

    def delete_browser(self, name_or_id: str) -> bool:
        """删除浏览器窗口

        Args:
            name_or_id (str): 浏览器窗口名称或ID

        Returns:
            bool: 删除是否成功

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当找不到对应的浏览器时
        """
        result = self.browser_manager.delete_browser(name_or_id)
        return result.get('success', False)

    def list_browsers(self, page: int = 0, page_size: int = 10, group_name_or_id: str = "",
                     get_all: bool = False, **filters) -> List[Dict[str, Any]]:
        """查询浏览器窗口列表
        https://doc2.bitbrowser.cn/jiekou/liu-lan-qi-jie-kou.html#%E5%88%86%E9%A1%B5%E8%8E%B7%E5%8F%96%E6%B5%8F%E8%A7%88%E5%99%A8%E7%AA%97%E5%8F%A3%E5%88%97%E8%A1%A8page-%E5%8F%82%E6%95%B0%E4%BB%8E-0-%E5%BC%80%E5%A7%8B0-%E6%98%AF%E7%AC%AC%E4%B8%80%E9%A1%B5%E7%9A%84%E6%95%B0%E6%8D%AE

        Args:
            page (int, optional): 页码，从0开始. Defaults to 0.
            page_size (int, optional): 每页数量，最大100. Defaults to 10.
            group_name_or_id (str, optional): 分组名称或ID，用于筛选特定分组的窗口. Defaults to "".
            get_all (bool, optional): 是否获取所有浏览器，忽略分页参数. Defaults to False.
            **filters: 其他筛选条件

        Returns:
            List[Dict[str, Any]]: 浏览器窗口列表，每个浏览器对象包含以下关键字段：
                - id (str): 浏览器窗口唯一标识符
                - seq (int): 窗口序列号
                - name (str): 窗口名称
                - remark (str): 备注信息
                - status (int): 窗口状态（0=关闭，1=打开）
                - proxyType (str): 代理类型（noproxy/http/https/socks5/ssh）
                - host (str): 代理主机地址
                - lastIp (str): 最后使用的IP地址
                - lastCountry (str): 最后使用的国家
                - coreVersion (str): 浏览器内核版本
                - os (str): 操作系统类型
                - createdTime (str): 创建时间
                - operTime (str): 最后操作时间

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当找不到对应的分组时
        """
        result = self.browser_manager.list_browsers(page, page_size, group_name_or_id, get_all, **filters)
        data = result.get('data', [])
        # API返回的data字段直接是列表，不是包含list字段的对象
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get('list', [])
        else:
            return []

    def close_all_browsers(self) -> bool:
        """关闭所有浏览器窗口

        Returns:
            bool: 关闭是否成功

        Raises:
            requests.RequestException: 当网络请求失败时
        """
        result = self.browser_manager.close_all_browsers()
        return result.get('success', False)

    # ==================== 分组管理方法 ====================

    def list_groups(self, page: int = 0, page_size: int = 10, all_groups: bool = True) -> List[Dict[str, Any]]:
        """查询分组列表

        Args:
            page (int, optional): 页码，从0开始. Defaults to 0.
            page_size (int, optional): 每页数量，最大100. Defaults to 10.
            all_groups (bool, optional): 是否获取权限范围内的所有分组. Defaults to True.

        Returns:
            List[Dict[str, Any]]: 分组列表

        Raises:
            requests.RequestException: 当网络请求失败时
        """
        result = self.group_manager.list_groups(page, page_size, all_groups)
        return result.get('data', {}).get('list', [])

    def add_group(self, group_name: str, sort_num: int = 0) -> str:
        """添加分组

        Args:
            group_name (str): 分组名称
            sort_num (int, optional): 排序数字. Defaults to 0.

        Returns:
            str: 创建的分组ID

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当参数格式不正确时
        """
        result = self.group_manager.add_group(group_name, sort_num)
        return result.get('data', {}).get('id', '')

    def edit_group(self, name_or_id: str, group_name: str, sort_num: int = 0) -> bool:
        """修改分组

        Args:
            name_or_id (str): 分组名称或ID
            group_name (str): 新的分组名称
            sort_num (int, optional): 新的排序数字. Defaults to 0.

        Returns:
            bool: 修改是否成功

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当参数格式不正确时或找不到对应的分组时
        """
        result = self.group_manager.edit_group(name_or_id, group_name, sort_num)
        return result.get('success', False)

    def delete_group(self, name_or_id: str) -> bool:
        """删除分组

        Args:
            name_or_id (str): 分组名称或ID

        Returns:
            bool: 删除是否成功

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当参数格式不正确时或找不到对应的分组时
        """
        result = self.group_manager.delete_group(name_or_id)
        return result.get('success', False)

    def get_group_detail(self, name_or_id: str) -> Dict[str, Any]:
        """获取分组详情

        Args:
            name_or_id (str): 分组名称或ID

        Returns:
            Dict[str, Any]: 分组详情数据

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当参数格式不正确时或找不到对应的分组时
        """
        result = self.group_manager.get_group_detail(name_or_id)
        return result.get('data', {})

    def get_all_groups(self) -> List[Dict[str, Any]]:
        """获取所有分组（便捷方法）

        Returns:
            List[Dict[str, Any]]: 所有分组的列表

        Raises:
            requests.RequestException: 当网络请求失败时
        """
        return self.group_manager.get_all_groups()

    def find_group_by_name(self, group_name: str) -> Optional[Dict[str, Any]]:
        """根据名称查找分组

        Args:
            group_name (str): 分组名称

        Returns:
            Optional[Dict[str, Any]]: 找到的分组信息，未找到返回None

        Raises:
            requests.RequestException: 当网络请求失败时
        """
        return self.group_manager.find_group_by_name(group_name)

    def get_group_id(self, name: str) -> Optional[str]:
        """根据名称获取分组ID

        Args:
            name (str): 分组名称

        Returns:
            Optional[str]: 分组ID，未找到返回None

        Raises:
            requests.RequestException: 当网络请求失败时
        """
        return self.group_manager.get_group_id(name)

    # ==================== 便捷组合方法 ====================

    def create_browser_with_group(self, name: str, group_name: str, **kwargs) -> str:
        """创建浏览器窗口并指定分组

        Args:
            name (str): 窗口名称
            group_name (str): 分组名称，如果不存在会自动创建
            **kwargs: 其他窗口配置参数

        Returns:
            str: 创建的浏览器窗口ID

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当参数格式不正确时
        """
        # 查找或创建分组
        group = self.find_group_by_name(group_name)
        if not group:
            group_id = self.add_group(group_name)
        else:
            group_id = group.get('id', '')

        # 创建浏览器窗口并指定分组
        kwargs['groupId'] = group_id
        return self.create_browser(name, **kwargs)

    def find_browser_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称查找浏览器窗口

        Args:
            name (str): 浏览器窗口名称

        Returns:
            Optional[Dict[str, Any]]: 找到的浏览器信息，未找到返回None

        Raises:
            requests.RequestException: 当网络请求失败时
        """
        return self.browser_manager.find_browser_by_name(name)

    def get_browser_id(self, name: str) -> Optional[str]:
        """根据名称获取浏览器窗口ID

        Args:
            name (str): 浏览器窗口名称

        Returns:
            Optional[str]: 浏览器ID，未找到返回None

        Raises:
            requests.RequestException: 当网络请求失败时
        """
        browser = self.find_browser_by_name(name)
        return browser.get('id') if browser else None

    def get_all_browsers(self, group_name_or_id: str = "", **filters) -> List[Dict[str, Any]]:
        """获取所有浏览器窗口

        Args:
            group_name_or_id (str, optional): 分组名称或ID. Defaults to "".
            **filters: 其他筛选条件

        Returns:
            List[Dict[str, Any]]: 所有浏览器窗口列表

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当找不到对应的分组时
        """
        return self.browser_manager.get_all_browsers(group_name_or_id, **filters)

    def refresh_browser_cache(self) -> None:
        """刷新浏览器缓存

        强制重新获取所有浏览器信息并更新缓存，用于确保数据最新。
        """
        self.browser_manager.refresh_cache()

    def clear_browser_cache(self) -> None:
        """清空浏览器缓存

        清空内存中的浏览器缓存，下次查找时会重新获取数据。
        """
        self.browser_manager.clear_cache()