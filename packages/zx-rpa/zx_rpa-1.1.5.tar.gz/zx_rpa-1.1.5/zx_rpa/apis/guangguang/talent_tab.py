"""
达人管理页面自动化操作
https://mcn.guanghe.taobao.com/page/talent
"""
from loguru import logger
from zx_rpa.dp_browser.common_actions import CommonActions
from .common_tab import CommonTab
from time import sleep
from .content_publish_tab import ContentPublishTab
from random import uniform


class TalentTab:

    def __init__(self, tab):
        self.tab = tab
        self.actions = CommonActions(tab)  # 基础操作（来自dp_browser）
        self.common = CommonTab(tab)  # 平台通用业务操作
        self.content_publish = ContentPublishTab(tab)  # 内容发布页面操作
    
    # ========== 单操作方法（元素定位+操作一体化） ==========
    
    def click_talent(self):
        """点击侧边菜单栏 - 达人管理"""
        self.common.click_talent()

    # 已绑定 选项卡相关啊从做
    def click_bound_talent(self):
        """点击 已绑定 选项卡"""
        self.tab.ele("t:div@@class=next-tabs-tab-inner@@text():已绑定").click()

    def input_search_talent(self, name_or_id: str):
        """搜索达人 - 逛逛号/昵称"""
        self.tab.ele("t:input@@placeholder=请输入创作者昵称/逛逛号进行搜索").input("", clear=True)
        self.tab.actions.type(name_or_id, interval=0.1) 

    def click_search_btn(self):
        """点击 搜索 按钮"""
        self.tab.ele("t:button@@text()=搜索").click()

    def wait_search_result(self, timeout=10):
        """等待搜索结果出现"""
        return self.actions.wait_element_appear("t:div@class=next-loading next-open next-loading-inline next-table-loading", timeout)
    
    def get_talent_info(self):
        """获取搜到到第一个达人信息
        Returns:
            dict: 达人信息
                - name (str): 昵称
                - level (str): 等级
                - publish_ele (Element): 发布元素
                - manage_works_ele (Element): 作品管理元素
                - unbind_ele (Element): 解绑元素
        """
        name_ele = self.tab.ele("t:span@@class:name--")
        level_ele = self.tab.ele("t:td@@data-next-table-col=1")
        publish_ele = self.tab.ele("t:span@@text()=发布")
        manage_works_ele = self.tab.ele("t:span@@text()=作品管理")
        unbind_ele = self.tab.ele("t:span@@text()=解绑")
        logger.debug("达人信息: {}", {"name": name_ele.text, "level": level_ele.text})
        return {"name": name_ele.text, "level": level_ele.text, "publish_ele": publish_ele, "manage_works_ele": manage_works_ele, "unbind_ele": unbind_ele}

    def click_publish_btn(self, publish_ele):
        """点击 发布 按钮"""
        publish_ele.wait.clickable()
        publish_ele.click()

    def click_publish_video_btn(self):
        """点击 发视频 按钮"""
        self.tab.ele("t:div@@class=publish-menu-item-container@@text()=发视频").wait.clickable()
        self.tab.ele("t:div@@class=publish-menu-item-container@@text()=发视频").click()

    def click_independent_publish_btn(self):
        """点击 独立发布 按钮"""
        self.tab.ele("t:div@@class=publish-menu-item-container@@text()=独立发布").wait.clickable()
        self.tab.ele("t:div@@class=publish-menu-item-container@@text()=独立发布").click()

    def click_batch_publish_btn(self):
        """点击 批量发布 按钮"""
        self.tab.ele("t:div@@class=publish-menu-item-container@@text()=批量发布").wait.clickable()
        self.tab.ele("t:div@@class=publish-menu-item-container@@text()=批量发布").click()

    def click_publish_text_image_btn(self):
        """点击 发图文 按钮"""
        self.tab.ele("t:div@@class=publish-menu-item-container@@text()=发图文").wait.clickable()
        self.tab.ele("t:div@@class=publish-menu-item-container@@text()=发图文").click()

    # ========== 组合相关操作 ==========

    def flow_search_talent(self, name_or_id):
        """搜索达人 - 逛逛号 返回达人信息
        
        Returns:
            dict: 达人信息
                - name (str): 昵称
                - level (str): 等级
                - publish_ele (Element): 发布元素
                - manage_works_ele (Element): 作品管理元素
                - unbind_ele (Element): 解绑元素
        """
        logger.debug("搜索达人: {}", name_or_id)
        self.click_bound_talent()
        self.input_search_talent(name_or_id)
        sleep(0.5)
        self.click_search_btn()
        if self.wait_search_result():
            sleep(0.5)
            result = self.get_talent_info()
            logger.debug("达人信息: {}", result)
            return result
        logger.debug("未找到达人: {}", name_or_id)
        return False

    # 点击进入发布视频或图文
    def flow_publish_video(self, publish_ele, publish_type="独立发布"):
        """进入发布视频/图文页面

        Args:
            publish_ele (Element): 发布元素
            publish_type (str): 发布类型，发视频_独立发布、发视频_批量发布、发图文
        """
        logger.debug("开始进入发布视频页面: {}", publish_type)
        self.click_publish_btn(publish_ele)
        if publish_type == "发视频_独立发布":
            self.click_publish_video_btn()
            self.click_independent_publish_btn()
            self.content_publish.wait_enter_publish_page()
        elif publish_type == "发视频_批量发布":
            self.click_publish_video_btn()
            self.click_batch_publish_btn()
            self.content_publish.wait_enter_publish_page()
        elif publish_type == "发图文":
            self.click_publish_text_image_btn()
            self.content_publish.wait_enter_publish_page()
        logger.debug("进入发布视频页面成功: {}", publish_type)
