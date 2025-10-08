
"""
DrissionPage Tab代理包装器

拦截tab的ele()方法，返回包装后的元素代理对象
"""
from typing import Any
from loguru import logger
from .element_proxy import ElementProxy


class ActionsProxy:
    """DrissionPage Actions代理包装器 - 完全兼容Actions API"""
    
    def __init__(self, original_actions, monitor):
        """初始化Actions代理
        
        Args:
            original_actions: 原始DrissionPage actions对象
            monitor: 监控管理器实例
        """
        self._original_actions = original_actions
        self._monitor = monitor
        
        # DrissionPage Actions中需要监控的方法
        self._monitored_actions = {
            'type', 'input', 'click', 'move', 'scroll', 'drag', 'hold'
        }
    
    def type(self, *args, **kwargs):
        """代理type操作，触发验证码检测"""
        # 执行原始操作
        result = self._original_actions.type(*args, **kwargs)
        
        # 触发验证码检测
        self._trigger_captcha_detection("type")
        
        return result
    
    def _trigger_captcha_detection(self, action_type: str):
        """触发验证码检测
        
        Args:
            action_type (str): 操作类型
        """
        try:
            # 检查是否为受监控的操作
            if not self._monitor.is_guarded_action(action_type):
                logger.debug("Actions操作不在监控范围: {}", action_type)
                return
            
            # 执行验证码检测（使用验证码平台配置）
            detected, selector, handler = self._monitor.detector.detect_after_action(
                self._monitor.current_tab,
                self._monitor.captcha_platform,
                action_type,
                "actions.type"  # 使用特殊选择器标识
            )
            
            if detected:
                # 保留关键日志：检测到验证码
                logger.debug("🚨 Actions操作检测到验证码: {}", handler)
                # 处理检测到的验证码
                self._monitor.handle_captcha_detected(selector, handler)
            
        except Exception as e:
            logger.debug("Actions验证码检测异常: {}", str(e))
    
    def __getattr__(self, name: str) -> Any:
        """代理其他Actions方法访问 - 智能监控
        
        Args:
            name (str): 方法名
            
        Returns:
            Any: 原始actions的方法
        """
        try:
            attr = getattr(self._original_actions, name)
            
            # 如果是可调用的方法且在监控列表中
            if callable(attr) and name in self._monitored_actions:
                def wrapped_method(*args, **kwargs):
                    result = attr(*args, **kwargs)
                    # 检查是否需要监控此类型的actions
                    if self._monitor.is_guarded_action(name):
                        self._trigger_captcha_detection(name)
                    return result
                return wrapped_method
            
            # 其他方法和属性直接返回
            return attr
            
        except AttributeError as e:
            logger.debug("ActionsProxy: 原始actions没有方法 '{}': {}", name, str(e))
            raise AttributeError(f"ActionsProxy和原始actions都没有方法 '{name}'") from e


