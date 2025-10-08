"""
数据处理模块 - 提供数据转换、验证、清洗等处理功能

## 引入方式
```python
# 多行列表数据提取器
from zx_rpa.data_handle import MultiRowExtractor
extractor = MultiRowExtractor()
nested_data = extractor.extract_to_nested(multi_row_data, target_field='items', row_fields=['颜色', '价格'])

# 列表处理工具
from zx_rpa.data_handle import ListUtils
list_utils = ListUtils()
result = list_utils.split_list_to_2d([1,2,3,4,5], 2, keep_remainder=True)
```

## 对外方法

### MultiRowExtractor（多行列表数据提取器）
- extract_to_nested(multi_row_data, target_field='items', row_fields=None, base_fields=None, field_mapping=None) -> dict - 多行列表转嵌套结构
- expand_from_nested(nested_data, source_field='skus', field_mapping=None) -> List[dict] - 嵌套结构转多行列表
- validate_data(data, data_type='auto') -> bool - 验证数据格式
- batch_extract_to_nested(large_data_list, group_by_field, target_field='items', row_fields=None, base_fields=None, field_mapping=None) -> List[dict] - 批量多行列表转嵌套结构

### ListUtils（列表处理工具）
- split_list_to_2d(input_list, sub_length, keep_remainder=True) -> List[List[Any]] - 将一维列表转换为二维列表
- list_to_string(input_list, separator=",") -> str - 将列表转换为字符串
- string_to_list(input_string, separator=",", strip_items=True) -> List[str] - 将字符串转换为列表


"""

from .multi_row_extractor import MultiRowExtractor
from .list_utils import ListUtils

__all__ = ["MultiRowExtractor", "ListUtils"]
