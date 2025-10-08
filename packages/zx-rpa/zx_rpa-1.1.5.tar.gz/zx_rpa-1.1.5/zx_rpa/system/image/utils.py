"""
图片处理通用工具模块

提供图片处理的通用常量、工具函数等
"""

from pathlib import Path
from urllib.parse import urlparse
from loguru import logger


class ImageConstants:
    """图片处理相关常量"""
    
    DEFAULT_USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")
    NETWORK_SCHEMES = {'http', 'https'}
    
    # 默认支持的图片格式
    DEFAULT_SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif']
    
    # 不支持压缩的格式
    UNSUPPORTED_COMPRESSION_FORMATS = ['GIF']


class ImageUtils:
    """图片处理通用工具类"""
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        格式化文件大小显示

        Args:
            size_bytes (int): 文件大小（字节）

        Returns:
            str: 格式化后的文件大小字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    @staticmethod
    def is_network_url(url: str) -> bool:
        """
        判断URL是否为网络资源

        Args:
            url: 待检测的URL

        Returns:
            bool: 是否为网络URL
        """
        try:
            parsed_url = urlparse(url)
            return parsed_url.scheme in ImageConstants.NETWORK_SCHEMES
        except Exception:
            return False
    
    @staticmethod
    def validate_quality_param(quality: int) -> None:
        """
        验证质量参数

        Args:
            quality: 质量参数

        Raises:
            ValueError: 质量参数无效时
        """
        if not 1 <= quality <= 100:
            logger.debug("质量参数无效: {}，必须在1-100之间", quality)
            raise ValueError("质量参数必须在1-100之间")
    
    @staticmethod
    def validate_strategy_param(strategy: str) -> None:
        """
        验证压缩策略参数

        Args:
            strategy: 压缩策略

        Raises:
            ValueError: 策略参数无效时
        """
        if strategy not in ['balanced', 'quality', 'size']:
            logger.debug("压缩策略无效: {}，支持: balanced, quality, size", strategy)
            raise ValueError("压缩策略必须是 'balanced', 'quality', 'size' 之一")
    
    @staticmethod
    def validate_file_exists(file_path: Path) -> None:
        """
        验证文件是否存在

        Args:
            file_path: 文件路径

        Raises:
            FileNotFoundError: 文件不存在时
            ValueError: 路径不是文件时
        """
        if not file_path.exists():
            logger.debug("输入图片文件不存在: {}", file_path)
            raise FileNotFoundError(f"输入图片文件不存在: {file_path}")
        
        if not file_path.is_file():
            logger.debug("输入路径不是文件: {}", file_path)
            raise ValueError(f"输入路径不是文件: {file_path}")
    
    @staticmethod
    def ensure_output_directory(output_path: Path) -> None:
        """
        确保输出目录存在

        Args:
            output_path: 输出路径
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_compression_params(strategy: str, base_quality: int) -> tuple:
        """
        根据压缩策略获取压缩参数

        Args:
            strategy (str): 压缩策略
            base_quality (int): 基础质量参数

        Returns:
            tuple: (最终质量, 是否优化)
        """
        if strategy == 'quality':
            # 质量优先：提高质量，启用优化
            final_quality = min(base_quality + 5, 95)
            optimize = True
        elif strategy == 'size':
            # 大小优先：降低质量，强制优化
            final_quality = max(base_quality - 10, 60)
            optimize = True
        else:  # balanced
            # 平衡模式：使用原始质量，启用优化
            final_quality = base_quality
            optimize = True

        return final_quality, optimize
