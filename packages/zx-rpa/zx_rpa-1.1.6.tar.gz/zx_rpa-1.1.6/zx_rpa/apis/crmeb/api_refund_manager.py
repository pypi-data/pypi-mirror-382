#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB售后服务管理器
提供售后服务相关的API操作功能
"""

from typing import Dict, List, Any, Optional
from loguru import logger


class RefundManager:
    """CRMEB售后服务管理器
    
    提供售后服务相关的API操作功能
    """

    def __init__(self, api_client):
        """初始化售后服务管理器
        
        Args:
            api_client: CRMEB API客户端实例
        """
        self._api_client = api_client
        logger.debug("初始化CRMEB售后服务管理器")

    def get_refund_list(self, page: Optional[int] = None, limit: Optional[int] = None, 
                       order_id: Optional[str] = None, time: Optional[str] = None,
                       refund_type: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取售后订单列表

        Args:
            page: 分页页码，可选
            limit: 每页条数，可选
            order_id: 售后单号，可选
            time: 退款时间范围，可选
                格式: "2022/06/01-2022/06/29"
            refund_type: 退款类型，可选
                1: 仅退款
                2: 退货退款
                3: 拒绝退款
                4: 商品待退货
                5: 退货待收货
                6: 已退款

        Returns:
            售后订单列表数据

        Example:
            >>> manager = RefundManager(api_client)
            >>> refunds = manager.get_refund_list(page=1, limit=20)
            >>> print(f"获取到 {len(refunds)} 个售后订单")
            >>> for refund in refunds:
            ...     print(f"售后单号: {refund.get('order_id')}")
            ...     print(f"退款类型: {refund.get('refund_type')}")
        """
        logger.debug("获取售后订单列表，页码: {}，条数: {}，售后单号: {}，时间: {}，退款类型: {}", 
                    page, limit, order_id, time, refund_type)

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
        
        if order_id:
            params['order_id'] = order_id
            
        if time:
            params['time'] = time
            
        if refund_type is not None:
            params['refund_type'] = refund_type

        try:
            result = self._api_client.make_request('GET', '/outapi/refund/list', params)
            
            if result.get('status') == 200:
                data_result = result.get('data', {})
                refunds = data_result.get('list', [])
                total_count = data_result.get('count', 0) if isinstance(data_result, dict) else len(refunds)
                
                logger.debug("获取售后订单列表成功，总数: {}，当前页售后订单数: {}", total_count, len(refunds))
                return refunds
            else:
                error_msg = result.get('msg', '未知错误')
                logger.debug("获取售后订单列表失败: {}", error_msg)
                raise RuntimeError(f"获取售后订单列表失败: {error_msg}")

        except Exception as e:
            logger.debug("获取售后订单列表时发生错误: {}", str(e))
            raise

    def get_refund_detail(self, order_id: str) -> Dict[str, Any]:
        """获取售后订单详情

        Args:
            order_id: 售后单号，如 "272753574860029952"

        Returns:
            售后订单详情数据

        Example:
            >>> manager = RefundManager(api_client)
            >>> refund = manager.get_refund_detail("272753574860029952")
            >>> print(refund['order_id'])  # 售后单号
            >>> print(refund['orderInfo'])  # 订单信息
        """
        logger.debug("获取售后订单详情，售后单号: {}", order_id)

        if not order_id:
            logger.debug("售后单号不能为空")
            raise ValueError("售后单号不能为空")

        try:
            result = self._api_client.make_request('GET', f'/outapi/refund/{order_id}')

            if result.get('status') == 200:
                refund_data = result.get('data', {})
                logger.debug("获取售后订单详情成功，售后单号: {}", order_id)
                return refund_data
            else:
                error_msg = result.get('msg', '未知错误')
                logger.debug("获取售后订单详情失败: {}", error_msg)
                raise RuntimeError(f"获取售后订单详情失败: {error_msg}")

        except Exception as e:
            logger.debug("获取售后订单详情时发生错误: {}", str(e))
            raise

    def approve_refund(self, order_id: str, refund_price: Optional[float] = None) -> Dict[str, Any]:
        """同意退款

        Args:
            order_id: 售后单号，如 "275306677517942784"
            refund_price: 退款金额，可选

        Returns:
            操作结果数据

        Example:
            >>> manager = RefundManager(api_client)
            >>> result = manager.approve_refund("275306677517942784", 100.0)
            >>> print(result['msg'])  # 操作结果信息
        """
        logger.debug("同意退款，售后单号: {}，退款金额: {}", order_id, refund_price)

        if not order_id:
            logger.debug("售后单号不能为空")
            raise ValueError("售后单号不能为空")

        # 构建请求数据
        data = {}
        if refund_price is not None:
            data['refund_price'] = refund_price

        try:
            result = self._api_client.make_request('PUT', f'/outapi/refund/{order_id}', data=data)

            if result.get('status') == 200:
                logger.debug("同意退款成功，售后单号: {}，结果: {}", order_id, result.get('msg'))
                return result
            else:
                error_msg = result.get('msg', '未知错误')
                logger.debug("同意退款失败: {}", error_msg)
                raise RuntimeError(f"同意退款失败: {error_msg}")

        except Exception as e:
            logger.debug("同意退款时发生错误: {}", str(e))
            raise

    def refuse_refund(self, order_id: str, refund_reason: Optional[str] = None) -> Dict[str, Any]:
        """拒绝退款

        Args:
            order_id: 售后单号，如 "275306677517942784"
            refund_reason: 拒绝原因，必填，如 "该商品不支持退款"

        Returns:
            操作结果数据

        Example:
            >>> manager = RefundManager(api_client)
            >>> result = manager.refuse_refund("275306677517942784", "该商品不支持退款")
            >>> print(result['msg'])  # 操作结果信息
        """
        logger.debug("拒绝退款，售后单号: {}，拒绝原因: {}", order_id, refund_reason)

        if not order_id:
            logger.debug("售后单号不能为空")
            raise ValueError("售后单号不能为空")

        # 构建请求数据
        data = {}
        if refund_reason:
            data['refund_reason'] = refund_reason

        try:
            result = self._api_client.make_request('PUT', f'/outapi/refund/refuse/{order_id}', data=data)

            if result.get('status') == 200:
                logger.debug("拒绝退款成功，售后单号: {}，结果: {}", order_id, result.get('msg'))
                return result
            else:
                error_msg = result.get('msg', '未知错误')
                logger.debug("拒绝退款失败: {}", error_msg)
                raise RuntimeError(f"拒绝退款失败: {error_msg}")

        except Exception as e:
            logger.debug("拒绝退款时发生错误: {}", str(e))
            raise

    def close(self):
        """关闭售后服务管理器"""
        logger.debug("关闭CRMEB售后服务管理器")
        # 这里可以添加清理资源的代码
        pass
