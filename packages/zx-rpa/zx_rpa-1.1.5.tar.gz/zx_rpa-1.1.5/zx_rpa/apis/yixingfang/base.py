"""
伊性坊平台基础操作模块

提供浏览器初始化、登录、模式切换等基础功能。
遵循ZX_RPA规范，每个函数不超过50行，使用loguru日志。
"""

import time
import requests
from typing import Optional, Any, Union
from DrissionPage import Chromium, ChromiumOptions
from loguru import logger

from .auth import AuthManager
from .captcha import CaptchaHandler

# 常量定义 - 避免硬编码
DEFAULT_BN_PARAM = "4589809440140"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
AUTHORIZATION_TIMEOUT = 100
VALID_COOKIE_DOMAINS = ['www.yxfshop.com', '.yxfshop.com']

# 限制对外暴露的类和方法
__all__ = ['YixingfangBase']


class YixingfangBase:
    """
    伊性坊平台基础操作类

    提供浏览器操作、登录认证、模式切换等基础功能。
    避免硬编码，支持参数化配置。

    公开方法（对外API）：
    - login() -> bool: 登录功能
    - switch_mode(mode: str) -> bool: 切换浏览器模式
    - get_authorization(force_refresh: bool = False) -> Optional[str]: 获取Authorization
    - close_browser(): 关闭浏览器
    """

    def __init__(self, username: str, password: str, tujian_username: str, tujian_password: str,
                 headless: bool = False,
                 port: Union[int, str, None] = None,
                 base_url: str = "https://www.yxfshop.com/",
                 default_bn: str = DEFAULT_BN_PARAM,
                 user_agent: str = DEFAULT_USER_AGENT,
                 timeout: int = AUTHORIZATION_TIMEOUT):
        """
        初始化伊性坊基础操作类

        Args:
            username: 伊性坊用户名
            password: 伊性坊密码
            tujian_username: 图鉴验证码用户名
            tujian_password: 图鉴验证码密码
            headless: 是否无头模式，默认False
            port: 浏览器端口，None=不设置端口(默认)，'auto'=自动端口，int=指定端口
            base_url: 基础URL，默认伊性坊官网
            default_bn: 默认bn参数，默认使用常量
            user_agent: 用户代理字符串，默认使用常量
            timeout: 请求超时时间，默认100秒
        """
        logger.debug("初始化伊性坊基础操作类，无头模式: {}", headless)
        
        # 参数验证
        if not username or not password:
            logger.debug("伊性坊用户名和密码不能为空")
            raise ValueError("伊性坊用户名和密码不能为空")
            
        if not tujian_username or not tujian_password:
            logger.debug("图鉴用户名和密码不能为空")
            raise ValueError("图鉴用户名和密码不能为空")

        # 基本配置
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip('/')
        self.port = port
        self.default_bn = default_bn
        self.user_agent = user_agent
        self.timeout = timeout
        self.mode = "d"  # 默认浏览器模式

        # 初始化浏览器
        self._init_browser(headless)
        
        # 初始化认证管理器
        self.auth_manager = AuthManager()
        
        # 初始化验证码处理器
        self.captcha_handler = CaptchaHandler(tujian_username, tujian_password)
        
        # 页面元素定位器
        self._init_selectors()
        
        logger.debug("伊性坊基础操作类初始化完成")

    def _init_browser(self, headless: bool):
        """初始化浏览器"""
        port_info = self._get_port_info()
        logger.debug("初始化浏览器，端口设置: {}，无头模式: {}", port_info, headless)

        try:
            co = ChromiumOptions()
            co.headless(headless)

            # 根据端口设置配置浏览器
            if self.port is None:
                # 不设置端口（默认模式）
                pass
            elif self.port == 'auto':
                # 自动端口模式
                co.auto_port(True)
            elif isinstance(self.port, int):
                # 指定端口模式
                co.set_local_port(self.port)
            else:
                logger.debug("无效的端口设置: {}", self.port)
                raise ValueError(f"无效的端口设置: {self.port}")

            self.browser = Chromium(co)

            # 尝试获取现有标签页或创建新标签页
            try:
                self.tab = self.browser.get_tab(url="yxfshop.com")
                logger.debug("获取到现有标签页")
            except Exception:
                logger.debug("未找到现有标签页，创建新标签页")
                self.tab = self.browser.new_tab(self.base_url)
                
        except Exception as e:
            logger.debug("初始化浏览器失败: {}", str(e))
            raise Exception(f"初始化浏览器失败: {str(e)}")

    def _get_port_info(self) -> str:
        """获取端口设置信息用于日志显示"""
        if self.port is None:
            return "默认(不设置端口)"
        elif self.port == 'auto':
            return "自动端口"
        elif isinstance(self.port, int):
            return f"指定端口 {self.port}"
        else:
            return f"未知设置 {self.port}"

    def _init_selectors(self):
        """初始化页面元素定位器"""
        self.selectors = {
            'username_input': "t:input@@id=in_login",
            'password_input': "t:input@@id=in_passwd", 
            'captcha_input': "t:input@@id=iptlogin",
            'captcha_img': "#LoginimgVerifyCode",
            'captcha_refresh': "t:a@@text()= 看不清楚?换个图片",
            'submit_btn': "t:input@@value=登录",
            'login_link': "t:a@@text()=[请登录]",
            'login_title': "t:h4@@text()=已注册用户，请登录",
            'login_error': "t:div@@class=error",
            'login_status': "@@id=loginBar_widgets_1970"
        }

    def login(self) -> bool:
        """
        检测登录状态，未登录则执行登录
        
        Returns:
            bool: 登录成功返回True
            
        Raises:
            Exception: 登录失败时抛出异常
        """
        logger.debug("开始登录检查")
        
        # 刷新页面
        self.tab.refresh()
        time.sleep(2)

        # 检查登录状态
        if self._is_logged_in():
            logger.debug("已处于登录状态")
            return True

        logger.debug("未登录，开始登录流程")
        
        # 点击登录链接
        self._click_login_link()
        
        # 等待登录页面加载
        if not self.tab.wait.ele_displayed(self.selectors['login_title'], timeout=10):
            logger.debug("登录页面加载失败")
            raise Exception("登录页面加载失败")

        # 尝试登录
        success = self._attempt_login_with_retry()
        if success:
            logger.debug("登录成功")
            # 登录成功后获取Authorization
            self._fetch_and_cache_authorization()
            return True
        else:
            logger.debug("登录失败")
            raise Exception("登录失败")

    def _is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            if self.tab.wait.eles_loaded(self.selectors['login_status'], timeout=10):
                ele_html = self.tab.ele(self.selectors['login_status']).html
                is_logged = "display" in ele_html
                logger.debug("登录状态检查结果: {}", is_logged)
                return is_logged
            return False
        except Exception as e:
            logger.debug("登录状态检查异常: {}", str(e))
            return False

    def _click_login_link(self):
        """点击登录链接"""
        try:
            login_ele = self.tab.ele(self.selectors['login_link'])
            if login_ele:
                login_ele.click()
                logger.debug("点击登录链接成功")
            else:
                logger.debug("未找到登录链接")
                raise Exception("未找到登录链接")
        except Exception as e:
            logger.debug("点击登录链接失败: {}", str(e))
            raise Exception(f"点击登录链接失败: {str(e)}")

    def switch_mode(self, mode: str) -> bool:
        """
        切换浏览器模式
        
        Args:
            mode: 目标模式，'d'表示浏览器模式，'s'表示requests模式
            
        Returns:
            bool: 切换成功返回True
            
        Raises:
            ValueError: 无效的模式参数
        """
        if mode not in ['d', 's']:
            logger.debug("无效的模式参数: {}，只支持 'd' 或 's'", mode)
            raise ValueError(f"无效的模式参数: {mode}，只支持 'd' 或 's'")

        current_mode = getattr(self, 'mode', 'd')
        
        if current_mode == mode:
            logger.debug("当前已是目标模式: {}", mode)
            return True

        logger.debug("切换模式: {} -> {}", current_mode, mode)
        self.tab.change_mode()
        self.mode = mode
        return True

    def close_browser(self):
        """关闭浏览器并清理资源"""
        logger.debug("开始关闭浏览器")
        
        try:
            if hasattr(self, 'browser') and self.browser:
                self.browser.quit()
                self.browser = None
                logger.debug("浏览器已关闭")
        except Exception as e:
            logger.debug("关闭浏览器异常: {}", str(e))

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """上下文管理器退出时清理资源"""
        self.close_browser()

    def _attempt_login_with_retry(self, max_attempts: int = 3) -> bool:
        """
        尝试登录，支持重试

        Args:
            max_attempts: 最大尝试次数

        Returns:
            bool: 登录成功返回True
        """
        for attempt in range(max_attempts):
            logger.debug("第{}次登录尝试", attempt + 1)

            if self._attempt_single_login():
                return True

            if attempt < max_attempts - 1:
                logger.debug("登录失败，准备重试")
                time.sleep(1)

        return False

    def _attempt_single_login(self) -> bool:
        """
        执行一次登录尝试

        Returns:
            bool: 登录成功返回True
        """
        try:
            # 输入用户名
            if not self._input_username():
                return False

            # 输入密码
            if not self._input_password():
                return False

            # 处理验证码
            if not self._handle_captcha_with_retry():
                return False

            # 等待登录结果
            time.sleep(3)

            # 检查是否有错误提示
            if self.tab.wait.ele_displayed(self.selectors['login_error'], timeout=5):
                logger.debug("登录失败，出现错误提示")
                return False

            return self._is_logged_in()

        except Exception as e:
            logger.debug("登录尝试异常: {}", str(e))
            return False

    def _input_username(self) -> bool:
        """输入用户名"""
        try:
            username_ele = self.tab.ele(self.selectors['username_input'])
            if username_ele:
                username_ele.click()
                username_ele.input(self.username, clear=True)
                logger.debug("用户名输入成功")
                time.sleep(0.5)
                return True
            else:
                logger.debug("未找到用户名输入框")
                return False
        except Exception as e:
            logger.debug("输入用户名失败: {}", str(e))
            return False

    def _input_password(self) -> bool:
        """输入密码"""
        try:
            password_ele = self.tab.ele(self.selectors['password_input'])
            if password_ele:
                password_ele.click()
                password_ele.input(self.password, clear=True)
                logger.debug("密码输入成功")
                time.sleep(0.5)
                return True
            else:
                logger.debug("未找到密码输入框")
                return False
        except Exception as e:
            logger.debug("输入密码失败: {}", str(e))
            return False

    def _handle_captcha_with_retry(self, max_attempts: int = 3) -> bool:
        """
        处理验证码，支持重试

        Args:
            max_attempts: 最大尝试次数

        Returns:
            bool: 处理成功返回True
        """
        for attempt in range(max_attempts):
            logger.debug("第{}次验证码处理", attempt + 1)

            if self._handle_single_captcha():
                return True

            if attempt < max_attempts - 1:
                logger.debug("验证码处理失败，刷新验证码")
                self._refresh_captcha()
                time.sleep(1)

        return False

    def _handle_single_captcha(self) -> bool:
        """
        处理一次验证码

        Returns:
            bool: 处理成功返回True
        """
        try:
            # 获取验证码图片
            captcha_img_ele = self.tab.ele(self.selectors['captcha_img'])
            if not captcha_img_ele:
                logger.debug("未找到验证码图片元素")
                return False

            base64_img = captcha_img_ele.get_screenshot(as_base64=True)
            if not base64_img:
                logger.debug("获取验证码图片失败")
                return False

            # 识别验证码
            captcha_result = self.captcha_handler.recognize_captcha(base64_img, 1)
            logger.debug("验证码识别结果: {}", captcha_result)

            # 输入验证码
            captcha_input_ele = self.tab.ele(self.selectors['captcha_input'])
            if not captcha_input_ele:
                logger.debug("未找到验证码输入框")
                return False

            captcha_input_ele.input(captcha_result, clear=True)

            # 点击提交按钮
            submit_ele = self.tab.ele(self.selectors['submit_btn'])
            if not submit_ele:
                logger.debug("未找到提交按钮")
                return False

            submit_ele.click()
            return True

        except Exception as e:
            logger.debug("验证码处理异常: {}", str(e))
            return False

    def _refresh_captcha(self):
        """刷新验证码"""
        try:
            refresh_ele = self.tab.ele(self.selectors['captcha_refresh'])
            if refresh_ele:
                refresh_ele.click()
                logger.debug("验证码刷新成功")
            else:
                logger.debug("未找到验证码刷新按钮")
        except Exception as e:
            logger.debug("刷新验证码异常: {}", str(e))

    def _fetch_and_cache_authorization(self):
        """获取并缓存Authorization到认证管理器"""
        logger.debug("开始获取Authorization")

        try:
            authorization = self._get_authorization_from_server()
            if authorization:
                self.auth_manager.set_authorization(authorization, expire_minutes=30)
                logger.debug("Authorization缓存成功")
            else:
                logger.debug("获取Authorization失败")
        except Exception as e:
            logger.debug("获取Authorization异常: {}", str(e))

    def _get_authorization_from_server(self) -> Optional[str]:
        """从服务器获取Authorization"""
        try:
            # 构造请求参数
            params = {"bn": self.default_bn}
            url = f"{self.base_url}/refund/transit/skip.php"

            # 获取cookies
            cookies_dict = self._get_cookies_dict()

            # 构造headers
            headers = {
                "User-Agent": self.user_agent
            }

            # 发送请求
            response = requests.get(
                url,
                params=params,
                headers=headers,
                cookies=cookies_dict,
                allow_redirects=False,
                timeout=self.timeout
            )

            # 获取Location头
            location = response.headers.get('Location')
            if location and "s=" in location:
                authorization = location.split("s=")[-1]
                logger.debug("获取到Authorization: {}...", authorization[:20])
                return authorization
            else:
                logger.debug("Location中未找到Authorization参数")
                return None

        except Exception as e:
            logger.debug("从服务器获取Authorization异常: {}", str(e))
            return None

    def _get_cookies_dict(self) -> dict:
        """获取浏览器cookies字典"""
        cookies_dict = {}
        try:
            cookies_list = self.browser.cookies()
            for cookie in cookies_list:
                if cookie['domain'] in VALID_COOKIE_DOMAINS:
                    cookies_dict[cookie['name']] = cookie['value']
            logger.debug("获取到{}个有效cookies", len(cookies_dict))
        except Exception as e:
            logger.debug("获取cookies异常: {}", str(e))
            raise Exception(f"获取cookies失败: {str(e)}")
        return cookies_dict

    def get_authorization(self, force_refresh: bool = False) -> Optional[str]:
        """
        获取Authorization令牌

        Args:
            force_refresh: 是否强制刷新

        Returns:
            str: Authorization令牌，获取失败返回None
        """
        # 首先尝试从缓存获取
        if not force_refresh:
            cached_auth = self.auth_manager.get_authorization()
            if cached_auth:
                logger.debug("使用缓存的Authorization")
                return cached_auth

        logger.debug("重新获取Authorization")

        # 重新获取
        authorization = self._get_authorization_from_server()
        if authorization:
            self.auth_manager.set_authorization(authorization, expire_minutes=30)
            return authorization
        else:
            logger.debug("获取Authorization失败")
            return None

    def refresh_authorization(self) -> bool:
        """
        手动刷新Authorization

        Returns:
            bool: 刷新成功返回True
        """
        logger.debug("手动刷新Authorization")
        authorization = self.get_authorization(force_refresh=True)
        return authorization is not None

    def get_cached_authorization(self) -> Optional[str]:
        """
        获取当前缓存的Authorization

        Returns:
            str: 当前缓存的Authorization，如果过期或不存在则返回None
        """
        return self.auth_manager.get_authorization()
