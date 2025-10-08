from contextlib import _AsyncGeneratorContextManager
from dataclasses import dataclass, field
from typing import Any, Callable, Literal
import mcp
from mcp import ClientSession, stdio_client, StdioServerParameters
from contextlib import AsyncExitStack
from typing import List
import logging
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from format import format_mcp_result, format_mcp_openai_schema


@dataclass
class MCPFunc:
    mcp_name: str
    name: str
    desc: str
    schema: dict[str, Any]
    format_result: bool = True
    client: Callable[..., _AsyncGeneratorContextManager[Any]] | None = None
    session: ClientSession | None = None

    def __post_init__(self):
        if (not self.client and not self.session) or (self.client and self.session):
            raise ValueError("Either client or session must be provided and not both")

    async def __call__(self, **kwargs: Any):
        if self.client:
            async with self.client() as client_context:
                read, write = client_context[0], client_context[1]
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    res = await session.call_tool(self.name, arguments=kwargs)
        else:
            res = await self.session.call_tool(self.name, arguments=kwargs)
        return format_mcp_result(res.content) if self.format_result else res.content


@dataclass
class MCPClient:
    name: str
    client: Any = None
    stack: AsyncExitStack | None = None
    session: ClientSession | None = None
    is_connected: bool = False
    _cache_tools: List[mcp.types.Tool] | None = None

    def __post_init__(self):
        pass

    async def connect(self):
        if self.is_connected:
            raise RuntimeError("MCPClient is already connected")
        self.stack = AsyncExitStack()
        try:
            context = await self.stack.enter_async_context(self.client)
            read, write = context[0], context[1]
            self.session = ClientSession(read, write)
            await self.stack.enter_async_context(self.session)
            await self.session.initialize()
            self.is_connected = True
        except Exception as e:
            await self.stack.aclose()
            self.stack = None
            raise RuntimeError(f"Failed to connect to MCP server: {e}")

    async def close(self):
        if not self.is_connected:
            raise RuntimeError("MCPClient is not connected")
        try:
            if self.stack:
                await self.stack.aclose()
            logging.info("MCPClient closed")
        finally:
            self.stack = None
            self.session = None
            self.is_connected = False

    async def list_tools(self):
        self._check_connect()
        res = await self.session.list_tools()
        self._cache_tools = res.tools
        return res.tools

    async def call_tool(
        self,
        func_name: str,
        format_result: bool = True,
    ):
        self._check_connect()
        if not self._cache_tools:
            await self.list_tools()

        target_tool = None
        for tool in self._cache_tools:
            if tool.name == func_name:
                target_tool = tool
                break
        if not target_tool:
            raise ValueError(f"Tool '{func_name}' not found")

        return MCPFunc(
            mcp_name=self.name,
            name=target_tool.name,
            desc=target_tool.description or "",
            schema=format_mcp_openai_schema(target_tool),
            format_result=format_result,
            session=self.session,
        )

    def _check_connect(self):
        if not self.is_connected:
            raise RuntimeError("MCPClient is not connected")
        if not self.session:
            raise RuntimeError("MCPClient session is not initialized")


@dataclass
class HttpStateLessClient:
    name: str
    transport: Literal["streamable_http", "sse"]
    url: str = ""
    headers: dict[str, str] | None = None
    timeout: float = 30.0
    sse_timeout: float = 300.0
    client_kwargs: dict[str, Any] = field(default_factory=dict)
    _tools: List[mcp.types.Tool] | None = None

    def __post_init__(self):
        self.client_cfg = {
            "url": self.url,
            "headers": self.headers or {},
            "timeout": self.timeout,
            "sse_read_timeout": self.sse_timeout,
            **self.client_kwargs,
        }

    def get_client(self):
        if self.transport == "sse":
            return sse_client(**self.client_cfg)
        if self.transport == "streamable_http":
            return streamablehttp_client(**self.client_cfg)
        raise ValueError(f"transport {self.transport} not supported")

    async def call_tool(
        self,
        func_name: str,
        format_result: bool = True,
    ):
        if not self._tools:
            await self.list_tools()

        target_tool = None
        for tool in self._tools:
            if tool.name == func_name:
                target_tool = tool
                break
        if not target_tool:
            raise ValueError(f"tool {func_name} not found")
        return MCPFunc(
            mcp_name=self.name,
            name=target_tool.name,
            desc=target_tool.description or "",
            schema=format_mcp_openai_schema(target_tool),
            format_result=format_result,
            client=self.get_client,
        )

    async def get_tools(
        self,
        func_name: str,
        format_result: bool = True,
    ):
        if not self._tools:
            await self.list_tools()

        target_tool = None
        for tool in self._tools:
            if tool.name == func_name:
                target_tool = tool
                break
        if not target_tool:
            raise ValueError(f"tool {func_name} not found")

        return MCPFunc(
            mcp_name=self.name,
            name=target_tool.name,
            desc=target_tool.description or "",
            schema=format_mcp_openai_schema(target_tool),
            format_result=format_result,
            client=self.get_client,
        )

    async def list_tools(self):
        async with self.get_client() as client_context:
            read, write = client_context[0], client_context[1]
            async with ClientSession(read, write) as session:
                await session.initialize()
                res = await session.list_tools()
                self._tools = res.tools
                return res.tools


@dataclass
class HttpStatefulClient(MCPClient):
    transport: Literal["streamable_http", "sse"] = "sse"
    url: str = ""
    headers: dict[str, str] | None = None
    timeout: float = 30.0
    sse_timeout: float = 300.0
    client_kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        if self.transport == "streamable_http":
            self.client = streamablehttp_client(
                url=self.url,
                headers=self.headers,
                timeout=self.timeout,
                sse_read_timeout=self.sse_timeout,
                **self.client_kwargs,
            )
        else:
            self.client = sse_client(
                url=self.url,
                headers=self.headers,
                timeout=self.timeout,
                sse_read_timeout=self.sse_timeout,
                **self.client_kwargs,
            )


@dataclass
class StdIoClient(MCPClient):
    command: str = ""
    args: List[str] | None = None
    env: dict[str, str] | None = None
    cwd: str | None = None
    encoding: str = "utf-8"
    encoding_error_handler: Literal["strict", "ignore", "replace"] = "strict"

    def __post_init__(self):
        super().__post_init__()
        self.client = stdio_client(
            StdioServerParameters(
                command=self.command,
                args=self.args or [],
                env=self.env,
                cwd=self.cwd,
                encoding=self.encoding,
                encoding_error_handler=self.encoding_error_handler,
            )
        )


if __name__ == "__main__":
    import asyncio

    async def test_mcp_thinking():
        client = StdIoClient(
            name="sequentialthinking",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-sequential-thinking"],
            env={},
            cwd=None,
            encoding="utf-8",
            encoding_error_handler="strict",
        )

        try:
            await client.connect()

            tools = await client.list_tools()
            print(f"find {len(tools)} tools")
            for tool in tools:
                print(f"- {tool.name}: {tool.description}")

            mcp_func = await client.call_tool("sequentialthinking")
            result = await mcp_func(
                thought="I need to analyze how to solve a complex problem",
                nextThoughtNeeded=True,
                thoughtNumber=1,
                totalThoughts=3,
                isRevision=False,
            )
            print("tool call result:")
            print(result)

        except Exception as e:
            print(f"error: {e}")
        finally:
            await client.close()
            print("closed MCP client connection")

    asyncio.run(test_mcp_thinking())
