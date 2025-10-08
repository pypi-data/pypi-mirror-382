"""
Excel数据过滤处理器
提供类似MySQL的where条件过滤功能
"""

from typing import Dict, List, Any, Optional
from loguru import logger


class ExcelFilterProcessor:
    """Excel数据过滤处理器，提供类似MySQL的where条件过滤"""

    def __init__(self):
        """初始化过滤处理器"""
        logger.debug("初始化Excel过滤处理器")

    def filter_data(self, data: List[Dict[str, Any]], where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        过滤数据，支持where条件
        
        Args:
            data: 要过滤的数据列表
            where: where条件字典（类似MySQL）
            
        Returns:
            List[Dict]: 过滤后的数据列表
        """
        if not data or not where:
            return data.copy()
        
        result = []
        for row in data:
            if self._match_where_conditions(row, where):
                result.append(row)
        
        logger.debug("数据过滤完成，原始{}行，过滤后{}行，过滤条件: {}", len(data), len(result), where)
        return result

    def _match_where_conditions(self, row: Dict[str, Any], where: Dict[str, Any]) -> bool:
        """
        检查单行数据是否匹配where条件
        
        Args:
            row: 单行数据字典
            where: where条件字典
            
        Returns:
            bool: 是否匹配所有条件
        """
        for key, value in where.items():
            if not self._match_single_condition(row, key, value):
                return False
        return True

    def _match_single_condition(self, row: Dict[str, Any], key: str, value: Any) -> bool:
        """
        检查单个条件是否匹配

        Args:
            row: 单行数据字典
            key: 条件键（可能包含操作符）
            value: 条件值

        Returns:
            bool: 是否匹配条件
        """
        # 检查双下划线格式的操作符：field__>=, field__like等
        if "__" in key:
            field, operator = key.split("__", 1)
        else:
            # 简单相等比较
            return row.get(key) == value

        field_value = row.get(field)

        # 处理None值
        if field_value is None:
            return value is None if operator in ["eq", "="] else False

        try:
            if operator in ["gte", ">="]:
                return self._safe_compare(field_value, value, ">=")
            elif operator in ["lte", "<="]:
                return self._safe_compare(field_value, value, "<=")
            elif operator in ["gt", ">"]:
                return self._safe_compare(field_value, value, ">")
            elif operator in ["lt", "<"]:
                return self._safe_compare(field_value, value, "<")
            elif operator in ["ne", "!="]:
                return field_value != value
            elif operator in ["like", "*"]:
                return self._match_wildcard_pattern(field_value, value)
            elif operator == "in":
                if not isinstance(value, (list, tuple)):
                    raise ValueError("in操作符的值必须是列表或元组")
                return field_value in value
            elif operator == "not_in":
                if not isinstance(value, (list, tuple)):
                    raise ValueError("not_in操作符的值必须是列表或元组")
                return field_value not in value
            elif operator == "isnull":
                return (field_value is None or field_value == "") if value else (field_value is not None and field_value != "")
            else:
                logger.debug("不支持的操作符: {}", operator)
                raise ValueError(f"不支持的操作符: {operator}")
        except Exception as e:
            logger.debug("条件匹配失败: {} {} {}, 错误: {}", field, operator, value, str(e))
            return False

    def _safe_compare(self, field_value: Any, compare_value: Any, operator: str) -> bool:
        """
        安全的数值比较
        
        Args:
            field_value: 字段值
            compare_value: 比较值
            operator: 比较操作符
            
        Returns:
            bool: 比较结果
        """
        try:
            # 尝试转换为数字进行比较
            if isinstance(field_value, (int, float)) and isinstance(compare_value, (int, float)):
                if operator == ">=":
                    return field_value >= compare_value
                elif operator == "<=":
                    return field_value <= compare_value
                elif operator == ">":
                    return field_value > compare_value
                elif operator == "<":
                    return field_value < compare_value
            
            # 尝试转换为字符串进行比较
            field_str = str(field_value) if field_value is not None else ""
            compare_str = str(compare_value) if compare_value is not None else ""
            
            if operator == ">=":
                return field_str >= compare_str
            elif operator == "<=":
                return field_str <= compare_str
            elif operator == ">":
                return field_str > compare_str
            elif operator == "<":
                return field_str < compare_str
                
        except Exception:
            return False
        
        return False

    def _match_wildcard_pattern(self, field_value: Any, pattern: Any) -> bool:
        """
        匹配通配符模式（新的简化版本）

        Args:
            field_value: 字段值
            pattern: 匹配模式，支持 * 和 ? 通配符

        Returns:
            bool: 是否匹配
        """
        if field_value is None:
            return False

        field_str = str(field_value)
        pattern_str = str(pattern)

        # 如果没有通配符，直接进行包含匹配
        if '*' not in pattern_str and '?' not in pattern_str:
            return pattern_str in field_str

        # 使用正则表达式处理通配符
        import re
        # 转义正则表达式特殊字符，但保留*和?
        escaped = re.escape(pattern_str)
        escaped = escaped.replace(r'\*', '.*').replace(r'\?', '.')
        return bool(re.search(escaped, field_str))

    def _match_like_pattern(self, field_value: Any, pattern: Any, operator: str) -> bool:
        """
        匹配LIKE模式
        
        Args:
            field_value: 字段值
            pattern: 匹配模式
            operator: 操作符类型
            
        Returns:
            bool: 是否匹配
        """
        if field_value is None:
            return False
        
        field_str = str(field_value)
        pattern_str = str(pattern)
        
        if operator == "*":
            # 支持通配符：* -> 任意字符，? -> 单个字符
            import re
            escaped = re.escape(pattern_str)
            escaped = escaped.replace(r'\*', '.*').replace(r'\?', '.')
            return bool(re.match(f"^{escaped}$", field_str))
        elif operator == "like":
            # SQL LIKE模式：% -> 任意字符，_ -> 单个字符
            import re
            escaped = re.escape(pattern_str)
            escaped = escaped.replace(r'\%', '.*').replace(r'\_', '.')
            return bool(re.match(f"^{escaped}$", field_str))
        
        return False
