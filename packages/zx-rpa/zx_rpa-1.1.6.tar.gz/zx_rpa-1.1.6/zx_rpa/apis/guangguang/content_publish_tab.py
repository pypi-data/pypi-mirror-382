"""
逛逛内容发布页面自动化操作
"""

from loguru import logger
from zx_rpa.dp_browser.common_actions import CommonActions
from .common_tab import CommonTab
from time import sleep
from random import uniform


class ContentPublishTab:

    def __init__(self, tab):
        self.tab = tab
        self.actions = CommonActions(tab)  # 基础操作（来自dp_browser）
        self.common = CommonTab(tab)  # 平台通用业务操作
    
    # ========== 单操作方法（元素定位+操作一体化） ==========
    
    # 等待进入发布页面
    def wait_enter_publish_page(self, timeout=10):
        """等待进入发布页面完成"""
        return self.tab.wait.eles_loaded("t:span@@tx():立即发布", timeout=timeout)

    def upload_video_button(self, video_path: str):
        """上传视频"""
        self.tab.ele("t:span@@class=upload-button@@tx():上传视频").click.to_upload(video_path)
        self.tab.wait.eles_loaded("t:div@@class:publish-guanghe__video-show--container", timeout=30)
        sleep(1)
    
    def wait_cover_loaded(self):
        """等待封面生成完毕"""
        self.tab.wait.eles_loaded("t:div@@tx()=默认封面", timeout=10)
        sleep(1)

    # 等待是否有视频警告出现
    def wait_video_warning(self, timeout=2):
        if self.tab.wait.eles_loaded(".detect-tips-container", timeout=timeout):
            if self.tab.wait.eles_loaded(".detect-tip-title", timeout=timeout):
                tip = self.tab.ele(".detect-tip-title").text
                return tip
            else:
                return True
        else:
            return False


    # 视频描述
    def input_video_title(self, title):
        """视频描述 输入视频标题"""
        self.tab.ele("t:div@@class:publish-content__title-input--inputWrap").ele("t:input").input("", clear=True)
        self.tab.actions.type(title, interval=0.1)  # 输入验证码

    def input_video_description(self, description):
        """视频描述 输入视频描述"""
        self.tab.ele(".richText-container").input("", clear=True)
        self.tab.actions.type(description, interval=0.1)

    def input_video_tags(self, tags: list):
        """视频描述 输入视频内容标签"""
        self.tab.ele(".richText-container").ele("t:div").input("")
        sleep(0.85)
        for tag in tags:
            self.tab.actions.type(f"#{tag} ", 0.1)
            sleep(0.65)

    # 参与话题活动
    def click_add_topic_btn(self, timeout=20):
        """点击添加话题按钮 确保打开加载完毕"""
        self.tab.ele("t:div@@class:publish-content__topic-v2--select").click()
        self.tab.wait.eles_loaded("t:div@@class=next-dialog-body", timeout=timeout)

    def input_topic(self, topic: str):
        """输入话题"""
        self.tab.ele("t:input@@aria-label=输入关键词搜索").input("", clear=True)
        self.tab.actions.type(topic, interval=0.1)  # 输入验证码

    def click_search_topic_btn(self):
        """点击搜索话题按钮"""
        f_ele = self.tab.ele("t:div@@class=next-dialog-body")
        f_ele.ele("t:span@@text()=搜索").click()
    
    def click_first_topic(self):
        """点击 话题列表 第一个话题"""
        if self.tab.wait.eles_loaded("t:div@@class:publish-content__topic-v2--topic-info"):
            sleep(0.5)
            self.tab.ele("t:div@@class:publish-content__topic-v2--topic-info").click()

    def click_publish_topic_btn(self):
        """点击 话题 确认提交 按钮"""
        self.tab.ele("t:span@@text()=确认提交").click()

    # 关联商品
    def wait_recommend_product_tab(self, timeout=20):
        """等待外部推荐商品选项卡出现"""
        return self.tab.wait.eles_loaded("已为您推荐综合收益最高的商品，可点击后直接挂品", timeout=timeout)

    def click_add_product_btn(self):
        """点击添加商品按钮"""
        self.tab.ele("t:div@@class:publish-content__item-v2--item-trigger-text@@text()=添加商品").click()

    def wait_recommend_product_tab_display(self):
        """等待 推荐商品 选项卡出现，可能没有 不会出现"""
        return self.tab.wait.eles_loaded("推荐商品", timeout=5)

    def click_recommend_product_tab(self):
        """点击 推荐商品 选项卡"""
        self.tab.ele("推荐商品").wait.clickable()
        self.tab.ele("推荐商品").click()
        sleep(1)

    def get_recommend_product_eles(self):
        """获取所有 推荐商品 选项卡 元素列表"""
        return self.tab.ele("t:div@class=next-tabs-tabpane active").ele("t:div@@class:publish-content__item-v2--content").eles("t:div@@class:publish-content__item-v2--item-desc")

    def wait_selection_product_tab_display(self):
        """等待 选品车 选项卡出现，可能没有 不会出现"""
        return self.tab.wait.eles_loaded("选品车", timeout=5)
    
    def click_selection_product_tab(self):
        """点击选品车选项卡"""
        self.tab.ele("选品车").wait.clickable()
        self.tab.ele("选品车").click()

    def input_product_id(self, product_id: str):
        """输入商品id"""
        self.tab.ele("t:input@@role=searchbox").input("", clear=True)  # 先清空输入框
        self.tab.actions.type(product_id, interval=0.1)  # 输入验证码

    def click_search_product_btn(self):
        """点击搜索商品按钮 等待搜索结果出现"""
        self.tab.ele("t:i@@class:next-icon next-icon-search").wait.clickable()
        self.tab.ele("t:i@@class:next-icon next-icon-search").click()
        return self.actions.wait_element_appear("数据加载中，请耐心等待哦~")

    def click_first_product(self):
        """点击第一个商品 如果没有找到商品则返回False"""
        if not self.tab.wait.eles_loaded(f"没有找到与", timeout=1):
            self.tab.ele("t:div@class=next-tabs-tabpane active").ele("t:div@@class=next-loading next-loading-inline").ele("t:div@@class:publish-content__item-v2--item").click()
            sleep(0.5)
            return True
        else:
            return False
    
    def click_confirm_product_btn(self):
        """点击 确定 按钮"""
        self.tab.ele("t:span@@text()=确定").wait.clickable()
        self.tab.ele("t:span@@text()=确定").click()

    def click_cancel_product_btn(self):
        """点击 取消 按钮"""
        self.tab.ele("t:span@@text()=取消").wait.clickable()
        self.tab.ele("t:span@@text()=取消").click()

    # 内容来源声明
    def click_content_source_declaration(self, source: str):
        """点击 内容来源声明
        
        Args:
            source (str): 来源类型
                - 内容由AI生成
                - 虚拟演绎，仅供娱乐
                - 自主拍摄
                - 引用转载
        """
        self.tab.ele(f"t:span@@text()={source}").click()

    def click_immediately_publish_btn(self):
        """点击 立即发布 按钮"""
        self.tab.ele("x://span[text()='立即发布']").wait.clickable()
        sleep(1)
        self.tab.ele("x://span[text()='立即发布']").click()
        self.actions.wait_element_appear("内容发布成功~")

    # ========== 组合相关操作 ==========
    def flow_upload_video(self, video_path: str):
        """上传视频并等待封面加载完成
        Args:
            video_path (str): 视频路径
        """
        self.upload_video_button(video_path)
        self.wait_cover_loaded()

    def flow_join_topic_activity(self, topic: str):
        """参与话题活动, 选择第一个搜索结果"""
        self.click_add_topic_btn()
        self.input_topic(topic)
        self.click_search_topic_btn()
        self.click_first_topic()
        self.click_publish_topic_btn()
        logger.debug("参与话题活动成功: {}", topic)

    def flow_associate_product(self, product_id: str, is_click_add_product_btn=True):
        """关联商品, 选品车搜索 勾选第一个商品
        
        Args:
            product_id (str): 商品id
            是否点击添加前置添加商品按钮 (bool, optional): 是否点击添加商品按钮. Defaults to True.
        """
        if is_click_add_product_btn:
            self.click_add_product_btn()
            
        try:
            if self.wait_selection_product_tab_display():
                sleep(0.5)
                self.click_selection_product_tab()
                self.input_product_id(product_id)
                if self.click_search_product_btn():
                    if self.click_first_product():
                        self.click_confirm_product_btn()
                        logger.debug("关联商品成功: {}", product_id)
                        return product_id
            self.click_cancel_product_btn()
            
            logger.debug("关联商品失败: 没有找到与{}相关的商品或加载异常", product_id) 
            return False
        except Exception as e:
            logger.debug("关联商品失败: {}", e)            
            self.click_cancel_product_btn()
            
            return False

    def flow_get_special_tag_product_id(self):
        """获取有特殊标签的推荐商品id, 如果不存在特殊标签商品返回第一个商品id, 如果没有推荐商品返回False"""
        if self.wait_recommend_product_tab_display():
            sleep(0.5)
            self.click_recommend_product_tab()
            
            product_card_eles = self.get_recommend_product_eles()
            for product_card_ele in product_card_eles:
                product_a_ele = product_card_ele.ele("t:a@@class:publish-content__item-v2--item-itemUrl")
                a_html = product_a_ele.html
                if "<img src" in a_html:
                    product_url = product_a_ele.link
                    return self.common.extract_product_id_from_url(product_url)
            product_url = product_card_eles[0].ele("t:a@@class:publish-content__item-v2--item-itemUrl").link
            return self.common.extract_product_id_from_url(product_url)
        return False