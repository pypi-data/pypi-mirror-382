"""
通知推送模块 - 提供简洁易用的多平台消息推送服务

## 引入方式
```python
from zx_rpa.notify import NotificationSender

# 创建专用通知客户端（配置一次，多次使用）
wecom = NotificationSender.wecom(webhook_url='your-wecom-webhook')
dingtalk = NotificationSender.dingtalk(webhook_url='your-dingtalk-webhook', secret='your-secret')
feishu = NotificationSender.feishu(webhook_url='your-feishu-webhook')

# 简洁的消息发送
wecom.send('企业微信消息内容')
dingtalk.send('钉钉消息内容')
feishu.send('飞书消息内容')
```

## 模块结构
- notifications.py - 工厂类和客户端实现

## 对外方法
### NotificationSender（通知发送器工厂类）
#### 工厂方法
- wecom(webhook_url) -> WecomClient - 创建企业微信客户端
- dingtalk(webhook_url, secret=None) -> DingtalkClient - 创建钉钉客户端
- feishu(webhook_url) -> FeishuClient - 创建飞书客户端

### 专用客户端类
#### WecomClient
- send(content) -> dict - 发送企业微信消息

#### DingtalkClient
- send(content) -> dict - 发送钉钉消息

#### FeishuClient
- send(content) -> dict - 发送飞书消息


"""

from .notifications import NotificationSender

__all__ = ['NotificationSender']
