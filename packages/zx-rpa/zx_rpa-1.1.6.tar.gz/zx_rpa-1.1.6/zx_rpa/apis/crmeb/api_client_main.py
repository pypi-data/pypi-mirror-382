#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB统一客户端模块

提供CRMEB平台的统一对外接口，封装所有API调用和前端请求功能。
"""

from typing import Dict, Optional, Any, List
from loguru import logger

from .api_product_manager import ProductManager
from .api_category_manager import CategoryManager
from .api_order_manager import OrderManager
from .api_refund_manager import RefundManager
from .api_client import CrmebApiClient as BaseCrmebApiClient


class CrmebApiClient:
    """CRMEB统一客户端 - 对外统一接口"""

    def __init__(self, main_url: str, appid: str, appsecret: str, timeout: int = 30):
        """初始化CRMEB客户端

        Args:
            main_url: CRMEB主域名
            appid: 应用ID
            appsecret: 应用密钥
            timeout: 请求超时时间（秒）
        """
        logger.debug("初始化CRMEB统一客户端")

        # 初始化各功能模块
        self._product_manager = ProductManager(main_url, appid, appsecret, timeout)
        self._category_manager = CategoryManager(main_url, appid, appsecret, timeout)

        # 为订单管理器创建独立的API客户端
        from .api_client import CrmebApiClient as BaseCrmebApiClient
        order_api_client = BaseCrmebApiClient(main_url, appid, appsecret, timeout)
        self._order_manager = OrderManager(order_api_client)

        # 为售后服务管理器创建独立的API客户端
        refund_api_client = BaseCrmebApiClient(main_url, appid, appsecret, timeout)
        self._refund_manager = RefundManager(refund_api_client)

        logger.debug("CRMEB统一客户端初始化完成")

    # ==================== 商品管理方法 ====================

    def update_product_status(self, product_id: int, is_show: int) -> Dict:
        """更新商品状态

        Args:
            product_id: 商品ID
            is_show: 上架状态，1表示上架展示，0表示下架隐藏

        Returns:
            API响应数据，包含status和msg字段
        """
        return self._product_manager.update_product_status(product_id, is_show)


    def get_product_data(self, product_id: int) -> Dict[str, Any]:
        """获取商品详情数据

        Args:
            product_id: 商品ID

        Returns:
            商品详情数据
        """
        return self._product_manager.get_product_data(product_id)

    def create_product_unified(self, unified_data: Dict[str, Any],
                              spec_columns: Optional[List[str]] = None,
                              base_field_mapping: Optional[Dict[str, str]] = None,
                              attr_mapping: Optional[Dict[str, str]] = None,
                              reverse_spec_order: bool = False) -> Dict:
        """使用统一格式创建商品

        Args:
            unified_data: 统一格式的商品数据
                {
                    "store_name": "商品名称",
                    "store_info": "商品描述",
                    "skus": [
                        {
                            "规格": "红色"
                            "描述": "就是副规格"
                            "code": "sku_001",
                            "price": 299.0,
                            "stock": 100,
                            "颜色": "红色",
                            "尺寸": "L"
                        }
                    ]
                }
            spec_columns: 规格列名列表，如 ['颜色', '尺寸']。如果不提供，会自动识别
            base_field_mapping: 基础字段映射，如 {'store_name': '商品名称'}
            attr_mapping: 属性字段映射，如 {'price': '价格', 'stock': '库存'}
            reverse_spec_order: 是否颠倒规格值顺序，用于解决上传后顺序颠倒的问题

        Returns:
            API响应数据，包含status和msg字段
        """
        return self._product_manager.create_product_unified(
            unified_data, spec_columns, base_field_mapping, attr_mapping, reverse_spec_order
        )

    def update_product_unified(self, product_id: int, unified_data: Dict[str, Any],
                              spec_columns: Optional[List[str]] = None,
                              base_field_mapping: Optional[Dict[str, str]] = None,
                              attr_mapping: Optional[Dict[str, str]] = None,
                              reverse_spec_order: bool = False) -> Dict:
        """使用统一格式更新商品

        Args:
            product_id: 商品ID
            unified_data: 统一格式的商品数据
            spec_columns: 规格列名列表，如 ['颜色', '尺寸']。如果不提供，会自动识别
            base_field_mapping: 基础字段映射，如 {'store_name': '商品名称'}
            attr_mapping: 属性字段映射，如 {'price': '价格', 'stock': '库存'}
            reverse_spec_order: 是否颠倒规格值顺序，用于解决上传后顺序颠倒的问题

        Returns:
            API响应数据，包含status和msg字段
        """
        return self._product_manager.update_product_unified(
            product_id, unified_data, spec_columns, base_field_mapping, attr_mapping, reverse_spec_order
        )

    def partial_update_product(self, product_id: int, update_data: Dict[str, Any]) -> Dict:
        """部分更新商品

        先获取商品完整数据，然后与更新数据合并，最后提交更新。
        支持基础字段更新和SKU精确更新。

        Args:
            product_id: 商品ID
            update_data: 统一格式的更新数据
                {
                    "store_name": "新商品名称",  # 基础字段更新
                    "skus": [                    # SKU更新（通过code匹配）
                        {
                            "code": "sku_001",
                            "price": 299.0,
                            "stock": 100,
                            "pic": "new_image.jpg"
                        }
                    ]
                }

        Returns:
            API响应数据，包含status和msg字段
        """
        return self._product_manager.partial_update_product(product_id, update_data)

    def search_product_by_keyword(self, keyword: str, return_all: bool = False):
        """通过关键词搜索获取商品ID

        Args:
            keyword: 搜索关键词
            return_all: 是否返回全部结果，False时返回ID最大的商品

        Returns:
            int: 单个商品ID（return_all=False时）
            List[int]: 商品ID列表（return_all=True时）
        """
        return self._product_manager.search_product_by_keyword(keyword, return_all)

    def get_product_list(self, page: Optional[int] = 1, limit: Optional[int] = 1000, cate_id: Optional[int] = None,
                        store_name: Optional[str] = None, product_type: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取商品列表

        Args:
            page: 分页页码，可选
            limit: 每页条数，可选
            cate_id: 分类ID，可选
            store_name: 商品名称|简介|关键字，可选
            product_type: 商品状态，可选 （当前其他状态查询有问题）
                1: 出售中(默认)
                2: 仓库中
                4: 已售罄
                5: 库存警戒
                6: 回收站

        Returns:
            商品列表数据

        Example:
            >>> client = CrmebApiClient(url, appid, secret)
            >>> products = client.get_product_list(page=1, limit=10)
            >>> print(f"获取到 {len(products)} 个商品")
        """
        return self._product_manager.get_product_list(page, limit, cate_id, store_name, product_type)

    # ==================== 其他商品字典方法 ====================

    def get_category_name_id_dict(self, include_hidden: bool = False) -> Dict[str, int]:
        """获取分类名称到ID的映射字典

        Args:
            include_hidden: 是否包含隐藏的分类，默认False只返回显示的分类

        Returns:
            分类名称到ID的字典 {分类名称: id, ...}
        """
        return self._category_manager.get_category_name_id_dict(include_hidden)

    # ==================== 订单管理方法 ====================

    def get_order_list(self, page: Optional[int] = None, limit: Optional[int] = None,
                      status: Optional[int] = None, real_name: Optional[str] = None,
                      pay_type: Optional[int] = None, data: Optional[str] = None,
                      paid: Optional[int] = 1) -> List[Dict[str, Any]]:
        """获取订单列表

        Args:
            page: 分页页码，可选
            limit: 每页条数，可选
            status: 订单状态，可选 (0未发货 1已发货 2已收货 3已完成 -2已退款)
            real_name: 订单ID|用户姓名，可选
            pay_type: 支付方式，可选 (1微信 2余额 3线下 4支付宝)
            data: 下单时间范围，可选 (格式: "2022/07/12 00:00:00-2022/08/17 00:00:00")
            paid: 是否支付，默认1 (1已支付 0未支付)

        Returns:
            订单列表数据

        Example:
            >>> client = CrmebApiClient(url, appid, secret)
            >>> orders = client.get_order_list(page=1, limit=20)
            >>> print(f"获取到 {len(orders)} 个订单")
        """
        return self._order_manager.get_order_list(page, limit, status, real_name, pay_type, data, paid)

    def get_order_detail(self, order_id: str) -> Dict[str, Any]:
        """获取订单详情

        Args:
            order_id: 订单号，如 "wx273866852013178880"

        Returns:
            订单详情数据

        Example:
            >>> client = CrmebApiClient(url, appid, secret)
            >>> order = client.get_order_detail("wx273866852013178880")
            >>> print(order['order_id'])  # 订单ID
        """
        return self._order_manager.get_order_detail(order_id)

    def get_order_split_cart_info(self, order_id: str) -> List[Dict[str, Any]]:
        """获取订单未发货商品列表（可拆分商品列表）

        Args:
            order_id: 订单号，如 "wx275230594223308800"

        Returns:
            订单未发货商品列表数据

        Example:
            >>> client = CrmebApiClient(url, appid, secret)
            >>> products = client.get_order_split_cart_info("wx275230594223308800")
            >>> print(f"未发货商品数量: {len(products)}")
        """
        return self._order_manager.get_order_split_cart_info(order_id)

    def delivery_order(self, order_id: str, delivery_name: Optional[str] = None,
                      delivery_id: Optional[str] = None, delivery_code: Optional[str] = None) -> Dict[str, Any]:
        """订单发货

        Args:
            order_id: 订单号，如 "wx273866852013178880"
            delivery_name: 快递公司名称，可选，如 "顺丰快运"
            delivery_id: 快递单号，可选，如 "SF5555:2356"
            delivery_code: 快递公司编码，可选，如 "shunfengkuaiyun"

        Returns:
            发货结果数据

        Example:
            >>> client = CrmebApiClient(url, appid, secret)
            >>> result = client.delivery_order(
            ...     "wx273866852013178880",
            ...     delivery_name="顺丰快运",
            ...     delivery_id="SF5555:2356",
            ...     delivery_code="shunfengkuaiyun"
            ... )
            >>> print(result['msg'])  # 发货结果信息
        """
        return self._order_manager.delivery_order(order_id, delivery_name, delivery_id, delivery_code)

    # ==================== 售后服务管理方法 ====================

    def get_refund_list(self, page: Optional[int] = None, limit: Optional[int] = None,
                       order_id: Optional[str] = None, time: Optional[str] = None,
                       refund_type: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取售后订单列表

        Args:
            page: 分页页码，可选
            limit: 每页条数，可选
            order_id: 售后单号，可选
            time: 退款时间范围，可选 (格式: "2022/06/01-2022/06/29")
            refund_type: 退款类型，可选 (1仅退款 2退货退款 3拒绝退款 4商品待退货 5退货待收货 6已退款)

        Returns:
            售后订单列表数据

        Example:
            >>> client = CrmebApiClient(url, appid, secret)
            >>> refunds = client.get_refund_list(page=1, limit=20)
            >>> print(f"获取到 {len(refunds)} 个售后订单")
        """
        return self._refund_manager.get_refund_list(page, limit, order_id, time, refund_type)

    def get_refund_detail(self, order_id: str) -> Dict[str, Any]:
        """获取售后订单详情

        Args:
            order_id: 售后单号，如 "272753574860029952"

        Returns:
            售后订单详情数据

        Example:
            >>> client = CrmebApiClient(url, appid, secret)
            >>> refund = client.get_refund_detail("272753574860029952")
            >>> print(refund['order_id'])  # 售后单号
        """
        return self._refund_manager.get_refund_detail(order_id)

    def approve_refund(self, order_id: str, refund_price: Optional[float] = None) -> Dict[str, Any]:
        """同意退款

        Args:
            order_id: 售后单号，如 "275306677517942784"
            refund_price: 退款金额，可选

        Returns:
            操作结果数据

        Example:
            >>> client = CrmebApiClient(url, appid, secret)
            >>> result = client.approve_refund("275306677517942784", 100.0)
            >>> print(result['msg'])  # 操作结果信息
        """
        return self._refund_manager.approve_refund(order_id, refund_price)

    def refuse_refund(self, order_id: str, refund_reason: Optional[str] = None) -> Dict[str, Any]:
        """拒绝退款

        Args:
            order_id: 售后单号，如 "275306677517942784"
            refund_reason: 拒绝原因，必填，如 "该商品不支持退款"

        Returns:
            操作结果数据

        Example:
            >>> client = CrmebApiClient(url, appid, secret)
            >>> result = client.refuse_refund("275306677517942784", "该商品不支持退款")
            >>> print(result['msg'])  # 操作结果信息
        """
        return self._refund_manager.refuse_refund(order_id, refund_reason)

    def close(self):
        """关闭客户端连接"""
        logger.debug("关闭CRMEB客户端")
        if hasattr(self, '_product_manager'):
            self._product_manager.close()
        if hasattr(self, '_category_manager'):
            self._category_manager.close()
        if hasattr(self, '_order_manager'):
            self._order_manager.close()
        if hasattr(self, '_refund_manager'):
            self._refund_manager.close()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        # 忽略异常信息，只进行清理
        _ = exc_type, exc_val, exc_tb
        self.close()
