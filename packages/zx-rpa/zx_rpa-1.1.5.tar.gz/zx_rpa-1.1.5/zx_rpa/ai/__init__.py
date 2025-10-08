"""
AI功能模块 - 提供简洁易用的AI服务接口

## 引入方式
```python
from zx_rpa.ai import AIAssistant

# 创建专用AI客户端（配置一次，多次使用）
deepseek = AIAssistant.deepseek(api_key='your-key', model='deepseek-chat')
doubao = AIAssistant.doubao(api_key='your-key', model='your-model-id')

# 简洁的对话调用
result1 = deepseek.chat('你好')
result2 = deepseek.chat('世界', system_content='你是专业助手')
result3 = doubao.chat('测试')

# 豆包智能体对话
result4 = doubao.chat_with_bot('智能体测试')

# 支持临时覆盖配置
result5 = deepseek.chat('推理任务', model='deepseek-reasoner')
result6 = doubao.chat_with_bot('测试', model_id='other-bot-id')
```

## 模块结构
- ai_assistant.py - 对外接口，工厂类
- deepseek_client.py - DeepSeek客户端实现
- doubao_client.py - 豆包客户端实现

## 对外方法
### AIAssistant（AI助手工厂类）
#### 工厂方法
- deepseek(api_key, model="deepseek-chat", base_url=None) -> DeepSeekClient - 创建DeepSeek客户端
- doubao(api_key, model, base_url=None) -> DoubaoClient - 创建豆包客户端

### 专用客户端类
#### DeepSeekClient
- chat(message, model=None, system_content=None, temperature=0.7) -> Union[str, Tuple[str, str]] - DeepSeek对话

#### DoubaoClient
- chat(message, model=None, system_content=None, temperature=0.7) -> str - 豆包对话
- chat_with_bot(message, model_id=None) -> str - 豆包智能体对话


"""

from .ai_assistant import AIAssistant

__all__ = ['AIAssistant']
