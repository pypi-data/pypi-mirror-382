import json
import asyncio
from typing import Optional, List
from tools import ToolKits
from memory import InstantMemory
from type import ChatResponse, ToolResult, ToolCall
from model import Chater
from config import PrintConfig
from format import (
    print_agent_response,
    print_user_prompt,
    print_tool_results,
    print_assistant_footer,
    print_error,
    print_end_color,
    print_empty_line,
    Colors,
)

default_system_prompt = """You are a helpful assistant."""


class Agent:
    def __init__(
        self,
        model: Chater,
        system_prompt: Optional[str] = None,
        tool_kits: ToolKits | None = None,
        memory: InstantMemory | None = None,
        max_iters: int = 10,
        parallel_func_exec: bool = True,
        print_config: Optional[PrintConfig] = PrintConfig(),
    ):
        self.model = model
        self.system_prompt = system_prompt or default_system_prompt
        self.tool_kits = tool_kits
        self.memory: InstantMemory = memory or InstantMemory()
        self.max_iters = max_iters
        self.parallel_func_exec = parallel_func_exec
        self.print_config = print_config or PrintConfig()
        self.tools = self.tool_kits.get_tools() if self.tool_kits else None

    async def execute_tool(self, tool_use: ToolCall):
        args_dict = (
            json.loads(tool_use.fn_args)
            if isinstance(tool_use.fn_args, str)
            else tool_use.fn_args
        )
        result = await self.tool_kits.execute_tool(tool_use.fn_name, args_dict)
        return ChatResponse(
            role="tool",
            tool_result=ToolResult(
                fn_id=tool_use.fn_id,
                fn_name=tool_use.fn_name,
                fn_args=args_dict,
                fn_output=str(result),
            ),
        )

    def _print(
        self,
        iteration: int,
        reasoning_content: str = "",
        content: str = "",
        is_stream: bool = True,
        header_printed: bool = False,
        reasoning_printed: bool = False,
        content_started: bool = False,
    ) -> tuple[bool, bool, bool]:
        return print_agent_response(
            print_config=self.print_config,
            iteration=iteration,
            reasoning_content=reasoning_content,
            content=content,
            is_stream=is_stream,
            header_printed=header_printed,
            reasoning_printed=reasoning_printed,
            content_started=content_started,
        )

    async def __call__(self, prompt: str, **kwargs):
        self.memory.add_memory(ChatResponse(role="user", content=prompt))
        return await self._agent_run(**kwargs)

    async def _agent_run(self, **kwargs):
        for iteration in range(self.max_iters):
            msgs = [
                ChatResponse(role="system", content=self.system_prompt).to_openai(),
                *self.memory.to_openai(),
            ]
            tool_choice = kwargs.get("tool_choice", "auto") if self.tools else None

            try:
                response = await self.model.chat(
                    messages=msgs, tools=self.tools, tool_choice=tool_choice, **kwargs
                )
            except Exception as e:
                print_error(str(e), "Model Error")
                break

            tool_calls: List[ToolCall] = []
            tool_results: List[ChatResponse] = []
            content = ""
            reasoning_content = ""
            last_msg = None

            reasoning_printed = False
            content_started = False
            header_printed = False

            try:
                if self.model.stream:
                    async for msg in response:
                        msg: ChatResponse
                        header_printed, reasoning_printed, content_started = (
                            self._print(
                                iteration=iteration,
                                reasoning_content=msg.reasoning_content,
                                content=msg.content,
                                is_stream=True,
                                header_printed=header_printed,
                                reasoning_printed=reasoning_printed,
                                content_started=content_started,
                            )
                        )
                        if msg.reasoning_content:
                            reasoning_content += msg.reasoning_content
                        if msg.content:
                            content += msg.content

                        if msg.tool_call:
                            tool_calls.append(msg.tool_call)
                            tool_results.append(await self.execute_tool(msg.tool_call))

                        last_msg = msg

                    print_end_color()
                else:
                    self._print(
                        iteration=iteration,
                        reasoning_content=response.reasoning_content,
                        content=response.content,
                        is_stream=False,
                        header_printed=False,
                        reasoning_printed=False,
                        content_started=False,
                    )

                    tool_calls = response.tool_calls
                    tool_results = [
                        await self.execute_tool(tool_call) for tool_call in tool_calls
                    ]
                    content = response.content
                    reasoning_content = response.reasoning_content
                    last_msg = response

            except asyncio.CancelledError:
                raise
            except Exception as e:
                print_error(str(e), "Processing Error")

            if last_msg is None:
                print_error("No response received from model", "Response Error")
                break

            id, created = last_msg.id, last_msg.created
            if tool_calls:
                if self.print_config.show_tools:
                    print_tool_results(tool_results)

                chat_response = ChatResponse(
                    id=id,
                    created=created,
                    tool_calls=tool_calls,
                    content=content,
                    reasoning_content=reasoning_content,
                )
                self.memory.add_memory(chat_response)
                self.memory.extend_memory(tool_results)
            else:
                chat_response = ChatResponse(
                    id=id,
                    created=created,
                    content=content,
                    reasoning_content=reasoning_content,
                )
                self.memory.add_memory(chat_response)
                print_empty_line()
                print_assistant_footer()
                break


if __name__ == "__main__":
    from model import Chater
    from tools import ToolKits
    from memory import InstantMemory
    from type import ChatResponse, ToolResult, ToolCall
    from model import Chater
    from config import zhipuai_config

    model = Chater(zhipuai_config().to_dict())
    tool_kits = ToolKits()

    def get_time():
        """
        获取当前时间

        Returns:
            str: 当前时间
        """
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_weather(city: str, unit: str = "celsius"):
        """
        获取指定城市的天气信息

        Args:
            city: 城市名称
            unit: 温度单位

        Returns:
            str: 天气信息
        """
        return f"{city}的天气是晴天，温度25{unit}"

    memory = InstantMemory()
    tool_kits.tool_register(get_time)
    tool_kits.tool_register(get_weather)
    agent = Agent(
        model=model,
        tool_kits=tool_kits,
        memory=memory,
        max_iters=10,
        parallel_func_exec=True,
    )

    async def run():
        turn = 0
        print(f"{Colors.CYAN}{'═' * 80}{Colors.END}")
        print(
            f"{Colors.CYAN}│{Colors.END} {Colors.BOLD}Mini Memory Agent{Colors.END} {Colors.GRAY}- Type 'q' to quit{Colors.END}"
        )
        print(f"{Colors.CYAN}{'═' * 80}{Colors.END}")
        print_empty_line()

        while True:
            turn += 1
            user_input = print_user_prompt(turn)

            if user_input:
                if user_input.lower() == "q":
                    print(f"\n{Colors.YELLOW}Goodbye!{Colors.END}\n")
                    break
                await agent(user_input)
            else:
                print(
                    f"{Colors.YELLOW}Please enter a message or 'q' to quit.{Colors.END}"
                )

    asyncio.run(run())
