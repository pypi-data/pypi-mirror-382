"""
配置管理模块 - YAML配置文件的全局管理

## 引入方式
```python
from zx_rpa.config import init_yaml_config

# 初始化全局YAML配置G
G = init_yaml_config("config.yaml")
```

## G的读写使用
```python
# 读取配置
host = G.database.host          # 链式访问
port = G.database.port
api_key = G.api.openai.key

# 写入配置（自动保存到文件）
G.database.host = "localhost"   # 链式赋值
G.api.openai.key = "new_key"

# 字典式访问
G['database']['host'] = "127.0.0.1"
value = G['api']['openai']['key']

# 检查配置是否存在
if 'database' in G:
    print("数据库配置存在")
```

## 对外方法
- init_yaml_config(config_file) -> GlobalYamlConfig - 初始化全局YAML配置G
- G.reload() - 重新加载配置文件
- G.get_all() -> Dict - 获取所有配置


"""

from .yaml_manager import init_yaml_config

__all__ = ['init_yaml_config']
