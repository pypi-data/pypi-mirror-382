"""
系统资源操作模块 - 提供文件、文件夹、压缩包、图片、进程等系统级操作

## 引入方式

# 文件处理器
from zx_rpa.system import FileHandler
- read_txt_to_list(file_path, strip=True, skip_empty=True, remove_duplicates=False) -> List[str] - 读取txt文件内容并转换为列表

# 文件夹处理器
from zx_rpa.system import FolderHandler
- create_output_folder_with_suffix(folder_path, suffix="_输出") -> str - 创建同级同名加指定后缀的新文件夹
- get_files_natural_sorted(folder_path) -> List[Path] - 获取文件夹中的文件列表，按自然排序
- check_file_exists_in_folder(folder_path, filename, extensions=None) -> Union[bool, dict] - 检查文件夹中是否存在指定文件

# 图片处理器
from zx_rpa.system import ImageHandler
- compress_image_smart(input_path, output_path=None, quality=85, max_size=None, strategy='balanced', skip_unsupported=True) -> str - 智能图片压缩
- batch_compress_images(folder_path, output_folder=None, quality=85, max_size=None, strategy='balanced', skip_unsupported=True, recursive=False) -> List[str] - 批量压缩文件夹中的图片
- process_image_to_base64(image) -> str - 处理图片转base64格式
- validate_image_format(image) -> bool - 验证图片格式是否有效
- convert_base64_to_file(base64_data, output_path) -> bool - 将base64数据转换为本地图片文件


# 压缩包处理器
from zx_rpa.system import ArchiveHandler
- is_archive_file(file_path) -> bool - 检查文件是否为支持的压缩包格式
- get_archive_info(archive_path) -> Dict[str, Any] - 获取压缩包信息
- extract_archive(archive_path, destination=None, password=None, overwrite=True, delete_source=False, progress_callback=None) -> str - 解压压缩包（destination为None时原地解压）
- create_archive(source_path, archive_path=None, archive_format="zip", compression_mode="balanced", password=None, delete_source=False, progress_callback=None) -> str - 创建压缩包（archive_path为None时原地压缩）
- extract_single_file(archive_path, file_name, destination=None, password=None, delete_source=False) -> str - 从压缩包中解压单个文件（destination为None时原地解压）
- list_archive_contents(archive_path) -> List[Dict[str, Any]] - 列出压缩包内容详情
- test_archive(archive_path, password=None) -> bool - 测试压缩包完整性
- batch_extract(archive_paths, destination=None, password=None, overwrite=True, delete_source=False, progress_callback=None) -> List[str] - 批量解压多个压缩包（destination为None时原地解压）


"""

from .file_handler import FileHandler
from .folder_handler import FolderHandler
from .archive_handler import ArchiveHandler
from .image import ImageHandler

__all__ = ['FileHandler', 'FolderHandler', 'ArchiveHandler', 'ImageHandler']
