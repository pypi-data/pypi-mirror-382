#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB分类管理模块

提供商品分类相关的API操作功能。
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from .api_client import CrmebApiClient


class CategoryManager:
    """CRMEB分类管理器"""

    def __init__(self, main_url: str, appid: str, appsecret: str, timeout: int = 30):
        """初始化分类管理器
        
        Args:
            main_url: CRMEB主域名
            appid: 应用ID
            appsecret: 应用密钥
            timeout: 请求超时时间（秒）
        """
        logger.debug("初始化CRMEB分类管理器")
        self._api_client = CrmebApiClient(main_url, appid, appsecret, timeout)
        logger.debug("分类管理器初始化完成")

    def get_category_list(self) -> List[Dict[str, Any]]:
        """获取分类列表
        
        Returns:
            分类列表数据
            
        Example:
            >>> manager = CategoryManager(url, appid, secret)
            >>> categories = manager.get_category_list()
            >>> print(categories[0])
            {
                "id": 11,
                "cate_name": "分类12",
                "pid": 9,
                "pic": "http://dummyimage.com/400x400",
                "big_pic": "http://dummyimage.com/400x400",
                "sort": 54,
                "is_show": 1,
                "add_time": "2022-07-20 14:24:14"
            }
        """
        logger.debug("获取商品分类列表")
        
        try:
            response = self._api_client.make_request('GET', '/outapi/category/list')
            categories = response.get('data', [])
            
            logger.debug("获取分类列表成功，分类数量: {}", len(categories))
            return categories
            
        except Exception as e:
            logger.debug("获取分类列表失败: {}", str(e))
            raise

    def get_category_name_id_dict(self, include_hidden: bool = False) -> Dict[str, int]:
        """获取分类名称到ID的映射字典
        
        Args:
            include_hidden: 是否包含隐藏的分类，默认False只返回显示的分类
            
        Returns:
            分类名称到ID的字典 {分类名称: id, ...}
            
        Example:
            >>> manager = CategoryManager(url, appid, secret)
            >>> name_id_dict = manager.get_category_name_id_dict()
            >>> print(name_id_dict)
            {
                "分类12": 11,
                "分类2": 4,
                "分类1": 5,
                "分类3": 6,
                "分类4": 7,
                "分类12342": 9,
                "分类10": 10,
                "办公用品": 1,
                "办公用品1": 2,
                "测试": 3
            }
        """
        logger.debug("获取分类名称ID字典，包含隐藏分类: {}", include_hidden)
        
        try:
            categories = self.get_category_list()
            name_id_dict = {}
            
            for category in categories:
                cate_name = category.get('cate_name')
                cate_id = category.get('id')
                is_show = category.get('is_show', 1)
                
                # 检查分类名称和ID是否有效
                if not cate_name or cate_id is None:
                    logger.debug("跳过无效分类数据: {}", category)
                    continue
                
                # 根据显示状态过滤
                if not include_hidden and is_show != 1:
                    logger.debug("跳过隐藏分类: {} (id: {})", cate_name, cate_id)
                    continue
                
                name_id_dict[cate_name] = cate_id
                logger.debug("添加分类映射: {} -> {}", cate_name, cate_id)
            
            logger.debug("分类名称ID字典生成完成，包含 {} 个分类", len(name_id_dict))
            return name_id_dict
            
        except Exception as e:
            logger.debug("获取分类名称ID字典失败: {}", str(e))
            raise



    def close(self):
        """关闭分类管理器"""
        logger.debug("关闭分类管理器")
        if hasattr(self, '_api_client'):
            self._api_client.close()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        self.close()
