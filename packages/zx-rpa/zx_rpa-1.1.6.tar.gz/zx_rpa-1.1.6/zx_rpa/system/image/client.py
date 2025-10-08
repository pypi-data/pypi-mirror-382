"""
图片处理统一客户端

整合图片压缩、Base64转换等所有功能，提供统一的对外接口
"""

from pathlib import Path
from typing import Union, List, Optional
from loguru import logger

from .compression import ImageCompressor
from .base64_converter import Base64Converter


class ImageHandler:
    """图片处理器 - 提供图片压缩、格式转换、base64转换等功能"""
    
    def __init__(self):
        """初始化图片处理器"""
        logger.debug("初始化图片处理器")
        self._compressor = ImageCompressor()
        self._converter = Base64Converter()
    
    # ==================== 图片压缩功能 ====================
    
    def compress_image_smart(self, input_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None,
                            quality: int = 85, max_size: Optional[tuple] = None,
                            strategy: str = 'balanced', keep_metadata: bool = False,
                            skip_unsupported: bool = True) -> str:
        """
        智能图片压缩，在保持视觉质量的基础上适当压缩文件大小

        Args:
            input_path (Union[str, Path]): 输入图片路径，支持 JPEG、PNG、WebP 等格式
            output_path (Optional[Union[str, Path]], optional): 输出图片路径，如果为None则覆盖原文件. Defaults to None.
            quality (int, optional): 压缩质量，1-100，数值越高质量越好但文件越大. Defaults to 85.
            max_size (Optional[tuple], optional): 最大尺寸限制 (width, height)，超过则等比缩放. Defaults to None.
            strategy (str, optional): 压缩策略，'balanced'平衡模式，'quality'质量优先，'size'大小优先. Defaults to 'balanced'.
            keep_metadata (bool, optional): 是否保留图片元数据（EXIF等）. Defaults to False.
            skip_unsupported (bool, optional): 是否跳过不支持的格式（如GIF），True=跳过，False=转换为静态图. Defaults to True.
            
        Returns:
            str: 压缩后的图片路径
            
        Raises:
            FileNotFoundError: 当输入文件不存在时
            ValueError: 当参数无效时
            ImportError: 当缺少必要的图片处理库时
            
        Example:
            >>> image_handler = ImageHandler()
            >>> # 基础压缩
            >>> compressed_path = image_handler.compress_image_smart("photo.jpg")
            >>> # 高质量压缩并限制尺寸
            >>> compressed_path = image_handler.compress_image_smart(
            ...     "large_photo.jpg",
            ...     "compressed_photo.jpg",
            ...     quality=90,
            ...     max_size=(1920, 1080),
            ...     strategy='quality'
            ... )
            >>> # 跳过GIF等不支持的格式
            >>> compressed_path = image_handler.compress_image_smart(
            ...     "animation.gif",
            ...     skip_unsupported=True  # 跳过GIF，不进行压缩
            ... )
        """
        return self._compressor.compress_image_smart(
            input_path, output_path, quality, max_size, strategy, keep_metadata, skip_unsupported
        )

    def batch_compress_images(self, folder_path: Union[str, Path], output_folder: Optional[Union[str, Path]] = None,
                             quality: int = 85, max_size: Optional[tuple] = None,
                             strategy: str = 'balanced', keep_metadata: bool = False,
                             supported_formats: Optional[List[str]] = None, skip_unsupported: bool = True,
                             recursive: bool = False) -> List[str]:
        """
        批量压缩文件夹中的所有图片

        Args:
            folder_path (Union[str, Path]): 输入文件夹路径
            output_folder (Optional[Union[str, Path]], optional): 输出文件夹路径，如果为None则覆盖原文件. Defaults to None.
            quality (int, optional): 压缩质量，1-100. Defaults to 85.
            max_size (Optional[tuple], optional): 最大尺寸限制 (width, height). Defaults to None.
            strategy (str, optional): 压缩策略，'balanced', 'quality', 'size'. Defaults to 'balanced'.
            keep_metadata (bool, optional): 是否保留图片元数据. Defaults to False.
            supported_formats (Optional[List[str]], optional): 支持的图片格式列表. Defaults to None.
            skip_unsupported (bool, optional): 是否跳过不支持的格式，True=跳过，False=转换为静态图. Defaults to True.
            recursive (bool, optional): 是否递归处理子文件夹. Defaults to False.

        Returns:
            List[str]: 成功压缩的图片路径列表

        Raises:
            FileNotFoundError: 当输入文件夹不存在时

        Example:
            >>> image_handler = ImageHandler()
            >>> compressed_files = image_handler.batch_compress_images(
            ...     "./photos",
            ...     "./compressed_photos",
            ...     quality=90,
            ...     max_size=(1920, 1080)
            ... )
            >>> print(f"成功压缩 {len(compressed_files)} 个文件")
            >>> # 递归压缩子文件夹
            >>> compressed_files = image_handler.batch_compress_images(
            ...     "./photos",
            ...     "./compressed_photos",
            ...     recursive=True,  # 递归处理子文件夹
            ...     skip_unsupported=True  # 跳过GIF等不支持格式
            ... )
        """
        return self._compressor.batch_compress_images(
            folder_path, output_folder, quality, max_size, strategy, 
            keep_metadata, supported_formats, skip_unsupported, recursive
        )

    # ==================== Base64 图片处理功能 ====================

    def process_image_to_base64(self, image: str) -> str:
        """
        处理图片，统一转换为base64格式

        Args:
            image: 图片来源（base64编码/文件路径/URL）

        Returns:
            str: base64编码的图片数据

        Raises:
            Exception: 图片处理失败

        Example:
            >>> handler = ImageHandler()
            >>> # 处理本地文件
            >>> base64_data = handler.process_image_to_base64("./photo.jpg")
            >>> # 处理网络图片
            >>> base64_data = handler.process_image_to_base64("https://example.com/photo.jpg")
            >>> # base64数据直接返回
            >>> base64_data = handler.process_image_to_base64("iVBORw0KGgoAAAANSUhEUgAA...")
        """
        return self._converter.process_image_to_base64(image)

    def validate_image_format(self, image: str) -> bool:
        """
        验证图片格式是否有效

        Args:
            image: 图片来源

        Returns:
            bool: 是否为有效图片

        Example:
            >>> handler = ImageHandler()
            >>> is_valid = handler.validate_image_format("./photo.jpg")
            >>> print(is_valid)  # True or False
        """
        return self._converter.validate_image_format(image)

    def convert_base64_to_file(self, base64_data: str, output_path: str) -> bool:
        """
        将base64数据转换为本地图片文件

        Args:
            base64_data: base64编码的图片数据
            output_path: 输出文件路径

        Returns:
            bool: 转换是否成功

        Raises:
            Exception: 转换失败

        Example:
            >>> handler = ImageHandler()
            >>> success = handler.convert_base64_to_file(base64_data, "./output.jpg")
            >>> print(success)  # True or False
        """
        return self._converter.convert_base64_to_file(base64_data, output_path)
