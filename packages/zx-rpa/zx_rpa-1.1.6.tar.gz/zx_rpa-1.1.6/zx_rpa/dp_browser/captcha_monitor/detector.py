"""
验证码检测引擎

负责执行验证码检测逻辑，支持多种检测策略和处理器
"""
import time
import random
from typing import Optional, Dict, Any, List, Tuple
from loguru import logger


class CaptchaDetector:
    """验证码检测引擎"""
    
    def __init__(self, config_manager):
        """初始化检测引擎
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        # 移除初始化完成的冗余日志
    
    def detect_after_action(self, tab, platform_name: str, action_type: str,
                          selector: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """在操作后执行验证码检测

        Args:
            tab: DrissionPage的tab对象
            platform_name (str): 平台名称
            action_type (str): 操作类型（click、input等）
            selector (str): 元素选择器

        Returns:
            Tuple[bool, Optional[str], Optional[str]]:
                (是否检测到验证码, 匹配的选择器, 处理器名称)
        """
        # 移除检测开始的冗余日志

        # 一次性获取平台配置，避免重复查找
        platform_config = self.config_manager.get_platform_config(platform_name)

        # 获取等待时间配置
        wait_time = self._calculate_wait_time_with_config(platform_config, selector)
        # 移除等待时间计算的冗余日志

        # 执行阻塞检测
        return self._blocking_detection(tab, platform_name, wait_time, platform_config)
    
    def _calculate_wait_time_with_config(self, platform_config: dict, selector: str) -> float:
        """使用已获取的配置计算等待时间

        Args:
            platform_config (dict): 平台配置
            selector (str): 元素选择器

        Returns:
            float: 等待时间（秒）
        """
        timing_config = platform_config.get("timing", {})
        base_wait = timing_config.get("base_block_wait", 0.65)
        randomize_max = timing_config.get("randomize_max", 0.85)

        # 修复等待时间计算：确保randomize_max >= base_wait
        if randomize_max < base_wait:
            randomize_max = base_wait + 0.2  # 至少比基础等待多0.2秒
            
        # 基础等待时间 + 随机化（在base_wait到randomize_max之间）
        wait_time = random.uniform(base_wait, randomize_max)

        # 检查是否为高危操作
        if self._is_high_risk_action_with_config(platform_config, selector):
            high_risk_additional = timing_config.get("high_risk_additional", 2.0)
            wait_time += high_risk_additional
            logger.debug("🔺 高危操作，基础等待: {:.2f}秒，增加: {:.2f}秒，总计: {:.2f}秒", 
                        wait_time - high_risk_additional, high_risk_additional, wait_time)

        return wait_time

    def _is_high_risk_action_with_config(self, platform_config: dict, selector: str) -> bool:
        """使用已获取的配置检查是否为高危操作

        Args:
            platform_config (dict): 平台配置
            selector (str): 元素选择器

        Returns:
            bool: 是否为高危操作
        """
        monitoring_config = platform_config.get("monitoring", {})
        high_risk_keywords = monitoring_config.get("high_risk_keywords", [])

        # 检查选择器是否包含高危关键词
        for keyword in high_risk_keywords:
            if keyword in selector:
                return True
        return False
    
    def _blocking_detection(self, tab, platform_name: str,
                          total_wait_time: float, platform_config: dict = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """执行阻塞式检测

        Args:
            tab: DrissionPage的tab对象
            platform_name (str): 平台名称
            total_wait_time (float): 总等待时间
            platform_config (dict): 平台配置（可选，避免重复查找）

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: 检测结果
        """
        # 使用传入的配置或重新获取
        if platform_config is None:
            platform_config = self.config_manager.get_platform_config(platform_name)

        timing_config = platform_config.get("timing", {})
        scan_interval = timing_config.get("scan_interval", 0.10)

        handlers = platform_config.get("captcha_handlers", [])
        if not handlers:
            logger.debug("平台无验证码处理器配置: {}", platform_name)
            time.sleep(total_wait_time)
            return False, None, None
        
        # 轮询检测 - 优化版本
        elapsed_time = 0.0
        detection_start_time = time.time()
        
        while elapsed_time < total_wait_time:
            # 检查每个处理器
            for handler_config in handlers:
                selector = handler_config.get("selector")
                handler_name = handler_config.get("handler")
                
                if self._check_captcha_element(tab, selector):
                    # 保留关键日志：检测到验证码
                    logger.debug("🚨 检测到验证码: {}", handler_config.get("name"))
                    return True, selector, handler_name
            
            # 等待下一次检测
            time.sleep(scan_interval)
            
            # 使用实际经过的时间，避免累积误差
            elapsed_time = time.time() - detection_start_time
        
        # 移除未发现验证码的冗余日志
        return False, None, None
    
    def _check_captcha_element(self, tab, selector: str) -> bool:
        """检查验证码元素是否存在
        
        Args:
            tab: DrissionPage的tab对象
            selector (str): 元素选择器
            
        Returns:
            bool: 元素是否存在且可见
        """
        try:
            if not selector:
                return False
                
            # 优化：使用更短的超时时间减少检测开销
            element = tab.ele(selector, timeout=0.01)  # 从0.1秒减少到0.01秒
            if element:
                # 检查元素是否可见
                return element.states.is_displayed
            return False
        except Exception as e:
            # 保留关键日志：检测异常
            logger.debug("❌ 验证码元素检测异常: {}", str(e))
            return False
    
    def quick_check(self, tab, platform_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """快速检测验证码（不等待）
        
        Args:
            tab: DrissionPage的tab对象
            platform_name (str): 平台名称
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: 检测结果
        """
        handlers = self.config_manager.get_captcha_handlers(platform_name)
        
        for handler_config in handlers:
            selector = handler_config.get("selector")
            handler_name = handler_config.get("handler")
            
            if self._check_captcha_element(tab, selector):
                # 保留关键日志：快速检测到验证码
                logger.debug("⚡ 快速检测到验证码: {}", handler_config.get("name"))
                return True, selector, handler_name
        
        return False, None, None

    def detect_after_tab_switch(self, tab, platform_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """tab切换后验证码检测（使用高危等待时间）

        Args:
            tab: DrissionPage的tab对象
            platform_name (str): 平台名称

        Returns:
            Tuple[bool, Optional[str], Optional[str]]:
                (是否检测到验证码, 匹配的选择器, 处理器名称)
        """
        # 移除tab切换检测开始的冗余日志

        # 一次性获取平台配置，避免重复查找
        platform_config = self.config_manager.get_platform_config(platform_name)

        # 计算高危等待时间
        wait_time = self._calculate_high_risk_wait_time(platform_config)
        # 移除等待时间的冗余日志

        # 执行阻塞检测
        return self._blocking_detection(tab, platform_name, wait_time, platform_config)

    def _calculate_high_risk_wait_time(self, platform_config: dict) -> float:
        """计算高危等待时间（用于tab切换后检测）

        Args:
            platform_config (dict): 平台配置

        Returns:
            float: 高危等待时间（秒）
        """
        timing_config = platform_config.get("timing", {})
        base_wait = timing_config.get("base_block_wait", 0.65)
        randomize_max = timing_config.get("randomize_max", 0.85)
        high_risk_additional = timing_config.get("high_risk_additional", 2.0)

        # 修复高危等待时间计算：确保randomize_max >= base_wait
        if randomize_max < base_wait:
            randomize_max = base_wait + 0.2
            
        # 基础随机等待时间 + 高危附加时间
        base_random_wait = random.uniform(base_wait, randomize_max)
        wait_time = base_random_wait + high_risk_additional

        # 添加调试日志：等待时间计算详情
        logger.debug("🧮 tab切换高危等待计算: {:.2f}(基础随机) + {:.2f}(高危附加) = {:.3f}秒",
                    base_random_wait, high_risk_additional, wait_time)

        return wait_time
