from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Set
from weakref import WeakKeyDictionary

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions, ServerCapabilities
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

from .config import get_settings
from .fal import FalAIService

logger = logging.getLogger(__name__)


@dataclass
class SessionOverrides:
    api_key: Optional[str] = None
    allowed_models: Optional[Set[str]] = None
    model_keywords: Optional[list[str]] = None


class FalAIMCPServer:
    def __init__(self):
        self.settings = get_settings()
        self.session_overrides: WeakKeyDictionary[Any, SessionOverrides] = WeakKeyDictionary()
        
        @lru_cache(maxsize=16)
        def service_for(api_key: Optional[str]) -> FalAIService:
            return FalAIService(api_key=api_key, timeout=self.settings.request_timeout)
        
        self.service_for = service_for
        self.default_service = service_for(self.settings.api_key)
        
        base_allowed = self.settings.allowed_models
        if not base_allowed and self.settings.default_model_keywords:
            base_allowed = self.default_service.search_models(self.settings.default_model_keywords)
        
        self.default_allowed_set: Optional[Set[str]] = set(base_allowed or []) or None

    def get_overrides(self, session: Any) -> SessionOverrides:
        overrides = self.session_overrides.get(session)
        if overrides is None:
            overrides = SessionOverrides()
            self.session_overrides[session] = overrides
        return overrides

    def resolve_runtime(self, session: Any) -> tuple[FalAIService, Optional[Set[str]]]:
        overrides = self.get_overrides(session)
        api_key = overrides.api_key if overrides.api_key is not None else self.settings.api_key
        service = self.service_for(api_key)

        allowed: Optional[Set[str]] = self.default_allowed_set.copy() if self.default_allowed_set else None

        if overrides.allowed_models is not None:
            override_set = {model for model in overrides.allowed_models if model}
            if allowed is not None:
                allowed = override_set & allowed
            else:
                allowed = override_set
        elif overrides.model_keywords:
            keywords = [kw for kw in overrides.model_keywords if kw]
            base = allowed if allowed is not None else None
            allowed = set(service.search_models(keywords, allowed=base))

        return service, allowed

    def ensure_allowed(self, model_id: str, allowed: Optional[Set[str]]) -> None:
        if allowed is not None and model_id not in allowed:
            raise ValueError(f"Model '{model_id}' is not enabled on this session.")

    def _wrap_http(self, callable_):
        try:
            return callable_()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise ValueError(f"fal.ai request failed with status {exc.response.status_code}: {detail}") from exc
        except httpx.HTTPError as exc:
            raise ValueError(f"fal.ai request failed: {exc}") from exc

    async def handle_list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        tools = [
            Tool(
                name="configure",
                description="Configure fal.ai credentials and allowed models for this session",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "api_key": {"type": "string", "description": "fal.ai API key"},
                        "allowed_models": {"type": "array", "items": {"type": "string"}, "description": "List of allowed model IDs"},
                        "model_keywords": {"type": "array", "items": {"type": "string"}, "description": "Keywords to filter models"}
                    }
                }
            ),
            Tool(
                name="models",
                description="List available fal.ai model identifiers",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page": {"type": "integer", "description": "Page number"},
                        "total": {"type": "integer", "description": "Total number of models to return"}
                    }
                }
            ),
            Tool(
                name="search",
                description="Search for fal.ai models by keyword",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "keywords": {"type": "string", "description": "Keywords to search for"}
                    },
                    "required": ["keywords"]
                }
            ),
            Tool(
                name="schema",
                description="Retrieve the OpenAPI schema for a fal.ai model",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model_id": {"type": "string", "description": "Model ID to get schema for"}
                    },
                    "required": ["model_id"]
                }
            ),
            Tool(
                name="generate",
                description="Generate content using a fal.ai model",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model": {"type": "string", "description": "Model ID to use"},
                        "parameters": {"type": "object", "description": "Parameters for the model"},
                        "queue": {"type": "boolean", "description": "Whether to queue the request"}
                    },
                    "required": ["model", "parameters"]
                }
            ),
            Tool(
                name="result",
                description="Get the result from a queued fal.ai request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL of the queued request"}
                    },
                    "required": ["url"]
                }
            ),
            Tool(
                name="status",
                description="Check the status of a queued fal.ai request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL of the queued request"}
                    },
                    "required": ["url"]
                }
            ),
            Tool(
                name="cancel",
                description="Cancel a queued fal.ai request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL of the queued request"}
                    },
                    "required": ["url"]
                }
            ),
            Tool(
                name="upload",
                description="Upload a file to fal.ai CDN and return the access URL",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file to upload"}
                    },
                    "required": ["path"]
                }
            )
        ]
        return ListToolsResult(tools=tools)

    async def handle_call_tool(self, request: CallToolRequest) -> CallToolResult:
        try:
            if request.name == "configure":
                args = request.arguments or {}
                session = getattr(request, 'session', None)
                overrides = self.get_overrides(session)
                
                if "api_key" in args:
                    overrides.api_key = args["api_key"] or None
                
                if "allowed_models" in args:
                    cleaned = {model.strip() for model in args["allowed_models"] if model and model.strip()}
                    overrides.allowed_models = cleaned if cleaned else None
                
                if "model_keywords" in args:
                    cleaned_keywords = [kw.strip() for kw in args["model_keywords"] if kw and kw.strip()]
                    overrides.model_keywords = cleaned_keywords or None
                
                _, allowed = self.resolve_runtime(session)
                result = {
                    "api_key": overrides.api_key or self.settings.api_key,
                    "allowed_models": sorted(allowed) if allowed is not None else None,
                }
                
            elif request.name == "models":
                args = request.arguments or {}
                session = getattr(request, 'session', None)
                service, allowed = self.resolve_runtime(session)
                result = service.list_models(
                    page=args.get("page"),
                    per_page=args.get("total"),
                    allowed=allowed
                )
                
            elif request.name == "search":
                args = request.arguments or {}
                keywords = args.get("keywords", "")
                tokens = [token for token in keywords.split() if token.strip()]
                if not tokens:
                    raise ValueError("Provide at least one keyword to search")
                
                session = getattr(request, 'session', None)
                service, allowed = self.resolve_runtime(session)
                results = service.search_models(tokens, allowed=allowed)
                result = {"keywords": tokens, "items": results}
                
            elif request.name == "schema":
                args = request.arguments or {}
                model_id = args.get("model_id")
                if not model_id:
                    raise ValueError("model_id is required")
                
                session = getattr(request, 'session', None)
                service, allowed = self.resolve_runtime(session)
                self.ensure_allowed(model_id, allowed)
                result = self._wrap_http(lambda: service.fetch_schema(model_id))
                
            elif request.name == "generate":
                args = request.arguments or {}
                model = args.get("model")
                parameters = args.get("parameters", {})
                queue = args.get("queue", False)
                
                if not model:
                    raise ValueError("model is required")
                if not isinstance(parameters, dict):
                    raise ValueError("parameters must be a JSON object")
                
                session = getattr(request, 'session', None)
                service, allowed = self.resolve_runtime(session)
                self.ensure_allowed(model, allowed)
                
                if queue:
                    result = self._wrap_http(lambda: service.submit(model, parameters))
                else:
                    result = self._wrap_http(lambda: service.run(model, parameters))
                    
            elif request.name == "result":
                args = request.arguments or {}
                url = args.get("url")
                if not url:
                    raise ValueError("url is required")
                
                session = getattr(request, 'session', None)
                service, _ = self.resolve_runtime(session)
                result = self._wrap_http(lambda: service.fetch_json(url))
                
            elif request.name == "status":
                args = request.arguments or {}
                url = args.get("url")
                if not url:
                    raise ValueError("url is required")
                
                session = getattr(request, 'session', None)
                service, _ = self.resolve_runtime(session)
                result = self._wrap_http(lambda: service.fetch_json(url))
                
            elif request.name == "cancel":
                args = request.arguments or {}
                url = args.get("url")
                if not url:
                    raise ValueError("url is required")
                
                session = getattr(request, 'session', None)
                service, _ = self.resolve_runtime(session)
                result = self._wrap_http(lambda: service.put(url))
                
            elif request.name == "upload":
                args = request.arguments or {}
                path = args.get("path")
                if not path:
                    raise ValueError("path is required")
                
                file_path = Path(path).expanduser()
                if not file_path.exists():
                    raise ValueError(f"File not found: {file_path}")
                if not file_path.is_file():
                    raise ValueError(f"Path is not a file: {file_path}")
                
                session = getattr(request, 'session', None)
                service, _ = self.resolve_runtime(session)
                url = service.upload_file(str(file_path))
                result = {"url": url}
                
            else:
                raise ValueError(f"Unknown tool: {request.name}")
                
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True
            )


_server: Optional[FalAIMCPServer] = None


def get_server() -> FalAIMCPServer:
    global _server
    if _server is None:
        _server = FalAIMCPServer()
    return _server


async def run_server():
    server = get_server()
    
    # Create MCP server
    mcp_server = Server("falai-mcp")
    
    @mcp_server.list_tools()
    async def list_tools() -> ListToolsResult:
        return await server.handle_list_tools(ListToolsRequest())
    
    @mcp_server.call_tool()
    async def call_tool(name: str, arguments: dict) -> CallToolResult:
        request = CallToolRequest(name=name, arguments=arguments)
        return await server.handle_call_tool(request)
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(
            server_name="falai-mcp-tools",
            server_version="0.2.2",
            capabilities=ServerCapabilities(
                tools={}
            )
        )
        await mcp_server.run(read_stream, write_stream, init_options)
