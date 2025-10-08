"""
网络通信模块 - 提供HTTP请求、文件下载上传、邮件等网络功能

## 引入方式
```python
from zx_rpa.network import NetworkClient

# 网络客户端（未来实现，统一接口）
client = NetworkClient()
response = client.get("https://api.example.com/data")
client.download("https://example.com/file.zip", "local_file.zip")
client.send_email("user@example.com", "标题", "内容")
```

## 对外方法
### NetworkClient（统一网络客户端，未来实现）
#### HTTP请求
- get(url, params, headers, timeout) -> dict - GET请求
- post(url, data, json, headers, timeout) -> dict - POST请求
- put(url, data, headers, timeout) -> dict - PUT请求
- delete(url, headers, timeout) -> dict - DELETE请求
- request(method, url, **kwargs) -> dict - 通用请求方法

#### 文件传输
- download(url, local_path, chunk_size, progress_callback) -> bool - 下载文件
- upload(url, file_path, headers, progress_callback) -> dict - 上传文件
- download_batch(urls, local_dir, max_workers) -> List[bool] - 批量下载

#### 邮件功能
- send_email(to, subject, content, attachments, cc, bcc) -> bool - 发送邮件
- send_html_email(to, subject, html_content, attachments) -> bool - 发送HTML邮件


"""

# TODO: 未来实现网络通信功能
# 只导出统一客户端
# from .network_client import NetworkClient
# __all__ = ['NetworkClient']

__all__ = []
