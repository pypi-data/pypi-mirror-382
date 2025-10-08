"""
比特浏览器分组管理器

提供分组的查询、添加、修改、删除等功能
"""

import requests
import json
from typing import Dict, List, Optional, Any
from loguru import logger


class GroupManager:
    """比特浏览器分组管理器"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:54345"):
        """初始化分组管理器
        
        Args:
            base_url (str): 比特浏览器本地服务地址，默认为 http://127.0.0.1:54345
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {'Content-Type': 'application/json'}
        logger.debug("初始化比特浏览器分组管理器，服务地址: {}", base_url)
    
    def list_groups(self, page: int = 0, page_size: int = 10, all_groups: bool = True) -> Dict[str, Any]:
        """查询分组列表
        
        Args:
            page (int, optional): 页码，从0开始. Defaults to 0.
            page_size (int, optional): 每页数量，最大100. Defaults to 10.
            all_groups (bool, optional): 是否获取权限范围内的所有分组. Defaults to True.
            
        Returns:
            Dict[str, Any]: 分组列表数据
            
        Raises:
            requests.RequestException: 当网络请求失败时
        """
        logger.debug("开始查询分组列表，页码: {}, 每页: {}", page, page_size)
        
        json_data = {
            'page': page,
            'pageSize': min(page_size, 100),  # 限制最大100条
            'all': all_groups
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/group/list",
                data=json.dumps(json_data),
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            total_count = result.get('data', {}).get('total', 0)
            logger.debug("分组列表查询完成，总数: {}", total_count)
            return result
            
        except requests.RequestException as e:
            logger.debug("查询分组列表异常: {}", str(e))
            raise
    
    def add_group(self, group_name: str, sort_num: int = 0) -> Dict[str, Any]:
        """添加分组
        
        Args:
            group_name (str): 分组名称
            sort_num (int, optional): 排序数字. Defaults to 0.
            
        Returns:
            Dict[str, Any]: 添加结果，包含分组ID等信息
            
        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当参数格式不正确时
        """
        logger.debug("开始添加分组，名称: {}", group_name)
        
        if not group_name or not group_name.strip():
            raise ValueError("分组名称不能为空")
        
        json_data = {
            'groupName': group_name.strip(),
            'sortNum': sort_num
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/group/add",
                data=json.dumps(json_data),
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            logger.debug("分组添加完成，分组ID: {}", result.get('data', {}).get('id'))
            return result
            
        except requests.RequestException as e:
            logger.debug("添加分组异常: {}", str(e))
            raise
    
    def edit_group(self, name_or_id: str, group_name: str, sort_num: int = 0) -> Dict[str, Any]:
        """修改分组

        Args:
            name_or_id (str): 分组名称或ID
            group_name (str): 新的分组名称
            sort_num (int, optional): 新的排序数字. Defaults to 0.

        Returns:
            Dict[str, Any]: 修改结果

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当参数格式不正确时或找不到对应的分组时
        """
        # 解析为分组ID
        group_id = self._resolve_group_id(name_or_id)
        logger.debug("开始修改分组，ID: {}, 新名称: {}", group_id, group_name)
        
        if not group_id or not group_id.strip():
            raise ValueError("分组ID不能为空")
        if not group_name or not group_name.strip():
            raise ValueError("分组名称不能为空")
        
        json_data = {
            'id': group_id.strip(),
            'groupName': group_name.strip(),
            'sortNum': sort_num
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/group/edit",
                data=json.dumps(json_data),
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            logger.debug("分组修改完成")
            return result
            
        except requests.RequestException as e:
            logger.debug("修改分组异常: {}", str(e))
            raise
    
    def delete_group(self, name_or_id: str) -> Dict[str, Any]:
        """删除分组

        Args:
            name_or_id (str): 分组名称或ID

        Returns:
            Dict[str, Any]: 删除结果

        Raises:
            requests.RequestException: 当网络请求失败时
            ValueError: 当参数格式不正确时或找不到对应的分组时
        """
        # 解析为分组ID
        group_id = self._resolve_group_id(name_or_id)
        logger.debug("开始删除分组，ID: {}", group_id)
        
        json_data = {'id': group_id.strip()}
        
        try:
            response = requests.post(
                f"{self.base_url}/group/delete",
                data=json.dumps(json_data),
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            logger.debug("分组删除完成")
            return result
            
        except requests.RequestException as e:
            logger.debug("删除分组异常: {}", str(e))
            raise
    
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
        # 解析为分组ID
        group_id = self._resolve_group_id(name_or_id)
        logger.debug("开始获取分组详情，ID: {}", group_id)
        
        json_data = {'id': group_id.strip()}
        
        try:
            response = requests.post(
                f"{self.base_url}/group/detail",
                data=json.dumps(json_data),
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            logger.debug("分组详情获取完成")
            return result
            
        except requests.RequestException as e:
            logger.debug("获取分组详情异常: {}", str(e))
            raise
    
    def get_all_groups(self) -> List[Dict[str, Any]]:
        """获取所有分组（便捷方法）
        
        Returns:
            List[Dict[str, Any]]: 所有分组的列表
            
        Raises:
            requests.RequestException: 当网络请求失败时
        """
        logger.debug("开始获取所有分组")
        
        all_groups = []
        page = 0
        page_size = 100
        
        try:
            while True:
                result = self.list_groups(page=page, page_size=page_size, all_groups=True)
                data = result.get('data', {})
                groups = data.get('list', [])
                
                if not groups:
                    break
                
                all_groups.extend(groups)
                
                # 检查是否还有更多数据
                total = data.get('total', 0)
                if len(all_groups) >= total:
                    break
                
                page += 1
            
            logger.debug("获取所有分组完成，总数: {}", len(all_groups))
            return all_groups
            
        except requests.RequestException as e:
            logger.debug("获取所有分组异常: {}", str(e))
            raise
    
    def find_group_by_name(self, group_name: str) -> Optional[Dict[str, Any]]:
        """根据名称查找分组
        
        Args:
            group_name (str): 分组名称
            
        Returns:
            Optional[Dict[str, Any]]: 找到的分组信息，未找到返回None
            
        Raises:
            requests.RequestException: 当网络请求失败时
        """
        logger.debug("开始根据名称查找分组: {}", group_name)
        
        if not group_name or not group_name.strip():
            return None
        
        try:
            all_groups = self.get_all_groups()
            target_name = group_name.strip()
            
            for group in all_groups:
                if group.get('groupName') == target_name:
                    logger.debug("找到匹配的分组，ID: {}", group.get('id'))
                    return group
            
            logger.debug("未找到名称为 {} 的分组", target_name)
            return None
            
        except requests.RequestException as e:
            logger.debug("根据名称查找分组异常: {}", str(e))
            raise

    def _resolve_group_id(self, name_or_id: str) -> str:
        """解析分组标识符（名称或ID）为ID

        Args:
            name_or_id (str): 分组名称或ID

        Returns:
            str: 分组ID

        Raises:
            ValueError: 当找不到对应的分组时
            requests.RequestException: 当网络请求失败时
        """
        if not name_or_id or not name_or_id.strip():
            raise ValueError("分组名称或ID不能为空")

        name_or_id = name_or_id.strip()

        # 如果看起来像ID（32位十六进制字符），直接返回
        if len(name_or_id) == 32 and all(c in '0123456789abcdefABCDEF' for c in name_or_id):
            logger.debug("识别为分组ID: {}", name_or_id)
            return name_or_id

        # 否则当作名称处理，查找对应的ID
        logger.debug("识别为分组名称，开始查找ID: {}", name_or_id)
        group = self.find_group_by_name(name_or_id)
        if group:
            group_id = group.get('id', '')
            logger.debug("找到分组ID: {}", group_id)
            return group_id
        else:
            raise ValueError(f"未找到名称为 '{name_or_id}' 的分组")

    def get_group_id(self, name: str) -> Optional[str]:
        """根据名称获取分组ID

        Args:
            name (str): 分组名称

        Returns:
            Optional[str]: 分组ID，未找到返回None

        Raises:
            requests.RequestException: 当网络请求失败时
        """
        group = self.find_group_by_name(name)
        return group.get('id') if group else None
