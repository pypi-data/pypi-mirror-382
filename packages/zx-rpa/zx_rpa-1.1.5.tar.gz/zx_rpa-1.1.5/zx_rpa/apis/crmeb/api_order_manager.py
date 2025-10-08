#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB订单管理器
提供订单相关的API操作功能
"""

from typing import Dict, List, Any, Optional
from loguru import logger


class OrderManager:
    """CRMEB订单管理器

    提供订单相关的API操作功能
    """

    def __init__(self, api_client):
        """初始化订单管理器
        
        Args:
            api_client: CRMEB API客户端实例
        """
        self._api_client = api_client
        logger.debug("初始化CRMEB订单管理器")

    def get_order_list(self, page: Optional[int] = None, limit: Optional[int] = None, 
                      status: Optional[int] = None, real_name: Optional[str] = None,
                      pay_type: Optional[int] = None, data: Optional[str] = None,
                      paid: Optional[int] = 1) -> List[Dict[str, Any]]:
        """获取订单列表

        Args:
            page: 分页页码，可选
            limit: 每页条数，可选
            status: 订单状态，可选
                0: 未发货
                1: 已发货
                2: 已收货
                3: 已完成
                -2: 已退款
            real_name: 订单ID|用户姓名，可选
            pay_type: 支付方式，可选
                1: 微信
                2: 余额
                3: 线下
                4: 支付宝
            data: 下单时间范围，可选
                格式: "2022/07/12 00:00:00-2022/08/17 00:00:00"
            paid: 是否支付，默认1（已支付）
                1: 已支付
                0: 未支付

        Returns:
            订单列表数据

        Example:
            >>> manager = OrderManager(api_client)
            >>> orders = manager.get_order_list(page=1, limit=20)
            >>> print(f"获取到 {len(orders)} 个订单")
            >>> print(orders[0]['order_id'])  # 订单ID
        """
        logger.debug("获取订单列表，页码: {}，条数: {}，状态: {}，姓名: {}，支付方式: {}，时间: {}，是否支付: {}", 
                    page, limit, status, real_name, pay_type, data, paid)

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
        
        if status is not None:
            params['status'] = status
        
        if real_name:
            params['real_name'] = real_name
            
        if pay_type is not None:
            params['pay_type'] = pay_type
            
        if data:
            params['data'] = data
            
        if paid is not None:
            params['paid'] = paid

        try:
            result = self._api_client.make_request('GET', '/outapi/order/list', params)
            
            if result.get('status') == 200:
                data_result = result.get('data', {})
                orders = data_result.get('list', [])
                total_count = data_result.get('count', 0) if isinstance(data_result, dict) else len(orders)
                
                logger.debug("获取订单列表成功，总数: {}，当前页订单数: {}", total_count, len(orders))
                return orders
            else:
                error_msg = result.get('msg', '未知错误')
                logger.debug("获取订单列表失败: {}", error_msg)
                raise RuntimeError(f"获取订单列表失败: {error_msg}")

        except Exception as e:
            logger.debug("获取订单列表时发生错误: {}", str(e))
            raise



    def get_order_detail(self, order_id: str) -> Dict[str, Any]:
        """获取订单详情

        Args:
            order_id: 订单号，如 "wx273866852013178880"

        Returns:
            订单详情数据

        Example:
            >>> manager = OrderManager(api_client)
            >>> order = manager.get_order_detail("wx273866852013178880")
            >>> print(order['order_id'])  # 订单ID
            >>> print(order['real_name'])  # 用户姓名
        """
        logger.debug("获取订单详情，订单ID: {}", order_id)

        if not order_id:
            logger.debug("订单ID不能为空")
            raise ValueError("订单ID不能为空")

        try:
            result = self._api_client.make_request('GET', f'/outapi/order/{order_id}')

            if result.get('status') == 200:
                order_data = result.get('data', {})
                logger.debug("获取订单详情成功，订单ID: {}", order_id)
                return order_data
            else:
                error_msg = result.get('msg', '未知错误')
                logger.debug("获取订单详情失败: {}", error_msg)
                raise RuntimeError(f"获取订单详情失败: {error_msg}")

        except Exception as e:
            logger.debug("获取订单详情时发生错误: {}", str(e))
            raise

    def get_order_split_cart_info(self, order_id: str) -> List[Dict[str, Any]]:
        """获取订单未发货商品列表（可拆分商品列表）

        Args:
            order_id: 订单号，如 "wx275230594223308800"

        Returns:
            订单未发货商品列表数据

        Example:
            >>> manager = OrderManager(api_client)
            >>> products = manager.get_order_split_cart_info("wx275230594223308800")
            >>> print(f"未发货商品数量: {len(products)}")
            >>> for product in products:
            ...     print(f"商品名称: {product.get('product_name')}")
        """
        logger.debug("获取订单未发货商品列表，订单ID: {}", order_id)

        if not order_id:
            logger.debug("订单ID不能为空")
            raise ValueError("订单ID不能为空")

        try:
            result = self._api_client.make_request('GET', f'/outapi/order/split_cart_info/{order_id}')

            if result.get('status') == 200:
                cart_data = result.get('data', [])
                # 如果返回的是字典且包含列表，提取列表部分
                if isinstance(cart_data, dict) and 'list' in cart_data:
                    cart_data = cart_data['list']
                elif not isinstance(cart_data, list):
                    cart_data = [cart_data] if cart_data else []

                logger.debug("获取订单未发货商品列表成功，订单ID: {}，商品数量: {}", order_id, len(cart_data))
                return cart_data
            else:
                error_msg = result.get('msg', '未知错误')
                logger.debug("获取订单未发货商品列表失败: {}", error_msg)
                raise RuntimeError(f"获取订单未发货商品列表失败: {error_msg}")

        except Exception as e:
            logger.debug("获取订单未发货商品列表时发生错误: {}", str(e))
            raise

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
            >>> manager = OrderManager(api_client)
            >>> result = manager.delivery_order(
            ...     "wx273866852013178880",
            ...     delivery_name="顺丰快运",
            ...     delivery_id="SF5555:2356",
            ...     delivery_code="shunfengkuaiyun"
            ... )
            >>> print(result['msg'])  # 发货结果信息
        """
        logger.debug("订单发货，订单ID: {}，快递公司: {}，快递单号: {}，快递编码: {}",
                    order_id, delivery_name, delivery_id, delivery_code)

        if not order_id:
            logger.debug("订单ID不能为空")
            raise ValueError("订单ID不能为空")

        # 构建请求数据
        data = {}
        if delivery_name:
            data['delivery_name'] = delivery_name
        if delivery_id:
            data['delivery_id'] = delivery_id
        if delivery_code:
            data['delivery_code'] = delivery_code

        try:
            result = self._api_client.make_request('PUT', f'/outapi/order/delivery/{order_id}', data=data)

            if result.get('status') == 200:
                logger.debug("订单发货成功，订单ID: {}，结果: {}", order_id, result.get('msg'))
                return result
            else:
                error_msg = result.get('msg', '未知错误')
                logger.debug("订单发货失败: {}", error_msg)
                raise RuntimeError(f"订单发货失败: {error_msg}")

        except Exception as e:
            logger.debug("订单发货时发生错误: {}", str(e))
            raise

    def close(self):
        """关闭订单管理器"""
        logger.debug("关闭CRMEB订单管理器")
        # 这里可以添加清理资源的代码
        pass
