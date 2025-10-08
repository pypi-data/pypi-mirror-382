"""
图鉴验证码识别平台 API 封装

from zx_rpa.apis.tujian import TujianClient

## 对外方法
### TujianClient（图鉴验证码客户端）
- 识别验证码：recognize_captcha
- 查询余额：get_balance
- 报错处理：report_error
- 获取支持类型：get_supported_types
"""

from .client import TujianClient

__all__ = ['TujianClient']
