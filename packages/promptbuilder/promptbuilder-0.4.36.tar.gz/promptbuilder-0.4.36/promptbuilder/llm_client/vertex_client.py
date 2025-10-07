import os
import importlib
from functools import wraps
from typing import AsyncIterator, Iterator, Callable, ParamSpec, Awaitable, Any, cast

from pydantic import BaseModel, ConfigDict
from tenacity import RetryError

from vertexai import init as vertex_init
from vertexai.generative_models import GenerativeModel

from promptbuilder.llm_client.base_client import BaseLLMClient, BaseLLMClientAsync, ResultType
from promptbuilder.llm_client.types import (
    Response,
    Content,
    Candidate,
    UsageMetadata,
    Part,
    PartLike,
    ApiKey,
    ThinkingConfig,
    Tool,
    ToolConfig,
    Model,
    CustomApiKey,
)
from promptbuilder.llm_client.config import DecoratorConfigs
from promptbuilder.llm_client.utils import inherited_decorator
from promptbuilder.llm_client.exceptions import APIError


P = ParamSpec("P")


class VertexApiKey(BaseModel, CustomApiKey):
    model_config = ConfigDict(frozen=True)
    project: str
    location: str


@inherited_decorator
def _error_handler(func: Callable[P, Response]) -> Callable[P, Response]:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RetryError as retry_error:
            e = retry_error.last_attempt._exception
            if e is None:
                raise APIError()
            code = getattr(e, "code", None)
            response_json = {
                "status": getattr(e, "status", None),
                "message": str(e),
            }
            response = getattr(e, "response", None)
            raise APIError(code, response_json, response)
        except Exception as e:  # noqa: BLE001
            raise APIError(None, {"status": None, "message": str(e)}, None)
    return wrapper


def _to_vertex_content(messages: list[Content]):
    gen_mod = importlib.import_module("vertexai.generative_models")
    VPart = getattr(gen_mod, "Part")
    VContent = getattr(gen_mod, "Content")
    v_messages: list[Any] = []
    for m in messages:
        v_parts: list[Any] = []
        if m.parts:
            for p in m.parts:
                if p.text is not None:
                    v_parts.append(VPart.from_text(p.text))
                elif p.inline_data is not None and p.inline_data.data is not None:
                    v_parts.append(VPart.from_bytes(data=p.inline_data.data, mime_type=p.inline_data.mime_type or "application/octet-stream"))
        v_messages.append(VContent(role=m.role, parts=v_parts))
    return v_messages


def _tool_to_vertex(tool: Tool):
    VTool = getattr(importlib.import_module("vertexai.generative_models"), "Tool")
    if not tool.function_declarations:
        return VTool(function_declarations=[])
    fds = []
    for fd in tool.function_declarations:
        fds.append({
            "name": fd.name,
            "description": fd.description,
            "parameters": fd.parameters.model_dump() if fd.parameters is not None else None,
            "response": fd.response.model_dump() if fd.response is not None else None,
        })
    return VTool(function_declarations=fds)


def _tool_config_to_vertex(cfg: ToolConfig | None):
    VToolConfig = getattr(importlib.import_module("vertexai.generative_models"), "ToolConfig")
    if cfg is None or cfg.function_calling_config is None:
        return None
    mode = cfg.function_calling_config.mode or "AUTO"
    allowed = cfg.function_calling_config.allowed_function_names
    return VToolConfig(function_calling_config={"mode": mode, "allowedFunctionNames": allowed})


def _from_vertex_response(v_resp: Any) -> Response:
    candidates: list[Candidate] = []
    if getattr(v_resp, "candidates", None):
        for c in v_resp.candidates:
            parts: list[Part] = []
            if c.content and getattr(c.content, "parts", None):
                for vp in c.content.parts:
                    t = getattr(vp, "text", None)
                    if isinstance(t, str):
                        parts.append(Part(text=t))
            candidates.append(Candidate(content=Content(parts=cast(list[Part | PartLike], parts), role="model")))

    usage = None
    um = getattr(v_resp, "usage_metadata", None)
    if um is not None:
        usage = UsageMetadata(
            cached_content_token_count=getattr(um, "cached_content_token_count", None),
            candidates_token_count=getattr(um, "candidates_token_count", None),
            prompt_token_count=getattr(um, "prompt_token_count", None),
            thoughts_token_count=getattr(um, "thoughts_token_count", None),
            total_token_count=getattr(um, "total_token_count", None),
        )

    return Response(candidates=candidates, usage_metadata=usage)


