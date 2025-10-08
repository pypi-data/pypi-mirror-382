from typing import Any
import mcp


def format_mcp_result(content: list):
    contents = []
    for item in content:
        if isinstance(item, mcp.types.TextContent):
            contents.append({"type": "text", "text": item.text})
        elif isinstance(item, mcp.types.ImageContent):
            contents.append(
                {"type": "image/base64", "media_type": item.mimeType, "data": item.data}
            )
        elif isinstance(item, mcp.types.AudioContent):
            contents.append(
                {"type": "audio/base64", "media_type": item.mimeType, "data": item.data}
            )
        else:
            raise ValueError(f"Unsupported content type: {type(item)}")
    return contents


def format_mcp_openai_schema(tool: mcp.types.Tool) -> dict[str, Any]:
    schema = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }

    if tool.inputSchema and "properties" in tool.inputSchema:
        schema["function"]["parameters"]["properties"] = tool.inputSchema["properties"]
        if "required" in tool.inputSchema:
            schema["function"]["parameters"]["required"] = tool.inputSchema["required"]

    return schema
