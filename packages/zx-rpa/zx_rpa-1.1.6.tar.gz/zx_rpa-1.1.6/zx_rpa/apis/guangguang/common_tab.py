"""
逛逛平台通用业务操作类

提供多个页面都会用到的相同业务操作，比如多个页面都有相同的用户名输入框等
"""
import re
from loguru import logger
from zx_rpa.dp_browser.common_actions import CommonActions
from time import sleep

class CommonTab:
    """通用业务操作类 - 提供跨页面复用的具体业务操作"""

    def __init__(self, tab):
        self.tab = tab
        self.actions = CommonActions(tab)  # 使用dp_browser的基础操作
    
    # ========== 通用单操作(元素定位+操作一体化) ==========

    # 侧边菜单栏
    def click_home(self):
        """点击侧边菜单栏 - 首页"""
        self.tab.ele("t:li@@text()=首页").click()

    def click_talent(self):
        """点击侧边菜单栏 - 达人管理"""
        self.tab.ele("t:li@@text()=达人管理").click()

    # 验证码
    def wait_captcha_appear(self, timeout=3):
        """等待验证码出现"""
        return self.tab.wait.eles_loaded("#nc_1_n1z", timeout=timeout)

    # 数据处理
    def extract_product_id_from_url(self, url: str) -> str:
        """从商品URL中提取商品ID

        Args:
            url (str): 淘宝商品URL，如 https://item.taobao.com/item.htm?id=520720076936

        Returns:
            str: 商品ID，如 '520720076936'，如果提取失败返回空字符串
        """
        if not url or not isinstance(url, str):
            return ''

        # 使用正则表达式匹配 id= 后面的数字
        
        match = re.search(r'[?&]id=(\d+)', url)
        if match:
            return match.group(1)

        return ''
    
    # ========== 通用组合操作 ==========
    def flow_handle_captcha(self):
        """处理验证码"""
        while self.wait_captcha_appear():
            logger.debug("检测到验证码，等待处理")
            sleep(5)
