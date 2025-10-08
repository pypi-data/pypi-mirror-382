from dataclasses import dataclass, field
from time import time
import uuid
from typing import Literal, Union
import uuid

_type = Literal["user_fact", "preference", "tool_result", "system_rule", "llm_response"]
_role = Literal["assistant", "user", "tool", "system"]


@dataclass
class EmbedResponse:
    source: Literal["api", "cache"]
    embedding: list[float]


@dataclass
class ToolCall:
    fn_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    fn_name: str = field(default_factory=lambda: "")
    fn_args: dict = field(default_factory=lambda: {})

    def to_dict(self) -> dict:
        return {
            "fn_id": self.fn_id,
            "fn_name": self.fn_name,
            "fn_args": self.fn_args,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ToolCall":
        return cls(
            fn_id=data["fn_id"],
            fn_name=data["fn_name"],
            fn_args=data["fn_args"],
        )

    def to_openai(self) -> dict:
        return {
            "id": self.fn_id,
            "type": "function",
            "function": {"name": self.fn_name, "arguments": self.fn_args},
        }


@dataclass
class ToolResult:
    fn_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    fn_name: str = field(default_factory=lambda: "")
    fn_args: dict = field(default_factory=lambda: {})
    fn_output: str = field(default_factory=lambda: "")

    def to_dict(self) -> dict:
        return {
            "fn_id": self.fn_id,
            "fn_name": self.fn_name,
            "fn_args": self.fn_args,
            "fn_output": self.fn_output,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ToolResult":
        return cls(
            fn_id=data["fn_id"],
            fn_name=data["fn_name"],
            fn_args=data["fn_args"],
            fn_output=data["fn_output"],
        )

    def to_openai(self) -> dict:
        return {"role": "tool", "tool_call_id": self.fn_id, "content": self.fn_output}


@dataclass
class ChatResponse:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created: str = field(default_factory=lambda: str(int(time())))
    role: _role = field(default_factory=lambda: "assistant")
    content: str = field(default_factory=lambda: "")
    reasoning_content: str = field(default_factory=lambda: "")
    tool_call: ToolCall = field(default_factory=lambda: None)
    tool_calls: list[ToolCall] = field(default_factory=lambda: [])
    tool_result: ToolResult = field(default_factory=lambda: None)
    tool_results: list[ToolResult] = field(default_factory=lambda: [])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created": self.created,
            "role": self.role,
            "content": self.content,
            "reasoning_content": self.reasoning_content,
            "tool_call": self.tool_call.to_dict() if self.tool_call else None,
            "tool_calls": [tool_call.to_dict() for tool_call in self.tool_calls],
            "tool_results": [
                tool_result.to_dict() for tool_result in self.tool_results
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChatResponse":
        return cls(
            id=data["id"],
            created=data["created"],
            role=data["role"],
            content=data["content"],
            reasoning_content=data["reasoning_content"],
            tool_call=(
                ToolCall.from_dict(data["tool_call"]) if data["tool_call"] else None
            ),
            tool_calls=[
                ToolCall.from_dict(tool_call) for tool_call in data["tool_calls"]
            ],
            tool_results=[
                ToolResult.from_dict(tool_result)
                for tool_result in data["tool_results"]
            ],
        )

    def to_openai(self) -> Union[dict, list[dict]]:
        if self.role == "system":
            return {"role": "system", "content": self.content}
        elif self.role == "user":
            return {"role": "user", "content": self.content}
        elif self.role == "assistant":
            if self.tool_call:
                return {
                    "role": "assistant",
                    "content": self.content or None,
                    "tool_calls": [self.tool_call.to_openai()],
                    "tool_results": [
                        tool_result.to_openai() for tool_result in self.tool_results
                    ],
                }
            if self.tool_calls:
                return {
                    "role": "assistant",
                    "content": self.content or None,
                    "tool_calls": [
                        tool_call.to_openai() for tool_call in self.tool_calls
                    ],
                }
            return {"role": "assistant", "content": self.content or None}
        elif self.role == "tool":
            if self.tool_result:
                return self.tool_result.to_openai()
            if self.tool_results:
                return [tool_result.to_openai() for tool_result in self.tool_results]
            raise ValueError(f"Invalid tool_result: {self.tool_result}")
        else:
            raise ValueError(f"Invalid role: {self.role}")
