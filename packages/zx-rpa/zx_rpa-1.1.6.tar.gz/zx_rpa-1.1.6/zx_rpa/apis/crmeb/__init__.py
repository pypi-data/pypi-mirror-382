#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB商城平台API封装模块 - 统一格式商品管理

## 引入方式
```python
from zx_rpa.apis.crmeb import CrmebApiClient, CrmebWebClient

# API客户端（后端接口）- 用于分类管理
api_client = CrmebApiClient(
    main_url="https://your-domain.com",
    appid="your_appid",
    appsecret="your_appsecret"
)

# Web客户端（管理后台）- 用于品牌、单位、标签、保障服务管理
web_client = CrmebWebClient(
    main_url="https://shop.shikejk.com",
    username="admin_username",
    password="admin_password"
)
```

## 对外方法

### 商品管理
- create_product_unified(unified_data, spec_columns=None, base_field_mapping=None, attr_mapping=None) -> dict - 统一格式创建商品
- update_product_unified(product_id, unified_data, spec_columns=None, base_field_mapping=None, attr_mapping=None) -> dict - 统一格式完整更新商品
- partial_update_product(product_id, update_data) -> dict - 智能部分更新商品
- get_product_data(product_id) -> dict - 获取完整商品数据
- get_product_list(page=None, limit=None, cate_id=None, store_name=None, product_type=None) -> list - 获取商品列表
- update_product_status(product_id, is_show) -> dict - 更新商品状态（上架/下架）
- search_product_by_keyword(keyword, return_all=False) -> int/list - 通过关键词搜索商品

### 订单管理
- get_order_list(page=None, limit=None, status=None, real_name=None, pay_type=None, data=None, paid=1) -> list - 获取订单列表
- get_order_detail(order_id) -> dict - 获取订单详情
- get_order_split_cart_info(order_id) -> list - 获取订单未发货商品列表
- delivery_order(order_id, delivery_name=None, delivery_id=None, delivery_code=None) -> dict - 订单发货

### 售后服务管理
- get_refund_list(page=None, limit=None, order_id=None, time=None, refund_type=None) -> list - 获取售后订单列表
- get_refund_detail(order_id) -> dict - 获取售后订单详情
- approve_refund(order_id, refund_price=None) -> dict - 同意退款
- refuse_refund(order_id, refund_reason=None) -> dict - 拒绝退款

### API客户端功能（CrmebApiClient）
- get_category_name_id_dict(include_hidden=False) -> dict - 获取分类名称到ID的映射字典

### Web客户端功能（CrmebWebClient）
- get_brand_name_id_dict(include_hidden=False) -> dict - 获取品牌名称到ID的映射字典
- get_unit_name_id_dict(include_disabled=False) -> dict - 获取商品单位名称到ID的映射字典
- get_label_name_id_dict(include_hidden=False) -> dict - 获取商品标签名称到ID的映射字典
- get_ensure_name_id_dict(include_disabled=False) -> dict - 获取保障服务名称到ID的映射字典
- get_all_dicts(include_hidden=False, include_disabled=False) -> dict - 批量获取所有字典

### 资源管理
- close() - 关闭客户端并清理资源

"""

from .api_client_main import CrmebApiClient
from .web_client_main import CrmebWebClient

__all__ = ["CrmebApiClient", "CrmebWebClient"]
