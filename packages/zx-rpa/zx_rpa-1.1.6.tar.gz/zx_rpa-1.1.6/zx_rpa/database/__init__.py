"""
数据库操作模块 - 提供简洁易用的数据库连接和操作服务

## 引入方式
```python
from zx_rpa.database import DatabaseManager

# 创建专用数据库客户端（配置一次，多次使用）
mysql = DatabaseManager.mysql(
    host='localhost',
    user='root',
    password='123456',
    database='test_db'
)

# 简洁的表操作
users_table = mysql.table('users')
data = users_table.select({'age__>=': 18})

# 执行原生SQL
result = mysql.execute("SELECT * FROM users WHERE age > %s", (18,))
```

## 模块结构
- database_manager.py - 对外接口，工厂类
- mysql_client.py - MySQL客户端实现
- mysql_table.py - MySQL表操作实现（保持不变）

## 对外方法
### DatabaseManager（数据库管理器工厂类）
#### 工厂方法
- mysql(host, user, password, database, port=3306, charset='utf8mb4', **kwargs) -> MySQLClient - 创建MySQL客户端
- sqlite(database_path, **kwargs) -> SQLiteClient - 创建SQLite客户端（预留）
- mongodb(connection_string, database, **kwargs) -> MongoClient - 创建MongoDB客户端（预留）

### 专用客户端类
#### MySQLClient
- table(table_name) -> MySQLTable - 获取表操作对象
- execute(sql, params=None) -> list - 执行原生SQL语句
- close() -> bool - 关闭数据库连接
- get_connection_info() -> dict - 获取连接信息

### 表操作类（通过客户端获取）
通过 `mysql.table('table_name')` 获取的 MySQLTable 对象支持：
- insert(data) -> int|List[int] - 插入数据，支持单条或批量
- select(where, fields, order_by, limit, offset) -> List[Dict] - 查询数据
- update(data, where) -> int - 更新数据
- delete(where) -> int - 删除数据
- count(where) -> int - 统计记录数
- exists(where) -> bool - 检查记录是否存在
- get_one(where, fields) -> Dict|None - 获取单条记录
- insert_or_update(data, where) -> tuple - 插入或更新
- close() -> bool - 关闭数据库连接
- execute(sql, params) -> List[Dict] - 执行原生SQL语句

## Where条件操作符使用说明
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


"""

# 导出工厂类
from .database_manager import DatabaseManager

__all__ = ['DatabaseManager']
