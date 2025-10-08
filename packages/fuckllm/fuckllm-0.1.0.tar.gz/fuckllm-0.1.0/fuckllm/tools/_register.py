import inspect
import json
from typing import Callable, Any, Dict, List, Optional
from functools import wraps
import asyncio
from ._mcp import MCPClient
from utils import parse_google_docstring, python_type_to_json_type
from format import format_mcp_openai_schema


class ToolKits:
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._functions: Dict[str, Callable] = {}
        self._mcp_clients: Dict[str, MCPClient] = {}

    def register(self, func: Callable, name: Optional[str] = None) -> Callable:

        tool_name = name or func.__name__
        schema = self._parse_function_to_schema(func, tool_name)

        self._tools[tool_name] = schema
        self._functions[tool_name] = func

        return func

    def tool_register(self, func: Callable, name: Optional[str] = None) -> Callable:
        return self.register(func, name)

    def tool_registers(
        self, funcs: List[Callable], names: Optional[List[str]] = None
    ) -> None:
        for func, name in zip(funcs, names or [None for _ in funcs]):
            self.register(func, name)

    def _parse_function_to_schema(self, func: Callable, name: str) -> Dict[str, Any]:

        docstring = inspect.getdoc(func) or ""
        sig = inspect.signature(func)

        doc_info = parse_google_docstring(docstring)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ["self", "cls"]:
                continue

            param_info = doc_info["args"].get(param_name, {})
            param_type = python_type_to_json_type(param.annotation)

            param_schema = {
                "type": param_type,
                "description": param_info.get("description", ""),
            }

            if param_info.get("enum"):
                param_schema["enum"] = param_info["enum"]

            properties[param_name] = param_schema

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": doc_info["description"],
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

        return schema

    async def register_mcp_client(self, client: MCPClient, prefix: str = "") -> None:
        try:
            await client.connect()
            tools = await client.list_tools()
            self._mcp_clients[prefix] = client
            for tool in tools:
                tool_name = f"{prefix}_{tool.name}" if prefix else tool.name

                def create_mcp_wrapper(mcp_client, tool_name_inner):
                    async def mcp_wrapper(**kwargs):
                        try:
                            mcp_func = await mcp_client.call_tool(tool_name_inner)
                            return await mcp_func(**kwargs)
                        except Exception as e:
                            return f"MCP工具调用失败: {str(e)}"

                    return mcp_wrapper

                wrapper = create_mcp_wrapper(client, tool.name)
                schema = format_mcp_openai_schema(tool)

                self._tools[tool_name] = schema
                self._functions[tool_name] = wrapper

        except Exception as e:
            raise

    async def close_mcp_clients(self) -> None:
        for name, client in self._mcp_clients.items():
            try:
                if client.is_connected:
                    await client.close()
            except Exception as e:
                raise ValueError(f"关闭MCP客户端 {name} 时出错: {str(e)}")

        self._mcp_clients.clear()

    def get_tools(self) -> List[Dict[str, Any]]:
        return list(self._tools.values())

    def get_tool_names(self) -> List[str]:
        return list(self._tools.keys())

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if tool_name not in self._functions:
            raise ValueError(f"Tool '{tool_name}' not found in registry")
        func = self._functions[tool_name]
        if asyncio.iscoroutinefunction(func):
            result = await func(**arguments)
        else:
            result = func(**arguments)

        return result

    def tool(self, name: Optional[str] = None):
        def decorator(func: Callable) -> Callable:
            self.register(func, name)

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)

            return async_wrapper

        return decorator


if __name__ == "__main__":
    import asyncio
    from . import _mcp

    StdIoClient = _mcp.StdIoClient

    registry = ToolKits()

    @registry.tool()
    def get_weather(city: str, unit: str = "celsius"):
        """
        Get weather information for a given city

        Args:
            city (str): city name, such as "Beijing", "Shanghai"
            unit (str, optional): temperature unit. Defaults to "celsius". Enum: ["celsius", "fahrenheit"]

        Returns:
            str: weather information description
        """
        return f"{city} is sunny, temperature is 25{unit}"

    async def search_web(query: str, max_results: int = 10):
        """
        Search information on the web

        Args:
            query (str): search query word
            max_results (int): maximum number of return results. Defaults to 10.

        Returns:
            str: search result
        """
        await asyncio.sleep(0.1)
        return f"Search '{query}' found {max_results} results"

    def calculate(expression: str):
        """
        Calculate the value of a mathematical expression

        Args:
            expression (str): mathematical expression to calculate, such as "2+2"

        Returns:
            float: calculation result
        """
        try:
            result = eval(expression)
            return float(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"

    def get_time():
        """
        Get current time

        Returns:
            str: current time
        """
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def main():
        registry.tool_register(search_web)
        registry.tool_registers([get_time, calculate])

        try:
            print("Trying to register MCP tools...")
            client = StdIoClient(
                name="sequential_thinking",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-sequential-thinking"],
                env={},
                cwd=None,
                encoding="utf-8",
                encoding_error_handler="strict",
            )

            await registry.register_mcp_client(client, "thinking")

            print("MCP tools registered successfully")

        except Exception as e:
            print(
                f"MCP tools registration failed (maybe the server is not available): {e}"
            )

        tools = registry.get_tools()
        print("Registered tools:")
        print(json.dumps(tools, indent=2, ensure_ascii=False))

        print("\n" + "=" * 50 + "\n")

        print("Testing tool calls:")

        result1 = await registry.execute_tool("get_weather", {"city": "Beijing"})
        print(f"get_weather: {result1}")

        result2 = await registry.execute_tool(
            "get_weather", {"city": "Shanghai", "unit": "fahrenheit"}
        )
        print(f"get_weather with unit: {result2}")

        result3 = await registry.execute_tool(
            "search_web", {"query": "Python programming"}
        )
        print(f"search_web: {result3}")

        result4 = await registry.execute_tool("calculate", {"expression": "2 + 2 * 3"})
        print(f"calculate: {result4}")

        tool_names = registry.get_tool_names()
        mcp_tools = [name for name in tool_names if name.startswith("thinking_")]
        if mcp_tools:
            print(f"\nTesting MCP tools call: {mcp_tools[0]}")
            try:
                mcp_result = await registry.execute_tool(
                    mcp_tools[0],
                    {
                        "thought": "I need to analyze a problem",
                        "nextThoughtNeeded": True,
                        "thoughtNumber": 1,
                        "totalThoughts": 3,
                        "isRevision": False,
                    },
                )
                print(f"MCP tools result: {mcp_result}")
            except Exception as e:
                print(f"MCP tools call failed: {e}")

        await registry.close_mcp_clients()

    asyncio.run(main())
