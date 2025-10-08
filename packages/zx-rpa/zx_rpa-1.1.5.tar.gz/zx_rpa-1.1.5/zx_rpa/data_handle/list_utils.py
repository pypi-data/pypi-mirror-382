"""
列表处理工具模块

提供各种列表数据处理和转换功能
"""

from typing import List, Any
from loguru import logger


class ListUtils:
    """列表处理工具类"""

    def __init__(self):
        """初始化列表处理工具"""
        logger.debug("初始化列表处理工具")

    def split_list_to_2d(
        self,
        input_list: List[Any],
        sub_length: int,
        keep_remainder: bool = True
    ) -> List[List[Any]]:
        """
        将一维列表转换为二维列表

        Args:
            input_list (List[Any]): 需要转换的输入一维列表
            sub_length (int): 每个子列表的长度
            keep_remainder (bool, optional): 是否保留不足sub_length长度的剩余元素. 默认为True

        Returns:
            List[List[Any]]: 转换后的二维列表
                例如:
                input_list=[1,2,3,4,5], sub_length=2, keep_remainder=True
                返回 [[1,2], [3,4], [5]]

        Raises:
            ValueError: 当input_list为空列表，或sub_length小于等于0时抛出异常
        """
        logger.debug("开始列表分割，输入长度: {}，子列表长度: {}，保留余数: {}",
                    len(input_list), sub_length, keep_remainder)

        # 参数验证
        if not input_list:
            logger.error("输入列表不能为空")
            raise ValueError("输入列表不能为空")

        if sub_length <= 0:
            logger.error("子列表长度必须大于0，当前值: {}", sub_length)
            raise ValueError("子列表长度必须大于0")

        result = []

        # 计算可以完整分割的子列表
        for i in range(0, len(input_list), sub_length):
            if i + sub_length <= len(input_list):
                result.append(input_list[i:i + sub_length])
            # 处理剩余元素
            elif keep_remainder:
                result.append(input_list[i:])

        logger.debug("列表分割完成，生成{}个子列表", len(result))
        return result

    def list_to_string(
        self,
        input_list: List[Any],
        separator: str = ","
    ) -> str:
        """
        将列表转换为字符串

        Args:
            input_list (List[Any]): 需要转换的输入列表
            separator (str, optional): 分隔符，默认为逗号

        Returns:
            str: 转换后的字符串
                例如:
                input_list=['A', 'B', 'C'], separator=','
                返回 'A,B,C'

        Raises:
            ValueError: 当input_list不是列表类型时抛出异常
        """
        logger.debug("开始列表转字符串，输入长度: {}，分隔符: '{}'",
                    len(input_list) if isinstance(input_list, list) else 0, separator)

        # 参数验证
        if not isinstance(input_list, list):
            logger.error("输入必须是列表类型，当前类型: {}", type(input_list).__name__)
            raise ValueError("输入必须是列表类型")

        if not input_list:
            logger.debug("输入列表为空，返回空字符串")
            return ""

        try:
            # 将列表元素转换为字符串并用分隔符连接
            result = separator.join(str(item) for item in input_list)
            logger.debug("列表转字符串完成，结果长度: {}", len(result))
            return result
        except Exception as e:
            logger.error("列表转字符串失败: {}", str(e))
            raise

    def string_to_list(
        self,
        input_string: str,
        separator: str = ",",
        strip_items: bool = True
    ) -> List[str]:
        """
        将字符串转换为列表

        Args:
            input_string (str): 需要转换的输入字符串
            separator (str, optional): 分隔符，默认为逗号
            strip_items (bool, optional): 是否去除每个元素的首尾空格，默认为True

        Returns:
            List[str]: 转换后的字符串列表
                例如:
                input_string='A,B,C', separator=','
                返回 ['A', 'B', 'C']

        Raises:
            ValueError: 当input_string不是字符串类型时抛出异常
        """
        logger.debug("开始字符串转列表，输入长度: {}，分隔符: '{}'，去除空格: {}",
                    len(input_string) if isinstance(input_string, str) else 0,
                    separator, strip_items)

        # 参数验证
        if not isinstance(input_string, str):
            logger.error("输入必须是字符串类型，当前类型: {}", type(input_string).__name__)
            raise ValueError("输入必须是字符串类型")

        if not input_string:
            logger.debug("输入字符串为空，返回空列表")
            return []

        try:
            # 按分隔符分割字符串
            result = input_string.split(separator)

            # 可选：去除每个元素的首尾空格
            if strip_items:
                result = [item.strip() for item in result]

            logger.debug("字符串转列表完成，生成{}个元素", len(result))
            return result
        except Exception as e:
            logger.error("字符串转列表失败: {}", str(e))
            raise
