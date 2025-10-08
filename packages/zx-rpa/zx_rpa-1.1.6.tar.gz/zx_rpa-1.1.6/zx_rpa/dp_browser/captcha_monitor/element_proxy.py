"""
DrissionPage元素代理包装器

拦截元素的click、input等操作，在操作后触发验证码检测
"""
from typing import Any, Optional
from loguru import logger


class ClickProxy:
    """Click操作代理，完全兼容DrissionPage的Click API结构"""
    
    def __init__(self, original_click_actions, monitor, selector: str):
        """初始化Click代理
        
        Args:
            original_click_actions: 原始DrissionPage的ClickActions对象
            monitor: 监控管理器实例  
            selector: 元素选择器
        """
        self._original_click_actions = original_click_actions
        self._monitor = monitor
        self._selector = selector
        
        # DrissionPage常见的click方法列表（需要监控的）
        self._monitored_click_methods = {
            'to_upload', 'to_download', 'to_move', 'to_drag', 'to_hold',
            'to_right', 'to_double', 'to_middle', 'at', 'on', 'for_times',
            'when_covered', 'if_covered'
        }
    
    def __call__(self, *args, **kwargs):
        """当作为方法调用时：element.click()"""
        # 执行原始点击操作
        result = self._original_click_actions(*args, **kwargs)
        
        # 触发验证码检测
        self._trigger_captcha_detection("click")
        
        return result
    
    def _trigger_captcha_detection(self, action_type: str):
        """触发验证码检测"""
        try:
            # 检查是否为受监控的操作
            if not self._monitor.is_guarded_action(action_type):
                logger.debug("操作不在监控范围: {}", action_type)
                return
            
            # 检查是否应跳过检测
            if self._should_skip_detection():
                logger.debug("🚫 跳过检测: 包含跳过关键词: {}", self._selector)
                return
            
            # 执行验证码检测
            detected, selector, handler = self._monitor.detector.detect_after_action(
                self._monitor.current_tab,
                self._monitor.captcha_platform,
                action_type,
                self._selector
            )
            
            if detected:
                logger.debug("🚨 检测到验证码: {}", handler)
                self._monitor.handle_captcha_detected(selector, handler)
                
        except Exception as e:
            logger.debug("验证码检测异常: {}", str(e))
    
    def _should_skip_detection(self) -> bool:
        """检查是否应跳过验证码检测"""
        try:
            monitoring_config = self._monitor.config_manager.get_monitoring_config(self._monitor.captcha_platform)
            skip_keywords = monitoring_config.get("skip_detection_keywords", [])
            
            selector_lower = self._selector.lower()
            for keyword in skip_keywords:
                if keyword.lower() in selector_lower:
                    return True
            return False
        except Exception as e:
            logger.debug("检查跳过关键词异常: {}", str(e))
            return False
    
    def __getattr__(self, name: str) -> Any:
        """代理其他ClickActions方法，完全兼容DrissionPage的Click API"""
        try:
            attr = getattr(self._original_click_actions, name)
            
            # 如果是需要监控的click方法
            if callable(attr) and name in self._monitored_click_methods:
                def wrapped_method(*args, **kwargs):
                    result = attr(*args, **kwargs)
                    # 触发验证码检测
                    self._trigger_captcha_detection("click")
                    return result
                return wrapped_method
            
            # 其他属性和方法直接返回（如链式调用的中间对象）
            return attr
            
        except AttributeError as e:
            raise AttributeError(f"ClickProxy没有属性或方法 '{name}'") from e


