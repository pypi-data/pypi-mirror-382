from dataclasses import dataclass
import os
from typing import Optional
@dataclass
class ClientConfig:
    api_key: str
    base_url: str
    def to_dict(self) -> dict:
        return self.__dict__

@dataclass
class ChatConfig:
    model: str
    stream: Optional[bool] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    temperature: Optional[float] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None

    def to_dict(self) -> dict:
        cfg={}
        for key, value in self.__dict__.items():
            if value:
                cfg[key] = value
        return cfg

@dataclass
class EmbedConfig:
    model: str
    dimension: Optional[int] = None


    def to_dict(self) -> dict:
        cfg={}
        for key, value in self.__dict__.items():
            if value:
                cfg[key] = value
        return cfg

@dataclass
class Config:
    client_cfg: ClientConfig
    chat_cfg: ChatConfig
    embed_cfg: EmbedConfig

    def to_dict(self) -> dict:
        return {key: value.to_dict() for key, value in self.__dict__.items()}

def zhipuai_config() -> Config:
    return Config(
        client_cfg=ClientConfig(
            api_key=os.getenv("zhipuai_api_key"),
            base_url="https://open.bigmodel.cn/api/paas/v4"
        ),
        chat_cfg=ChatConfig(
            model="glm-4.5",        
            stream=True,
        ),
        embed_cfg=EmbedConfig(
            model="embedding-3",
        )
    )
def siliconflow_config() -> Config:
    return Config(
        client_cfg=ClientConfig(
            api_key=os.getenv("siliconflow_api_key"),
            base_url="https://api.siliconflow.cn/v1"
        ),
        chat_cfg=ChatConfig(
            model="zai-org/GLM-4.5",
            stream=True,
        ),
        embed_cfg=EmbedConfig(
            model="Qwen/Qwen3-Embedding-8B"
        )
    )
def ark_config() -> Config:
    return Config(
        client_cfg=ClientConfig(
            api_key=os.getenv("ark_api_key"),
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        ),
        chat_cfg=ChatConfig(
            model="doubao-1-5-thinking-pro-250415",
            stream=True,
        ),
        embed_cfg=EmbedConfig(
            model="doubao-embedding-text-240715",
        )
    )
def ali_config() -> Config:
    return Config(
        client_cfg=ClientConfig(
            api_key=os.getenv("ali_api_key"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        ),
        chat_cfg=ChatConfig(
            model="qwen3-max",
            stream=True,
        ),
        embed_cfg=EmbedConfig(
            model="text-embedding-v4",
        )
    )