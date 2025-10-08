#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多行列表数据提取器

提供多行列表数据与嵌套结构数据的双向转换功能。
支持自定义字段名称和灵活的数据结构转换。

主要功能：
1. 多行列表 → 嵌套结构：将多行数据提取到指定字段的列表中
2. 嵌套结构 → 多行列表：将嵌套结构数据展开为多行列表
3. 支持自定义字段名称（默认为'skus'）
4. 支持字段映射和数据验证

使用场景：
- Excel数据导入处理
- API数据格式转换
- 数据库查询结果处理
- 批量数据操作
"""

from typing import List, Dict, Any, Optional, Union
from loguru import logger


class MultiRowExtractor:
    """多行列表数据提取器"""
    
    def __init__(self):
        """初始化多行列表数据提取器"""
        logger.debug("初始化多行列表数据提取器")
    
    def extract_to_nested(self,
                         multi_row_data: List[Dict[str, Any]],
                         target_field: str = 'skus',
                         row_fields: Optional[List[str]] = None,
                         base_fields: Optional[List[str]] = None,
                         field_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        将多行列表数据提取为嵌套结构格式
        
        Args:
            multi_row_data: 多行数据列表
            target_field: 目标字段名称，默认'skus'
            row_fields: 行字段列表（需要提取到skus里面的字段），必传
            base_fields: 基础字段列表（公共字段），可选，不传则自动计算为除row_fields外的所有字段
            field_mapping: 字段映射字典，用于重命名字段

        Returns:
            嵌套结构数据字典
            
        Example:
            multi_row_data = [
                {"商品名称": "测试商品", "颜色": "红色", "尺寸": "L", "价格": 199.0, "库存": 100},
                {"商品名称": "测试商品", "颜色": "蓝色", "尺寸": "M", "价格": 189.0, "库存": 80}
            ]
            
            result = extractor.extract_to_nested(
                multi_row_data,
                target_field='skus',
                row_fields=['颜色', '尺寸', '价格', '库存'],
                base_fields=['商品名称']  # 可选，不传则自动计算
            )

            # 结果：
            # {
            #     "商品名称": "测试商品",
            #     "skus": [
            #         {"颜色": "红色", "尺寸": "L", "价格": 199.0, "库存": 100},
            #         {"颜色": "蓝色", "尺寸": "M", "价格": 189.0, "库存": 80}
            #     ]
            # }
        """
        logger.debug(f"开始提取多行数据为嵌套结构，数据行数: {len(multi_row_data)}, 目标字段: {target_field}")
        
        if not multi_row_data:
            logger.warning("输入数据为空")
            return {}

        # 如果没有指定row_fields，自动分析所有字段
        if row_fields is None:
            base_fields, row_fields = self._auto_analyze_fields(multi_row_data)
            logger.debug(f"自动分析字段 - 基础字段: {base_fields}, 行字段: {row_fields}")
        else:
            # 如果指定了row_fields但没有指定base_fields，自动计算base_fields
            if base_fields is None:
                # 获取所有字段
                all_fields = set()
                for row in multi_row_data:
                    all_fields.update(row.keys())

                # base_fields = 所有字段 - row_fields
                base_fields = list(all_fields - set(row_fields))
                logger.debug(f"自动计算基础字段: {base_fields}")

            logger.debug(f"使用指定字段 - 基础字段: {base_fields}, 行字段: {row_fields}")
        
        # 构建嵌套结构数据
        nested_data = {}

        # 提取基础字段（从第一行）
        first_row = multi_row_data[0]
        for field in base_fields:
            if field in first_row:
                # 应用字段映射
                mapped_field = field_mapping.get(field, field) if field_mapping else field
                nested_data[mapped_field] = first_row[field]

        # 提取行数据到目标字段
        target_list = []
        for row in multi_row_data:
            row_data = {}
            for field in row_fields:
                if field in row:
                    # 应用字段映射
                    mapped_field = field_mapping.get(field, field) if field_mapping else field
                    row_data[mapped_field] = row[field]
            if row_data:  # 只添加非空的行数据
                target_list.append(row_data)

        nested_data[target_field] = target_list

        logger.debug(f"提取完成，基础字段数: {len(base_fields)}, {target_field}数量: {len(target_list)}")
        return nested_data
    
    def expand_from_nested(self,
                          nested_data: Dict[str, Any],
                          source_field: str = 'skus',
                          field_mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        将嵌套结构数据展开为多行列表
        
        Args:
            nested_data: 嵌套结构数据
            source_field: 源字段名称，默认'skus'
            field_mapping: 字段映射字典，用于重命名字段

        Returns:
            多行数据列表

        Example:
            nested_data = {
                "商品名称": "测试商品",
                "skus": [
                    {"颜色": "红色", "尺寸": "L", "价格": 199.0, "库存": 100},
                    {"颜色": "蓝色", "尺寸": "M", "价格": 189.0, "库存": 80}
                ]
            }

            result = extractor.expand_from_nested(nested_data, source_field='skus')

            # 结果：
            # [
            #     {"商品名称": "测试商品", "颜色": "红色", "尺寸": "L", "价格": 199.0, "库存": 100},
            #     {"商品名称": "测试商品", "颜色": "蓝色", "尺寸": "M", "价格": 189.0, "库存": 80}
            # ]
        """
        logger.debug(f"开始展开嵌套结构数据为多行列表，源字段: {source_field}")

        if not nested_data or source_field not in nested_data:
            logger.warning(f"嵌套结构数据为空或不包含字段: {source_field}")
            return []

        source_list = nested_data[source_field]
        if not isinstance(source_list, list):
            logger.warning(f"字段 {source_field} 不是列表类型")
            return []

        # 获取基础字段（除了源字段之外的所有字段）
        base_data = {k: v for k, v in nested_data.items() if k != source_field}
        
        # 展开为多行数据
        multi_row_data = []
        for item in source_list:
            if isinstance(item, dict):
                # 合并基础数据和行数据
                row_data = base_data.copy()
                row_data.update(item)
                
                # 应用字段映射
                if field_mapping:
                    mapped_row = {}
                    for key, value in row_data.items():
                        mapped_key = field_mapping.get(key, key)
                        mapped_row[mapped_key] = value
                    row_data = mapped_row
                
                multi_row_data.append(row_data)
        
        logger.debug(f"展开完成，生成行数: {len(multi_row_data)}")
        return multi_row_data
    
    def _auto_analyze_fields(self, multi_row_data: List[Dict[str, Any]]) -> tuple:
        """
        自动分析字段分类
        
        Args:
            multi_row_data: 多行数据列表
            
        Returns:
            (base_fields, row_fields) 元组
        """
        if not multi_row_data:
            return [], []
        
        # 获取所有字段
        all_fields = set()
        for row in multi_row_data:
            all_fields.update(row.keys())
        
        # 分析字段变化情况
        base_fields = []
        row_fields = []
        
        for field in all_fields:
            # 获取该字段在所有行中的值
            values = [row.get(field) for row in multi_row_data if field in row]
            unique_values = set(values)
            
            # 如果所有行的值都相同，认为是基础字段
            if len(unique_values) <= 1:
                base_fields.append(field)
            else:
                row_fields.append(field)
        
        logger.debug(f"自动分析完成 - 基础字段: {base_fields}, 变化字段: {row_fields}")
        return base_fields, row_fields
    
    def validate_data(self, data: Union[List[Dict], Dict], data_type: str = 'auto') -> bool:
        """
        验证数据格式是否符合预期结构

        Args:
            data (Union[List[Dict], Dict]): 要验证的数据，可以是多行列表或嵌套结构
            data_type (str, optional): 数据类型，'multi_row'表示多行列表，'nested'表示嵌套结构，'auto'表示自动判断. Defaults to 'auto'.

        Returns:
            bool: 数据格式是否有效，True表示格式正确，False表示格式错误

        Example:
            >>> extractor = MultiRowExtractor()
            >>> multi_row_data = [{"name": "A", "age": 20}, {"name": "B", "age": 25}]
            >>> extractor.validate_data(multi_row_data, 'multi_row')
            True
            >>> nested_data = {"name": "Product", "skus": [{"color": "red"}, {"color": "blue"}]}
            >>> extractor.validate_data(nested_data, 'nested')
            True
        """
        if data_type == 'auto':
            # 自动判断数据类型
            if isinstance(data, list):
                data_type = 'multi_row'
            elif isinstance(data, dict):
                data_type = 'nested'
            else:
                return False

        if data_type == 'multi_row':
            return self._validate_multi_row(data)
        elif data_type == 'nested':
            return self._validate_nested(data)
        
        return False
    
    def _validate_multi_row(self, data: List[Dict]) -> bool:
        """验证多行数据格式"""
        if not isinstance(data, list) or not data:
            return False
        
        for row in data:
            if not isinstance(row, dict):
                return False
        
        return True
    
    def _validate_nested(self, data: Dict) -> bool:
        """验证嵌套结构数据"""
        if not isinstance(data, dict):
            return False

        # 至少包含一个列表字段
        has_list_field = any(isinstance(v, list) for v in data.values())
        return has_list_field

    def batch_extract_to_nested(self,
                               large_data_list: List[Dict[str, Any]],
                               group_by_field: str,
                               target_field: str = 'skus',
                               row_fields: Optional[List[str]] = None,
                               base_fields: Optional[List[str]] = None,
                               field_mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        批量将大列表按指定字段分组，然后转换为嵌套格式

        Args:
            large_data_list: 大的数据列表
            group_by_field: 分组字段名（如"商品名称"）
            target_field: 目标字段名称，默认'skus'
            row_fields: 行字段列表（需要提取到skus里面的字段），必传
            base_fields: 基础字段列表（公共字段），可选，不传则自动计算
            field_mapping: 字段映射字典，用于重命名字段

        Returns:
            嵌套结构数据列表

        Example:
            large_data_list = [
                {"商品名称": "商品A", "颜色": "红色", "尺寸": "L", "价格": 199.0, "库存": 100},
                {"商品名称": "商品A", "颜色": "蓝色", "尺寸": "M", "价格": 189.0, "库存": 80},
                {"商品名称": "商品B", "颜色": "绿色", "尺寸": "S", "价格": 159.0, "库存": 50},
                {"商品名称": "商品B", "颜色": "黄色", "尺寸": "L", "价格": 169.0, "库存": 60},
                {"商品名称": "商品A", "颜色": "白色", "尺寸": "XL", "价格": 209.0, "库存": 30}
            ]

            result = extractor.batch_extract_to_nested(
                large_data_list,
                group_by_field='商品名称',
                target_field='skus',
                row_fields=['颜色', '尺寸', '价格', '库存']
            )

            # 结果：
            # [
            #     {
            #         "商品名称": "商品A",
            #         "skus": [
            #             {"颜色": "红色", "尺寸": "L", "价格": 199.0, "库存": 100},
            #             {"颜色": "蓝色", "尺寸": "M", "价格": 189.0, "库存": 80},
            #             {"颜色": "白色", "尺寸": "XL", "价格": 209.0, "库存": 30}
            #         ]
            #     },
            #     {
            #         "商品名称": "商品B",
            #         "skus": [
            #             {"颜色": "绿色", "尺寸": "S", "价格": 159.0, "库存": 50},
            #             {"颜色": "黄色", "尺寸": "L", "价格": 169.0, "库存": 60}
            #         ]
            #     }
            # ]
        """
        logger.debug(f"开始批量提取数据为嵌套结构，数据总数: {len(large_data_list)}, 分组字段: {group_by_field}")

        if not large_data_list:
            logger.warning("输入数据为空")
            return []

        if group_by_field not in large_data_list[0]:
            logger.error(f"分组字段 '{group_by_field}' 在数据中不存在")
            raise ValueError(f"分组字段 '{group_by_field}' 在数据中不存在")

        # 第一步：按指定字段分组
        grouped_data = self._group_by_field(large_data_list, group_by_field)
        logger.debug(f"分组完成，共 {len(grouped_data)} 个组")

        # 第二步：对每组数据调用现有的嵌套方法
        nested_results = []
        for group_value, group_data in grouped_data.items():
            logger.debug(f"处理分组: {group_value}, 数据量: {len(group_data)}")

            try:
                nested_result = self.extract_to_nested(
                    multi_row_data=group_data,
                    target_field=target_field,
                    row_fields=row_fields,
                    base_fields=base_fields,
                    field_mapping=field_mapping
                )

                if nested_result:
                    nested_results.append(nested_result)

            except Exception as e:
                logger.error(f"处理分组 '{group_value}' 时出错: {e}")
                continue

        logger.debug(f"批量提取完成，生成 {len(nested_results)} 个嵌套结构")
        return nested_results

    def _group_by_field(self, data_list: List[Dict[str, Any]], group_field: str) -> Dict[Any, List[Dict[str, Any]]]:
        """
        按指定字段对数据进行分组

        Args:
            data_list: 数据列表
            group_field: 分组字段名

        Returns:
            分组后的数据字典，key为分组值，value为该组的数据列表
        """
        grouped = {}

        for item in data_list:
            if group_field in item:
                group_value = item[group_field]

                if group_value not in grouped:
                    grouped[group_value] = []

                grouped[group_value].append(item)
            else:
                logger.warning(f"数据项缺少分组字段 '{group_field}': {item}")

        # 按分组值排序，确保结果的一致性
        sorted_grouped = dict(sorted(grouped.items()))

        logger.debug(f"分组统计: {[(k, len(v)) for k, v in sorted_grouped.items()]}")
        return sorted_grouped

    def get_group_statistics(self, data_list: List[Dict[str, Any]], group_field: str) -> Dict[str, Any]:
        """
        获取分组统计信息

        Args:
            data_list: 数据列表
            group_field: 分组字段名

        Returns:
            分组统计信息
        """
        if not data_list:
            return {"total_records": 0, "groups": {}, "group_count": 0}

        grouped = self._group_by_field(data_list, group_field)

        statistics = {
            "total_records": len(data_list),
            "group_count": len(grouped),
            "groups": {}
        }

        for group_value, group_data in grouped.items():
            statistics["groups"][group_value] = {
                "count": len(group_data),
                "percentage": round(len(group_data) / len(data_list) * 100, 2)
            }

        logger.debug(f"分组统计: 总记录数={statistics['total_records']}, 分组数={statistics['group_count']}")
        return statistics


