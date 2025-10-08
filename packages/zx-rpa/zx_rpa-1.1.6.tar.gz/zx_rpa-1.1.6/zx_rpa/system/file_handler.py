"""
文件处理器模块

提供文件读取功能
"""

from pathlib import Path
from typing import List, Union
from loguru import logger


class FileHandler:
    """文件处理器 操作文件的"""
    
    def __init__(self):
        """初始化文件处理器"""
        logger.debug("初始化文件处理器")
    
    def read_txt_to_list(
        self, 
        file_path: Union[str, Path], 
        strip: bool = True, 
        skip_empty: bool = True, 
        remove_duplicates: bool = False
    ) -> List[str]:
        """
        读取txt文件内容并转换为列表
        
        Args:
            file_path (str | Path): 文件路径，支持字符串或Path对象
            strip (bool): 是否去除每行首尾的空白字符，默认为True
            skip_empty (bool): 是否跳过空行和只包含空白字符的行，默认为True
            remove_duplicates (bool): 是否去除重复行，默认为False
            
        Returns:
            list: 文件内容列表
            
        Raises:
            FileNotFoundError: 当文件不存在时抛出异常
            Exception: 当读取文件失败时抛出异常
        """
        logger.debug("开始读取文本文件: {}，strip: {}，skip_empty: {}，remove_duplicates: {}", 
                    file_path, strip, skip_empty, remove_duplicates)
        
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.error("文件不存在: {}", file_path)
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            if not path.is_file():
                logger.error("路径不是文件: {}", file_path)
                raise ValueError(f"路径不是文件: {file_path}")
                
            with path.open('r', encoding='utf-8') as f:
                lines = f.readlines()
            
            logger.debug("文件读取完成，原始行数: {}", len(lines))
            
            # 处理每行数据
            if strip:
                lines = [line.strip('\r\n\t ') for line in lines]
                logger.debug("去除空白字符完成")
            
            if skip_empty:
                original_count = len(lines)
                lines = [line for line in lines if line and not line.isspace()]
                logger.debug("跳过空行完成，过滤掉{}行", original_count - len(lines))
            
            if remove_duplicates:
                original_count = len(lines)
                seen = set()
                lines = [line for line in lines if not (line in seen or seen.add(line))]
                logger.debug("去重完成，去除{}行重复", original_count - len(lines))
            
            logger.debug("文本文件处理完成，最终行数: {}", len(lines))
            return lines
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error("读取文件{}失败: {}", file_path, str(e))
            raise Exception(f"读取文件 {file_path} 失败: {str(e)}")
    

