#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB前端管理器

专门处理前端管理后台的所有功能，包括品牌、单位、标签、保障服务等。
与API客户端完全分离，避免参数混淆。
"""

from typing import Dict
from loguru import logger

from .web_product_manager import ProductOtherManager


class CrmebWebClient:
    """CRMEB前端管理器
    
    专门处理前端管理后台功能，初始化时传入前端认证信息，
    之后所有方法都不需要重复传入认证参数。
    """

    def __init__(self, main_url: str, username: str, password: str, timeout: int = 30):
        """初始化前端管理器
        
        Args:
            main_url: 完整的主域名URL（如：https://shop.shikejk.com 或 http://shop.example.com）
            username: 管理员用户名
            password: 管理员密码
            timeout: 请求超时时间（秒）
        """
        logger.debug("初始化CRMEB前端管理器")
        
        self.main_url = main_url
        self.username = username
        self.password = password
        self.timeout = timeout
        
        # 初始化商品其他管理器
        self._product_other_manager = None
        
        logger.debug("CRMEB前端管理器初始化完成")

    def _get_product_other_manager(self) -> ProductOtherManager:
        """获取商品其他管理器实例（懒加载）"""
        if self._product_other_manager is None:
            self._product_other_manager = ProductOtherManager(
                self.main_url, 
                self.username, 
                self.password, 
                self.timeout
            )
        return self._product_other_manager

    # ==================== 品牌管理 ====================

    def get_brand_name_id_dict(self, include_hidden: bool = False) -> Dict[str, int]:
        """获取品牌名称到ID的映射字典
        
        Args:
            include_hidden: 是否包含隐藏的品牌，默认False只返回显示的品牌
            
        Returns:
            品牌名称到ID的字典 {品牌名称: id, ...}
            
        Example:
            >>> manager = CrmebFrontendManager("https://shop.shikejk.com", "admin", "password")
            >>> brand_dict = manager.get_brand_name_id_dict()
            >>> print(brand_dict)
            {'杜蕾斯': 38, '冈本': 37, '杰士邦': 40}
        """
        with self._get_product_other_manager() as manager:
            return manager.get_brand_name_id_dict(include_hidden)

    # ==================== 商品单位管理 ====================

    def get_unit_name_id_dict(self, include_disabled: bool = False) -> Dict[str, int]:
        """获取商品单位名称到ID的映射字典
        
        Args:
            include_disabled: 是否包含禁用的单位，默认False只返回启用的单位
            
        Returns:
            单位名称到ID的字典 {单位名称: id, ...}
            
        Example:
            >>> manager = CrmebFrontendManager("https://shop.shikejk.com", "admin", "password")
            >>> unit_dict = manager.get_unit_name_id_dict()
            >>> print(unit_dict)
            {'个': 1, '瓶': 2, '盒': 3, '件': 4}
        """
        with self._get_product_other_manager() as manager:
            return manager.get_unit_name_id_dict(include_disabled)

    # ==================== 商品标签管理 ====================

    def get_label_name_id_dict(self, include_hidden: bool = False) -> Dict[str, int]:
        """获取商品标签名称到ID的映射字典
        
        Args:
            include_hidden: 是否包含隐藏的标签，默认False只返回显示的标签
            
        Returns:
            标签名称到ID的字典 {标签名称: id, ...}
            
        Example:
            >>> manager = CrmebFrontendManager("https://shop.shikejk.com", "admin", "password")
            >>> label_dict = manager.get_label_name_id_dict()
            >>> print(label_dict)
            {'玩具搭配': 26, '优品推荐': 5, '热卖单品': 1}
        """
        with self._get_product_other_manager() as manager:
            return manager.get_label_name_id_dict(include_hidden)

    # ==================== 保障服务管理 ====================

    def get_ensure_name_id_dict(self, include_disabled: bool = False) -> Dict[str, int]:
        """获取保障服务名称到ID的映射字典
        
        Args:
            include_disabled: 是否包含禁用的服务，默认False只返回启用的服务
            
        Returns:
            保障服务名称到ID的字典 {服务名称: id, ...}
            
        Example:
            >>> manager = CrmebFrontendManager("https://shop.shikejk.com", "admin", "password")
            >>> ensure_dict = manager.get_ensure_name_id_dict()
            >>> print(ensure_dict)
            {'私密发货': 9, '买贵退差': 8, '支持试用': 7, '正品认证': 6}
        """
        with self._get_product_other_manager() as manager:
            return manager.get_ensure_name_id_dict(include_disabled)

    # ==================== 批量获取所有字典 ====================

    def get_all_dicts(self, include_hidden: bool = False, include_disabled: bool = False) -> Dict[str, Dict[str, int]]:
        """批量获取所有字典
        
        Args:
            include_hidden: 是否包含隐藏项（品牌、标签）
            include_disabled: 是否包含禁用项（单位、保障服务）
            
        Returns:
            包含所有字典的字典 {
                'brands': {品牌名称: id, ...},
                'units': {单位名称: id, ...},
                'labels': {标签名称: id, ...},
                'ensures': {服务名称: id, ...}
            }
            
        Example:
            >>> manager = CrmebFrontendManager("https://shop.shikejk.com", "admin", "password")
            >>> all_dicts = manager.get_all_dicts()
            >>> print(f"品牌数量: {len(all_dicts['brands'])}")
            >>> print(f"单位数量: {len(all_dicts['units'])}")
        """
        with self._get_product_other_manager() as manager:
            return {
                'brands': manager.get_brand_name_id_dict(include_hidden),
                'units': manager.get_unit_name_id_dict(include_disabled),
                'labels': manager.get_label_name_id_dict(include_hidden),
                'ensures': manager.get_ensure_name_id_dict(include_disabled)
            }

    # ==================== 资源管理 ====================

    def close(self):
        """关闭前端管理器"""
        logger.debug("关闭CRMEB前端管理器")
        if self._product_other_manager is not None:
            self._product_other_manager.close()
            self._product_other_manager = None

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        self.close()
