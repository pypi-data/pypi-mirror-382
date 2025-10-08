"""
跨页面通用业务操作类

提供多个页面都会用到的相同业务操作，比如多个页面都有相同的用户名输入框
"""
from loguru import logger
from zx_rpa.dp_browser.common_actions import CommonActions
from time import sleep

class CommonTab:
    """通用业务操作类 - 提供跨页面复用的具体业务操作"""

    def __init__(self, tab):
        self.tab = tab
        self.actions = CommonActions(tab)  # 使用dp_browser的基础操作
    
    # ========== 通用单操作(元素定位+操作一体化) ==========

    # 按照位置大致分组

    # ========== 通用组合操作 ==========