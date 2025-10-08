"""
伊性坊平台自动化操作模块 - 商品数据采集和图片包下载

## 引入方式
```python
from zx_rpa.apis.yixingfang import YixingfangClient

# 统一客户端（推荐）
yxf = YixingfangClient(
        username="user",
        password="pass",
        tujian_username="tj_user",
        tujian_password="tj_pass"
    )
```

## 对外方法
### 基础操作
- login() -> bool - 登录伊性坊平台
- switch_mode(mode) -> bool - 切换浏览器/requests模式
- get_authorization_status() -> dict - 获取认证状态
- refresh_authorization() -> bool - 刷新认证信息

### 数据采集
- collect_product_link(product_code, mode="s") -> str - 根据商品编号获取链接
- collect_product_data(url, mode="s") -> dict - 采集商品详细数据
- download_image_package(image_url, save_folder, product_code=None) -> str - 下载图片包

### 资源管理
- close() - 关闭浏览器并清理资源


"""

from .client import YixingfangClient

__all__ = ['YixingfangClient']
