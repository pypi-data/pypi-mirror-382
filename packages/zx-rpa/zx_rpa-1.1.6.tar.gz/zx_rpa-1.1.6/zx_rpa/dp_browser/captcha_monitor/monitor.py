"""
验证码监控管理器

主要负责单例管理、配置管理、平台切换和智能拦截
"""
import importlib
from typing import Dict, Any
from loguru import logger
from .config_manager import ConfigManager
from .detector import CaptchaDetector
from .tab_proxy import TabProxy


class CaptchaMonitor:
    """验证码监控管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """单例模式实现，智能切换监控实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        else:
            # 已有实例，检查是否需要切换平台
            if hasattr(cls._instance, 'captcha_platform') and len(args) > 0:
                new_platform = args[0] if args else kwargs.get('platform', 'default')
                if new_platform != cls._instance.captcha_platform:
                    logger.debug("🔄 智能切换监控平台: {} -> {}", cls._instance.captcha_platform, new_platform)
                    # 重置初始化状态，允许重新初始化
                    cls._initialized = False
        return cls._instance
    
    def __init__(self, platform: str = "default",
                 on_detect_policy: str = "manual",
                 quduo_token: str = None, **kwargs):
        """初始化验证码监控管理器

        Args:
            platform (str): 平台名称，会自动查找对应的yaml配置文件
            on_detect_policy (str): 检测策略 ("manual" | "auto" | "auto_then_manual")
            quduo_token (str): 趣多推送的TOKEN，用于发送验证码通知
            **kwargs: 自定义配置参数，支持timing、monitoring、detection中的所有参数
                - base_block_wait (float): 基础阻塞等待时间
                - high_risk_additional (float): 高危操作附加等待时间
                - scan_interval (float): 检测间隔时间
                - randomize_max (float): 随机化上限时间
                - guarded_actions (list): 受监控的操作类型
                - high_risk_keywords (list): 高危操作关键词
                - manual_timeout (int): 手动处理超时时间
                - retry_count (int): 重试次数
        """
        # 避免重复初始化
        if self._initialized:
            return

        self.captcha_platform = platform  # 验证码处理平台
        self.current_platform = platform  # 当前业务平台（可动态变化）
        self.current_tab = None
        self.patched_modules = set()  # 记录已拦截的模块
        self.quduo_token = quduo_token  # 保存趣多推送token
        # 将on_detect_policy加入自定义配置
        self.custom_config = kwargs.copy()
        self.custom_config['on_detect_policy'] = on_detect_policy

        # 初始化配置管理器（自动根据平台名称查找yaml文件）
        self.config_manager = ConfigManager()

        # 初始化检测引擎
        self.detector = CaptchaDetector(self.config_manager)

        # 初始化验证码处理器
        from .captcha_handler import CaptchaHandler
        if quduo_token:
            self.captcha_handler = CaptchaHandler(quduo_token)
        else:
            logger.warning("未提供趣多推送token，验证码处理器将无法发送通知")
            # 使用空token初始化，但会在使用时报错
            self.captcha_handler = CaptchaHandler("")

        # 应用自定义配置
        self._apply_custom_config(self.custom_config)
        
        # 启动监控
        self._start_monitoring()
        
        self._initialized = True
        # 初始化完成，移除冗余日志
    
    def _apply_custom_config(self, custom_config: Dict[str, Any]):
        """应用自定义配置参数

        Args:
            custom_config (dict): 自定义配置字典
        """
        if not custom_config:
            return

        # 修复：动态更新验证码平台的配置，而不是业务平台配置
        if self.captcha_platform in self.config_manager.configs:
            config = self.config_manager.configs[self.captcha_platform]

            # 更新timing配置
            timing_keys = ["base_block_wait", "high_risk_additional", "scan_interval", "randomize_max"]
            for key in timing_keys:
                if key in custom_config:
                    if "timing" not in config:
                        config["timing"] = {}
                    config["timing"][key] = custom_config[key]
                    # 移除配置更新的冗余日志

            # 更新monitoring配置
            monitoring_keys = ["guarded_actions", "high_risk_keywords"]
            for key in monitoring_keys:
                if key in custom_config:
                    if "monitoring" not in config:
                        config["monitoring"] = {}
                    config["monitoring"][key] = custom_config[key]
                    # 移除配置更新的冗余日志

            # 更新detection配置
            detection_keys = ["on_detect_policy", "manual_timeout", "retry_count"]
            for key in detection_keys:
                if key in custom_config:
                    if "detection" not in config:
                        config["detection"] = {}
                    config["detection"][key] = custom_config[key]
                    # 移除配置更新的冗余日志
    
    def _start_monitoring(self):
        """启动监控，设置智能按需拦截"""
        try:
            # 检查并拦截已经导入的业务模块
            self._patch_already_imported_modules()
            # 移除启动成功的冗余日志
        except Exception as e:
            logger.debug("启动监控失败: {}", str(e))
    
    def get_module_for_platform(self, platform_name: str) -> str:
        """根据平台名称获取对应的模块路径

        Args:
            platform_name (str): 平台名称

        Returns:
            str: 模块路径
        """
        # 业务平台模块映射
        business_modules = {
            "guangguang": "zx_rpa.apis.guangguang",
            "taobao": "zx_rpa.apis.taobao",
            "tmall": "zx_rpa.apis.tmall",
            "platform_template": "zx_rpa.apis.platform_template"
        }

        return business_modules.get(platform_name, "")

    def _patch_already_imported_modules(self):
        """拦截已经导入的业务模块"""
        import sys

        # 业务平台模块映射
        business_modules = {
            "guangguang": "zx_rpa.apis.guangguang",
            "taobao": "zx_rpa.apis.taobao",
            "tmall": "zx_rpa.apis.tmall",
            "platform_template": "zx_rpa.apis.platform_template"
        }

        # 检查哪些业务模块已经被导入
        for module_path in business_modules.values():
            if module_path in sys.modules:
                # 检测到已导入的业务模块，进行拦截
                self._patch_module_factories(module_path)
            else:
                # 业务模块未导入，跳过
                pass
    
    def _patch_module_factories(self, module_name: str):
        """拦截指定模块的工厂函数

        Args:
            module_name (str): 模块名称
        """
        # 避免重复拦截同一个模块
        if module_name in self.patched_modules:
            logger.debug("模块已拦截，跳过: {}", module_name)
            return

        try:
            module = importlib.import_module(module_name)
            
            # 获取模块的所有导出函数
            if hasattr(module, '__all__'):
                factory_names = [name for name in module.__all__ if name]  # 过滤空字符串
            else:
                # 如果没有__all__，获取所有不以下划线开头的函数
                factory_names = [name for name in dir(module)
                               if not name.startswith('_') and callable(getattr(module, name))]
            
            # 拦截每个工厂函数
            for factory_name in factory_names:
                if hasattr(module, factory_name):
                    original_factory = getattr(module, factory_name)
                    wrapped_factory = self._create_wrapped_factory(original_factory, module_name)
                    setattr(module, factory_name, wrapped_factory)
                    # 拦截工厂函数（移除冗余日志）

            # 记录已拦截的模块
            self.patched_modules.add(module_name)
            # 模块拦截完成（移除冗余日志）

        except ImportError as e:
            logger.debug("模块导入失败: {}, 错误: {}", module_name, str(e))
        except Exception as e:
            logger.debug("拦截模块工厂函数失败: {}, 错误: {}", module_name, str(e))
    
    def _create_wrapped_factory(self, original_factory, module_name: str):
        """创建包装后的工厂函数

        Args:
            original_factory: 原始工厂函数
            module_name (str): 模块名称

        Returns:
            function: 包装后的工厂函数
        """
        def wrapped_factory(tab, *args, **kwargs):
            # 提取业务平台名称
            business_platform = self._extract_platform_name(module_name)

            # 保留关键日志：平台切换信息
            logger.debug("业务平台切换: {}", business_platform)

            # 包装tab对象（标记来自工厂函数）
            wrapped_tab = self.wrap_tab(tab, _from_factory=True, _business_platform=business_platform)

            # 调用原始工厂函数
            return original_factory(wrapped_tab, *args, **kwargs)

        return wrapped_factory
    
    def _extract_platform_name(self, module_name: str) -> str:
        """从模块名称提取平台名称
        
        Args:
            module_name (str): 模块名称
            
        Returns:
            str: 平台名称
        """
        # 从 "zx_rpa.apis.guangguang" 提取 "guangguang"
        parts = module_name.split('.')
        return parts[-1] if len(parts) > 0 else "default"
    
    def wrap_tab(self, tab, _from_factory: bool = False, _business_platform: str = None) -> TabProxy:
        """包装tab对象为代理

        Args:
            tab: 原始DrissionPage tab对象
            _from_factory (bool): 是否来自工厂函数调用（内部参数）
            _business_platform (str): 业务平台名称（仅工厂函数内部使用）

        Returns:
            TabProxy: 包装后的tab代理对象
        """
        if _from_factory and _business_platform:
            # 来自工厂函数调用：处理业务平台
            business_platform = _business_platform

            # 获取业务平台对应的模块路径
            module_path = self.get_module_for_platform(business_platform)

            # 只有在首次调用时才拦截该模块
            if module_path and module_path not in self.patched_modules:
                logger.debug("🎯 首次调用检测到，按需拦截模块: {}", module_path)
                self._patch_module_factories(module_path)

            # 更新当前业务平台
            self.current_platform = business_platform
            # 保留关键日志：双平台模式
            logger.debug("双平台模式 - 验证码平台: {}, 业务平台: {}",
                        self.captcha_platform, self.current_platform)
        else:
            # 手动调用：直接使用初始化时的验证码平台
            self.current_platform = self.captcha_platform
            # 保留关键日志：单平台模式
            logger.debug("单平台模式 - 验证码平台: {}", self.captcha_platform)

        self.current_tab = tab
        return TabProxy(tab, self)
    
    def is_guarded_action(self, action_type: str) -> bool:
        """检查是否为受监控的操作类型

        Args:
            action_type (str): 操作类型

        Returns:
            bool: 是否为受监控操作
        """
        # 修复：使用验证码平台配置，而不是业务平台配置
        monitoring_config = self.config_manager.get_monitoring_config(self.captcha_platform)
        guarded_actions = monitoring_config.get("guarded_actions", ["click", "input"])
        return action_type in guarded_actions
    
    def quick_check_captcha(self) -> tuple:
        """快速检测当前页面是否有验证码

        Returns:
            tuple: (是否检测到, 选择器, 处理器名称)
        """
        if self.current_tab is None:
            return False, None, None

        return self.detector.quick_check(self.current_tab, self.captcha_platform)

    def handle_captcha_detected(self, selector: str, handler: str):
        """处理检测到的验证码

        Args:
            selector (str): 验证码选择器
            handler (str): 处理器名称
        """
        logger.debug("委托验证码处理器处理: {}, 处理器: {}", selector, handler)

        # 获取验证码平台的配置参数（用于验证码处理）
        detection_config = self.config_manager.get_platform_config(self.captcha_platform).get("detection", {})
        mode = detection_config.get("on_detect_policy", "manual")
        timeout = detection_config.get("manual_timeout", 120)
        retry_count = detection_config.get("retry_count", 3)

        logger.debug("使用验证码平台配置: {}, 业务平台: {}", self.captcha_platform, self.current_platform)

        # 委托给专门的验证码处理器（使用验证码平台）
        success = self.captcha_handler.handle_captcha(
            self.current_tab,
            self.captcha_platform,  # 使用验证码平台进行处理
            selector,
            handler,
            mode=mode,
            timeout=timeout,
            retry_count=retry_count
        )

        logger.debug("验证码处理结果: {}", "成功" if success else "失败")
        return success

    def switch_captcha_platform(self, captcha_platform: str):
        """动态切换验证码处理平台

        Args:
            captcha_platform (str): 新的验证码平台名称
        """
        if captcha_platform == self.captcha_platform:
            logger.debug("验证码平台未变化，无需切换: {}", captcha_platform)
            return

        old_platform = self.captcha_platform
        self.captcha_platform = captcha_platform
        logger.debug("验证码平台切换成功: {} -> {}", old_platform, captcha_platform)

    def get_platform_info(self) -> dict:
        """获取当前平台信息

        Returns:
            dict: 平台信息
        """
        return {
            "captcha_platform": self.captcha_platform,  # 验证码处理平台
            "business_platform": self.current_platform,  # 当前业务平台
            "patched_modules": list(self.patched_modules)  # 已拦截的模块
        }