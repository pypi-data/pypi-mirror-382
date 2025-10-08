"""
比特指纹浏览器 API 封装

这是一个专业的比特指纹浏览器API封装库，提供完整的浏览器窗口管理和分组管理功能。
支持创建、打开、关闭、删除浏览器窗口，以及分组的增删改查操作。

主要特性:
- 🚀 简洁易用的API接口
- 🔧 完整的浏览器窗口生命周期管理
- 📁 灵活的分组管理功能
- 🛡️ 完善的错误处理和日志记录
- 📝 详细的参数说明和类型提示

基本用法:
    >>> from zx_rpa.apis.bitbrowser import BitBrowserClient
    >>> 
    >>> # 初始化客户端
    >>> client = BitBrowserClient()
    >>> 
    >>> # 创建浏览器窗口
    >>> browser_id = client.create_browser(
    ...     name="测试窗口",
    ...     remark="用于测试的浏览器窗口",
    ...     proxy_type="http",
    ...     host="127.0.0.1",
    ...     port="8080"
    ... )
    >>> 
    >>> # 打开浏览器窗口
    >>> browser_info = client.open_browser(browser_id)
    >>> print(f"调试端口: {browser_info.get('http')}")
    >>> 
    >>> # 关闭浏览器窗口
    >>> client.close_browser(browser_id)
    >>> 
    >>> # 删除浏览器窗口
    >>> client.delete_browser(browser_id)

分组管理示例:
    >>> # 创建分组
    >>> group_id = client.add_group("测试分组")
    >>> 
    >>> # 创建浏览器窗口并指定分组
    >>> browser_id = client.create_browser_with_group(
    ...     name="分组窗口",
    ...     group_name="测试分组"
    ... )
    >>> 
    >>> # 查询分组列表
    >>> groups = client.list_groups()
    >>> for group in groups:
    ...     print(f"分组: {group['groupName']}, ID: {group['id']}")

名称/ID自动识别（缓存优化）:
    >>> # 支持使用浏览器名称或ID进行操作（首次查找会缓存所有浏览器）
    >>> client.open_browser("我的浏览器")      # 使用名称，~1ms（缓存命中）
    >>> client.open_browser("abc123...")      # 使用ID
    >>> client.close_browser("我的浏览器")     # 使用名称
    >>> client.delete_browser("我的浏览器")    # 使用名称
    >>>
    >>> # 根据名称查找浏览器信息
    >>> browser = client.find_browser_by_name("我的浏览器")
    >>> browser_id = client.get_browser_id("我的浏览器")
    >>>
    >>> # 获取所有浏览器（自动分页获取）
    >>> all_browsers = client.get_all_browsers()
    >>> all_browsers = client.get_all_browsers("我的分组")  # 获取指定分组的所有浏览器
    >>> all_browsers = client.list_browsers(get_all=True)
    >>> browsers = client.list_browsers(group_name_or_id="我的分组")  # 按分组筛选
    >>>
    >>> # 缓存管理
    >>> client.refresh_browser_cache()  # 强制刷新缓存
    >>> client.clear_browser_cache()    # 清空缓存
    >>>
    >>> # 缓存自动同步（无需手动操作）
    >>> browser_id = client.create_browser("新窗口")  # 自动添加到缓存
    >>> client.delete_browser("新窗口")              # 自动从缓存移除

分组名称/ID自动识别:
    >>> # 支持使用分组名称或ID进行操作（无缓存，实时查询）
    >>> client.edit_group("我的分组", "新名称")     # 使用名称
    >>> client.edit_group("abc123...", "新名称")   # 使用ID
    >>> client.delete_group("我的分组")            # 使用名称
    >>> client.get_group_detail("我的分组")        # 使用名称
    >>>
    >>> # 根据名称查找分组信息
    >>> group = client.find_group_by_name("我的分组")
    >>> group_id = client.get_group_id("我的分组")

高级功能:
    >>> # 批量更新浏览器窗口
    >>> client.update_browsers(
    ...     browser_ids=["id1", "id2"],
    ...     remark="批量更新的备注"
    ... )
    >>>
    >>> # 查询浏览器窗口列表
    >>> browsers = client.list_browsers(page=0, page_size=20)
    >>> 
    >>> # 关闭所有浏览器窗口
    >>> client.close_all_browsers()

注意事项:
    - 确保比特浏览器客户端已启动并运行在默认端口 54345
    - 建议使用 try-except 捕获 requests.RequestException 和 ValueError 异常
    - 浏览器指纹配置支持自定义，默认使用 Chrome 124 内核
    - 代理配置支持多种类型：noproxy、http、https、socks5、ssh

API参考:
    BitBrowserClient: 主要的客户端类，提供所有功能接口
    
    浏览器窗口管理:
        - create_browser(): 创建浏览器窗口
        - update_browsers(): 批量更新浏览器窗口
        - open_browser(): 打开浏览器窗口
        - close_browser(): 关闭浏览器窗口
        - delete_browser(): 删除浏览器窗口
        - list_browsers(): 查询浏览器窗口列表
        - close_all_browsers(): 关闭所有浏览器窗口
    
    分组管理:
        - list_groups(): 查询分组列表
        - add_group(): 添加分组
        - edit_group(): 修改分组
        - delete_group(): 删除分组
        - get_group_detail(): 获取分组详情
        - get_all_groups(): 获取所有分组
        - find_group_by_name(): 根据名称查找分组
    
    便捷方法:
        - create_browser_with_group(): 创建浏览器窗口并指定分组

版本信息:
    - 版本: 1.0.0
    - 支持: 比特指纹浏览器 v2.0+
    - Python: 3.7+

作者: ZX_RPA开发团队
更新时间: 2024-09-19
"""

from .client import BitBrowserClient

# 对外暴露的接口
__all__ = ['BitBrowserClient']

# 版本信息
__version__ = '1.0.0'
__author__ = 'ZX_RPA开发团队'
__email__ = 'support@zx-rpa.com'
__description__ = '比特指纹浏览器API封装库'

# 依赖信息
__requires__ = [
    'requests>=2.25.0',
    'loguru>=0.5.0',
    'typing-extensions>=3.7.0'
]

# 配置信息
DEFAULT_BASE_URL = "http://127.0.0.1:54345"
DEFAULT_TIMEOUT = 30
MAX_PAGE_SIZE = 100

# 支持的代理类型
SUPPORTED_PROXY_TYPES = [
    'noproxy',    # 不使用代理
    'http',       # HTTP代理
    'https',      # HTTPS代理
    'socks5',     # SOCKS5代理
    'ssh'         # SSH代理
]

# 代理方式
PROXY_METHODS = {
    'CUSTOM': 2,      # 自定义代理
    'EXTRACT_IP': 3   # 提取IP
}

# 浏览器指纹默认配置
DEFAULT_BROWSER_FINGERPRINT = {
    'coreVersion': '124'  # Chrome 124内核
}

def get_version():
    """获取版本信息
    
    Returns:
        str: 当前版本号
    """
    return __version__

def get_supported_proxy_types():
    """获取支持的代理类型列表
    
    Returns:
        List[str]: 支持的代理类型
    """
    return SUPPORTED_PROXY_TYPES.copy()

def get_default_config():
    """获取默认配置信息
    
    Returns:
        Dict[str, Any]: 默认配置字典
    """
    return {
        'base_url': DEFAULT_BASE_URL,
        'timeout': DEFAULT_TIMEOUT,
        'max_page_size': MAX_PAGE_SIZE,
        'browser_fingerprint': DEFAULT_BROWSER_FINGERPRINT.copy(),
        'proxy_methods': PROXY_METHODS.copy()
    }