class VertexLLMClient(BaseLLMClient):
    PROVIDER: str = "vertexai"

    def __init__(
        self,
        model: str,
        api_key: ApiKey | None = None,
        decorator_configs: DecoratorConfigs | None = None,
        default_thinking_config: ThinkingConfig | None = None,
        default_max_tokens: int | None = None,
        project: str | None = None,
        location: str | None = None,
        **kwargs,
    ):
        # Resolve project/location from args or env
        project = project or os.getenv("VERTEXAI_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCLOUD_PROJECT")
        location = location or os.getenv("VERTEXAI_LOCATION") or os.getenv("GOOGLE_CLOUD_REGION") or os.getenv("GOOGLE_CLOUD_LOCATION")

        # Allow API Key (string) or ADC (VertexApiKey)
        api_key_str: str | None = None
        if isinstance(api_key, str):
            api_key_str = api_key
        elif api_key is None:
            # Fallback to env vars for API key
            api_key_str = os.getenv("VERTEX_API_KEY") or os.getenv("GOOGLE_API_KEY")
        elif isinstance(api_key, VertexApiKey):
            # ADC path with explicit project/location
            pass
        else:
            # Unexpected CustomApiKey subtype
            raise ValueError("Unsupported api_key type for Vertex: expected str or VertexApiKey")

        if not project or not location:
            raise ValueError("To create a vertexai llm client you need to provide project and location via args or env vars VERTEXAI_PROJECT and VERTEXAI_LOCATION")

        if not isinstance(api_key, VertexApiKey):
            api_key = VertexApiKey(project=project, location=location)

        super().__init__(
            VertexLLMClient.PROVIDER,
            model,
            decorator_configs=decorator_configs,
            default_thinking_config=default_thinking_config,
            default_max_tokens=default_max_tokens,
        )
        self._api_key = api_key
        self._api_key_str = api_key_str

        vertex_init(project=self._api_key.project, location=self._api_key.location)
        self._model = GenerativeModel(self.model)

    @property
    def api_key(self) -> VertexApiKey:
        return self._api_key

    @_error_handler
    def _create(
        self,
        messages: list[Content],
        result_type: ResultType = None,
        *,
        thinking_config: ThinkingConfig | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
        timeout: float | None = None,
        tools: list[Tool] | None = None,
        tool_config: ToolConfig = ToolConfig(),
    ) -> Response:
        v_messages = _to_vertex_content(messages)
        GenerationConfig = getattr(importlib.import_module("vertexai.generative_models"), "GenerationConfig")
        gen_cfg = GenerationConfig(max_output_tokens=max_tokens or self.default_max_tokens)
        
        # Handle thinking config
        if thinking_config is None:
            thinking_config = self.default_thinking_config
        if thinking_config is not None:
            # Vertex AI supports thinking via response_logprobs and logprobs parameters
            # but the exact implementation may vary - for now, we'll store it for potential future use
            pass
        
        req_opts: dict[str, Any] | None = {}
        if timeout is not None:
            req_opts["timeout"] = timeout
        if self._api_key_str:
            req_opts["api_key"] = self._api_key_str
        if not req_opts:
            req_opts = None

        v_tools = None
        if tools is not None:
            v_tools = [_tool_to_vertex(t) for t in tools]
        v_tool_cfg = _tool_config_to_vertex(tool_config)

        v_resp = self._model.generate_content(
            contents=v_messages,
            generation_config=gen_cfg,
            tools=v_tools,
            tool_config=v_tool_cfg,
            system_instruction=system_message,
            request_options=req_opts,
        )

        resp = _from_vertex_response(v_resp)
        if result_type == "json" and resp.text is not None:
            resp.parsed = BaseLLMClient.as_json(resp.text)
        elif isinstance(result_type, type(BaseModel)) and resp.text is not None:
            parsed = BaseLLMClient.as_json(resp.text)
            resp.parsed = result_type.model_validate(parsed)
        return resp

    def create_stream(
        self,
        messages: list[Content],
        *,
        thinking_config: ThinkingConfig | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[Response]:
        v_messages = _to_vertex_content(messages)
        GenerationConfig = getattr(importlib.import_module("vertexai.generative_models"), "GenerationConfig")
        gen_cfg = GenerationConfig(max_output_tokens=max_tokens or self.default_max_tokens)
        
        # Handle thinking config
        if thinking_config is None:
            thinking_config = self.default_thinking_config
        if thinking_config is not None:
            # Store for potential future use when Vertex AI supports thinking features
            pass
        
        req_opts: dict[str, Any] | None = {}
        if self._api_key_str:
            req_opts["api_key"] = self._api_key_str
        if not req_opts:
            req_opts = None
        stream = self._model.generate_content(
            contents=v_messages,
            generation_config=gen_cfg,
            system_instruction=system_message,
            request_options=req_opts,
            stream=True,
        )
        for ev in stream:
            yield _from_vertex_response(ev)

    @staticmethod
    def models_list() -> list[Model]:
        return []


@inherited_decorator
def _error_handler_async(func: Callable[P, Awaitable[Response]]) -> Callable[P, Awaitable[Response]]:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except RetryError as retry_error:
            e = retry_error.last_attempt._exception
            if e is None:
                raise APIError()
            code = getattr(e, "code", None)
            response_json = {
                "status": getattr(e, "status", None),
                "message": str(e),
            }
            response = getattr(e, "response", None)
            raise APIError(code, response_json, response)
        except Exception as e:  # noqa: BLE001
            raise APIError(None, {"status": None, "message": str(e)}, None)
    return wrapper


class VertexLLMClientAsync(BaseLLMClientAsync):
    PROVIDER: str = "vertexai"

    def __init__(
        self,
        model: str,
        api_key: ApiKey | None = None,
        decorator_configs: DecoratorConfigs | None = None,
        default_thinking_config: ThinkingConfig | None = None,
        default_max_tokens: int | None = None,
        project: str | None = None,
        location: str | None = None,
        **kwargs,
    ):
        project = project or os.getenv("VERTEXAI_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCLOUD_PROJECT")
        location = location or os.getenv("VERTEXAI_LOCATION") or os.getenv("GOOGLE_CLOUD_REGION") or os.getenv("GOOGLE_CLOUD_LOCATION")

        api_key_str: str | None = None
        if isinstance(api_key, str):
            api_key_str = api_key
        elif api_key is None:
            api_key_str = os.getenv("VERTEX_API_KEY") or os.getenv("GOOGLE_API_KEY")
        elif isinstance(api_key, VertexApiKey):
            pass
        else:
            raise ValueError("Unsupported api_key type for Vertex: expected str or VertexApiKey")

        if not project or not location:
            raise ValueError("To create a vertexai llm client you need to provide project and location via args or env vars VERTEXAI_PROJECT and VERTEXAI_LOCATION")

        if not isinstance(api_key, VertexApiKey):
            api_key = VertexApiKey(project=project, location=location)

        super().__init__(
            VertexLLMClientAsync.PROVIDER,
            model,
            decorator_configs=decorator_configs,
            default_thinking_config=default_thinking_config,
            default_max_tokens=default_max_tokens,
        )
        self._api_key = api_key
        self._api_key_str = api_key_str

        vertex_init(project=self._api_key.project, location=self._api_key.location)
        self._model = GenerativeModel(self.model)

    @property
    def api_key(self) -> VertexApiKey:
        return self._api_key

    @_error_handler_async
    async def _create(
        self,
        messages: list[Content],
        result_type: ResultType = None,
        *,
        thinking_config: ThinkingConfig | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
        timeout: float | None = None,
        tools: list[Tool] | None = None,
        tool_config: ToolConfig = ToolConfig(),
    ) -> Response:
        # Reuse sync implementation (SDK is sync). For real async, offload to thread.
        client = VertexLLMClient(
            model=self.model,
            api_key=self._api_key,
            decorator_configs=self._decorator_configs,
            default_thinking_config=self.default_thinking_config,
            default_max_tokens=self.default_max_tokens,
        )
        return client._create(
            messages=messages,
            result_type=result_type,
            thinking_config=thinking_config,
            system_message=system_message,
            max_tokens=max_tokens,
            timeout=timeout,
            tools=tools,
            tool_config=tool_config,
        )

    async def create_stream(
        self,
        messages: list[Content],
        *,
        thinking_config: ThinkingConfig | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[Response]:
        # Provide a simple wrapper yielding once (non-streaming)
        resp = await self._create(
            messages=messages,
            result_type=None,
            thinking_config=thinking_config,
            system_message=system_message,
            max_tokens=max_tokens,
        )
        yield resp

    @staticmethod
    def models_list() -> list[Model]:
        return VertexLLMClient.models_list()
