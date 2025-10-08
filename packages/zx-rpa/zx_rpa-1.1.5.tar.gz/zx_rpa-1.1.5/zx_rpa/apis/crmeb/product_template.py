#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB商品数据模板管理器

提供商品数据的默认模板和数据合并功能。
"""

import copy
from typing import Dict, Any, List
from loguru import logger


class ProductTemplate:
    """商品数据模板管理器"""

    # 商品数据默认模板
    DEFAULT_TEMPLATE = {
        "id": 0,  # 商品ID，新增时为0
        "brand_id": [],  # 品牌ID数组
        "code": "",  # 商品编码
        "slider_image": [  # 轮播图数组（必填）
            "https://qn.shikejk.com//attach/2025/08/c856d202508311636394243.jpg",
            "https://qn.shikejk.com//attach/2025/08/60bb9202508311633553990.jpg"
        ],
        "store_name": "商品名称",  # 商品名称（必填）
        "cate_id": [228],  # 分类ID数组（必填，至少一个分类）
        "store_label_id": [],  # 商品标签ID数组
        "unit_name": "个",  # 单位名称（必填）
        "video_link": "",  # 视频链接地址
        "video_open": False,  # 是否开启视频，1开启0关闭
        "is_show": 1,  # 上架状态，1上架0下架
        "auto_on_time": "",  # 自动上架时间
        "auto_off_time": "",  # 自动下架时间
        "off_show": 0,  # 下架显示
        "product_type": 0,  # 商品类型，0普通商品1卡密2优惠券3虚拟商品
        "ficti": 0,  # 虚拟销量
        "sort": 0,  # 排序
        "give_integral": 0,  # 赠送积分
        "couponName": [],  # 赠送优惠券名称
        "coupon_ids": [],  # 关联优惠券ID
        "is_presale_product": 0,  # 是否预售商品
        "is_limit": 0,  # 是否开启限购，1开启0关闭
        "limit_type": 1,  # 限购类型，1单次限购2永久限购
        "limit_num": 1,  # 限购数量
        "presale_time": [],  # 预售时间段
        "presale_day": 1,  # 预售发货日
        "is_good": 0,  # 是否好物推荐
        "is_vip_product": 0,  # 是否开启会员价格
        "label_id": [],  # 用户标签ID
        "ensure_id": [],  # 商品保障服务区ID
        "min_qty": 1,  # 最小购买数量
        "presale_status": 1,  # 预售状态
        "recommend_list": [],  # 推荐产品列表
        "keyword": "",  # 商品关键字
        "store_info": "",  # 商品简介
        "command_word": "",  # 复制口令
        "recommend_image": "",  # 商品推荐图
        "specs_id": "",  # 商品参数ID
        "is_support_refund": 1,  # 是否支持退款
        "system_form_id": "",  # 系统表单ID
        "specs": [],  # 商品参数
        "share_content": "",  # 分享内容
        "type": 0,  # 商品所属，0平台1门店2供应商
        "spec_type": 1,  # 规格类型，0单规格1多规格
        "items": [  # 商品规格（多规格必填）
            {
                "value": "规格",  # 规格名称
                "add_pic": 1,  # 是否添加图片
                "detail": [  # 规格详情
                    {
                        "value": "规格值1",  # 规格值
                        "pic": "https://qn.shikejk.com//attach/2025/08/c856d202508311636394243.jpg"  # 规格图片
                    },
                    {
                        "value": "规格值2",
                        "pic": "https://qn.shikejk.com//attach/2025/08/c856d202508311636394243.jpg"
                    }
                ]
            },
            {
                "value": "描述",
                "add_pic": 0,
                "detail": [
                    {
                        "value": "这是描述值",
                        "pic": ""
                    }
                ]
            }
        ],
        "attr": {  # 单规格属性
            "pic": "",  # 商品图片
            "price": 0,  # 商品价格
            "settle_price": 0,  # 结算价格
            "cost": 0,  # 成本价
            "ot_price": 0,  # 原价
            "stock": 0,  # 库存
            "bar_code": "",  # 条形码
            "code": "",  # 编码
            "weight": 0,  # 重量
            "volume": 0,  # 体积
            "brokerage": 0,  # 一级佣金
            "brokerage_two": 0,  # 二级佣金
            "vip_price": 0,  # 会员价格
            "virtual_list": [],  # 虚拟商品列表
            "write_times": 0,  # 写入次数
            "write_valid": 1,  # 写入有效期
            "days": 1  # 天数
        },
        "attrs": [  # 多规格属性数组（默认单个SKU项，实际使用时会被替换为多个SKU）
            {
                "attr_arr": ["规格值1", "这是描述值"],  # 属性数组
                "detail": {"规格": "规格值1", "描述": "这是描述值"},  # sku详情
                "title": "描述",  # 标题
                "key": "描述",  # 键
                "price": 100,  # 价格
                "pic": "https://qn.shikejk.com//attach/2025/08/c856d202508311636394243.jpg",  # 图片
                "ot_price": 150,  # 原价
                "cost": 0,  # 成本
                "stock": 100,  # 库存
                "is_show": 1,  # 是否显示
                "is_default_select": 1,  # 是否默认选中
                "unique": "",  # 唯一标识
                "weight": 0,  # 重量
                "volume": 0,  # 体积
                "brokerage": 0,  # 一级佣金
                "brokerage_two": 0,  # 二级佣金
                "vip_price": 0,  # 会员价格
                "vip_proportion": 0,  # 会员比例
                "规格": "规格值1",  # 规格值
                "描述": "这是描述值",  # 描述值
                "index": 1,  # 索引
                "code": "sku_code1"  # SKU编码
            }
        ],
        "description": '',  # 商品详情
        "delivery_type": ["1"],  # 商品配送方式
        "freight": 1,  # 运费类型
        "postage": 0,  # 邮费，0元则包邮（必填）
        "temp_id": ""  # 运费模版ID
    }

    @classmethod
    def create_product_data(cls, custom_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建商品数据
        
        Args:
            custom_data: 自定义商品数据，会覆盖默认模板中的对应字段
            
        Returns:
            合并后的完整商品数据
        """
        logger.debug("创建商品数据，自定义字段数量: {}", len(custom_data))
        
        # 深拷贝默认模板，避免修改原模板
        product_data = copy.deepcopy(cls.DEFAULT_TEMPLATE)
        
        # 递归合并自定义数据
        cls._deep_merge(product_data, custom_data)
        
        logger.debug("商品数据创建完成，总字段数量: {}", len(product_data))
        return product_data

    @classmethod
    def _deep_merge(cls, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """深度合并字典

        Args:
            target: 目标字典（会被修改）
            source: 源字典
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # 如果都是字典，递归合并
                cls._deep_merge(target[key], value)
            elif key == 'attrs' and isinstance(value, list) and isinstance(target.get(key), list):
                # 特殊处理attrs数组：合并每个SKU项的字段
                target[key] = cls._merge_attrs_array(target[key], value)
            else:
                # 否则直接覆盖
                target[key] = value

    @classmethod
    def _merge_attrs_array(cls, default_attrs: List[Dict], custom_attrs: List[Dict]) -> List[Dict]:
        """合并attrs数组，确保每个SKU项都包含默认字段

        Args:
            default_attrs: 默认attrs数组（通常只有一个模板项）
            custom_attrs: 自定义attrs数组

        Returns:
            合并后的attrs数组
        """
        if not default_attrs:
            return custom_attrs

        # 获取默认SKU模板
        default_sku_template = default_attrs[0]

        # 为每个自定义SKU合并默认字段
        merged_attrs = []
        for i, custom_sku in enumerate(custom_attrs):
            # 深拷贝默认模板
            merged_sku = copy.deepcopy(default_sku_template)

            # 清理默认模板中的规格字段（这些会被自定义数据替换）
            default_spec_fields = ['规格', '描述']  # 默认模板中的规格字段
            for field in default_spec_fields:
                if field in merged_sku:
                    del merged_sku[field]

            # 用自定义数据覆盖
            for field, value in custom_sku.items():
                merged_sku[field] = value

            # 更新索引
            merged_sku['index'] = i + 1

            merged_attrs.append(merged_sku)

        return merged_attrs

    @classmethod
    def get_required_fields(cls) -> List[str]:
        """获取必填字段列表

        Returns:
            必填字段名称列表
        """
        return [
            "store_name",      # 商品名称
            "cate_id",         # 分类ID
            "slider_image"     # 轮播图
        ]

    @classmethod
    def validate_required_fields(cls, product_data: Dict[str, Any]) -> List[str]:
        """
        验证商品数据中的必填字段

        Args:
            product_data (Dict[str, Any]): 商品数据字典，包含商品的各种属性信息

        Returns:
            List[str]: 缺失的必填字段名称列表，空列表表示所有必填字段都存在

        Example:
            >>> data = {"store_name": "商品名称"}  # 缺少其他必填字段
            >>> missing = ProductTemplate.validate_required_fields(data)
            >>> print(missing)
            ['store_info', 'cate_id', 'slider_image']
        """
        required_fields = cls.get_required_fields()
        missing_fields = []
        
        for field in required_fields:
            if field not in product_data or not product_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            logger.debug("商品数据缺失必填字段: {}", missing_fields)
        
        return missing_fields
