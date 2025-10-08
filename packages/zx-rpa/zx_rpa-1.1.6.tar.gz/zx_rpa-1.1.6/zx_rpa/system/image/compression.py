"""
图片压缩功能模块

提供智能图片压缩、批量压缩等功能
"""

from pathlib import Path
from typing import Union, List, Optional
from loguru import logger

from .utils import ImageConstants, ImageUtils


class ImageCompressor:
    """图片压缩器 - 专门负责图片压缩相关功能"""
    
    def __init__(self):
        """初始化图片压缩器"""
        logger.debug("初始化图片压缩器")
    
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
        """
        logger.debug("开始智能图片压缩，输入: {}，质量: {}，策略: {}", input_path, quality, strategy)
        
        # 参数验证
        input_path = Path(input_path)
        ImageUtils.validate_file_exists(input_path)
        ImageUtils.validate_quality_param(quality)
        ImageUtils.validate_strategy_param(strategy)
        
        # 确定输出路径
        if output_path is None:
            output_path = input_path
        else:
            output_path = Path(output_path)
            ImageUtils.ensure_output_directory(output_path)
        
        try:
            # 尝试导入Pillow库
            try:
                from PIL import Image, ImageOps
                logger.debug("使用Pillow库进行图片压缩")
            except ImportError:
                logger.debug("缺少Pillow库，请安装: pip install Pillow")
                raise ImportError("缺少Pillow库，请安装: pip install Pillow")
            
            # 打开图片
            with Image.open(input_path) as img:
                logger.debug("原始图片信息: 格式={}, 尺寸={}, 模式={}", img.format, img.size, img.mode)

                # 检查是否为不支持的格式
                if img.format in ImageConstants.UNSUPPORTED_COMPRESSION_FORMATS:
                    if skip_unsupported:
                        logger.debug("跳过不支持的格式: {}", img.format)
                        return str(input_path)  # 返回原文件路径，不进行压缩
                    else:
                        img = self._convert_unsupported_format(img, output_path)

                # 根据策略调整参数
                final_quality, optimize_flag = ImageUtils.get_compression_params(strategy, quality)
                logger.debug("压缩参数: 质量={}, 优化={}", final_quality, optimize_flag)
                
                # 处理图片方向（自动旋转）
                if hasattr(ImageOps, 'exif_transpose'):
                    img = ImageOps.exif_transpose(img)
                    logger.debug("已处理图片方向")
                
                # 尺寸调整
                if max_size and (img.size[0] > max_size[0] or img.size[1] > max_size[1]):
                    original_size = img.size
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    logger.debug("图片尺寸调整: {} -> {}", original_size, img.size)
                
                # 颜色模式优化
                img = self._optimize_color_mode(img, output_path)
                
                # 保存压缩后的图片
                save_kwargs = self._get_save_kwargs(final_quality, optimize_flag, strategy, output_path)
                
                # 处理元数据
                if keep_metadata and hasattr(img, 'info'):
                    safe_info = {k: v for k, v in img.info.items() 
                               if k in ['dpi', 'transparency', 'gamma']}
                    save_kwargs.update(safe_info)
                    logger.debug("保留元数据: {}", list(safe_info.keys()))
                
                # 保存图片
                img.save(output_path, **save_kwargs)
                
                # 记录压缩结果
                self._log_compression_result(input_path, output_path)
                
                return str(output_path)
                
        except Exception as e:
            logger.debug("图片压缩失败: {}", str(e))
            raise
    
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
        """
        logger.debug("开始批量压缩图片，文件夹: {}，质量: {}，策略: {}", folder_path, quality, strategy)

        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            logger.debug("输入文件夹不存在或不是目录: {}", folder_path)
            raise FileNotFoundError(f"输入文件夹不存在或不是目录: {folder_path}")

        # 默认支持的图片格式
        if supported_formats is None:
            supported_formats = ImageConstants.DEFAULT_SUPPORTED_FORMATS

        # 获取所有图片文件
        image_files = self._get_image_files(folder_path, supported_formats, recursive)
        logger.debug("找到 {} 个图片文件", len(image_files))

        if not image_files:
            logger.debug("文件夹中没有找到支持的图片文件")
            return []

        # 准备输出文件夹
        if output_folder is not None:
            output_folder = Path(output_folder)
            output_folder.mkdir(parents=True, exist_ok=True)
            logger.debug("输出文件夹: {}", output_folder)

        # 批量压缩
        return self._process_batch_compression(
            image_files, folder_path, output_folder, quality, max_size, 
            strategy, keep_metadata, skip_unsupported, recursive
        )
    
    def _convert_unsupported_format(self, img, output_path: Path):
        """转换不支持的格式为静态图"""
        logger.debug("转换不支持的格式 {} 为静态图", img.format)
        
        if img.mode in ('RGBA', 'LA', 'P'):
            if 'transparency' in img.info or img.mode in ('RGBA', 'LA'):
                # 有透明度，转换为PNG
                if output_path.suffix.lower() not in ['.png']:
                    output_path = output_path.with_suffix('.png')
                img = img.convert('RGBA')
            else:
                # 无透明度，转换为RGB
                img = img.convert('RGB')
                if output_path.suffix.lower() not in ['.jpg', '.jpeg']:
                    output_path = output_path.with_suffix('.jpg')
        return img
    
    def _optimize_color_mode(self, img, output_path: Path):
        """优化颜色模式"""
        if img.mode in ('RGBA', 'LA', 'P') and output_path.suffix.lower() in ['.jpg', '.jpeg']:
            # JPEG不支持透明度，转换为RGB
            from PIL import Image
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
            logger.debug("已转换颜色模式为RGB")
        return img

    def _get_save_kwargs(self, final_quality: int, optimize_flag: bool, strategy: str, output_path: Path) -> dict:
        """获取保存参数"""
        save_kwargs = {
            'quality': final_quality,
            'optimize': optimize_flag,
        }

        # 根据文件格式添加特定参数
        if output_path.suffix.lower() in ['.jpg', '.jpeg']:
            save_kwargs.update({
                'progressive': True,  # 渐进式JPEG
                'subsampling': 0 if strategy == 'quality' else 2,  # 色度子采样
            })
        elif output_path.suffix.lower() == '.png':
            save_kwargs.update({
                'compress_level': 6 if strategy == 'balanced' else (3 if strategy == 'quality' else 9),
            })
        elif output_path.suffix.lower() == '.webp':
            save_kwargs.update({
                'method': 6,  # 压缩方法
                'lossless': strategy == 'quality',
            })

        return save_kwargs

    def _log_compression_result(self, input_path: Path, output_path: Path):
        """记录压缩结果"""
        original_size = input_path.stat().st_size
        compressed_size = output_path.stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100

        logger.debug("图片压缩完成: {} -> {}，压缩率: {:.1f}%",
                   ImageUtils.format_file_size(original_size),
                   ImageUtils.format_file_size(compressed_size),
                   compression_ratio)

    def _get_image_files(self, folder_path: Path, supported_formats: List[str], recursive: bool) -> List[Path]:
        """获取图片文件列表"""
        image_files = []
        if recursive:
            # 递归获取所有子文件夹中的图片
            for file_path in folder_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                    image_files.append(file_path)
        else:
            # 只获取当前文件夹中的图片
            for file_path in folder_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                    image_files.append(file_path)
        return image_files

    def _process_batch_compression(self, image_files: List[Path], folder_path: Path,
                                 output_folder: Optional[Path], quality: int, max_size: Optional[tuple],
                                 strategy: str, keep_metadata: bool, skip_unsupported: bool,
                                 recursive: bool) -> List[str]:
        """处理批量压缩"""
        compressed_files = []
        failed_files = []

        for i, image_file in enumerate(image_files, 1):
            try:
                logger.debug("压缩进度: {}/{} - {}", i, len(image_files), image_file.name)

                # 确定输出路径
                output_path = self._get_output_path(image_file, folder_path, output_folder, recursive)

                # 压缩单个图片
                compressed_path = self.compress_image_smart(
                    image_file, output_path, quality, max_size, strategy, keep_metadata, skip_unsupported
                )

                # 只有实际压缩了的文件才添加到结果列表
                if compressed_path != str(image_file) or not skip_unsupported:
                    compressed_files.append(compressed_path)
                else:
                    logger.debug("跳过文件: {}", image_file.name)

            except Exception as e:
                logger.debug("压缩文件失败: {} - {}", image_file.name, str(e))
                failed_files.append(str(image_file))

        logger.debug("批量压缩完成，成功: {}，失败: {}", len(compressed_files), len(failed_files))

        if failed_files:
            logger.debug("以下文件压缩失败: {}", failed_files)

        return compressed_files

    def _get_output_path(self, image_file: Path, folder_path: Path,
                        output_folder: Optional[Path], recursive: bool) -> Optional[Path]:
        """获取输出路径"""
        if output_folder is not None:
            if recursive:
                # 递归模式：保持相对路径结构
                relative_path = image_file.relative_to(folder_path)
                output_path = output_folder / relative_path
                # 确保输出目录存在
                output_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                # 非递归模式：直接放在输出文件夹
                output_path = output_folder / image_file.name
            return output_path
        else:
            return None  # 覆盖原文件
