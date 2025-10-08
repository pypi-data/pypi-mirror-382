from typing import List
from fuckllm.type import ChatResponse, ToolResult
from fuckllm.config import PrintConfig
import json


class Colors:
    BLUE = "\033[1;34m"
    CYAN = "\033[1;36m"
    GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[1;31m"
    MAGENTA = "\033[1;35m"
    PURPLE = "\033[0;35m"
    WHITE_BOLD = "\033[1;37m"
    GRAY = "\033[0;90m"
    GRAY_ITALIC = "\033[3;90m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_user_prompt(turn_number: int = None):
    if turn_number and turn_number > 1:
        print(f"\n{Colors.GRAY}{'═' * 80}{Colors.END}")

    prompt = f"{Colors.BLUE}─ USER{Colors.END} {Colors.GRAY}│{Colors.END} "
    return input(prompt)


def format_tool_result(tool_result: ToolResult) -> str:
    args_str = ""
    if tool_result.fn_args:
        args_str = ", ".join(
            [
                f"{k}={json.dumps(v, ensure_ascii=False)}"
                for k, v in tool_result.fn_args.items()
            ]
        )

    output = tool_result.fn_output
    if len(output) > 200:
        output = output[:200] + "..."

    return f"  {Colors.CYAN}• {tool_result.fn_name}({args_str}){Colors.END}\n    {Colors.GRAY}↳ {output}{Colors.END}"


def print_tool_results(tool_results: List[ChatResponse]):
    if not tool_results:
        return

    print(f"\n{Colors.BLUE}├─ Tool Calls:{Colors.END}")
    for result in tool_results:
        if result.tool_result:
            print(format_tool_result(result.tool_result))


def print_assistant_header(iteration: int):
    if iteration == 0:
        print(
            f"{Colors.GREEN}┌─ ASSISTANT{Colors.END} {Colors.GRAY}│ Response #{iteration + 1}{Colors.END}"
        )
    else:
        print(
            f"{Colors.GREEN}├─ ASSISTANT{Colors.END} {Colors.GRAY}│ Response #{iteration + 1}{Colors.END}"
        )


def print_assistant_footer():
    print(f"{Colors.GREEN}└{'─' * 78}{Colors.END}")


def print_thinking_section():
    print(f"{Colors.PURPLE}├── [Thinking]{Colors.END}")


def print_reply_section():
    print(f"{Colors.CYAN}├── [Reply]{Colors.END}")


def format_thinking_line(text: str) -> str:
    lines = text.split("\n")
    formatted = []
    for line in lines:
        if line.strip():
            formatted.append(f"{Colors.GRAY}│   {Colors.GRAY_ITALIC}{line}{Colors.END}")
        else:
            formatted.append(f"{Colors.GRAY}│{Colors.END}")
    return "\n".join(formatted)


def format_reply_line(text: str) -> str:
    lines = text.split("\n")
    formatted = []
    for line in lines:
        if line.strip():
            formatted.append(f"{Colors.GRAY}│   {Colors.WHITE_BOLD}{line}{Colors.END}")
        else:
            formatted.append(f"{Colors.GRAY}│{Colors.END}")
    return "\n".join(formatted)


def print_agent_response(
    print_config: PrintConfig,
    iteration: int,
    reasoning_content: str = "",
    content: str = "",
    is_stream: bool = True,
    header_printed: bool = False,
    reasoning_printed: bool = False,
    content_started: bool = False,
) -> tuple[bool, bool, bool]:

    if not header_printed and (reasoning_content or content):
        print_assistant_header(iteration)
        header_printed = True

    if reasoning_content and print_config.show_reasoning:
        if not reasoning_printed:
            print_thinking_section()
            if is_stream:
                print(f"{Colors.GRAY}│   {Colors.GRAY_ITALIC}", end="", flush=True)
            reasoning_printed = True

        if is_stream:
            if "\n" in reasoning_content:
                lines = reasoning_content.split("\n")
                for i, line in enumerate(lines):
                    if i > 0:
                        print(
                            f"{Colors.END}\n{Colors.GRAY}│   {Colors.GRAY_ITALIC}",
                            end="",
                            flush=True,
                        )
                    print(line, end="", flush=True)
            else:
                print(reasoning_content, end="", flush=True)
        else:
            lines = reasoning_content.split("\n")
            for line in lines:
                if line.strip():
                    print(f"{Colors.GRAY}│   {Colors.GRAY_ITALIC}{line}{Colors.END}")
                else:
                    print(f"{Colors.GRAY}│{Colors.END}")

    if content and print_config.show_content:
        if reasoning_printed and not content_started:
            if is_stream:
                print(f"{Colors.END}")
            print_reply_section()
            if is_stream:
                print(f"{Colors.GRAY}│   {Colors.WHITE_BOLD}", end="", flush=True)
            content_started = True
        elif not content_started:
            print_reply_section()
            if is_stream:
                print(f"{Colors.GRAY}│   {Colors.WHITE_BOLD}", end="", flush=True)
            content_started = True

        if is_stream:
            if "\n" in content:
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if i > 0:
                        print(
                            f"{Colors.END}\n{Colors.GRAY}│   {Colors.WHITE_BOLD}",
                            end="",
                            flush=True,
                        )
                    print(line, end="", flush=True)
            else:
                print(content, end="", flush=True)
        else:
            lines = content.split("\n")
            for line in lines:
                if line.strip():
                    print(f"{Colors.GRAY}│   {Colors.WHITE_BOLD}{line}{Colors.END}")
                else:
                    print(f"{Colors.GRAY}│{Colors.END}")

    return header_printed, reasoning_printed, content_started


def print_error(error_message: str, error_type: str = "Error"):
    print(f"\n{Colors.RED}✗ {error_type}: {error_message}{Colors.END}")


def print_end_color():
    print(Colors.END, end="", flush=True)


def print_empty_line():
    print()


def print_separator(char: str = "═", length: int = 80, color: str = None):
    color_code = color or Colors.GRAY
    print(f"\n{color_code}{char * length}{Colors.END}")
