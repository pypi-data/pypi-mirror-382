"""
验证码监控框架使用示例

演示如何使用验证码监控框架进行自动化操作
"""
from zx_rpa.dp_browser.captcha_monitor import CaptchaMonitor
from zx_rpa.apis import guangguang
from DrissionPage import Chromium
from loguru import logger


def example_basic_usage():
    """基础使用示例"""
    logger.info("=== 基础使用示例 ===")
    
    # 1. 创建浏览器实例
    browser = Chromium()
    
    # 2. 初始化验证码监控（全局生效）
    monitor = CaptchaMonitor(
        platform="guangguang",
        on_detect_policy="manual",
        quduo_token="your_quduo_token_here",  # 趣多推送token，用于发送验证码通知
        base_block_wait=0.65,
        high_risk_additional=2.0
    )
    
    # 3. 正常使用业务代码（无需修改）
    tab1 = browser.new_tab("https://mcn.guanghe.taobao.com")
    
    # 创建业务操作实例（自动被监控包装）
    talent_tab = guangguang.talent_tab(tab1)
    
    # 执行业务操作（自动检测验证码）
    talent_tab.click_talent()  # 自动检测验证码
    talent_tab.input_search_talent("测试达人")  # 自动检测验证码
    talent_tab.click_search_btn()  # 自动检测验证码
    
    logger.info("基础使用示例完成")


def example_multi_tab_usage():
    """多tab使用示例"""
    logger.info("=== 多tab使用示例 ===")
    
    browser = Chromium()
    monitor = CaptchaMonitor(
        platform="guangguang",
        on_detect_policy="manual",
        quduo_token="your_quduo_token_here"  # 趣多推送token
    )
    
    # tab1 - 达人管理
    tab1 = browser.new_tab("https://mcn.guanghe.taobao.com/page/talent")
    talent_tab = guangguang.talent_tab(tab1)  # 监控自动切换到tab1
    talent_tab.click_bound_talent()
    
    # tab2 - 内容发布
    tab2 = browser.new_tab("https://mcn.guanghe.taobao.com/page/publish")
    publish_tab = guangguang.content_publish_tab(tab2)  # 监控自动切换到tab2
    publish_tab.input_title("测试标题")
    
    # 回到tab1继续操作
    talent_tab.input_search_talent("达人名称")  # 监控自动切换回tab1
    
    logger.info("多tab使用示例完成")


def example_custom_config():
    """自定义配置示例"""
    logger.info("=== 自定义配置示例 ===")
    
    browser = Chromium()
    
    # 使用自定义配置
    monitor = CaptchaMonitor(
        platform="guangguang",
        on_detect_policy="auto_then_manual",  # 先自动后手动
        quduo_token="your_quduo_token_here",  # 趣多推送token
        base_block_wait=1.0,                  # 增加基础等待时间
        high_risk_additional=3.0,             # 增加高危操作等待时间
        retry_count=5                         # 自定义重试次数
    )
    
    tab = browser.new_tab("https://example.com")
    
    # 手动包装tab（通常不需要，工厂函数会自动包装）
    wrapped_tab = monitor.wrap_tab(tab, platform="guangguang")
    
    # 快速检测当前页面是否有验证码
    has_captcha, selector, handler = monitor.quick_check_captcha()
    if has_captcha:
        logger.info("检测到验证码: {}, 处理器: {}", selector, handler)
    else:
        logger.info("未检测到验证码")
    
    logger.info("自定义配置示例完成")


def example_error_handling():
    """错误处理示例"""
    logger.info("=== 错误处理示例 ===")
    
    try:
        browser = Chromium()
        monitor = CaptchaMonitor(
            platform="guangguang",
            on_detect_policy="manual",
            quduo_token="your_quduo_token_here"  # 趣多推送token
        )
        
        tab = browser.new_tab("https://example.com")
        talent_tab = guangguang.talent_tab(tab)
        
        # 即使验证码检测出现异常，也不会影响正常业务流程
        talent_tab.click_talent()
        
        logger.info("业务操作正常完成")
        
    except Exception as e:
        logger.error("示例执行异常: {}", str(e))
    
    logger.info("错误处理示例完成")


if __name__ == "__main__":
    # 运行所有示例
    example_basic_usage()
    example_multi_tab_usage() 
    example_custom_config()
    example_error_handling()
    
    logger.info("所有示例执行完成")
