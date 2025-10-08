"""
Excel表格处理模块 - 提供Excel读写、数据操作功能

## 引入方式
```python
from zx_rpa.excel import ExcelHandler

# Excel处理器（默认检查文件占用）
handler = ExcelHandler("data.xlsx")

# 跳过文件占用检查（提升性能）
handler = ExcelHandler("data.xlsx", check_file_lock=False)

data = handler.select()
handler.insert({"姓名": "张三", "年龄": 25})
handler.update({"年龄": 26}, where={"姓名": "张三"})
```

## 对外方法
### 数据操作（类似MySQL接口）
- select(where=None, fields=None, order_by=None, limit=None, sheet_name=None) -> List[Dict] - 查询数据
- insert(data, sheet_name=None, auto_save=True) -> Union[int, List[int]] - 插入数据
- update(data, where, sheet_name=None, auto_save=True) -> int - 更新数据
- delete(where, sheet_name=None, auto_save=True) -> int - 删除数据
- exists(where, sheet_name=None) -> bool - 判断数据是否存在

### 文件操作
- save() - 保存文件
- close() - 关闭工作簿

### 原生对象操作
- get_workbook() -> Workbook - 获取原生openpyxl工作簿对象
- get_worksheet(sheet_name=None) -> Worksheet - 获取原生openpyxl工作表对象
- sync_from_workbook() - 同步原生工作簿修改


## Where条件操作符
- 相等: {"name": "张三"}
- 大于等于: {"age__>=": 18} 或 {"age__gte": 18}
- 小于等于: {"age__<=": 60} 或 {"age__lte": 60}
- 大于: {"age__>": 18} 或 {"age__gt": 18}
- 小于: {"age__<": 60} 或 {"age__lt": 60}
- 不等于: {"age__!=": 25} 或 {"age__ne": 25}
- 通配符匹配: {"name__*": "张"} 或 {"name__like": "张"}  # 包含"张"，支持*和?通配符
- 在列表中: {"status__in": ["完成", "进行中"]}
- 不在列表中: {"status__not_in": ["取消"]}
- 是否为空: {"remark__isnull": True}
- 行号条件: {"index__>=": 5}  # index为虚拟字段，表示Excel行号

"""

from .excel_handler import ExcelHandler

__all__ = ['ExcelHandler']
