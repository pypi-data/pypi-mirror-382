"""
伊性坊平台统一客户端

提供简洁的API接口，整合所有功能到一个类中。
这是推荐的使用方式，避免用户接触到内部实现细节。
"""

from typing import Dict, Optional, Any, Union
from loguru import logger

from .base import YixingfangBase
from .collector import YixingfangCollector
from .operator import YixingfangOperator

# 只导出客户端类
__all__ = ['YixingfangClient']


class YixingfangClient:
    """
    伊性坊平台统一客户端
    
    这是推荐的使用方式，提供简洁的API接口。
    用户只需要使用这一个类就能完成所有操作。
    
    主要功能：
    - login() -> bool: 登录伊性坊平台
    - collect_product_link(product_code: str) -> str: 根据商品编号获取商品链接
    - collect_product_data(url: str) -> Dict: 采集商品详细数据
    - download_image_package(image_url: str, save_folder: str, product_code: str = None) -> str: 下载图片包
    - close(): 关闭浏览器并清理资源
    
    使用示例：
    ```python
    from zx_rpa.apis.yixingfang import YixingfangClient
    
    # 初始化客户端
    client = YixingfangClient(
        username="your_username",
        password="your_password", 
        tujian_username="tujian_user",
        tujian_password="tujian_pass"
    )
    
    # 登录
    client.login()
    
    # 采集商品链接
    link = client.collect_product_link("商品编号")
    
    # 采集商品数据
    data = client.collect_product_data(link)
    
    # 下载图片包
    file_path = client.download_image_package(data['image_package_url'], "./downloads")
    
    # 关闭客户端
    client.close()
    ```
    """

    def __init__(self, username: str, password: str, tujian_username: str, tujian_password: str,
                 headless: bool = False,
                 port: Union[int, str, None] = None,
                 base_url: str = "https://www.yxfshop.com/",
                 **options):
        """
        初始化伊性坊客户端

        Args:
            username: 伊性坊用户名
            password: 伊性坊密码
            tujian_username: 图鉴验证码用户名
            tujian_password: 图鉴验证码密码
            headless: 是否无头模式，默认False
            port: 浏览器端口，None=不设置端口(默认)，'auto'=自动端口，int=指定端口
            base_url: 基础URL，默认伊性坊官网
            **options: 配置选项（包括过滤选项和API配置等）
        """
        logger.debug("初始化伊性坊统一客户端")

        # 分离基础操作和采集器的配置选项
        base_options = {k: v for k, v in options.items()
                       if k in ['default_bn', 'user_agent', 'timeout']}
        collector_options = {k: v for k, v in options.items()
                           if k not in ['default_bn', 'user_agent', 'timeout']}

        # 初始化基础操作
        self._base = YixingfangBase(
            username=username,
            password=password,
            tujian_username=tujian_username,
            tujian_password=tujian_password,
            headless=headless,
            port=port,
            base_url=base_url,
            **base_options
        )

        # 初始化数据采集器
        self._collector = YixingfangCollector(
            base=self._base,
            **collector_options
        )
        
        # 初始化数据操作器
        self._operator = YixingfangOperator(self._base)
        
        logger.debug("伊性坊统一客户端初始化完成")

    def login(self) -> bool:
        """
        登录伊性坊平台
        
        Returns:
            bool: 登录成功返回True
            
        Raises:
            Exception: 登录失败时抛出异常
        """
        logger.debug("客户端执行登录")
        return self._base.login()

    def collect_product_link(self, product_code: str, mode: str = "s") -> str:
        """
        根据商品编号采集商品链接
        
        Args:
            product_code: 商品编号
            mode: 模式，'d'表示浏览器模式，'s'表示requests模式
            
        Returns:
            str: 商品链接
            
        Raises:
            Exception: 采集失败时抛出异常
        """
        logger.debug("客户端采集商品链接: {}", product_code)
        return self._collector.collect_product_link(product_code, mode)

    def collect_product_data(self, url: str, mode: str = "s") -> Dict:
        """
        采集商品详细数据
        
        Args:
            url: 商品URL
            mode: 模式，'d'表示浏览器模式，'s'表示requests模式
            
        Returns:
            dict: 商品数据字典
            
        Raises:
            Exception: 采集失败时抛出异常
        """
        logger.debug("客户端采集商品数据: {}", url[:100])
        return self._collector.collect_product_data(url, mode)

    def download_image_package(self, image_package_url: str, save_folder: str, 
                              product_code: str = None) -> str:
        """
        下载商品图片包
        
        Args:
            image_package_url: 图片包链接
            save_folder: 保存目录
            product_code: 商品编号（用于重命名，可选）
            
        Returns:
            str: 下载成功时返回文件路径
            
        Raises:
            Exception: 下载失败时抛出异常
        """
        logger.debug("客户端下载图片包")
        return self._collector.download_image_package(image_package_url, save_folder, product_code)

    def switch_mode(self, mode: str) -> bool:
        """
        切换浏览器模式
        
        Args:
            mode: 目标模式，'d'表示浏览器模式，'s'表示requests模式
            
        Returns:
            bool: 切换成功返回True
        """
        logger.debug("客户端切换模式: {}", mode)
        return self._base.switch_mode(mode)

    def get_authorization_status(self) -> Dict:
        """
        获取Authorization状态信息
        
        Returns:
            dict: 包含认证状态的字典
        """
        return self._base.auth_manager.get_status()

    def refresh_authorization(self) -> bool:
        """
        手动刷新Authorization
        
        Returns:
            bool: 刷新成功返回True
        """
        logger.debug("客户端刷新Authorization")
        return self._base.refresh_authorization()

    def close(self):
        """关闭浏览器并清理资源"""
        logger.debug("客户端关闭")
        self._base.close_browser()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """上下文管理器退出时清理资源"""
        self.close()
