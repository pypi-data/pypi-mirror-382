"""
平台自动化模板

from zx_rpa.apis import platform_template
login_tab = platform_template.login_tab(tab)

## LoginTab 对外方法
- 单操作方法：input_username, input_password, click_login_btn, click_remember_me 等
- 组合操作方法：login, quick_login, login_with_retry, reset_login_form 等
- 状态检查方法：is_logged_in, is_login_btn_enabled, wait_login_page_load 等
- 调试方法：debug_screenshot, highlight_login_elements 等

## 内部组合的模块
- tab.actions：基础操作（CommonActions）- 等待、点击、输入等基础方法
- tab.common：通用业务操作（CommonTab）- 跨页面复用的业务操作
"""

from .login_tab import LoginTab
from .common_tab import CommonTab

def login_tab(tab):
    """创建登录页面操作实例

    Args:
        tab: DrissionPage的tab对象

    Returns:
        LoginTab: 登录页面操作实例
    """
    return LoginTab(tab)

def common_tab(tab):
    """创建通用业务操作实例

    Args:
        tab: DrissionPage的tab对象

    Returns:
        CommonTab: 通用业务操作实例
    """
    return CommonTab(tab)

# 如果需要添加更多页面，继续添加工厂函数
# def product_tab(tab):
#     """创建商品页面操作实例"""
#     from .product_tab import ProductTab
#     return ProductTab(tab)

# def order_tab(tab):
#     """创建订单页面操作实例"""
#     from .order_tab import OrderTab
#     return OrderTab(tab)

__all__ = ['login_tab', 'common_tab']
