"""Conversions between internal and MCP types."""

from __future__ import annotations

from typing import TYPE_CHECKING
import urllib.parse

from mcp import types


if TYPE_CHECKING:
    from llmling.prompts.models import BasePrompt, PromptMessage, PromptParameter
    from llmling.resources.models import LoadedResource
    from llmling.tools.base import LLMCallableTool


def to_mcp_tool(tool: LLMCallableTool) -> types.Tool:
    """Convert internal Tool to MCP Tool."""
    schema = tool.get_schema()
    return types.Tool(
        name=schema["function"]["name"],
        description=schema["function"]["description"],
        inputSchema=schema["function"]["parameters"],  # pyright: ignore
        annotations=types.ToolAnnotations(
            title=tool.name,
            readOnlyHint=tool.hints.read_only if tool.hints else None,
            destructiveHint=tool.hints.destructive if tool.hints else None,
            idempotentHint=tool.hints.idempotent if tool.hints else None,
            openWorldHint=tool.hints.open_world if tool.hints else None,
        ),
    )


def to_mcp_resource(resource: LoadedResource) -> types.Resource:
    """Convert LoadedResource to MCP Resource."""
    return types.Resource(
        uri=to_mcp_uri(resource.metadata.uri),
        name=resource.metadata.name or "",
        description=resource.metadata.description,
        mimeType=resource.metadata.mime_type,
    )


def to_mcp_message(msg: PromptMessage) -> types.PromptMessage:
    """Convert internal PromptMessage to MCP PromptMessage."""
    role: types.Role = "assistant" if msg.role == "assistant" else "user"
    content = types.TextContent(type="text", text=msg.get_text_content())
    return types.PromptMessage(role=role, content=content)


def to_mcp_argument(arg: PromptParameter) -> types.PromptArgument:
    """Convert to MCP PromptArgument."""
    return types.PromptArgument(
        name=arg.name,
        description=arg.description,
        required=arg.required,
    )


def to_mcp_prompt(prompt: BasePrompt) -> types.Prompt:
    """Convert to MCP Prompt."""
    if prompt.name is None:
        msg = "Prompt name not set. This should be set during registration."
        raise ValueError(msg)
    args = [to_mcp_argument(arg) for arg in prompt.arguments]
    return types.Prompt(name=prompt.name, description=prompt.description, arguments=args)


def _is_windows_drive_letter(text: str) -> bool:
    """Check if text is a valid Windows drive letter (A-Z)."""
    return len(text) == 1 and text.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _normalize_windows_path(path: str) -> str:
    """Convert Windows path to URL-compatible format."""
    # Split on first colon only
    parts = path.split(":", 1)
    if len(parts) == 2 and _is_windows_drive_letter(parts[0]):  # noqa: PLR2004
        drive, rest = parts
        return f"/{drive.lower()}{rest}"
    # If no valid drive letter, treat as regular path
    return path.replace("\\", "/")


def _denormalize_windows_path(path: str) -> str:
    """Convert URL path back to Windows format."""
    parts = path.strip("/").split("/")
    # Need at least drive + path
    if parts and len(parts) > 1 and _is_windows_drive_letter(parts[0]):
        drive = parts[0].upper()
        rest = "/".join(parts[1:])
        return f"{drive}:/{rest}"
    return "/".join(parts)


def to_mcp_uri(uri: str) -> types.AnyUrl:
    """Convert internal URI to MCP-compatible AnyUrl."""
    try:
        if not uri:
            msg = "URI cannot be empty"
            raise ValueError(msg)  # noqa: TRY301

        try:
            scheme, rest = uri.split("://", 1)
        except ValueError as exc:
            msg = f"Invalid URI format: {uri}"
            raise ValueError(msg) from exc

        match scheme:
            case "http" | "https":
                return types.AnyUrl(uri)

            case "file":
                path = _normalize_windows_path(rest.lstrip("/"))
                if not path:
                    msg = "Empty path in file URI"
                    raise ValueError(msg)  # noqa: TRY301
                parts = path.split("/")
                encoded = [urllib.parse.quote(part) for part in parts if part]
                return types.AnyUrl(f"file://host/{'/'.join(encoded)}")

            case "text" | "python" | "cli" | "callable" | "image":
                name = urllib.parse.quote(rest)
                return types.AnyUrl(f"resource://host/{name}")

            case _:
                msg = f"Unsupported URI scheme: {scheme}"
                raise ValueError(msg)  # noqa: TRY301

    except Exception as exc:
        if isinstance(exc, ValueError):
            raise
        msg = f"Failed to convert URI {uri!r} to MCP format"
        raise ValueError(msg) from exc


def from_mcp_uri(uri: str) -> str:
    """Convert MCP URI to internal format."""
    try:
        if not uri:
            msg = "URI cannot be empty"
            raise ValueError(msg)  # noqa: TRY301

        try:
            scheme, rest = uri.split("://", 1)
        except ValueError as exc:
            msg = f"Invalid URI format: {uri}"
            raise ValueError(msg) from exc

        match scheme:
            case "http" | "https":
                return uri.rstrip("/")

            case "file":
                # Remove host part and decode path
                path = rest.split("/", 1)[1] if "host/" in rest else rest
                parts = [urllib.parse.unquote(p) for p in path.split("/")]
                path = _denormalize_windows_path("/".join(parts))
                return f"file:///{path}"

            case "resource":
                name = rest.split("/", 1)[1] if "/" in rest else rest
                return urllib.parse.unquote(name)

            case _:
                msg = f"Unsupported URI scheme: {scheme}"
                raise ValueError(msg)  # noqa: TRY301

    except Exception as exc:
        if isinstance(exc, ValueError):
            raise
        msg = f"Failed to convert URI {uri!r}"
        raise ValueError(msg) from exc


def to_mcp_resource_template(
    template_uri: str,
    name: str,
    description: str | None = None,
    mime_type: str | None = None,
) -> types.ResourceTemplate:
    """Convert internal template information to MCP ResourceTemplate."""
    return types.ResourceTemplate(
        uriTemplate=template_uri,
        name=name,
        description=description,
        mimeType=mime_type,
    )
