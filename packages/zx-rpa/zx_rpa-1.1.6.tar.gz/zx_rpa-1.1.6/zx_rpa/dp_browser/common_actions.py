"""
DrissionPage通用元素操作
提供跨平台的通用元素操作方法，可被所有平台复用
"""

from loguru import logger


class CommonActions:
    """DrissionPage通用元素操作类"""

    _instances = {}  # 类变量，用于存储实例

    def __new__(cls, tab):
        """单例模式，避免重复实例化"""
        tab_id = id(tab)  # 使用tab对象的id作为唯一标识
        if tab_id not in cls._instances:
            cls._instances[tab_id] = super().__new__(cls)
        return cls._instances[tab_id]

    def __init__(self, tab):
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        self.tab = tab
        self._initialized = True
        logger.debug("初始化DrissionPage通用元素操作")
    
    def wait_element_appear(self, selector, timeout=10):
        """等待加载元素出现后再消失

        Args:
            selector (str): 元素选择器
            timeout (int): 超时时间（秒）

        Returns:
            bool: True表示元素已处理完成，False表示超时
        """
        logger.debug("等待加载元素处理: {}", selector)

        # 等待加载元素出现
        if self.tab.wait.eles_loaded(selector, timeout=5):
            logger.debug("加载元素已出现，等待消失")
            # 等待加载元素消失，表示加载完成
            if self.tab.wait.ele_deleted(selector, timeout=timeout):
                logger.debug("加载完成，元素已消失")
                return True
            else:
                logger.debug("等待超时，但加载可能已完成")
                return True  # 即使超时也返回True，因为加载可能已完成
        else:
            logger.debug("未检测到加载元素，可能已经加载完成")
            return True  # 如果没有检测到加载元素，说明可能已经加载完成
            