class TabProxy:
    """DrissionPage Tab代理包装器"""
    
    def __init__(self, original_tab, monitor):
        """初始化Tab代理

        Args:
            original_tab: 原始DrissionPage tab对象
            monitor: 监控管理器实例
        """
        self._original_tab = original_tab
        self._monitor = monitor
        # 移除Tab代理创建的冗余日志

        # 执行tab切换后的验证码检测
        self._check_captcha_after_tab_switch()
    
    def ele(self, locator, *args, **kwargs):
        """代理ele方法，返回包装后的元素代理
        
        Args:
            locator: 元素定位符
            *args: 其他位置参数
            **kwargs: 其他关键字参数
            
        Returns:
            ElementProxy: 包装后的元素代理对象
        """
        # 移除元素拦截的冗余日志
        
        # 调用原始tab的ele方法获取元素
        original_element = self._original_tab.ele(locator, *args, **kwargs)
        
        # 如果元素不存在，直接返回None
        if original_element is None:
            return None
        
        # 包装成元素代理并返回
        return ElementProxy(original_element, self._monitor, str(locator))
    
    def eles(self, locator, *args, **kwargs):
        """代理eles方法，返回包装后的元素代理列表
        
        Args:
            locator: 元素定位符
            *args: 其他位置参数
            **kwargs: 其他关键字参数
            
        Returns:
            list: 包装后的元素代理对象列表
        """
        logger.debug("拦截eles方法，定位符: {}", locator)
        
        # 调用原始tab的eles方法获取元素列表
        original_elements = self._original_tab.eles(locator, *args, **kwargs)
        
        # 包装每个元素
        wrapped_elements = []
        for i, element in enumerate(original_elements):
            if element is not None:
                selector = f"{locator}[{i}]"
                wrapped_elements.append(ElementProxy(element, self._monitor, selector))
        
        return wrapped_elements
    
    def __getattr__(self, name: str) -> Any:
        """代理其他属性和方法访问
        
        Args:
            name (str): 属性或方法名
            
        Returns:
            Any: 原始tab的属性或方法
        """
        try:
            # 特殊处理：actions属性返回代理对象
            if name == 'actions':
                return ActionsProxy(self._original_tab.actions, self._monitor)
            
            # 直接从原始tab获取属性或方法
            attr = getattr(self._original_tab, name)
            
            # 如果是方法且可能影响页面状态，记录日志
            if callable(attr) and name in ['get', 'refresh', 'back', 'forward']:
                def wrapped_method(*args, **kwargs):
                    logger.debug("Tab操作: {}", name)
                    result = attr(*args, **kwargs)
                    # 页面状态改变后，可能需要重新检测验证码
                    return result
                return wrapped_method
            
            # 特殊处理：可能返回新tab/frame的方法需要包装
            if name in ['new_tab', 'get_tab', 'get_frame', 'get_shadow']:
                if callable(attr):
                    def wrapped_tab_method(*args, **kwargs):
                        result = attr(*args, **kwargs)
                        # 如果返回的是tab/page对象，也需要包装
                        if result and hasattr(result, 'ele'):
                            logger.debug("包装新的tab/frame对象: {}", type(result).__name__)
                            return self._monitor.wrap_tab(result)
                        return result
                    return wrapped_tab_method
            
            # 其他所有属性和方法完全透明代理
            # 包括: wait, url, title, html, cookies, states, style, rect等等
            return attr
            
        except AttributeError as e:
            # 如果原始tab没有这个属性，抛出清晰的错误信息
            logger.debug("TabProxy: 原始tab没有属性 '{}': {}", name, str(e))
            raise AttributeError(f"TabProxy和原始tab都没有属性 '{name}'") from e
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"TabProxy(url={self.url})"
    
    def __repr__(self) -> str:
        """对象表示"""
        return f"TabProxy(tab_id={id(self._original_tab)}, url='{self.url}')"

    def _check_captcha_after_tab_switch(self):
        """tab切换后的验证码检测（高危等待时间）"""
        try:
            # 添加调试日志：开始tab切换后检测
            logger.debug("🔄 开始tab切换后验证码检测")
            import time
            start_time = time.time()

            # 使用高危等待时间进行检测
            detected, selector, handler = self._monitor.detector.detect_after_tab_switch(
                self._original_tab,
                self._monitor.captcha_platform
            )

            end_time = time.time()
            detection_time = end_time - start_time
            
            # 计算预算时间（用于比较）
            timing_config = self._monitor.config_manager.get_timing_config(self._monitor.captcha_platform)
            estimated_time = timing_config.get("base_block_wait", 0.65) + timing_config.get("high_risk_additional", 2.0)
            
            logger.debug("⏱️ tab切换后检测耗时: {:.2f}秒 (预算约: {:.2f}秒)", detection_time, estimated_time)

            if detected:
                # 保留关键日志：tab切换后检测到验证码
                logger.debug("⚠️ tab切换后检测到验证码: {}", handler)
                # tab切换后检测到验证码，需要阻塞处理
                logger.debug("🔧 tab切换后验证码检测：开始阻塞处理")
                self._handle_captcha_detected_after_switch(selector, handler)
            else:
                # tab切换后未检测到验证码
                logger.debug("✅ tab切换后未检测到验证码")

        except Exception as e:
            # 保留关键日志：异常信息
            logger.debug("❌ tab切换后验证码检测异常: {}", str(e))

    def _handle_captcha_detected_after_switch(self, selector: str, handler: str):
        """处理tab切换后检测到的验证码

        Args:
            selector (str): 验证码元素选择器
            handler (str): 处理器名称
        """
        try:
            logger.debug("🔧 开始处理tab切换后检测到的验证码: {}", handler)
            
            # 委托给监控管理器处理
            success = self._monitor.handle_captcha_detected(selector, handler)

            if success:
                # 保留关键日志：处理成功
                logger.debug("✅ tab切换后验证码处理成功")
            else:
                # 保留关键日志：处理失败
                logger.debug("❌ tab切换后验证码处理失败")
                
            return success
            
        except Exception as e:
            logger.debug("❌ tab切换后验证码处理异常: {}", str(e))
            return False
