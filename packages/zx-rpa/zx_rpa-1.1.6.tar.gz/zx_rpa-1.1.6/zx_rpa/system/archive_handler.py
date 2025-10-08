"""
压缩包处理器 - 提供统一的压缩包解压和压缩功能

支持格式：ZIP, RAR, 7Z, TAR, TAR.GZ, TAR.BZ2 等常见压缩格式
功能特性：自动格式识别、密码保护、压缩级别设置、进度回调
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Union, List, Callable, Dict, Any
from loguru import logger

try:
    from archivefile import ArchiveFile
    import rarfile
except ImportError:
    logger.error("archivefile库未安装，请执行: pip install archivefile")
    raise ImportError("请先安装archivefile库: pip install archivefile")


class ArchiveHandler:
    """压缩包处理器 - 统一的压缩包操作接口"""
    
    # 支持的压缩格式
    SUPPORTED_FORMATS = {
        '.zip': 'ZIP压缩文件',
        '.rar': 'RAR压缩文件', 
        '.7z': '7Z压缩文件',
        '.tar': 'TAR归档文件',
        '.tar.gz': 'TAR.GZ压缩文件',
        '.tgz': 'TGZ压缩文件',
        '.tar.bz2': 'TAR.BZ2压缩文件',
        '.tbz2': 'TBZ2压缩文件',
        '.tar.xz': 'TAR.XZ压缩文件',
        '.txz': 'TXZ压缩文件'
    }
    
    def __init__(self):
        """初始化压缩包处理器"""
        logger.debug("初始化压缩包处理器")
        self._setup_rar_tool()
    
    def is_archive_file(self, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否为支持的压缩包格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为支持的压缩包格式
        """
        file_path = Path(file_path)
        logger.debug("检查文件格式: {}", file_path)
        
        if not file_path.exists():
            logger.debug("文件不存在: {}", file_path)
            return False
        
        # 检查文件扩展名
        file_lower = str(file_path).lower()
        for ext in self.SUPPORTED_FORMATS:
            if file_lower.endswith(ext):
                logger.debug("识别为{}格式: {}", self.SUPPORTED_FORMATS[ext], file_path)
                return True
        
        logger.debug("不支持的文件格式: {}", file_path)
        return False
    
    def get_archive_info(self, archive_path: Union[str, Path], password: Optional[str] = None) -> Dict[str, Any]:
        """
        获取压缩包信息

        Args:
            archive_path: 压缩包路径
            password: 解压密码（可选）

        Returns:
            Dict: 压缩包信息字典
        """
        archive_path = Path(archive_path)
        logger.debug("获取压缩包信息: {}", archive_path)

        if not self.is_archive_file(archive_path):
            logger.error("不支持的压缩包格式: {}", archive_path)
            raise ValueError(f"不支持的压缩包格式: {archive_path}")

        try:
            # 如果是RAR文件，使用专门的处理方式
            if self._detect_format(archive_path) == 'rar':
                return self._get_rar_info(archive_path, password)

            # 其他格式使用archivefile，优先无密码尝试
            def get_info_operation(archive_kwargs):
                with ArchiveFile(str(archive_path), **archive_kwargs) as archive:
                    file_names = archive.get_names()

                    info = {
                        'path': str(archive_path),
                        'size': archive_path.stat().st_size,
                        'file_count': len(file_names),
                        'files': list(file_names),
                        'format': self._detect_format(archive_path)
                    }

                    logger.debug("压缩包信息获取成功，文件数量: {}", info['file_count'])
                    return info

            return self._execute_with_password_fallback(get_info_operation, str(archive_path), password)

        except Exception as e:
            logger.error("获取压缩包信息失败: {}", str(e))
            raise
    
    def extract_archive(self,
                       archive_path: Union[str, Path],
                       destination: Optional[Union[str, Path]] = None,
                       password: Optional[str] = None,
                       overwrite: bool = True,
                       delete_source: bool = False,
                       progress_callback: Optional[Callable[[int, int], None]] = None) -> str:
        """
        解压压缩包

        Args:
            archive_path: 压缩包路径
            destination: 解压目标目录（如果为None，则原地解压到压缩包同目录）
            password: 解压密码（如果需要）
            overwrite: 是否覆盖已存在的文件
            delete_source: 是否删除源压缩包文件
            progress_callback: 进度回调函数 callback(current, total)

        Returns:
            str: 解压后的目录路径
        """
        archive_path = Path(archive_path)

        # 如果没有指定目标目录，则原地解压
        if destination is None:
            destination = archive_path.parent / archive_path.stem
            logger.debug("原地解压，目标目录: {}", destination)
        else:
            destination = Path(destination)

        logger.debug("开始解压: {} -> {}", archive_path, destination)
        
        if not self.is_archive_file(archive_path):
            logger.error("不支持的压缩包格式: {}", archive_path)
            raise ValueError(f"不支持的压缩包格式: {archive_path}")
        
        # 创建目标目录
        destination.mkdir(parents=True, exist_ok=True)
        
        try:
            # 如果是RAR文件，使用专门的处理方式
            if self._detect_format(archive_path) == 'rar':
                return self._extract_rar_archive(archive_path, destination, password, overwrite, progress_callback, delete_source)

            # 其他格式使用archivefile，优先无密码尝试
            def extract_operation(archive_kwargs):
                with ArchiveFile(str(archive_path), **archive_kwargs) as archive:
                    file_names = archive.get_names()
                    total_files = len(file_names)

                    logger.debug("压缩包包含{}个文件", total_files)

                    if progress_callback:
                        progress_callback(0, total_files)

                    # 检查是否需要覆盖文件
                    if not overwrite:
                        existing_files = []
                        for name in file_names:
                            target_path = destination / name
                            if target_path.exists():
                                existing_files.append(name)

                        if existing_files:
                            logger.error("目标文件已存在且不允许覆盖: {}", existing_files[:5])
                            raise FileExistsError(f"目标文件已存在: {len(existing_files)}个文件")

                    # 解压所有文件
                    archive.extractall(destination=str(destination))

                    if progress_callback:
                        progress_callback(total_files, total_files)

                    logger.debug("解压完成: {} -> {}", archive_path, destination)
                    return str(destination)

            result = self._execute_with_password_fallback(extract_operation, str(archive_path), password)

            # 删除源压缩包文件（如果需要）
            if delete_source:
                self._safe_delete_source(archive_path, is_file=True)

            return result

        except Exception as e:
            logger.error("解压失败: {}", str(e))
            raise
    
    def create_archive(self,
                      source_path: Union[str, Path],
                      archive_path: Optional[Union[str, Path]] = None,
                      archive_format: str = 'zip',
                      compression_mode: str = 'balanced',
                      password: Optional[str] = None,
                      delete_source: bool = False,
                      progress_callback: Optional[Callable[[int, int], None]] = None) -> str:
        """
        创建压缩包

        Args:
            source_path: 源文件或目录路径
            archive_path: 压缩包输出路径（如果为None，则原地压缩到源文件同目录）
            archive_format: 压缩格式 ('zip', '7z', 'tar', 'tar.gz')
            compression_mode: 压缩模式 ('fast'=快速, 'balanced'=平衡, 'best'=最佳压缩)
            password: 压缩密码（如果支持）
            delete_source: 是否删除源文件或目录
            progress_callback: 进度回调函数 callback(current, total)

        Returns:
            str: 创建的压缩包路径
        """
        source_path = Path(source_path)

        # 如果没有指定压缩包路径，则原地压缩
        if archive_path is None:
            if source_path.is_file():
                archive_path = source_path.parent / f"{source_path.stem}.{archive_format}"
            else:
                archive_path = source_path.parent / f"{source_path.name}.{archive_format}"
            logger.debug("原地压缩，压缩包路径: {}", archive_path)
        else:
            archive_path = Path(archive_path)

        logger.debug("开始创建压缩包: {} -> {}, 格式: {}", source_path, archive_path, archive_format)
        
        if not source_path.exists():
            logger.error("源路径不存在: {}", source_path)
            raise FileNotFoundError(f"源路径不存在: {source_path}")
        
        # 确保输出目录存在
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 确保压缩包有正确的扩展名
        if not str(archive_path).lower().endswith(f'.{archive_format.lower()}'):
            archive_path = archive_path.with_suffix(f'.{archive_format.lower()}')

        # 转换压缩模式为具体的压缩级别
        compression_level = self._get_compression_level(compression_mode)
        logger.debug("压缩模式: {}, 压缩级别: {}", compression_mode, compression_level)

        try:
            # 根据格式和密码创建压缩包
            archive_kwargs = self._create_archive_with_password(password, archive_format)

            with ArchiveFile(str(archive_path), 'w', **archive_kwargs) as archive:
                if source_path.is_file():
                    # 压缩单个文件
                    logger.debug("压缩单个文件: {}", source_path)
                    archive.write(str(source_path), arcname=source_path.name)
                    
                    if progress_callback:
                        progress_callback(1, 1)
                        
                else:
                    # 压缩目录 - 直接使用 archivefile 的内置功能
                    logger.debug("压缩目录: {}", source_path)

                    # 计算文件数量用于进度回调
                    if progress_callback:
                        files_to_compress = list(source_path.rglob("*"))
                        files_to_compress = [f for f in files_to_compress if f.is_file()]
                        total_files = len(files_to_compress)
                        logger.debug("压缩目录，包含{}个文件", total_files)
                        progress_callback(0, total_files)

                    # 使用 archivefile 的内置目录压缩功能
                    current_file = 0
                    for root, _, filenames in os.walk(source_path):
                        for filename in filenames:
                            file_path = Path(root) / filename
                            rel_path = file_path.relative_to(source_path)
                            archive.write(str(file_path), arcname=str(rel_path))

                            if progress_callback:
                                current_file += 1
                                progress_callback(current_file, total_files if progress_callback else current_file)
                
                logger.debug("压缩包创建完成: {}", archive_path)

                # 删除源文件或目录（如果需要）
                if delete_source:
                    self._safe_delete_source(source_path, is_file=source_path.is_file())

                return str(archive_path)

        except Exception as e:
            logger.error("创建压缩包失败: {}", str(e))
            # 清理失败的压缩包文件
            if archive_path.exists():
                archive_path.unlink()
            raise
    
    def _detect_format(self, file_path: Path) -> str:
        """检测压缩包格式"""
        file_lower = str(file_path).lower()
        for ext in self.SUPPORTED_FORMATS.keys():
            if file_lower.endswith(ext):
                return ext.lstrip('.')
        return 'unknown'

    def _setup_rar_tool(self):
        """设置RAR解压工具"""
        try:
            # 设置本地UnRAR.exe路径
            unrar_path = Path(__file__).parent / "UnRAR.exe"
            if unrar_path.exists():
                rarfile.UNRAR_TOOL = str(unrar_path)
                # 强制重新初始化工具设置
                rarfile._tool_setup_done = False
                logger.debug("配置本地UnRAR工具: {}", unrar_path)
            else:
                logger.warning("本地UnRAR.exe不存在: {}", unrar_path)
        except Exception as e:
            logger.warning("配置RAR工具失败: {}", str(e))

    def _ensure_rar_tool(self):
        """确保RAR工具配置正确"""
        try:
            unrar_path = Path(__file__).parent / "UnRAR.exe"
            if unrar_path.exists():
                rarfile.UNRAR_TOOL = str(unrar_path)
                # 强制重新初始化
                if hasattr(rarfile, '_tool_setup_done'):
                    rarfile._tool_setup_done = False
        except Exception as e:
            logger.warning("重新配置RAR工具失败: {}", str(e))

    def _get_compression_level(self, compression_mode: str) -> int:
        """
        将压缩模式转换为具体的压缩级别

        Args:
            compression_mode: 压缩模式 ('fast', 'balanced', 'best')

        Returns:
            int: 压缩级别 (0-9)
        """
        mode_mapping = {
            'fast': 1,      # 快速压缩
            'balanced': 6,  # 平衡压缩（默认）
            'best': 9       # 最佳压缩
        }
        return mode_mapping.get(compression_mode.lower(), 6)

    def _create_archive_with_password(self, password: Optional[str], archive_format: str) -> Dict[str, Any]:
        """
        创建带密码的压缩包参数

        Args:
            password: 密码
            archive_format: 压缩格式

        Returns:
            Dict: 压缩包创建参数
        """
        archive_kwargs = {}
        if password and archive_format.lower() in ['zip', '7z']:
            archive_kwargs['password'] = password
            logger.debug("使用密码保护")
        return archive_kwargs

    def _execute_with_password_fallback(self, operation_func, archive_path: str, password: Optional[str] = None):
        """
        执行操作，优先无密码，遇到密码保护时使用提供的密码

        Args:
            operation_func: 要执行的操作函数，接受archive_kwargs参数
            archive_path: 压缩包路径
            password: 备用密码

        Returns:
            操作函数的返回值
        """
        # 首先尝试无密码操作
        try:
            logger.debug("尝试无密码操作: {}", archive_path)
            return operation_func({})
        except Exception as e:
            error_msg = str(e).lower()
            # 检查是否是密码相关的错误
            password_error_keywords = [
                'password', 'encrypted', 'wrong password', 'bad password',
                'needs password', 'requires password', 'password required',
                'password protected', 'bad decrypt', 'decrypt'
            ]

            is_password_error = any(keyword in error_msg for keyword in password_error_keywords)

            if is_password_error and password:
                logger.debug("检测到密码保护，尝试使用提供的密码: {}", archive_path)
                try:
                    return operation_func({'password': password})
                except Exception as pwd_e:
                    logger.error("使用密码操作也失败: {}", str(pwd_e))
                    raise pwd_e
            else:
                # 如果不是密码错误，或者没有提供密码，直接抛出原始错误
                logger.error("操作失败: {}", str(e))
                raise e

    def _extract_rar_archive(self, archive_path: Path, destination: Path, password: Optional[str],
                           overwrite: bool, progress_callback: Optional[Callable[[int, int], None]],
                           delete_source: bool = False) -> str:
        """
        专门处理RAR文件解压

        Args:
            archive_path: RAR文件路径
            destination: 解压目标目录
            password: 解压密码
            overwrite: 是否覆盖文件
            progress_callback: 进度回调
            delete_source: 是否删除源压缩包文件

        Returns:
            str: 解压后的目录路径
        """
        logger.debug("使用专门的RAR解压方法")

        # 确保RAR工具配置正确
        self._ensure_rar_tool()

        try:
            # 首先尝试无密码解压
            try:
                with rarfile.RarFile(str(archive_path)) as rf:
                    file_names = rf.namelist()
                    total_files = len(file_names)

                    logger.debug("RAR文件包含{}个文件", total_files)

                    if progress_callback:
                        progress_callback(0, total_files)

                    # 检查是否需要覆盖文件
                    if not overwrite:
                        existing_files = []
                        for name in file_names:
                            target_path = destination / name
                            if target_path.exists():
                                existing_files.append(name)

                        if existing_files:
                            logger.error("目标文件已存在且不允许覆盖: {}", existing_files[:5])
                            raise FileExistsError(f"目标文件已存在: {len(existing_files)}个文件")

                    # 解压所有文件（无密码）
                    rf.extractall(path=str(destination))

                    if progress_callback:
                        progress_callback(total_files, total_files)

                    logger.debug("RAR文件解压完成")

                    # 删除源压缩包文件（如果需要）
                    if delete_source:
                        self._safe_delete_source(archive_path, is_file=True)

                    return str(destination)
            except Exception as e:
                # 如果失败且有密码，尝试使用密码
                if password and ('password' in str(e).lower() or 'encrypted' in str(e).lower()):
                    logger.debug("RAR文件需要密码，尝试使用提供的密码")
                    with rarfile.RarFile(str(archive_path)) as rf:
                        file_names = rf.namelist()
                        total_files = len(file_names)

                        logger.debug("RAR文件包含{}个文件（使用密码）", total_files)

                        if progress_callback:
                            progress_callback(0, total_files)

                        # 检查是否需要覆盖文件
                        if not overwrite:
                            existing_files = []
                            for name in file_names:
                                target_path = destination / name
                                if target_path.exists():
                                    existing_files.append(name)

                            if existing_files:
                                logger.error("目标文件已存在且不允许覆盖: {}", existing_files[:5])
                                raise FileExistsError(f"目标文件已存在: {len(existing_files)}个文件")

                        # 解压所有文件（使用密码）
                        rf.extractall(path=str(destination), pwd=password)

                        if progress_callback:
                            progress_callback(total_files, total_files)

                        logger.debug("RAR文件解压完成（使用密码）")

                        # 删除源压缩包文件（如果需要）
                        if delete_source:
                            self._safe_delete_source(archive_path, is_file=True)

                        return str(destination)
                else:
                    raise e

        except Exception as e:
            logger.error("RAR文件解压失败: {}", str(e))
            raise

    def _list_rar_contents(self, archive_path: Path, password: Optional[str]) -> List[Dict[str, Any]]:
        """
        专门处理RAR文件内容列表

        Args:
            archive_path: RAR文件路径
            password: 解压密码

        Returns:
            List[Dict]: 文件信息列表
        """
        logger.debug("使用专门的RAR内容列表方法")

        # 确保RAR工具配置正确
        self._ensure_rar_tool()

        try:
            # 首先尝试无密码打开
            try:
                with rarfile.RarFile(str(archive_path)) as rf:
                    members = rf.infolist()
                    contents = []

                    for member in members:
                        file_info = {
                            'name': member.filename,
                            'is_dir': member.is_dir(),
                            'size': member.file_size,
                            'compressed_size': member.compress_size,
                            'mtime': member.date_time if hasattr(member, 'date_time') else None
                        }
                        contents.append(file_info)

                    logger.debug("RAR内容列表获取完成，共{}项", len(contents))
                    return contents
            except Exception as e:
                # 如果失败且有密码，尝试使用密码
                if password and ('password' in str(e).lower() or 'encrypted' in str(e).lower()):
                    logger.debug("RAR文件需要密码，尝试使用提供的密码")
                    with rarfile.RarFile(str(archive_path)) as rf:
                        rf.setpassword(password)
                        members = rf.infolist()
                        contents = []

                        for member in members:
                            file_info = {
                                'name': member.filename,
                                'is_dir': member.is_dir(),
                                'size': member.file_size,
                                'compressed_size': member.compress_size,
                                'mtime': member.date_time if hasattr(member, 'date_time') else None
                            }
                            contents.append(file_info)

                        logger.debug("RAR内容列表获取完成（使用密码），共{}项", len(contents))
                        return contents
                else:
                    raise e

        except Exception as e:
            logger.error("RAR文件内容列表获取失败: {}", str(e))
            raise

    def _get_rar_info(self, archive_path: Path, password: Optional[str]) -> Dict[str, Any]:
        """
        专门处理RAR文件信息获取

        Args:
            archive_path: RAR文件路径
            password: 解压密码

        Returns:
            Dict: 压缩包信息字典
        """
        logger.debug("使用专门的RAR信息获取方法")

        # 确保RAR工具配置正确
        self._ensure_rar_tool()

        try:
            # 首先尝试无密码打开
            try:
                with rarfile.RarFile(str(archive_path)) as rf:
                    file_names = rf.namelist()

                    info = {
                        'path': str(archive_path),
                        'size': archive_path.stat().st_size,
                        'file_count': len(file_names),
                        'files': list(file_names),
                        'format': 'rar'
                    }

                    logger.debug("RAR信息获取成功，文件数量: {}", info['file_count'])
                    return info
            except Exception as e:
                # 如果失败且有密码，尝试使用密码
                if password and ('password' in str(e).lower() or 'encrypted' in str(e).lower()):
                    logger.debug("RAR文件需要密码，尝试使用提供的密码")
                    with rarfile.RarFile(str(archive_path)) as rf:
                        rf.setpassword(password)
                        file_names = rf.namelist()

                        info = {
                            'path': str(archive_path),
                            'size': archive_path.stat().st_size,
                            'file_count': len(file_names),
                            'files': list(file_names),
                            'format': 'rar'
                        }

                        logger.debug("RAR信息获取成功（使用密码），文件数量: {}", info['file_count'])
                        return info
                else:
                    raise e

        except Exception as e:
            logger.error("RAR文件信息获取失败: {}", str(e))
            raise

    def _safe_delete_source(self, source_path: Path, is_file: bool = True):
        """
        安全删除源文件或目录

        Args:
            source_path: 源路径
            is_file: 是否为文件
        """
        try:
            # 添加延迟以确保文件句柄被释放
            import time
            time.sleep(0.1)

            if is_file:
                source_path.unlink()
                logger.debug("已删除源文件: {}", source_path)
            else:
                shutil.rmtree(source_path)
                logger.debug("已删除源目录: {}", source_path)
        except Exception as e:
            logger.error("删除源文件/目录失败: {}", str(e))
            # 不抛出异常，因为主要操作已经成功


    def extract_single_file(self,
                           archive_path: Union[str, Path],
                           file_name: str,
                           destination: Optional[Union[str, Path]] = None,
                           password: Optional[str] = None,
                           delete_source: bool = False) -> str:
        """
        从压缩包中解压单个文件

        Args:
            archive_path: 压缩包路径
            file_name: 要解压的文件名
            destination: 解压目标目录（如果为None，则原地解压到压缩包同目录）
            password: 解压密码（如果需要）
            delete_source: 是否删除源压缩包文件

        Returns:
            str: 解压后的文件路径
        """
        archive_path = Path(archive_path)

        # 如果没有指定目标目录，则原地解压
        if destination is None:
            destination = archive_path.parent
            logger.debug("原地解压单个文件，目标目录: {}", destination)
        else:
            destination = Path(destination)

        logger.debug("解压单个文件: {} 从 {} 到 {}", file_name, archive_path, destination)

        if not self.is_archive_file(archive_path):
            logger.error("不支持的压缩包格式: {}", archive_path)
            raise ValueError(f"不支持的压缩包格式: {archive_path}")

        destination.mkdir(parents=True, exist_ok=True)

        try:
            # 优先无密码尝试解压单个文件
            def extract_single_operation(archive_kwargs):
                with ArchiveFile(str(archive_path), **archive_kwargs) as archive:
                    # 检查文件是否存在
                    file_names = archive.get_names()
                    if file_name not in file_names:
                        logger.error("文件不存在于压缩包中: {}", file_name)
                        raise FileNotFoundError(f"文件不存在于压缩包中: {file_name}")

                    # 解压单个文件
                    archive.extract(file_name, destination=str(destination))

                    extracted_path = destination / file_name
                    logger.debug("单个文件解压完成: {}", extracted_path)
                    return str(extracted_path)

            result = self._execute_with_password_fallback(extract_single_operation, str(archive_path), password)

            # 删除源压缩包文件（如果需要）
            if delete_source:
                self._safe_delete_source(archive_path, is_file=True)

            return result

        except Exception as e:
            logger.error("解压单个文件失败: {}", str(e))
            raise

    def list_archive_contents(self, archive_path: Union[str, Path], password: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出压缩包内容详情

        Args:
            archive_path: 压缩包路径
            password: 解压密码（可选）

        Returns:
            List[Dict]: 文件信息列表
        """
        archive_path = Path(archive_path)
        logger.debug("列出压缩包内容: {}", archive_path)

        if not self.is_archive_file(archive_path):
            logger.error("不支持的压缩包格式: {}", archive_path)
            raise ValueError(f"不支持的压缩包格式: {archive_path}")

        try:
            # 如果是RAR文件，使用专门的处理方式
            if self._detect_format(archive_path) == 'rar':
                return self._list_rar_contents(archive_path, password)

            # 其他格式使用archivefile，优先无密码尝试
            def list_contents_operation(archive_kwargs):
                with ArchiveFile(str(archive_path), **archive_kwargs) as archive:
                    members = list(archive.get_members())
                    contents = []

                    for member in members:
                        # 处理不同类型的member对象
                        is_dir = member.is_dir() if callable(member.is_dir) else member.is_dir

                        file_info = {
                            'name': member.name,
                            'is_dir': is_dir,
                            'size': getattr(member, 'size', 0) if hasattr(member, 'size') else 0,
                            'compressed_size': getattr(member, 'compressed_size', 0) if hasattr(member, 'compressed_size') else 0,
                            'mtime': getattr(member, 'mtime', None) if hasattr(member, 'mtime') else None
                        }
                        contents.append(file_info)

                    logger.debug("压缩包内容列表获取完成，共{}项", len(contents))
                    return contents

            return self._execute_with_password_fallback(list_contents_operation, str(archive_path), password)

        except Exception as e:
            logger.error("列出压缩包内容失败: {}", str(e))
            raise

    def test_archive(self, archive_path: Union[str, Path], password: Optional[str] = None) -> bool:
        """
        测试压缩包完整性

        Args:
            archive_path: 压缩包路径
            password: 测试密码（如果需要）

        Returns:
            bool: 压缩包是否完整
        """
        archive_path = Path(archive_path)
        logger.debug("测试压缩包完整性: {}", archive_path)

        if not self.is_archive_file(archive_path):
            logger.error("不支持的压缩包格式: {}", archive_path)
            return False

        try:
            # 优先无密码测试压缩包
            def test_operation(archive_kwargs):
                with ArchiveFile(str(archive_path), **archive_kwargs) as archive:
                    # 尝试读取所有文件名
                    file_names = archive.get_names()
                    logger.debug("压缩包测试通过，包含{}个文件", len(file_names))
                    return True

            return self._execute_with_password_fallback(test_operation, str(archive_path), password)

        except Exception as e:
            logger.error("压缩包测试失败: {}", str(e))
            return False

    def get_supported_formats(self) -> Dict[str, str]:
        """
        获取支持的压缩格式列表

        Returns:
            Dict[str, str]: 格式扩展名和描述的字典
        """
        return self.SUPPORTED_FORMATS.copy()

    def batch_extract(self,
                     archive_paths: List[Union[str, Path]],
                     destination: Optional[Union[str, Path]] = None,
                     password: Optional[str] = None,
                     overwrite: bool = True,
                     delete_source: bool = False,
                     progress_callback: Optional[Callable[[int, int], None]] = None) -> List[str]:
        """
        批量解压多个压缩包

        Args:
            archive_paths: 压缩包路径列表
            destination: 解压目标目录（如果为None，则每个压缩包原地解压）
            password: 解压密码（如果需要）
            overwrite: 是否覆盖已存在的文件
            delete_source: 是否删除源压缩包文件
            progress_callback: 进度回调函数 callback(current, total)

        Returns:
            List[str]: 成功解压的目录路径列表
        """
        total_archives = len(archive_paths)
        successful_extracts = []

        logger.debug("开始批量解压{}个压缩包", total_archives)

        for i, archive_path in enumerate(archive_paths):
            try:
                if destination is None:
                    # 原地解压
                    extract_dir = None
                else:
                    # 为每个压缩包创建单独的子目录
                    destination = Path(destination)
                    archive_name = Path(archive_path).stem
                    extract_dir = destination / archive_name

                result = self.extract_archive(
                    archive_path=archive_path,
                    destination=extract_dir,
                    password=password,
                    overwrite=overwrite,
                    delete_source=delete_source
                )

                successful_extracts.append(result)
                logger.debug("批量解压进度: {}/{}", i + 1, total_archives)

                if progress_callback:
                    progress_callback(i + 1, total_archives)

            except Exception as e:
                logger.error("解压失败: {} - {}", archive_path, str(e))
                continue

        logger.debug("批量解压完成，成功: {}/{}", len(successful_extracts), total_archives)
        return successful_extracts
