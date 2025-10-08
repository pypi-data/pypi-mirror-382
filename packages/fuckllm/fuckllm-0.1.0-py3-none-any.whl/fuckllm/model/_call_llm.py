from collections import OrderedDict
from typing import Optional, AsyncGenerator
import numpy as np
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from type import (
    ChatResponse,
    EmbedResponse,
    ToolCall,
)
from utils import FileCache


class Chater:
    def __init__(self, chater_cfg: dict):
        client_cfg = chater_cfg.get("client_cfg", {})
        self.chat_cfg = chater_cfg.get("chat_cfg", {})
        self.client = AsyncOpenAI(**client_cfg)

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        tool_choice: str | None = None,
        **kwargs,
    ):
        kwargs = {"messages": messages, **self.chat_cfg, **kwargs}
        if (tools and not tool_choice) or (not tools and tool_choice):
            raise ValueError("tools and tool_choice must be provided together")
        if tools:
            kwargs["tools"] = tools
        if tool_choice:
            kwargs["tool_choice"] = tool_choice
        response = await self.client.chat.completions.create(**kwargs)
        return (
            self._stream(
                response,
            )
            if kwargs.get("stream", False)
            else self._no_stream(
                response,
            )
        )

    def _no_stream(
        self,
        response: ChatCompletion,
    ):
        msg = response.choices[0].message
        id, created, role, tools = response.id, response.created, msg.role, []
        reasoning = (
            msg.reasoning_content
            if hasattr(msg, "reasoning_content") and msg.reasoning_content
            else ""
        )
        content = msg.content if hasattr(msg, "content") and msg.content else ""
        tool_calls = (
            msg.tool_calls if hasattr(msg, "tool_calls") and msg.tool_calls else []
        )
        if tool_calls:
            tools = [
                ToolCall(
                    fn_id=tool_call.id,
                    fn_name=tool_call.function.name,
                    fn_args=tool_call.function.arguments,
                )
                for tool_call in tool_calls
            ]
        return ChatResponse(
            id=id,
            created=created,
            role=role,
            reasoning_content=reasoning,
            content=content,
            tool_calls=tools,
        )

    async def _stream(
        self,
        response: AsyncStream[ChatCompletionChunk],
    ) -> AsyncGenerator[ChatResponse, None]:
        tool_calls = OrderedDict()
        completed_calls = set()
        content, reasoning = "", ""
        id, created, role = None, None, None

        async for chunk in response:
            delte = chunk.choices[0].delta
            id, created, role = chunk.id, chunk.created, delte.role

            if hasattr(delte, "reasoning_content") and delte.reasoning_content:
                reasoning = delte.reasoning_content
                yield ChatResponse(
                    id=id, created=created, role=role, reasoning_content=reasoning
                )

            if hasattr(delte, "content") and delte.content:
                content = delte.content
                yield ChatResponse(id=id, created=created, role=role, content=content)

            current_tool_indices = set()
            for tool_call in delte.tool_calls or []:
                current_tool_indices.add(tool_call.index)

                if tool_call.index in tool_calls:
                    tool_calls[tool_call.index].fn_args += tool_call.function.arguments
                else:
                    tool_calls[tool_call.index] = ToolCall(
                        fn_id=tool_call.id,
                        fn_name=tool_call.function.name,
                        fn_args=tool_call.function.arguments,
                    )

            completed_indices = (
                set(tool_calls.keys()) - current_tool_indices - completed_calls
            )
            for tool_idx in completed_indices:
                completed_calls.add(tool_idx)
                yield ChatResponse(
                    id=id,
                    created=created,
                    role=role,
                    tool_call=tool_calls[tool_idx],
                )

    @property
    def stream(
        self,
    ) -> bool:
        return self.chat_cfg.get("stream", False)


class Embedder:
    def __init__(self, embedder_cfg: dict, embed_cache: Optional[FileCache] = None):
        client_cfg = embedder_cfg.get("client_cfg", {})
        self.embed_cfg = embedder_cfg.get("embed_cfg", {})
        self.embed_cache = embed_cache or FileCache()
        self.client = AsyncOpenAI(**client_cfg)

    async def embed(self, text: list[str], **kwargs) -> EmbedResponse:
        kwargs = {"input": text, **self.embed_cfg, **kwargs}
        if self.embed_cache:
            response = await self.embed_cache.retrieve(kwargs)
            if response:
                return EmbedResponse(
                    source="cache", embedding=[np.array(_.embedding) for _ in response]
                )
        response = await self.client.embeddings.create(**kwargs)
        if self.embed_cache:
            await self.embed_cache.store(response.data, kwargs)
        return EmbedResponse(
            source="api", embedding=[np.array(_.embedding) for _ in response.data]
        )


if __name__ == "__main__":
    import asyncio
    from config import zhipuai_config

    client = Chater(zhipuai_config().to_dict())
    messages = [
        {"role": "system", "content": "你可以使用工具来帮助用户获取天气信息。"},
        {"role": "user", "content": "查看一下日本东京和大阪今天的天气如何"},
    ]
    tool_schema = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取指定城市的天气信息。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city to query weather for.",
                        },
                    },
                    "required": ["city"],
                },
            },
        }
    ]

    async def run():
        if client.stream:
            async for msg in await client.chat(
                messages, tools=tool_schema, tool_choice="auto"
            ):
                if msg.reasoning_content:
                    print(msg.reasoning_content, end="", flush=True)
                if msg.content:
                    print(msg.content, end="", flush=True)
                if msg.tool_calls:
                    print(msg)
                if msg.tool_call:
                    print(msg)
        else:
            msg = await client.chat(messages, tools=tool_schema, tool_choice="auto")
            print(msg)

    asyncio.run(run())
    embedder = Embedder(zhipuai_config().to_dict())
    embed = asyncio.run(embedder.embed(["Hello, how are you?"]))
    print(embed.source)
