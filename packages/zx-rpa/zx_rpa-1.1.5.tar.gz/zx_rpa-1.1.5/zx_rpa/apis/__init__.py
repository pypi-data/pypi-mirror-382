"""
ZX_RPA APIs模块
统一的第三方平台API封装
"""

# 导入单个平台API
from .qiniuyun import QiniuManager

# 导入复杂平台API（子模块）
from .crmeb import CrmebApiClient, CrmebWebClient
from .yixingfang import YixingfangClient
from .bitbrowser import BitBrowserClient

# 导入阿里平台API



__all__ = [
    "QiniuManager",
    "CrmebApiClient",
    "CrmebWebClient",
    "YixingfangClient",
    "BitBrowserClient",
]
