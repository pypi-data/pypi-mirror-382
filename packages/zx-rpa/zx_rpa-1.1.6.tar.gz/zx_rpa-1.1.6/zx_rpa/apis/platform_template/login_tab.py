"""
登录页面自动化操作

示例页面类，展示如何使用通用操作和实现页面特定功能
"""
from loguru import logger
from zx_rpa.dp_browser.common_actions import CommonActions
from .common_tab import CommonTab


class LoginTab:
    """登录页面操作类 - 完全扁平化设计"""

    def __init__(self, tab):
        self.tab = tab
        self.actions = CommonActions(tab)  # 基础操作（来自dp_browser）
        self.common = CommonTab(tab)  # 平台通用业务操作
    
    # ========== 单操作方法（元素定位+操作一体化） ==========
    
    # 按照位置大致分组

    # ========== 组合相关操作 ==========
