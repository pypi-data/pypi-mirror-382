"""
图片处理模块 - 提供图片压缩、格式转换、base64转换等功能

from zx_rpa.system.image import ImageHandler
handler = ImageHandler()

## 对外方法

### 图片压缩功能
- 智能图片压缩：compress_image_smart
- 批量压缩图片：batch_compress_images

### Base64转换功能
- 图片file/url转base64：process_image_to_base64
- 验证图片格式：validate_image_format
- base64转文件：convert_base64_to_file
"""

from .client import ImageHandler

__all__ = ['ImageHandler']
