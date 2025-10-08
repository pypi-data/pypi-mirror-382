#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB商品管理模块

提供CRMEB平台的商品管理功能实现。
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from .api_client import CrmebApiClient
from .product_template import ProductTemplate
from .unified_converter import UnifiedProductConverter


class ProductManager:
    """CRMEB商品管理器"""

    def __init__(self, main_url: str, appid: str, appsecret: str, timeout: int = 30):
        """初始化商品管理器
        
        Args:
            main_url: CRMEB主域名
            appid: 应用ID
            appsecret: 应用密钥
            timeout: 请求超时时间（秒）
        """
        logger.debug("初始化CRMEB商品管理器")
        self._api_client = CrmebApiClient(main_url, appid, appsecret, timeout)
        logger.debug("CRMEB商品管理器初始化完成")

    def update_product_status(self, product_id: int, is_show: int) -> Dict:
        """更新商品状态
        
        Args:
            product_id: 商品ID
            is_show: 上架状态，1表示上架展示，0表示下架隐藏
            
        Returns:
            API响应数据，包含status和msg字段
        """
        logger.debug("更新商品状态，商品ID: {}，状态: {}", product_id, is_show)
        
        # 参数验证
        if not isinstance(product_id, int) or product_id <= 0:
            logger.debug("商品ID无效: {}", product_id)
            raise ValueError("商品ID必须是正整数")
        
        if is_show not in [0, 1]:
            logger.debug("商品状态参数无效: {}", is_show)
            raise ValueError("商品状态参数必须是0（下架）或1（上架）")
        
        # 构建API端点
        endpoint = f"/outapi/product/set_show/{product_id}/{is_show}"
        
        try:
            result = self._api_client.make_request("PUT", endpoint)
            
            status_text = "上架" if is_show == 1 else "下架"
            logger.debug("商品状态更新成功，商品ID: {}，状态: {}", product_id, status_text)
            
            return result
            
        except Exception as e:
            logger.debug("更新商品状态失败，商品ID: {}，错误: {}", product_id, str(e))
            raise

    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Dict:
        """更新商品

        Args:
            product_id: 商品ID
            product_data: 商品数据

        Returns:
            API响应数据
        """
        logger.debug("开始更新商品，商品ID: {}, 传入字段数量: {}", product_id, len(product_data))
        logger.debug("更新商品原始数据: {}", product_data)

        # 设置商品ID
        product_data['id'] = product_id

        # 使用模板确保数据完整性
        complete_data = ProductTemplate.create_product_data(product_data)

        # 修复数据类型问题
        complete_data = self._fix_data_types(complete_data, product_id)
        logger.debug("模板处理后的完整更新数据: {}", complete_data)

        try:
            response = self._api_client.make_request('POST', '/outapi/product', complete_data)
            logger.debug("更新商品API响应: {}", response)

            if response.get('status') == 200:
                product_name = complete_data.get('store_name', '未知商品')
                logger.debug("商品更新成功，商品名称: {}", product_name)
            else:
                logger.warning("商品更新失败，响应: {}", response)

            return response

        except Exception as e:
            logger.debug("更新商品时发生错误: {}", str(e))
            raise

    def get_product_data(self, product_id: int) -> Dict[str, Any]:
        """获取商品详情

        Args:
            product_id: 商品ID

        Returns:
            商品详情数据
        """
        logger.debug("开始获取商品详情，商品ID: {}", product_id)

        try:
            response = self._api_client.make_request('GET', f'/outapi/product/{product_id}')
            logger.debug("获取商品API响应: {}", response)

            if response.get('status') == 200:
                # API返回的数据结构是 {'status': 200, 'data': {'productInfo': {...}}}
                data = response.get('data', {})
                product_info = data.get('productInfo', {})
                if product_info:
                    product_name = product_info.get('store_name', '未知商品')
                    logger.debug("商品详情获取成功，商品名称: {}", product_name)
                    logger.debug("获取到的完整商品数据: {}", product_info)
                    return product_info
                else:
                    logger.warning("商品详情数据为空，响应: {}", response)
                    return response
            else:
                logger.warning("商品详情获取失败，响应: {}", response)
                return response

        except Exception as e:
            logger.debug("获取商品详情时发生错误: {}", str(e))
            raise

    def create_product(self, product_data: Dict[str, Any]) -> Dict:
        """创建商品

        Args:
            product_data: 商品数据字典，会与默认模板合并

        Returns:
            API响应数据，包含status和msg字段
        """
        logger.debug("开始创建商品，传入字段数量: {}", len(product_data))
        logger.debug("创建商品原始数据: {}", product_data)

        # 使用模板创建完整的商品数据
        full_product_data = ProductTemplate.create_product_data(product_data)
        logger.debug("模板处理后的完整商品数据: {}", full_product_data)

        # 验证必填字段
        missing_fields = ProductTemplate.validate_required_fields(full_product_data)
        if missing_fields:
            error_msg = f"商品数据缺失必填字段: {missing_fields}"
            logger.debug(error_msg)
            raise ValueError(error_msg)

        # 调用API创建商品
        try:
            result = self._api_client.make_request("POST", "/outapi/product", full_product_data)
            logger.debug("创建商品API响应: {}", result)

            logger.debug("商品创建成功，商品名称: {}", full_product_data.get('store_name', '未知'))
            return result

        except Exception as e:
            logger.debug("创建商品失败，错误: {}", str(e))
            raise

    def create_product_unified(self, unified_data: Dict[str, Any],
                              spec_columns: Optional[List[str]] = None,
                              base_field_mapping: Optional[Dict[str, str]] = None,
                              attr_mapping: Optional[Dict[str, str]] = None,
                              reverse_spec_order: bool = False) -> Dict:
        """使用统一格式创建商品

        Args:
            unified_data: 统一格式的商品数据
            spec_columns: 规格列名列表
            base_field_mapping: 基础字段映射
            attr_mapping: 属性字段映射
            reverse_spec_order: 是否颠倒规格值顺序，用于解决上传后顺序颠倒的问题

        Returns:
            API响应数据
        """
        logger.debug("使用统一格式创建商品，SKU数量: {}", len(unified_data.get('skus', [])))
        logger.debug("统一格式商品数据: {}", unified_data)

        # 使用统一格式转换器转换数据
        converter = UnifiedProductConverter()
        product_data = converter.convert(unified_data, spec_columns, base_field_mapping, attr_mapping, reverse_spec_order)

        logger.debug("转换后的CRMEB格式数据: {}", product_data)

        # 创建商品
        return self.create_product(product_data)

    def update_product_unified(self, product_id: int, unified_data: Dict[str, Any],
                              spec_columns: Optional[List[str]] = None,
                              base_field_mapping: Optional[Dict[str, str]] = None,
                              attr_mapping: Optional[Dict[str, str]] = None,
                              reverse_spec_order: bool = False) -> Dict:
        """使用统一格式更新商品

        Args:
            product_id: 商品ID
            unified_data: 统一格式的商品数据
            spec_columns: 规格列名列表
            base_field_mapping: 基础字段映射
            attr_mapping: 属性字段映射
            reverse_spec_order: 是否颠倒规格值顺序，用于解决上传后顺序颠倒的问题

        Returns:
            API响应数据
        """
        logger.debug("使用统一格式更新商品，商品ID: {}, SKU数量: {}", product_id, len(unified_data.get('skus', [])))
        logger.debug("统一格式商品数据: {}", unified_data)

        # 使用统一格式转换器转换数据
        converter = UnifiedProductConverter()
        product_data = converter.convert(unified_data, spec_columns, base_field_mapping, attr_mapping, reverse_spec_order)

        logger.debug("转换后的CRMEB格式数据: {}", product_data)

        # 更新商品
        return self.update_product(product_id, product_data)

    def partial_update_product(self, product_id: int, update_data: Dict[str, Any]) -> Dict:
        """部分更新商品

        Args:
            product_id: 商品ID
            update_data: 统一格式的更新数据

        Returns:
            API响应数据
        """
        logger.debug("部分更新商品，商品ID: {}, 更新字段数: {}", product_id, len(update_data))
        logger.debug("部分更新数据: {}", update_data)

        # 1. 获取原始商品数据
        original_data = self.get_product_data(product_id)
        if not original_data or 'id' not in original_data:
            raise ValueError(f"商品ID {product_id} 不存在或获取失败")

        logger.debug("获取到的原始商品数据: {}", original_data)

        # 2. 转换原始数据为统一格式
        unified_original = self._convert_to_unified_format(original_data)
        logger.debug("转换为统一格式的原始数据: {}", unified_original)

        # 3. 合并更新数据
        merged_data = self._merge_update_data(unified_original, update_data)
        logger.debug("合并后的统一格式数据: {}", merged_data)

        # 4. 使用统一格式更新商品，传递原始规格顺序
        original_spec_order = merged_data.pop('_original_spec_order', None)
        if original_spec_order:
            logger.debug("使用原始规格顺序: {}", original_spec_order)
            return self.update_product_unified(product_id, merged_data, spec_columns=original_spec_order)
        else:
            return self.update_product_unified(product_id, merged_data)

    def _convert_to_unified_format(self, crmeb_data: Dict[str, Any]) -> Dict[str, Any]:
        """将CRMEB格式数据转换为统一格式"""
        logger.debug("转换CRMEB数据为统一格式")

        # 提取基础字段 - 从ProductTemplate获取完整的基础字段列表
        unified_data = {}

        # 排除SKU相关字段，提取所有基础商品字段
        sku_related_fields = {'items', 'attrs', 'attr', 'spec_type'}

        # 从ProductTemplate获取所有字段，排除SKU相关字段
        from .product_template import ProductTemplate
        template_fields = set(ProductTemplate.DEFAULT_TEMPLATE.keys()) - sku_related_fields

        for field in template_fields:
            if field in crmeb_data:
                unified_data[field] = crmeb_data[field]
                logger.debug("提取基础字段: {} = {}", field, crmeb_data[field])

        # 提取原始规格顺序信息
        original_spec_order = []
        items = crmeb_data.get('items', [])
        if items:
            original_spec_order = [item.get('value', '') for item in items if item.get('value')]
            logger.debug("提取原始规格顺序: {}", original_spec_order)
            # 将规格顺序信息保存到统一数据中
            unified_data['_original_spec_order'] = original_spec_order

        # 转换SKU数据
        attrs = crmeb_data.get('attrs', [])
        if attrs:
            skus = []
            for attr in attrs:
                sku = {
                    'code': attr.get('code', ''),
                    'price': attr.get('price', 0),
                    'stock': attr.get('stock', 0),
                    'cost': attr.get('cost', 0),
                    'ot_price': attr.get('ot_price', 0),
                    'pic': attr.get('pic', ''),
                    'weight': attr.get('weight', 0),
                    'volume': attr.get('volume', 0),
                    'brokerage': attr.get('brokerage', 0),
                    'brokerage_two': attr.get('brokerage_two', 0),
                    'vip_price': attr.get('vip_price', 0)
                }

                # 添加规格字段
                detail = attr.get('detail', {})
                for spec_name, spec_value in detail.items():
                    sku[spec_name] = spec_value

                skus.append(sku)

            unified_data['skus'] = skus

        return unified_data

    def _merge_update_data(self, original: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """合并原始数据和更新数据，实现交集更新逻辑"""
        logger.debug("合并原始数据和更新数据")

        merged = original.copy()

        # 更新基础字段
        for key, value in update.items():
            if key != 'skus' and not key.startswith('_'):  # 排除内部字段
                merged[key] = value
                logger.debug("更新基础字段: {} = {}", key, value)

        # 更新SKU数据 - 实现交集更新逻辑
        if 'skus' in update:
            update_skus = update['skus']
            original_skus = merged.get('skus', [])

            # 创建code到SKU的映射
            original_sku_map = {sku.get('code'): sku for sku in original_skus if sku.get('code')}
            update_sku_codes = {sku.get('code') for sku in update_skus if sku.get('code')}

            logger.debug("原始SKU编号: {}", set(original_sku_map.keys()))
            logger.debug("更新SKU编号: {}", update_sku_codes)

            # 计算交集 - 只保留两边都存在的SKU
            intersection_codes = set(original_sku_map.keys()) & update_sku_codes
            logger.debug("交集SKU编号: {}", intersection_codes)

            # 过滤原始SKU，只保留交集中的SKU
            filtered_original_skus = [sku for sku in original_skus if sku.get('code') in intersection_codes]

            # 重新创建映射
            sku_map = {sku.get('code'): sku for sku in filtered_original_skus}

            # 更新交集中的SKU
            for update_sku in update_skus:
                sku_code = update_sku.get('code')
                if not sku_code:
                    logger.warning("更新SKU缺少code字段，跳过: {}", update_sku)
                    continue

                if sku_code in sku_map:
                    # 更新现有SKU
                    original_sku = sku_map[sku_code]
                    for field, value in update_sku.items():
                        if field != 'code':  # code字段不更新
                            original_sku[field] = value
                            logger.debug("更新SKU {} 字段: {} = {}", sku_code, field, value)
                else:
                    logger.warning("SKU code {} 不在交集中，跳过更新", sku_code)

            # 更新合并数据中的SKU列表
            merged['skus'] = filtered_original_skus
            logger.debug("最终保留的SKU数量: {}", len(filtered_original_skus))

        return merged

    def _fix_data_types(self, data: Dict[str, Any], product_id: int) -> Dict[str, Any]:
        """修复数据类型问题，确保API调用成功

        主要修复：
        1. 确保ID是整数
        2. 处理复杂对象数组（如store_label_id）- 这是导致"Array to string conversion"错误的根本原因
        3. 基本的布尔值转换
        """
        logger.debug("修复数据类型问题")

        # 1. 确保ID字段是整数类型
        data['id'] = int(product_id)

        # 2. 处理复杂对象数组 - 关键修复！
        # 这是导致"Array to string conversion"错误的根本原因
        for field, value in data.items():
            if (isinstance(value, list) and value and
                isinstance(value[0], dict) and 'id' in value[0]):
                # 将复杂对象数组转换为简单ID数组
                try:
                    data[field] = [int(item['id']) for item in value if isinstance(item, dict) and 'id' in item]
                    logger.debug("字段 {} 的复杂对象数组已转换为ID数组: {}", field, data[field])
                except (ValueError, TypeError, KeyError):
                    logger.warning("字段 {} 的复杂对象数组转换失败，使用空数组", field)
                    data[field] = []

        # 3. 基本的布尔值转换（PHP API要求0/1）
        for field, value in data.items():
            if isinstance(value, bool):
                data[field] = int(value)

        logger.debug("数据类型修复完成")
        return data

    def search_product_by_keyword(self, keyword: str, return_all: bool = False):
        """通过关键词搜索获取商品ID

        Args:
            keyword: 搜索关键词
            return_all: 是否返回全部结果，False时返回ID最大的商品

        Returns:
            int: 单个商品ID（return_all=False时）
            List[int]: 商品ID列表（return_all=True时）
        """
        logger.debug("通过关键词搜索商品，关键词: {}，返回全部: {}", keyword, return_all)

        if not keyword:
            logger.debug("搜索关键词不能为空")
            raise ValueError("搜索关键词不能为空")

        endpoint = f"/api/pc/get_products?page=1&limit=20&keyword={keyword}"

        try:
            result = self._api_client.make_request('GET', endpoint)
            products = result.get('data', {}).get('list', [])

            if not products:
                logger.debug("未找到商品: {}", keyword)
                raise RuntimeError(f"未找到商品: {keyword}")

            if return_all:
                # 返回所有商品的ID列表
                product_ids = [product.get('id') for product in products if product.get('id')]
                logger.debug("搜索到 {} 个商品，返回所有ID", len(product_ids))
                return product_ids
            else:
                # 返回ID最大的商品
                max_product = max(products, key=lambda x: x.get('id', 0))
                product_id = max_product.get('id')
                logger.debug("搜索到 {} 个商品，返回最大ID: {}", len(products), product_id)
                return product_id

        except Exception as e:
            logger.debug("搜索商品失败，关键词: {}，错误: {}", keyword, str(e))
            raise

    def get_product_list(self, page: Optional[int] = None, limit: Optional[int] = None, cate_id: Optional[int] = None,
                        store_name: Optional[str] = None, product_type: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取商品列表

        Args:
            page: 分页页码，可选
            limit: 每页条数，可选
            cate_id: 分类ID，可选
            store_name: 商品名称|简介|关键字，可选
            product_type: 商品状态，可选
                1: 出售中(默认)
                2: 仓库中
                4: 已售罄
                5: 库存警戒
                6: 回收站

        Returns:
            商品列表数据

        Example:
            >>> manager = ProductManager(url, appid, secret)
            >>> products = manager.get_product_list(page=1, limit=10)
            >>> print(f"获取到 {len(products)} 个商品")
            >>> print(products[0]['store_name'])  # 商品名称
        """
        logger.debug("获取商品列表，页码: {}，条数: {}，分类ID: {}，商品名称: {}，商品状态: {}",
                    page, limit, cate_id, store_name, product_type)

        # 参数验证
        if page is not None and page < 1:
            logger.debug("页码必须大于0: {}", page)
            raise ValueError("页码必须大于0")

        # 构建查询参数
        params = {}

        if page is not None:
            params['page'] = page

        if limit is not None:
            params['limit'] = limit

        if cate_id is not None:
            params['cate_id'] = cate_id

        if store_name:
            params['store_name'] = store_name

        if product_type is not None:
            params['type'] = product_type

        try:
            result = self._api_client.make_request('GET', '/outapi/product/list', params)

            if result.get('status') == 200:
                data = result.get('data', {})
                products = data.get('list', [])
                total_count = data.get('count', 0)

                logger.debug("获取商品列表成功，总数: {}，当前页商品数: {}", total_count, len(products))
                return products
            else:
                error_msg = result.get('msg', '未知错误')
                logger.debug("获取商品列表失败: {}", error_msg)
                raise RuntimeError(f"获取商品列表失败: {error_msg}")

        except Exception as e:
            logger.debug("获取商品列表时发生错误: {}", str(e))
            raise

    def close(self):
        """关闭管理器连接"""
        logger.debug("关闭CRMEB商品管理器")
        if hasattr(self, '_api_client'):
            self._api_client.close()
