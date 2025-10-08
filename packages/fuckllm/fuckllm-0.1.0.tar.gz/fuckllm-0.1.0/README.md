# Mini AI

一个功能完整的 AI Agent 框架，支持记忆管理、工具调用、TTS（文字转语音）等功能。

## 功能特性

- 🤖 **Agent 系统**: React 模式的智能代理，支持工具调用和推理
- 🧠 **记忆管理**: Memory Card 和 Memory State 系统，实现长期记忆和短期状态管理
- 🔧 **工具集成**: 支持自定义工具和 MCP (Model Context Protocol) 工具
- 🗣️ **TTS 支持**: 集成阿里云 CosyVoice 和 Qwen TTS
- 💾 **向量数据库**: 支持 ChromaDB 和自定义 JSON 向量存储
- 🎯 **多模型支持**: 兼容 OpenAI、智谱 AI、阿里云等多种 LLM 提供商

## 安装

### 基础安装

```bash
pip install -e .
```

### 安装包含 TTS 功能

```bash
pip install -e ".[tts]"
```

### 安装包含向量数据库功能

```bash
pip install -e ".[vectordb]"
```

### 完整安装（包含所有功能）

```bash
pip install -e ".[full]"
```

### 开发模式安装

```bash
pip install -e ".[dev]"
```

## 快速开始

### 1. 配置环境变量

创建 `.env` 文件或设置环境变量：

```bash
# OpenAI 兼容的 API
export zhipuai_api_key="your_zhipuai_key"
export siliconflow_api_key="your_siliconflow_key"
export ark_api_key="your_ark_key"

# 阿里云（用于 TTS）
export ali_api_key="your_ali_key"
```

### 2. 使用基础 Agent

```python
from mini_ai.agent import Agent
from mini_ai.model import Chater
from mini_ai.config import zhipuai_config
from mini_ai.tools import ToolKits

# 初始化模型
model = Chater(zhipuai_config().to_dict())

# 创建工具集
tool_kits = ToolKits()

@tool_kits.tool()
def get_weather(city: str):
    """获取指定城市的天气信息
    
    Args:
        city: 城市名称
    
    Returns:
        str: 天气信息
    """
    return f"{city} 今天晴天，温度25度"

# 创建 Agent
agent = Agent(
    model=model,
    tool_kits=tool_kits,
    system_prompt="你是一个有用的AI助手"
)

# 使用 Agent
import asyncio
async def main():
    response = await agent("今天北京天气怎么样？")
    
asyncio.run(main())
```

### 3. 使用记忆管理

```python
from mini_ai.agent import AgenticMemory
from mini_ai.model import Chater, Embedder
from mini_ai.config import zhipuai_config

chater = Chater(zhipuai_config().to_dict())
embedder = Embedder(zhipuai_config().to_dict())

memory = AgenticMemory(chater, embedder)

# 使用记忆系统
# ... (详见文档)
```

### 4. 使用 TTS

```python
from mini_ai.tts._tts_cache import AliTTS

tts = AliTTS(
    api_key="your_ali_key",
    default_model="cosyvoice-v2",
    default_voice="longxiaochun_v2"
)

# 合成语音
result = tts.cosyvoice_synthesize(
    text="你好，这是一个测试",
    voice="longxiaochun_v2"
)

print(f"音频文件保存在: {result.file_path}")
```

## 项目结构

```
mini_ai/
├── agent/          # Agent 实现（React, Memory, 角色扮演等）
├── config/         # 配置管理（模型配置、打印配置、TTS配置）
├── format/         # 格式化工具（Memory 格式化、MCP 格式化、打印格式化）
├── memory/         # 记忆系统（即时记忆）
├── model/          # 模型调用（Chat、Embedding）
├── prompt/         # 提示词模板（Memory Card、Cursor等）
├── tools/          # 工具系统（工具注册、MCP 支持）
├── tts/            # 文字转语音（阿里云、Qwen）
├── type/           # 类型定义
├── utils/          # 工具函数（文件操作、缓存等）
└── vb/             # 向量数据库（Chroma、JSON）
```

## 支持的模型

- ✅ 智谱 AI (GLM-4.5)
- ✅ SiliconFlow
- ✅ 火山引擎 ARK
- ✅ 阿里云 Qwen
- ✅ 任何 OpenAI 兼容的 API

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