class ElementProxy:
    """DrissionPage元素代理包装器 - 完全兼容所有元素类型"""
    
    def __init__(self, original_element, monitor, selector: str):
        """初始化元素代理
        
        Args:
            original_element: 原始DrissionPage元素对象（支持ChromiumElement, SessionElement等）
            monitor: 监控管理器实例
            selector (str): 元素选择器
        """
        self._original_element = original_element
        self._monitor = monitor
        self._selector = selector
        
        # DrissionPage中需要特殊处理的属性列表
        self._special_attributes = {
            'click',     # ClickActions对象
            'hover',     # HoverActions对象  
            'drag',      # DragActions对象
            'states',    # 状态对象
            'style',     # 样式对象
            'shadow_root'  # Shadow DOM根元素
        }
        
        # 需要监控的直接方法
        self._monitored_direct_methods = {
            'input', 'send_keys', 'clear', 'submit', 'select'
        }
    
    
    def input(self, *args, **kwargs) -> Any:
        """代理input操作"""
        # 移除input操作拦截的冗余日志
        
        # 执行原始操作
        result = self._original_element.input(*args, **kwargs)
        
        # 触发验证码检测
        self._trigger_captcha_detection("input")
        
        return result
    
    def _trigger_captcha_detection(self, action_type: str):
        """触发验证码检测
        
        Args:
            action_type (str): 操作类型
        """
        try:
            # 检查是否为受监控的操作
            if not self._monitor.is_guarded_action(action_type):
                logger.debug("操作不在监控范围: {}", action_type)
                return
            
            # 检查是否应跳过检测
            if self._should_skip_detection():
                logger.debug("🚫 跳过检测: 包含跳过关键词: {}", self._selector)
                return
            
            # 执行验证码检测（使用验证码平台配置）
            detected, selector, handler = self._monitor.detector.detect_after_action(
                self._monitor.current_tab,
                self._monitor.captcha_platform,  # 使用验证码平台配置
                action_type,
                self._selector
            )
            
            if detected:
                # 保留关键日志：检测到验证码
                logger.debug("🚨 检测到验证码: {}", handler)
                # 这里可以扩展处理逻辑
                self._handle_captcha_detected(selector, handler)
            
        except Exception as e:
            logger.debug("验证码检测异常: {}", str(e))
    
    def _handle_captcha_detected(self, selector: str, handler: str):
        """处理检测到的验证码

        Args:
            selector (str): 验证码选择器
            handler (str): 处理器名称
        """
        # 移除验证码处理过程的冗余日志

        # 调用监控器的验证码处理方法
        self._monitor.handle_captcha_detected(selector, handler)
    
    def _should_skip_detection(self) -> bool:
        """检查是否应跳过验证码检测
        
        Returns:
            bool: 是否应跳过检测
        """
        try:
            # 获取跳过检测的关键词配置
            monitoring_config = self._monitor.config_manager.get_monitoring_config(self._monitor.captcha_platform)
            skip_keywords = monitoring_config.get("skip_detection_keywords", [])
            
            # 检查选择器是否包含跳过关键词
            selector_lower = self._selector.lower()
            for keyword in skip_keywords:
                if keyword.lower() in selector_lower:
                    return True
            return False
        except Exception as e:
            logger.debug("检查跳过关键词异常: {}", str(e))
            return False
    
    def __getattr__(self, name: str) -> Any:
        """代理其他属性和方法访问 - 完全兼容DrissionPage结构
        
        Args:
            name (str): 属性或方法名
            
        Returns:
            Any: 原始元素的属性或方法
        """
        try:
            # 特殊处理：click属性返回ClickProxy
            if name == 'click':
                return ClickProxy(self._original_element.click, self._monitor, self._selector)
            
            # 特殊处理：其他需要代理的动作属性
            if name in ['hover', 'drag']:
                # 对于hover和drag操作，也可能需要监控（根据配置）
                original_attr = getattr(self._original_element, name)
                return self._create_action_proxy(original_attr, name)
            
            # 特殊处理：子元素（可能返回新的元素，需要包装）
            if name in ['shadow_root', 'sr']:
                original_attr = getattr(self._original_element, name)
                if original_attr and hasattr(original_attr, 'ele'):  # 如果是元素对象
                    return ElementProxy(original_attr, self._monitor, f"{self._selector}.{name}")
                return original_attr
            
            # 获取原始属性或方法
            attr = getattr(self._original_element, name)
            
            # 如果是方法，检查是否需要监控
            if callable(attr) and name in self._monitored_direct_methods:
                def wrapped_method(*args, **kwargs):
                    result = attr(*args, **kwargs)
                    # 检查是否在监控范围内
                    if self._monitor.is_guarded_action(name):
                        # 检查是否应跳过检测
                        if not self._should_skip_detection():
                            self._trigger_captcha_detection(name)
                    return result
                return wrapped_method
            
            # 其他所有属性和方法完全透明代理
            return attr
            
        except AttributeError as e:
            logger.debug("ElementProxy: 原始元素没有属性 '{}': {}", name, str(e))
            raise AttributeError(f"ElementProxy和原始元素都没有属性 '{name}'") from e
    
    def _create_action_proxy(self, original_action, action_name: str):
        """为动作对象创建代理"""
        class ActionProxy:
            def __init__(self, original, monitor, selector, action_type):
                self._original = original
                self._monitor = monitor
                self._selector = selector
                self._action_type = action_type
            
            def __getattr__(self, name):
                attr = getattr(self._original, name)
                if callable(attr):
                    def wrapped_method(*args, **kwargs):
                        result = attr(*args, **kwargs)
                        # 根据配置决定是否监控hover/drag操作
                        if self._monitor.is_guarded_action(self._action_type):
                            self._trigger_detection()
                        return result
                    return wrapped_method
                return attr
            
            def _trigger_detection(self):
                try:
                    detected, selector, handler = self._monitor.detector.detect_after_action(
                        self._monitor.current_tab,
                        self._monitor.captcha_platform,
                        self._action_type,
                        self._selector
                    )
                    if detected:
                        self._monitor.handle_captcha_detected(selector, handler)
                except Exception as e:
                    logger.debug("动作验证码检测异常: {}", str(e))
        
        return ActionProxy(original_action, self._monitor, self._selector, action_name)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"ElementProxy({self._selector})"
    
    def __repr__(self) -> str:
        """对象表示"""
        return f"ElementProxy(selector='{self._selector}', element={repr(self._original_element)})"
