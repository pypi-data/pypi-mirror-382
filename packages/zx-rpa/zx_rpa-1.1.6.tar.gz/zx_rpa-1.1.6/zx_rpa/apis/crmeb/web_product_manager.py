#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB商品其他管理器

提供商品相关的其他功能，如品牌管理、规格管理等。
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from .web_http_client import CrmebFrontendClient


class ProductOtherManager:
    """CRMEB商品其他管理器"""

    def __init__(self, main_url: str, username: str, password: str, timeout: int = 30):
        """初始化商品其他管理器

        Args:
            main_url: 完整的主域名URL（如：https://shop.shikejk.com 或 http://shop.example.com）
            username: 管理员用户名
            password: 管理员密码
            timeout: 请求超时时间（秒）
        """
        logger.debug("初始化CRMEB商品其他管理器")
        self._frontend_client = CrmebFrontendClient(main_url, username, password, timeout)
        logger.debug("商品其他管理器初始化完成")

    def get_brand_list(self, brand_name: str = "", pid: int = None) -> List[Dict[str, Any]]:
        """获取品牌列表

        Args:
            brand_name: 品牌名称过滤条件，空字符串表示获取所有品牌
            pid: 父品牌ID，用于获取子品牌列表

        Returns:
            品牌列表数据

        Example:
            >>> manager = ProductOtherManager("https://shop.shikejk.com", "admin", "password")
            >>> brands = manager.get_brand_list()  # 获取所有顶级品牌
            >>> sub_brands = manager.get_brand_list(pid=9)  # 获取ID为9的品牌的子品牌
            >>> print(brands[0])
            {
                "id": 1,
                "brand_name": "测试品牌",
                "brand_logo": "https://example.com/logo.jpg",
                "sort": 1,
                "is_show": 1,
                "add_time": "2025-01-01 10:00:00"
            }
        """
        filter_info = []
        if brand_name:
            filter_info.append(f"品牌名称: {brand_name}")
        if pid is not None:
            filter_info.append(f"父品牌ID: {pid}")

        logger.debug("获取品牌列表，过滤条件: {}", ", ".join(filter_info) if filter_info else "无")

        try:
            params = {}
            if brand_name:
                params["brand_name"] = brand_name
            if pid is not None:
                params["pid"] = pid

            response = self._frontend_client.make_request('GET', '/adminapi/product/brand', params=params)

            if response.get('status') == 200:
                data = response.get('data', {})
                brands = data.get('list', [])
                logger.debug("获取品牌列表成功，品牌数量: {}", len(brands))
                return brands
            else:
                error_msg = response.get('msg', '未知错误')
                raise Exception(f"获取品牌列表失败: {error_msg}")

        except Exception as e:
            logger.debug("获取品牌列表失败: {}", str(e))
            raise

    def get_brand_name_id_dict(self, include_hidden: bool = False) -> Dict[str, int]:
        """获取品牌名称到ID的映射字典
        
        Args:
            include_hidden: 是否包含隐藏的品牌，默认False只返回显示的品牌
            
        Returns:
            品牌名称到ID的字典 {品牌名称: id, ...}
            
        Example:
            >>> manager = ProductOtherManager("https://shop.shikejk.com", "admin", "password")
            >>> brand_dict = manager.get_brand_name_id_dict()
            >>> print(brand_dict)
            {
                "苹果": 1,
                "华为": 2,
                "小米": 3,
                "OPPO": 4
            }
        """
        logger.debug("获取品牌名称ID字典，包含隐藏品牌: {}", include_hidden)
        
        try:
            brands = self.get_brand_list()
            brand_dict = {}

            def add_brands_recursive(brand_list, level=0):
                """递归添加品牌和子品牌"""
                indent = "  " * level

                for brand in brand_list:
                    brand_name = brand.get('brand_name')
                    brand_id = brand.get('id')
                    is_show = brand.get('is_show', 1)

                    # 检查品牌名称和ID是否有效
                    if not brand_name or brand_id is None:
                        logger.debug("{}跳过无效品牌数据: {}", indent, brand)
                        continue

                    # 根据显示状态过滤
                    if not include_hidden and is_show != 1:
                        logger.debug("{}跳过隐藏品牌: {} (id: {})", indent, brand_name, brand_id)
                        continue

                    # 添加当前品牌
                    brand_dict[brand_name] = brand_id
                    logger.debug("{}添加品牌映射: {} -> {}", indent, brand_name, brand_id)

                    # 关键优化：检查返回数据中是否有children字段，有则表示有子品牌
                    has_children = 'children' in brand

                    if has_children:
                        logger.debug("{}品牌 {} 有children字段，获取子品牌", indent, brand_name)
                        try:
                            sub_brands = self.get_brand_list(pid=brand_id)
                            if sub_brands:
                                logger.debug("{}发现 {} 个子品牌，递归处理", indent, len(sub_brands))
                                add_brands_recursive(sub_brands, level + 1)
                            else:
                                logger.debug("{}品牌 {} 的children字段存在但没有子品牌", indent, brand_name)
                        except Exception as e:
                            logger.debug("{}获取子品牌失败: {}", indent, e)
                    else:
                        logger.debug("{}品牌 {} 没有children字段，跳过子品牌检查", indent, brand_name)

            # 开始递归处理
            add_brands_recursive(brands)

            logger.debug("品牌名称ID字典生成完成，包含 {} 个品牌（含子品牌）", len(brand_dict))
            return brand_dict

        except Exception as e:
            logger.debug("获取品牌名称ID字典失败: {}", str(e))
            raise





    def get_unit_list(self, name: str = "", page: int = 1, limit: int = 15) -> List[Dict[str, Any]]:
        """获取商品单位列表

        Args:
            name: 单位名称过滤条件，空字符串表示获取所有单位
            page: 页码，默认1
            limit: 每页数量，默认15

        Returns:
            单位列表数据

        Example:
            >>> manager = ProductOtherManager("https://shop.shikejk.com", "admin", "password")
            >>> units = manager.get_unit_list()
            >>> print(units[0])
            {
                "id": 1,
                "name": "个",
                "type": 0,
                "status": 1,
                "sort": 0,
                "add_time": 1699950438
            }
        """
        logger.debug("获取商品单位列表，过滤条件: {}", name or "无")

        try:
            params = {
                "page": page,
                "limit": limit,
                "name": name
            }
            response = self._frontend_client.make_request('GET', '/adminapi/product/unit', params=params)

            if response.get('status') == 200:
                data = response.get('data', {})
                units = data.get('list', [])
                logger.debug("获取商品单位列表成功，单位数量: {}", len(units))
                return units
            else:
                error_msg = response.get('msg', '未知错误')
                raise Exception(f"获取商品单位列表失败: {error_msg}")

        except Exception as e:
            logger.debug("获取商品单位列表失败: {}", str(e))
            raise

    def get_unit_name_id_dict(self, include_disabled: bool = False) -> Dict[str, int]:
        """获取商品单位名称到ID的映射字典

        Args:
            include_disabled: 是否包含禁用的单位，默认False只返回启用的单位

        Returns:
            单位名称到ID的字典 {单位名称: id, ...}

        Example:
            >>> manager = ProductOtherManager("https://shop.shikejk.com", "admin", "password")
            >>> unit_dict = manager.get_unit_name_id_dict()
            >>> print(unit_dict)
            {
                "个": 1,
                "瓶": 2,
                "盒": 3,
                "件": 4,
                "人购买": 5,
                "万": 6
            }
        """
        logger.debug("获取商品单位名称ID字典，包含禁用单位: {}", include_disabled)

        try:
            # 获取所有单位（设置较大的limit确保获取全部）
            units = self.get_unit_list(limit=1000)
            unit_dict = {}

            for unit in units:
                unit_name = unit.get('name')
                unit_id = unit.get('id')
                status = unit.get('status', 1)
                is_del = unit.get('is_del', 0)

                # 检查单位名称和ID是否有效
                if not unit_name or unit_id is None:
                    logger.debug("跳过无效单位数据: {}", unit)
                    continue

                # 跳过已删除的单位
                if is_del == 1:
                    logger.debug("跳过已删除单位: {} (id: {})", unit_name, unit_id)
                    continue

                # 根据状态过滤
                if not include_disabled and status != 1:
                    logger.debug("跳过禁用单位: {} (id: {})", unit_name, unit_id)
                    continue

                unit_dict[unit_name] = unit_id
                logger.debug("添加单位映射: {} -> {}", unit_name, unit_id)

            logger.debug("商品单位名称ID字典生成完成，包含 {} 个单位", len(unit_dict))
            return unit_dict

        except Exception as e:
            logger.debug("获取商品单位名称ID字典失败: {}", str(e))
            raise

    def get_label_list(self, label_cate: str = "", page: int = 1, limit: int = 15) -> List[Dict[str, Any]]:
        """获取商品标签列表

        Args:
            label_cate: 标签分类过滤条件，空字符串表示获取所有标签
            page: 页码，默认1
            limit: 每页数量，默认15

        Returns:
            标签列表数据

        Example:
            >>> manager = ProductOtherManager("https://shop.shikejk.com", "admin", "password")
            >>> labels = manager.get_label_list()
            >>> print(labels[0])
            {
                "id": 26,
                "label_name": "玩具搭配",
                "label_cate": 1,
                "is_show": 1,
                "status": 1,
                "color": "#e93323"
            }
        """
        logger.debug("获取商品标签列表，过滤条件: {}", label_cate or "无")

        try:
            params = {
                "page": page,
                "limit": limit,
                "label_cate": label_cate
            }
            response = self._frontend_client.make_request('GET', '/adminapi/product/label', params=params)

            if response.get('status') == 200:
                data = response.get('data', {})
                labels = data.get('list', [])
                logger.debug("获取商品标签列表成功，标签数量: {}", len(labels))
                return labels
            else:
                error_msg = response.get('msg', '未知错误')
                raise Exception(f"获取商品标签列表失败: {error_msg}")

        except Exception as e:
            logger.debug("获取商品标签列表失败: {}", str(e))
            raise

    def get_label_name_id_dict(self, include_hidden: bool = False) -> Dict[str, int]:
        """获取商品标签名称到ID的映射字典

        Args:
            include_hidden: 是否包含隐藏的标签，默认False只返回显示的标签

        Returns:
            标签名称到ID的字典 {标签名称: id, ...}

        Example:
            >>> manager = ProductOtherManager("https://shop.shikejk.com", "admin", "password")
            >>> label_dict = manager.get_label_name_id_dict()
            >>> print(label_dict)
            {
                "玩具搭配": 26,
                "后庭开发-赠送润滑液": 25,
                "情侣互动-赠送润滑液": 24,
                "优品推荐": 5
            }
        """
        logger.debug("获取商品标签名称ID字典，包含隐藏标签: {}", include_hidden)

        try:
            # 获取所有标签（设置较大的limit确保获取全部）
            labels = self.get_label_list(limit=1000)
            label_dict = {}

            for label in labels:
                label_name = label.get('label_name')
                label_id = label.get('id')
                is_show = label.get('is_show', 1)
                status = label.get('status', 1)

                # 检查标签名称和ID是否有效
                if not label_name or label_id is None:
                    logger.debug("跳过无效标签数据: {}", label)
                    continue

                # 根据显示状态过滤
                if not include_hidden and (is_show != 1 or status != 1):
                    logger.debug("跳过隐藏标签: {} (id: {})", label_name, label_id)
                    continue

                label_dict[label_name] = label_id
                logger.debug("添加标签映射: {} -> {}", label_name, label_id)

            logger.debug("商品标签名称ID字典生成完成，包含 {} 个标签", len(label_dict))
            return label_dict

        except Exception as e:
            logger.debug("获取商品标签名称ID字典失败: {}", str(e))
            raise

    def get_ensure_list(self, name: str = "", page: int = 1, limit: int = 15) -> List[Dict[str, Any]]:
        """获取保障服务列表

        Args:
            name: 服务名称过滤条件，空字符串表示获取所有服务
            page: 页码，默认1
            limit: 每页数量，默认15

        Returns:
            保障服务列表数据

        Example:
            >>> manager = ProductOtherManager("https://shop.shikejk.com", "admin", "password")
            >>> ensures = manager.get_ensure_list()
            >>> print(ensures[0])
            {
                "id": 9,
                "name": "私密发货",
                "desc": "包装上只写生活用品，请您放心收件",
                "status": 1,
                "sort": 60
            }
        """
        logger.debug("获取保障服务列表，过滤条件: {}", name or "无")

        try:
            params = {
                "page": page,
                "limit": limit,
                "name": name
            }
            response = self._frontend_client.make_request('GET', '/adminapi/product/ensure', params=params)

            if response.get('status') == 200:
                data = response.get('data', {})
                ensures = data.get('list', [])
                logger.debug("获取保障服务列表成功，服务数量: {}", len(ensures))
                return ensures
            else:
                error_msg = response.get('msg', '未知错误')
                raise Exception(f"获取保障服务列表失败: {error_msg}")

        except Exception as e:
            logger.debug("获取保障服务列表失败: {}", str(e))
            raise

    def get_ensure_name_id_dict(self, include_disabled: bool = False) -> Dict[str, int]:
        """获取保障服务名称到ID的映射字典

        Args:
            include_disabled: 是否包含禁用的服务，默认False只返回启用的服务

        Returns:
            保障服务名称到ID的字典 {服务名称: id, ...}

        Example:
            >>> manager = ProductOtherManager("https://shop.shikejk.com", "admin", "password")
            >>> ensure_dict = manager.get_ensure_name_id_dict()
            >>> print(ensure_dict)
            {
                "私密发货": 9,
                "买贵退差": 8,
                "支持试用": 7,
                "正品认证": 6
            }
        """
        logger.debug("获取保障服务名称ID字典，包含禁用服务: {}", include_disabled)

        try:
            # 获取所有保障服务（设置较大的limit确保获取全部）
            ensures = self.get_ensure_list(limit=1000)
            ensure_dict = {}

            for ensure in ensures:
                ensure_name = ensure.get('name')
                ensure_id = ensure.get('id')
                status = ensure.get('status', 1)

                # 检查服务名称和ID是否有效
                if not ensure_name or ensure_id is None:
                    logger.debug("跳过无效保障服务数据: {}", ensure)
                    continue

                # 根据状态过滤
                if not include_disabled and status != 1:
                    logger.debug("跳过禁用保障服务: {} (id: {})", ensure_name, ensure_id)
                    continue

                ensure_dict[ensure_name] = ensure_id
                logger.debug("添加保障服务映射: {} -> {}", ensure_name, ensure_id)

            logger.debug("保障服务名称ID字典生成完成，包含 {} 个服务", len(ensure_dict))
            return ensure_dict

        except Exception as e:
            logger.debug("获取保障服务名称ID字典失败: {}", str(e))
            raise

    def close(self):
        """关闭商品其他管理器"""
        logger.debug("关闭商品其他管理器")
        if hasattr(self, '_frontend_client'):
            self._frontend_client.close()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        self.close()
