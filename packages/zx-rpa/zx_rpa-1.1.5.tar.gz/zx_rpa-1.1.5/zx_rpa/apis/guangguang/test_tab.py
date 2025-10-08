from loguru import logger
from zx_rpa.dp_browser.common_actions import CommonActions
from .common_tab import CommonTab
from time import sleep
from .content_publish_tab import ContentPublishTab

class TestTab:

    def __init__(self, tab):
        self.tab = tab
        self.actions = CommonActions(tab)  # 基础操作（来自dp_browser）
        self.common = CommonTab(tab)  # 平台通用业务操作
        self.content_publish = ContentPublishTab(tab)  # 内容发布页面操作
    
    # ========== 单操作方法（元素定位+操作一体化） ==========
    def test_captcha(self):
        """测试验证码"""
        self.tab.ele("t:a@@text()=无图直接滑动").click()
        sleep(5)
        self.tab.ele("t:a@@text()=展示浏览器环境语言").click()
