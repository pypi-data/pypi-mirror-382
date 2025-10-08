"""
MySQL数据库客户端
专注于MySQL数据库的连接和表操作
"""

from loguru import logger
from typing import Dict, Any
from .mysql_table import MySQLConnection, MySQLTable


class MySQLClient:
    """MySQL数据库客户端"""

    def __init__(self, host: str, user: str, password: str, database: str, 
                 port: int = 3306, charset: str = 'utf8mb4', **kwargs):
        """
        初始化MySQL客户端

        Args:
            host: 数据库主机地址
            user: 用户名
            password: 密码
            database: 数据库名
            port: 端口号，默认3306
            charset: 字符集，默认utf8mb4
            **kwargs: 其他连接参数
        """
        logger.debug("初始化MySQL数据库客户端，主机: {}，数据库: {}", host, database)
        
        if not all([host, user, password, database]):
            logger.error("MySQL连接参数不能为空")
            raise ValueError("MySQL连接参数不能为空")

        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.charset = charset
        self.kwargs = kwargs
        
        # 创建数据库连接
        self._connection = MySQLConnection(host, user, password, database, port, charset, **kwargs)

    def table(self, table_name: str) -> MySQLTable:
        """
        获取表操作对象

        Args:
            table_name: 表名

        Returns:
            MySQLTable: 表操作对象
        """
        logger.debug("获取MySQL表操作对象: {}", table_name)
        
        if not table_name:
            logger.error("表名不能为空")
            raise ValueError("表名不能为空")

        return MySQLTable(self._connection.get_connection(), table_name)

    def execute(self, sql: str, params: tuple = None) -> list:
        """
        执行原生SQL语句

        Args:
            sql: SQL语句
            params: 参数元组

        Returns:
            list: 查询结果列表
        """
        logger.debug("执行原生SQL语句")
        
        # 创建临时表对象来执行SQL
        temp_table = MySQLTable(self._connection.get_connection(), "temp")
        return temp_table.execute(sql, params)

    def close(self) -> bool:
        """
        关闭数据库连接

        Returns:
            bool: 关闭是否成功
        """
        logger.debug("关闭MySQL数据库连接")
        
        try:
            if self._connection:
                return self._connection.close()
            return True
        except Exception as e:
            logger.error("关闭MySQL连接失败: {}", str(e))
            return False

    def get_connection_info(self) -> Dict[str, Any]:
        """
        获取连接信息

        Returns:
            Dict: 连接信息
        """
        return {
            "host": self.host,
            "user": self.user,
            "database": self.database,
            "port": self.port,
            "charset": self.charset
        }
