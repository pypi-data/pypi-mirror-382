"""
验证码处理器

根据传入的浏览器、平台、选择器、执行模式等参数来处理验证码
支持手动模式（循环检测元素消失）和自动模式
"""
import time
from typing import Optional
from loguru import logger
from .quduo_client import QuduoClient


class CaptchaHandler:
    """验证码处理器"""
    
    def __init__(self, token: str):
        """初始化验证码处理器

        Args:
            token (str): 趣多推送的TOKEN，如果为空则不发送通知
        """
        self.token = token
        if token:
            self.quduo_client = QuduoClient(token)
            logger.debug("验证码处理器初始化完成，已启用趣多推送通知")
        else:
            self.quduo_client = None
            logger.debug("验证码处理器初始化完成，未启用趣多推送通知")

        # 移除初始化完成的冗余日志
    
    def handle_captcha(self, tab, platform: str, selector: str, handler: str, 
                      mode: str = "manual", timeout: int = 120, retry_count: int = 3) -> bool:
        """处理验证码
        
        Args:
            tab: DrissionPage的tab对象
            platform (str): 平台名称
            selector (str): 验证码选择器
            handler (str): 处理器名称
            mode (str): 执行模式 ("manual" | "auto" | "auto_then_manual")
            timeout (int): 超时时间（秒）
            retry_count (int): 重试次数
            
        Returns:
            bool: 是否处理成功
        """
        # 保留关键日志：开始处理验证码
        logger.debug("🔧 开始处理验证码: {} ({}模式)", handler, mode)
        
        if mode == "manual":
            return self._handle_manual_mode(tab, selector, timeout)
        elif mode == "auto":
            return self._handle_auto_mode(tab, platform, selector, handler, retry_count)
        elif mode == "auto_then_manual":
            # 先尝试自动处理
            success = self._handle_auto_mode(tab, platform, selector, handler, retry_count)
            if not success:
                # 自动处理失败，转为手动模式
                logger.debug("自动处理失败，转为手动模式")
                return self._handle_manual_mode(tab, selector, timeout)
            return success
        else:
            logger.debug("未知的处理模式: {}", mode)
            return False
    
    def _handle_manual_mode(self, tab, selector: str, timeout: int) -> bool:
        """手动模式处理
        
        程序循环检测指定元素是否消失，消失代表处理完成
        
        Args:
            tab: DrissionPage的tab对象
            selector (str): 验证码选择器
            timeout (int): 超时时间（秒）
            
        Returns:
            bool: 是否处理成功
        """
        # 保留关键日志：进入手动处理模式
        logger.debug("👤 进入手动处理模式")
        
        # 显示提示信息
        print(f"\n🚨 检测到验证码需要手动处理:")
        print(f"   选择器: {selector}")
        print(f"   请在 {timeout} 秒内完成验证码处理...")
        print(f"   程序将自动检测验证码是否消失")
        
        # 发送通知
        if self.quduo_client:
            try:
                self.quduo_client.send("检测到验证码，请尽快处理")
            except Exception as e:
                logger.warning("发送趣多推送通知失败: {}", str(e))
        else:
            logger.debug("未配置趣多推送token，跳过通知发送")

        # 循环检测元素是否消失
        start_time = time.time()
        check_interval = 1.0  # 每秒检测一次
        last_check_time = start_time

        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time

            # 检查是否超时
            if elapsed_time >= timeout:
                # 保留关键日志：处理超时
                logger.debug("⏰ 手动处理超时，已等待: {:.1f}秒", elapsed_time)
                print("⏰ 处理超时，验证码可能未完成")
                return False

            try:
                # 检测验证码元素是否还存在
                element = tab.ele(selector, timeout=0.5)
                if not element:
                    # 保留关键日志：处理成功
                    logger.debug("✅ 验证码元素不存在，处理成功")
                    print("✅ 验证码处理成功！")
                    return True
                elif not element.states.is_displayed:
                    # 保留关键日志：处理成功
                    logger.debug("✅ 验证码元素已隐藏，处理成功")
                    print("✅ 验证码处理成功！")
                    return True
                else:
                    # 元素仍然存在且可见，继续等待
                    if current_time - last_check_time >= 10:  # 每10秒提示一次
                        remaining_time = timeout - elapsed_time
                        logger.debug("🔍 验证码检测中，剩余时间: {:.1f}秒", remaining_time)
                        last_check_time = current_time

                # 等待下次检测
                time.sleep(check_interval)

            except Exception as e:
                # 保留关键日志：检测异常
                logger.debug("❌ 验证码元素检测异常: {}", str(e))
                # 异常时不立即返回，继续检测直到超时
                time.sleep(check_interval)
    
    def _handle_auto_mode(self, tab, platform: str, selector: str, 
                         handler: str, retry_count: int) -> bool:
        """自动模式处理
        
        Args:
            tab: DrissionPage的tab对象
            platform (str): 平台名称
            selector (str): 验证码选择器
            handler (str): 处理器名称
            retry_count (int): 重试次数
            
        Returns:
            bool: 是否处理成功
        """
        logger.debug("进入自动处理模式，处理器: {}", handler)
        
        for attempt in range(retry_count):
            logger.debug("自动处理尝试 {}/{}", attempt + 1, retry_count)
            
            try:
                # 调用具体的处理器
                success = self._call_handler(tab, platform, selector, handler)
                
                if success:
                    logger.debug("自动处理成功")
                    return True
                else:
                    logger.debug("自动处理失败，尝试 {}/{}", attempt + 1, retry_count)
                    if attempt < retry_count - 1:
                        time.sleep(1)  # 重试前等待1秒
                        
            except Exception as e:
                logger.debug("自动处理异常: {}", str(e))
        
        logger.debug("自动处理失败，已达到最大重试次数")
        return False
    
    def _call_handler(self, tab, platform: str, selector: str, handler: str) -> bool:
        """调用具体的处理器
        
        Args:
            tab: DrissionPage的tab对象
            platform (str): 平台名称
            selector (str): 验证码选择器
            handler (str): 处理器名称
            
        Returns:
            bool: 是否处理成功
        """
        try:
            # 动态导入平台处理器
            module_name = f"zx_rpa.dp_browser.captcha_monitor.handlers.{platform}"
            handler_module = __import__(module_name, fromlist=[handler])
            
            if hasattr(handler_module, handler):
                handler_func = getattr(handler_module, handler)
                return handler_func(tab, selector)
            else:
                logger.debug("处理器函数不存在: {}.{}", platform, handler)
                return False
                
        except ImportError as e:
            logger.debug("导入处理器模块失败: {}, 错误: {}", platform, str(e))
            return False
        except Exception as e:
            logger.debug("调用处理器异常: {}", str(e))
            return False
