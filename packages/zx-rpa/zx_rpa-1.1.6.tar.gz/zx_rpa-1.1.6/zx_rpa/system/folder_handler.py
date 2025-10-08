"""
文件夹处理器模块

提供文件夹创建和管理功能
"""

import re
from pathlib import Path
from typing import Union, List, Optional
from loguru import logger


class FolderHandler:
    """文件夹处理器 获取文件夹内部信息和操作文件夹"""
    
    def __init__(self):
        """初始化文件夹处理器"""
        logger.debug("初始化文件夹处理器")
    
    def create_output_folder_with_suffix(
        self, folder_path: Union[str, Path], suffix: str = "_输出"
    ) -> str:
        """
        创建同级同名加指定后缀的新文件夹
        
        Args:
            folder_path (Union[str, Path]): 原文件夹路径，可以是字符串或Path对象
            suffix (str, optional): 新文件夹名称后缀，默认为"_输出". Defaults to "_输出".
            
        Returns:
            str: 创建的新文件夹路径
            
        Raises:
            ValueError: 当原文件夹不存在或不是目录时抛出异常
            Exception: 当创建文件夹失败时抛出异常
            
        Example:
            >>> folder_handler = FolderHandler()
            >>> output_path = folder_handler.create_output_folder_with_suffix("./data", "_processed")
            >>> print(output_path)
            './data_processed'
        """
        logger.debug("创建输出文件夹，原路径: {}，后缀: {}", folder_path, suffix)
        
        try:
            # 转换为Path对象
            original_folder = Path(folder_path)
            
            # 检查原文件夹是否存在
            if not original_folder.exists():
                logger.error("原文件夹不存在: {}", folder_path)
                raise ValueError(f"原文件夹不存在: {folder_path}")
            
            if not original_folder.is_dir():
                logger.error("路径不是文件夹: {}", folder_path)
                raise ValueError(f"路径不是文件夹: {folder_path}")
            
            # 构建新文件夹路径
            parent_dir = original_folder.parent
            folder_name = original_folder.name
            new_folder_name = f"{folder_name}{suffix}"
            new_folder_path = parent_dir / new_folder_name
            
            # 创建新文件夹
            new_folder_path.mkdir(parents=True, exist_ok=True)
            
            logger.debug("输出文件夹创建成功: {}", new_folder_path)
            return str(new_folder_path)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error("创建输出文件夹失败: {}", str(e))
            raise Exception(f"创建输出文件夹失败: {e}")
    
    def get_files_natural_sorted(self, folder_path: Union[str, Path]) -> List[Path]:
        """
        获取文件夹中的文件列表，按自然排序
        
        Args:
            folder_path (str | Path): 文件夹路径
            
        Returns:
            List[Path]: 按自然排序的文件路径列表
            
        Raises:
            FileNotFoundError: 当文件夹不存在时抛出异常
            NotADirectoryError: 当路径不是文件夹时抛出异常
            
        Example:
            >>> folder_handler = FolderHandler()
            >>> files = folder_handler.get_files_natural_sorted("./data")
            >>> print([f.name for f in files])
            ['file1.txt', 'file2.txt', 'file10.txt']
        """
        logger.debug("获取文件夹文件列表，路径: {}", folder_path)
        
        try:
            folder = Path(folder_path)
            
            if not folder.exists():
                logger.error("文件夹不存在: {}", folder_path)
                raise FileNotFoundError(f"文件夹不存在: {folder_path}")
                
            if not folder.is_dir():
                logger.error("路径不是文件夹: {}", folder_path)
                raise NotADirectoryError(f"路径不是文件夹: {folder_path}")
            
            # 获取所有文件（不包括子文件夹）
            files = [f for f in folder.iterdir() if f.is_file()]
            
            # 自然排序
            def natural_sort_key(path):
                """自然排序的键函数"""
                filename = path.name
                # 将文件名分解为数字和非数字部分
                parts = re.split(r'(\d+)', filename)
                # 将数字部分转换为整数，非数字部分保持字符串
                return [int(part) if part.isdigit() else part.lower() for part in parts]
            
            sorted_files = sorted(files, key=natural_sort_key)
            
            logger.debug("文件列表获取完成，文件数量: {}", len(sorted_files))
            return sorted_files
            
        except (FileNotFoundError, NotADirectoryError):
            raise
        except Exception as e:
            logger.error("获取文件列表失败: {}", str(e))
            raise Exception(f"获取文件列表失败: {e}")

    def check_file_exists_in_folder(self, folder_path: Union[str, Path], filename: Union[str, List[str]],
                                    extensions: Optional[Union[str, List[str]]] = None) -> Union[bool, dict]:
        """
        检查文件夹中是否存在指定文件名的文件（严格精确匹配）

        Args:
            folder_path (Union[str, Path]): 文件夹路径，要检查的目标文件夹
            filename (Union[str, List[str]]): 文件名，支持单个文件名(str)或多个文件名(list)，不包含扩展名
            extensions (Optional[Union[str, List[str]]], optional): 可选的文件扩展名，不指定则匹配任何扩展名。
                支持单个扩展名(str)如'.jpg'或多个扩展名(list)如['.jpg', '.png']. Defaults to None.

        Returns:
            Union[bool, dict]:
                - 如果filename是str: 返回bool，True表示文件存在
                - 如果filename是list: 返回dict，格式为 {"文件名": True/False, ...}

        Example:
            >>> folder_handler = FolderHandler()
            >>> # 检查单个文件
            >>> exists = folder_handler.check_file_exists_in_folder("./data", "report", [".pdf", ".docx"])
            >>> print(exists)
            True
            >>> # 检查多个文件
            >>> results = folder_handler.check_file_exists_in_folder("./data", ["file1", "file2"], ".txt")
            >>> print(results)
            {'file1': True, 'file2': False}
        """
        logger.debug("检查文件是否存在，文件夹: {}，文件名: {}，扩展名: {}", folder_path, filename, extensions)

        try:
            folder_path = Path(folder_path)

            if not folder_path.exists() or not folder_path.is_dir():
                logger.debug("文件夹不存在或不是目录: {}", folder_path)
                # 文件夹不存在，返回对应格式的False结果
                if isinstance(filename, str):
                    return False
                else:
                    return {name: False for name in filename}

            # 获取文件夹中所有文件
            all_files = [f for f in folder_path.iterdir() if f.is_file()]

            # 处理扩展名参数 - 严格匹配，不转换大小写
            if extensions is None:
                target_extensions = None
            elif isinstance(extensions, str):
                target_extensions = [extensions]
            else:
                target_extensions = list(extensions)

            def file_exists_strict(target_name: str) -> bool:
                """严格检查单个文件是否存在 - 精确匹配，区分大小写"""
                logger.debug("检查文件: {}", target_name)

                for file_path in all_files:
                    file_stem = file_path.stem  # 不带扩展名的文件名，保持原始大小写
                    file_ext = file_path.suffix  # 扩展名，保持原始大小写

                    # 严格精确匹配文件名（区分大小写）
                    if file_stem == target_name:
                        # 如果没有指定扩展名，直接返回True
                        if target_extensions is None:
                            logger.debug("找到文件: {}", file_path.name)
                            return True
                        # 如果指定了扩展名，检查扩展名是否匹配（不区分大小写）
                        elif file_ext.lower() in [ext.lower() for ext in target_extensions]:
                            logger.debug("找到匹配文件: {}", file_path.name)
                            return True

                logger.debug("未找到文件: {}", target_name)
                return False

            # 处理单个文件名
            if isinstance(filename, str):
                result = file_exists_strict(filename)
                logger.debug("单文件检查结果: {}", result)
                return result

            # 处理多个文件名
            else:
                result = {}
                for name in filename:
                    result[name] = file_exists_strict(name)
                logger.debug("多文件检查结果: {}", result)
                return result

        except Exception as e:
            logger.error("检查文件存在性时发生异常: {}", str(e))
            # 发生异常时返回对应格式的False结果
            if isinstance(filename, str):
                return False
            else:
                return {name: False for name in filename}
