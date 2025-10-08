"""
ZX_RPA - 机器人流程自动化工具库

一个专注于RPA开发的Python工具库，提供统一、简洁的API接口。

## 快速开始

### 数据库操作
```python
from zx_rpa import MySQLTable

table = MySQLTable({'host': 'localhost', 'user': 'root', 'password': '123456', 'database': 'test'}, 'users')
data = table.select({'age__>=': 18})
```

### 配置管理
```python
from zx_rpa import YamlManager

config = YamlManager("config.yaml")
db_host = config.get_by_path(["database", "host"], "localhost")
```

### 通知推送
```python
from zx_rpa import NotificationSender

sender = NotificationSender()
sender.send_wecom("消息内容", webhook_url)
```

### 验证码识别
```python
from zx_rpa import CaptchaSolver

solver = CaptchaSolver(provider="tujian", username="user", password="pass")
result = solver.recognize("image_data", type_id=1)
```

### AI对话
```python
from zx_rpa import AIAssistant

assistant = AIAssistant(provider="deepseek", api_key="your_key")
response = assistant.chat("你好")
```

## 模块化导入

如果需要更精确的控制，可以从具体模块导入：

```python
from zx_rpa.database import MySQLTable
from zx_rpa.config import init_yaml_config
from zx_rpa.notify import NotificationSender
from zx_rpa.captcha import CaptchaSolver
from zx_rpa.ai import AIAssistant
from zx_rpa.excel import ExcelHandler
```
"""

# 导入最主要的统一接口类
from .database import DatabaseManager
from .config import init_yaml_config
from .notify import NotificationSender
from .ai import AIAssistant

# Excel模块需要可选依赖，使用try-except导入
try:
    from .excel import ExcelHandler
    _excel_available = True
except ImportError:
    _excel_available = False

# 只导出最核心的类，保持根目录导入简洁
__all__ = [
    # 数据库操作
    "DatabaseManager",

    # 配置管理
    "init_yaml_config",

    # 通知推送
    "NotificationSender",

    # 验证码识别
    "CaptchaSolver",

    # AI助手
    "AIAssistant",
]

# 如果Excel依赖可用，添加到导出列表
if _excel_available:
    __all__.append("ExcelHandler")

# 版本信息
__version__ = "1.0.0"
__author__ = "ZX_RPA Team"
__description__ = "机器人流程自动化工具库"
