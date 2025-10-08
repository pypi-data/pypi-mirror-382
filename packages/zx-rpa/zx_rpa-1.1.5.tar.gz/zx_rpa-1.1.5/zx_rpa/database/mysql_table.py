import json
from typing import Dict, List, Any, Optional, Union
from collections import defaultdict
from loguru import logger


class MySQLConnection:
    """MySQL数据库连接管理器"""
    
    def __init__(self, host: str, user: str, password: str, database: str, 
                 port: int = 3306, charset: str = 'utf8mb4', **kwargs):
        """
        初始化MySQL连接
        
        Args:
            host: 数据库主机地址
            user: 用户名
            password: 密码
            database: 数据库名
            port: 端口号，默认3306
            charset: 字符集，默认utf8mb4
            **kwargs: 其他连接参数
        """
        logger.debug("初始化MySQL连接，主机: {}，数据库: {}", host, database)
        
        self._config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port,
            'charset': charset,
            **kwargs
        }
        self._connection = None
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            import pymysql
            self._connection = pymysql.connect(**self._config)
            logger.debug("MySQL连接建立成功")
        except ImportError as e:
            logger.error("pymysql库未安装: {}", str(e))
            raise ImportError("请安装pymysql库: pip install pymysql")
        except Exception as e:
            logger.error("MySQL连接失败: {}", str(e))
            raise
    
    def get_connection(self):
        """获取数据库连接对象"""
        if not self._connection or not self._connection.open:
            logger.debug("重新建立MySQL连接")
            self._connect()
        return self._connection
    
    def close(self):
        """关闭数据库连接"""
        if self._connection:
            self._connection.close()
            logger.debug("MySQL连接已关闭")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MySQLTable:
    """MySQL单表操作器"""
    
    def __init__(self, connection_or_config, table_name: str):
        """
        初始化表操作器
        
        Args:
            connection_or_config: 数据库连接对象或连接配置字典
            table_name: 表名
        """
        logger.debug("初始化MySQL表操作器，表名: {}", table_name)
        
        if isinstance(connection_or_config, dict):
            # 如果传入配置字典，创建连接管理器
            self._conn_manager = MySQLConnection(**connection_or_config)
            self._connection = self._conn_manager.get_connection()
            self._own_connection = True
        else:
            # 如果传入连接对象，直接使用
            self._connection = connection_or_config
            self._conn_manager = None
            self._own_connection = False
        
        self._table_name = table_name
        self._table_columns = None  # 缓存表字段列表

        # 初始化时获取表字段列表
        self._init_table_columns()

    def _init_table_columns(self):
        """
        初始化时获取表字段列表并缓存
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(f"DESCRIBE `{self._table_name}`")
            self._table_columns = [row[0] for row in cursor.fetchall()]
            logger.debug("缓存表 {} 字段列表: {}", self._table_name, self._table_columns)
        except Exception as e:
            logger.debug("获取表字段失败，将在运行时处理: {}", str(e))
            self._table_columns = []

    def _build_where_clause(self, where: Optional[Dict]) -> tuple:
        """
        构建WHERE子句
        
        Args:
            where: 条件字典
            
        Returns:
            tuple: (where_sql, params)
        """
        if not where:
            return "", []
        
        conditions = []
        params = []
        
        for key, value in where.items():
            if "__" in key:
                field, operator = key.split("__", 1)
                field = f"`{field}`"
                
                # 支持符号操作符和文字操作符
                if operator in [">=", "gte"]:
                    conditions.append(f"{field} >= %s")
                    params.append(value)
                elif operator in ["<=", "lte"]:
                    conditions.append(f"{field} <= %s")
                    params.append(value)
                elif operator in [">", "gt"]:
                    conditions.append(f"{field} > %s")
                    params.append(value)
                elif operator in ["<", "lt"]:
                    conditions.append(f"{field} < %s")
                    params.append(value)
                elif operator in ["!=", "ne"]:
                    conditions.append(f"{field} != %s")
                    params.append(value)
                elif operator in ["*", "like"]:
                    # 支持通配符转换：* -> %，? -> _
                    if "*" in str(value) or "?" in str(value):
                        value = str(value).replace("*", "%").replace("?", "_")
                    else:
                        # 无通配符时自动进行包含匹配
                        value = f"%{value}%"
                    conditions.append(f"{field} LIKE %s")
                    params.append(value)
                elif operator == "in":
                    if not isinstance(value, (list, tuple)):
                        raise ValueError("in操作符的值必须是列表或元组")
                    placeholders = ",".join(["%s"] * len(value))
                    conditions.append(f"{field} IN ({placeholders})")
                    params.extend(value)
                elif operator == "not_in":
                    if not isinstance(value, (list, tuple)):
                        raise ValueError("not_in操作符的值必须是列表或元组")
                    placeholders = ",".join(["%s"] * len(value))
                    conditions.append(f"{field} NOT IN ({placeholders})")
                    params.extend(value)
                elif operator == "isnull":
                    if value:
                        conditions.append(f"{field} IS NULL")
                    else:
                        conditions.append(f"{field} IS NOT NULL")
                else:
                    raise ValueError(f"不支持的操作符: {operator}")
            else:
                conditions.append(f"`{key}` = %s")
                params.append(value)
        
        where_sql = " AND ".join(conditions)
        return f"WHERE {where_sql}", params
    
    def _build_update_clause(self, data: Dict) -> tuple:
        """
        构建UPDATE SET子句

        Args:
            data: 更新数据字典

        Returns:
            tuple: (set_sql, params)
        """
        set_parts = []
        params = []

        for key, value in data.items():
            field = f"`{key}`"
            set_parts.append(f"{field} = %s")
            params.append(value)

        set_sql = ", ".join(set_parts)
        return set_sql, params

    def _serialize_json_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        JSON字段自动序列化处理

        Args:
            data: 原始数据字典

        Returns:
            Dict[str, Any]: 处理后的数据字典
        """
        processed_data = data.copy()

        for field, value in processed_data.items():
            if isinstance(value, (list, dict)):
                # 自动检测并序列化list和dict类型的字段
                processed_data[field] = json.dumps(value, ensure_ascii=False)
                logger.debug("自动JSON序列化字段 {}: {} -> {}", field, type(value).__name__, processed_data[field])

        return processed_data

    def _deserialize_json_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        JSON字段自动反序列化处理

        Args:
            data: 数据库查询结果字典

        Returns:
            Dict[str, Any]: 处理后的数据字典
        """
        processed_data = data.copy()

        for field, value in processed_data.items():
            if isinstance(value, str) and value is not None:
                # 尝试自动检测并反序列化JSON字符串
                if self._is_json_string(value):
                    try:
                        processed_data[field] = json.loads(value)
                        logger.debug("自动JSON反序列化字段 {}: str -> {}", field, type(processed_data[field]).__name__)
                    except json.JSONDecodeError:
                        # 反序列化失败，保持原值
                        pass

        return processed_data

    def _is_json_string(self, value: str) -> bool:
        """
        检测字符串是否为JSON格式

        Args:
            value: 要检测的字符串

        Returns:
            bool: 是否为JSON格式
        """
        if not isinstance(value, str) or len(value) < 2:
            return False

        # 简单检测：以 [ 或 { 开头，以 ] 或 } 结尾
        value = value.strip()
        return (value.startswith('[') and value.endswith(']')) or \
               (value.startswith('{') and value.endswith('}'))

    def _get_table_columns(self) -> List[str]:
        """
        获取数据库表的所有字段名（使用缓存）

        Returns:
            List[str]: 表字段名列表
        """
        if self._table_columns is None:
            # 如果缓存为空，重新获取
            self._init_table_columns()

        return self._table_columns or []

    def _filter_valid_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        过滤数据中的有效字段，忽略表中不存在的字段

        Args:
            data: 原始数据字典

        Returns:
            Dict[str, Any]: 过滤后的数据字典
        """
        table_columns = self._get_table_columns()

        if not table_columns:
            # 如果无法获取表字段，返回原数据
            logger.debug("无法获取表字段，跳过字段过滤")
            return data

        filtered_data = {}
        ignored_fields = []

        for key, value in data.items():
            if key in table_columns:
                filtered_data[key] = value
            else:
                ignored_fields.append(key)

        if ignored_fields:
            logger.debug("忽略不存在的字段: {}", ignored_fields)

        return filtered_data

    def _group_results(self, results: List[Dict], group_by: str) -> List[List[Dict]]:
        """
        按指定字段对查询结果进行分组

        Args:
            results: 查询结果列表
            group_by: 分组字段名

        Returns:
            List[List[Dict]]: 分组后的二维列表
        """
        if not results:
            logger.debug("查询结果为空，返回空分组列表")
            return []

        # 验证分组字段是否存在
        if group_by not in results[0]:
            available_fields = list(results[0].keys())
            raise ValueError(f"分组字段 '{group_by}' 不存在于查询结果中。可用字段: {available_fields}")

        # 使用有序字典保持分组顺序（按第一次出现的顺序）
        groups = {}
        group_order = []

        for record in results:
            group_value = record[group_by]
            # 将None值转换为字符串以便作为字典键
            group_key = str(group_value) if group_value is not None else "None"

            if group_key not in groups:
                groups[group_key] = []
                group_order.append(group_key)

            groups[group_key].append(record)

        # 按出现顺序返回分组结果
        grouped_results = [groups[key] for key in group_order]

        logger.debug("分组完成，按字段 '{}' 分为 {} 组，各组记录数: {}",
                    group_by, len(grouped_results), [len(group) for group in grouped_results])

        return grouped_results

    def insert(self, data: Union[Dict[str, Any], List[Dict[str, Any]]],
              ignore_extra_fields: bool = True) -> Union[int, List[int]]:
        """
        插入数据，支持单条或批量，自动JSON序列化，自动忽略多余字段

        Args:
            data: 要插入的数据字典或字典列表
            ignore_extra_fields: 是否忽略表中不存在的字段，默认True

        Returns:
            Union[int, List[int]]: 单条插入返回ID，批量插入返回ID列表

        Example:
            >>> # 插入包含JSON字段和多余字段的数据
            >>> data = {'name': '商品', '分类': ['服装', '女装'], '多余字段': 'value'}
            >>> table.insert(data, ignore_extra_fields=True)  # 自动处理JSON和多余字段
        """
        if isinstance(data, list):
            return self._batch_insert(data, ignore_extra_fields)
        else:
            return self._single_insert(data, ignore_extra_fields)

    def _single_insert(self, data: Dict[str, Any], ignore_extra_fields: bool = True) -> int:
        """插入单条数据"""
        if not data:
            raise ValueError("插入数据不能为空")

        # 字段过滤处理
        if ignore_extra_fields:
            filtered_data = self._filter_valid_fields(data)
        else:
            filtered_data = data

        # JSON字段自动序列化处理
        processed_data = self._serialize_json_fields(filtered_data)
        logger.debug("插入数据到表 {}，记录数: 1", self._table_name)

        try:
            fields = list(processed_data.keys())
            values = list(processed_data.values())

            fields_sql = ", ".join(f"`{field}`" for field in fields)
            placeholders = ", ".join(["%s"] * len(values))

            sql = f"INSERT INTO `{self._table_name}` ({fields_sql}) VALUES ({placeholders})"

            cursor = self._connection.cursor()
            cursor.execute(sql, values)
            self._connection.commit()

            insert_id = cursor.lastrowid
            logger.debug("数据插入成功，插入ID: {}，SQL: {}", insert_id, sql)
            return insert_id

        except Exception as e:
            self._connection.rollback()
            logger.error("数据插入失败，表: {}，错误: {}", self._table_name, str(e))
            raise

    def _batch_insert(self, data_list: List[Dict[str, Any]], ignore_extra_fields: bool = True) -> List[int]:
        """批量插入数据"""
        if not data_list:
            raise ValueError("批量插入数据不能为空")

        # 字段过滤和JSON字段自动序列化处理
        processed_data_list = []
        for data in data_list:
            # 字段过滤处理
            if ignore_extra_fields:
                filtered_data = self._filter_valid_fields(data)
            else:
                filtered_data = data

            # JSON字段自动序列化处理
            processed_data = self._serialize_json_fields(filtered_data)
            processed_data_list.append(processed_data)

        logger.debug("批量插入数据到表 {}，记录数量: {}", self._table_name, len(processed_data_list))

        # 验证所有记录的字段一致性
        first_keys = set(processed_data_list[0].keys())
        for i, record in enumerate(processed_data_list[1:], 1):
            if set(record.keys()) != first_keys:
                raise ValueError(f"第{i+1}条记录的字段与第1条不一致")

        try:
            fields = list(first_keys)
            fields_sql = ", ".join(f"`{field}`" for field in fields)
            placeholders = ", ".join(["%s"] * len(fields))

            sql = f"INSERT INTO `{self._table_name}` ({fields_sql}) VALUES ({placeholders})"

            # 准备批量数据
            values_list = []
            for record in processed_data_list:
                values_list.append([record[field] for field in fields])

            cursor = self._connection.cursor()
            cursor.executemany(sql, values_list)
            self._connection.commit()

            # 获取插入的ID列表（MySQL特性）
            first_id = cursor.lastrowid
            if first_id:
                insert_ids = list(range(first_id, first_id + len(data_list)))
            else:
                insert_ids = [0] * len(data_list)  # 表没有自增ID

            logger.debug("批量插入成功，插入记录数: {}，起始ID: {}，SQL: {}",
                        len(data_list), first_id, sql)
            return insert_ids

        except Exception as e:
            self._connection.rollback()
            logger.error("批量插入失败，表: {}，错误: {}", self._table_name, str(e))
            raise

    def select(self, where: Optional[Dict] = None, fields: Optional[List[str]] = None,
               order_by: Optional[Dict[str, str]] = None, limit: Optional[int] = None,
               offset: Optional[int] = None, group_by: Optional[str] = None) -> Union[List[Dict], List[List[Dict]]]:
        """
        查询数据，自动反序列化JSON字段，支持按字段分组

        Args:
            where: 查询条件字典
            fields: 要查询的字段列表
            order_by: 排序字典，如 {"created_at": "DESC", "id": "ASC"}
            limit: 限制返回记录数
            offset: 偏移量
            group_by: 分组字段名，如果指定则按该字段值分组返回二维列表

        Returns:
            Union[List[Dict], List[List[Dict]]]:
                - 不分组时返回 List[Dict]: 查询结果列表
                - 分组时返回 List[List[Dict]]: 外层列表是分组，内层列表是每组的记录

        Example:
            >>> # 普通查询
            >>> results = table.select(where={'status': 'active'})
            >>> print(len(results))  # 返回记录数

            >>> # 按分类字段分组查询
            >>> grouped_results = table.select(where={'status': 'active'}, group_by='category')
            >>> print(len(grouped_results))  # 返回分组数
            >>> print(len(grouped_results[0]))  # 第一组的记录数
        """
        logger.debug("查询表 {}，条件: {}，字段: {}，排序: {}，限制: {}，分组: {}",
                    self._table_name, where, fields, order_by, limit, group_by)

        try:
            # 构建字段部分
            if fields:
                fields_sql = ", ".join(f"`{field}`" for field in fields)
            else:
                fields_sql = "*"

            # 构建WHERE子句
            where_sql, where_params = self._build_where_clause(where)

            # 构建ORDER BY子句
            order_sql = ""
            if order_by:
                order_parts = []
                for field, direction in order_by.items():
                    direction = direction.upper()
                    if direction not in ["ASC", "DESC"]:
                        raise ValueError(f"排序方向必须是ASC或DESC: {direction}")
                    order_parts.append(f"`{field}` {direction}")
                order_sql = f"ORDER BY {', '.join(order_parts)}"

            # 构建LIMIT子句
            limit_sql = ""
            if limit is not None:
                limit_sql = f"LIMIT {int(limit)}"
                if offset is not None:
                    limit_sql += f" OFFSET {int(offset)}"

            # 组装完整SQL
            sql_parts = [f"SELECT {fields_sql} FROM `{self._table_name}`"]
            if where_sql:
                sql_parts.append(where_sql)
            if order_sql:
                sql_parts.append(order_sql)
            if limit_sql:
                sql_parts.append(limit_sql)

            sql = " ".join(sql_parts)

            cursor = self._connection.cursor()
            cursor.execute(sql, where_params)

            # 获取字段名
            columns = [desc[0] for desc in cursor.description]

            # 转换为字典列表
            results = []
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                # JSON字段自动反序列化处理
                processed_row = self._deserialize_json_fields(row_dict)
                results.append(processed_row)

            # 处理分组逻辑
            if group_by is not None:
                return self._group_results(results, group_by)

            logger.debug("查询完成，返回记录数: {}，SQL: {}", len(results), sql)
            return results

        except Exception as e:
            logger.error("数据查询失败，表: {}，错误: {}", self._table_name, str(e))
            raise

    def update(self, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """
        更新数据

        Args:
            data: 要更新的数据字典
            where: 更新条件字典

        Returns:
            int: 影响的行数
        """
        logger.debug("更新表 {}，更新数据: {}，条件: {}",
                    self._table_name, data, where)

        if not data:
            raise ValueError("更新数据不能为空")
        if not where:
            raise ValueError("更新条件不能为空，防止误操作")

        try:
            # 构建SET子句
            set_sql, set_params = self._build_update_clause(data)

            # 构建WHERE子句
            where_sql, where_params = self._build_where_clause(where)

            # 组装完整SQL
            sql = f"UPDATE `{self._table_name}` SET {set_sql} {where_sql}"
            params = set_params + where_params

            cursor = self._connection.cursor()
            cursor.execute(sql, params)
            self._connection.commit()

            affected_rows = cursor.rowcount
            logger.debug("数据更新成功，影响行数: {}，SQL: {}", affected_rows, sql)
            return affected_rows

        except Exception as e:
            self._connection.rollback()
            logger.error("数据更新失败，表: {}，错误: {}", self._table_name, str(e))
            raise

    def delete(self, where: Dict[str, Any]) -> int:
        """
        删除数据

        Args:
            where: 删除条件字典

        Returns:
            int: 删除的行数
        """
        logger.debug("删除表 {} 数据，条件: {}", self._table_name, where)

        if not where:
            raise ValueError("删除条件不能为空，防止误操作")

        try:
            # 构建WHERE子句
            where_sql, where_params = self._build_where_clause(where)

            # 组装完整SQL
            sql = f"DELETE FROM `{self._table_name}` {where_sql}"

            cursor = self._connection.cursor()
            cursor.execute(sql, where_params)
            self._connection.commit()

            deleted_rows = cursor.rowcount
            logger.debug("数据删除成功，删除行数: {}，SQL: {}", deleted_rows, sql)
            return deleted_rows

        except Exception as e:
            self._connection.rollback()
            logger.error("数据删除失败，表: {}，错误: {}", self._table_name, str(e))
            raise

    def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        """
        统计记录数

        Args:
            where: 统计条件字典

        Returns:
            int: 记录数量
        """
        logger.debug("统计表 {} 记录数，条件数量: {}", self._table_name, len(where) if where else 0)

        try:
            # 构建WHERE子句
            where_sql, where_params = self._build_where_clause(where)

            # 组装完整SQL
            sql = f"SELECT COUNT(*) FROM `{self._table_name}`"
            if where_sql:
                sql += f" {where_sql}"

            cursor = self._connection.cursor()
            cursor.execute(sql, where_params)

            count_result = cursor.fetchone()[0]
            logger.debug("统计完成，记录数: {}", count_result)
            return count_result

        except Exception as e:
            logger.error("记录统计失败，表: {}，错误: {}", self._table_name, str(e))
            raise

    def exists(self, where: Dict[str, Any]) -> bool:
        """
        检查记录是否存在

        Args:
            where: 查询条件字典

        Returns:
            bool: 是否存在
        """
        logger.debug("检查记录是否存在，表: {}，条件: {}", self._table_name, where)
        exists = self.count(where) > 0
        logger.debug("存在性检查完成，结果: {}", exists)
        return exists

    def get_one(self, where: Dict[str, Any], fields: Optional[List[str]] = None) -> Optional[Dict]:
        """
        获取单条记录，自动反序列化JSON字段

        Args:
            where: 查询条件字典
            fields: 要查询的字段列表

        Returns:
            Optional[Dict]: 查询结果，不存在时返回None，JSON字段自动反序列化
        """
        results = self.select(where=where, fields=fields, limit=1)
        return results[0] if results else None

    def insert_or_update(self, data: Dict[str, Any], where: Dict[str, Any]) -> tuple:
        """
        插入或更新数据（如果存在则更新，不存在则插入），自动处理JSON字段

        Args:
            data: 数据字典
            where: 查询条件字典

        Returns:
            tuple: (操作类型, 结果) - ("insert", insert_id) 或 ("update", affected_rows)
        """
        if self.exists(where):
            affected_rows = self.update(data, where)
            return ("update", affected_rows)
        else:
            # 合并where条件到data中进行插入
            insert_data = {**where, **data}
            insert_id = self.insert(insert_data)
            return ("insert", insert_id)

    def execute(self, sql: str, params: Optional[List] = None) -> List[Dict]:
        """
        执行原生SQL语句

        Args:
            sql: SQL语句，支持参数化查询
            params: 参数列表，防止SQL注入

        Returns:
            List[Dict]: 查询结果列表，对于非查询语句返回空列表
        """
        logger.debug("执行原生SQL，语句长度: {}", len(sql))

        if params is None:
            params = []

        try:
            cursor = self._connection.cursor()
            cursor.execute(sql, params)

            # 判断是否为查询语句
            sql_upper = sql.strip().upper()
            if sql_upper.startswith('SELECT') or sql_upper.startswith('SHOW') or sql_upper.startswith('DESCRIBE'):
                # 查询语句，返回结果
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                logger.debug("SQL执行成功，返回记录数: {}", len(results))
                return results
            else:
                # 非查询语句，提交事务
                self._connection.commit()
                affected_rows = cursor.rowcount
                logger.debug("SQL执行成功，影响行数: {}", affected_rows)
                return []

        except Exception as e:
            if not sql_upper.startswith('SELECT'):
                self._connection.rollback()
            logger.error("SQL执行失败，错误: {}", str(e))
            raise

    def close(self):
        """关闭数据库连接"""
        if self._own_connection and self._conn_manager:
            self._conn_manager.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        # 参数用于上下文管理器协议，不需要使用
        return False



