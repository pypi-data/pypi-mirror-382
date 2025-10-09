import os
from functools import wraps
from typing import AsyncIterator, Iterator, Callable, ParamSpec, Awaitable

from pydantic import BaseModel
from tenacity import RetryError
from google.genai import Client, types

from promptbuilder.llm_client.base_client import BaseLLMClient, BaseLLMClientAsync, ResultType
from promptbuilder.llm_client.types import Response, Content, Part, ThinkingConfig, Tool, ToolConfig, Model
from promptbuilder.llm_client.config import DecoratorConfigs
from promptbuilder.llm_client.utils import inherited_decorator
from promptbuilder.llm_client.exceptions import APIError


P = ParamSpec("P")


@inherited_decorator
def _error_handler(func: Callable[P, Response]) -> Callable[P, Response]:
    """
    Decorator to catch error from google.genai and transform it into unified one
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RetryError as retry_error:
            e = retry_error.last_attempt._exception
            if e is None:
                raise APIError()
            code = e.code
            response_json = {
                "status": e.status,
                "message": e.message,
            }
            response = e.response
            raise APIError(code, response_json, response)
    return wrapper


class GoogleLLMClient(BaseLLMClient):
    PROVIDER: str = "google"
    
    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        decorator_configs: DecoratorConfigs | None = None,
        default_thinking_config: ThinkingConfig | None = None,
        default_max_tokens: int | None = None,
        **kwargs,
    ):
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        if api_key is None or not isinstance(api_key, str):
            raise ValueError("To create a google llm client you need to either set the environment variable GOOGLE_API_KEY or pass the api_key in string format")
        super().__init__(GoogleLLMClient.PROVIDER, model, decorator_configs=decorator_configs, default_thinking_config=default_thinking_config, default_max_tokens=default_max_tokens)
        self._api_key = api_key
        self.client = Client(api_key=api_key, **kwargs)
    
    @property
    def api_key(self) -> str:
        return self._api_key
    
    @staticmethod
    def _preprocess_messages(messages: list[Content]) -> list[Content]:
        new_messages = []
        for message in messages:
            # TODO:
            # copy parts from message to new_message
            # if part has inline_data, set display_name to None in new_message
            new_parts = []
            if message.parts:
                for part in message.parts:
                    if part.inline_data is not None:
                        new_part = Part.model_copy(part, deep=True)
                        new_part.inline_data.display_name = None
                    else:
                        new_part = part
                    new_parts.append(new_part)
            new_message = Content(
                role=message.role,
                parts=new_parts
            )
            new_messages.append(new_message)
        return new_messages
    
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
        messages = self._preprocess_messages(messages)
        if max_tokens is None:
            max_tokens = self.default_max_tokens
        config = types.GenerateContentConfig(
            system_instruction=system_message,
            max_output_tokens=max_tokens,
            tools=tools,
            tool_config=tool_config,
        )
        if timeout is not None:
            # Google processes timeout via HttpOptions on the request/config
            config.http_options = types.HttpOptions(timeout=int(timeout * 1_000))
        
        if thinking_config is None:
            thinking_config = self.default_thinking_config
        config.thinking_config = thinking_config
        
        if result_type is None:
            return self.client.models.generate_content(
                model=self.model,
                contents=messages,
                config=config,
            )
        elif result_type == "json":
            response = self.client.models.generate_content(
                model=self.model,
                contents=messages,
                config=config,
            )
            response.parsed = BaseLLMClient.as_json(response.text)
            return response
        elif isinstance(result_type, type(BaseModel)):
            config.response_mime_type = "application/json"
            config.response_schema = result_type
            return self.client.models.generate_content(
                model=self.model,
                contents=messages,
                config=config,
            )
        else:
            raise ValueError(f"Unsupported result_type: {result_type}. Supported types are: None, 'json', or a Pydantic model.")
    
    @_error_handler
    def _create_stream(
        self,
        messages: list[Content],
        *,
        thinking_config: ThinkingConfig | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[Response]:
        if max_tokens is None:
            max_tokens = self.default_max_tokens
        config = types.GenerateContentConfig(
            system_instruction=system_message,
            max_output_tokens=max_tokens,
        )
        
        if thinking_config is None:
            thinking_config = self.default_thinking_config
        config.thinking_config = thinking_config
        
        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=[msg.model_dump() for msg in  messages],
            config=config,
        )
        return response
    
    @staticmethod
    def models_list() -> list[Model]:
        models: list[Model] = []
        client = Client()
        for google_model in client.models.list():
            for action in google_model.supported_actions:
                if action == "generateContent":
                    model_name = google_model.name
                    if model_name.startswith("models/"):
                        model_name = model_name[7:]
                    
                    if "tts" in model_name.lower():
                        continue
                    if "emb" in model_name.lower():
                        continue
                    if "image-generation" in model_name.lower():
                        continue
                    if "gemini" not in model_name.lower():
                        continue
                    
                    models.append(Model(
                        full_model_name=GoogleLLMClient.PROVIDER + ":" + model_name,
                        model=model_name,
                        provider=GoogleLLMClient.PROVIDER,
                        display_name=google_model.display_name,
                    ))
        return models


@inherited_decorator
def _error_handler_async(func: Callable[P, Awaitable[Response]]) -> Callable[P, Awaitable[Response]]:
    """
    Decorator to catch error from google.genai and transform it into unified one
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except RetryError as retry_error:
            e = retry_error.last_attempt._exception
            if e is None:
                raise APIError()
            code = e.code
            response_json = {
                "status": e.status,
                "message": e.message,
            }
            response = e.response
            raise APIError(code, response_json, response)
    return wrapper

class GoogleLLMClientAsync(BaseLLMClientAsync):
    PROVIDER: str = "google"
    
    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        decorator_configs: DecoratorConfigs | None = None,
        default_thinking_config: ThinkingConfig | None = None,
        default_max_tokens: int | None = None,
        **kwargs,
    ):
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        if api_key is None or not isinstance(api_key, str):
            raise ValueError("To create a google llm client you need to either set the environment variable GOOGLE_API_KEY or pass the api_key in string format")
        super().__init__(GoogleLLMClientAsync.PROVIDER, model, decorator_configs=decorator_configs, default_thinking_config=default_thinking_config, default_max_tokens=default_max_tokens)
        self._api_key = api_key
        self.client = Client(api_key=api_key, **kwargs)

    @property
    def api_key(self) -> str:
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
        messages = GoogleLLMClient._preprocess_messages(messages)
        if max_tokens is None:
            max_tokens = self.default_max_tokens
        config = types.GenerateContentConfig(
            system_instruction=system_message,
            max_output_tokens=max_tokens,
            tools=tools,
            tool_config=tool_config,
        )
        if timeout is not None:
            config.http_options = types.HttpOptions(timeout=int(timeout * 1_000))

        if thinking_config is None:
            thinking_config = self.default_thinking_config
        config.thinking_config = thinking_config

        if result_type is None or result_type == "json":
            return await self.client.aio.models.generate_content(
                model=self.model,
                contents=messages,
                config=config,
            )
        elif isinstance(result_type, type(BaseModel)):
            config.response_mime_type = "application/json"
            config.response_schema = result_type
            return await self.client.aio.models.generate_content(
                model=self.model,
                contents=messages,
                config=config,
            )
        else:
            raise ValueError(f"Unsupported result_type: {result_type}. Supported types are: None, 'json', or a Pydantic model.")
    
    @_error_handler_async
    async def _create_stream(
        self,
        messages: list[Content],
        *,
        thinking_config: ThinkingConfig | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[Response]:
        if max_tokens is None:
            max_tokens = self.default_max_tokens
        config = types.GenerateContentConfig(
            system_instruction=system_message,
            max_output_tokens=max_tokens,
        )
        
        if thinking_config is None:
            thinking_config = self.default_thinking_config
        config.thinking_config = thinking_config
        
        response = await self.client.aio.models.generate_content_stream(
            model=self.model,
            contents=[msg.model_dump() for msg in  messages],
            config=config,
        )
        return response

    @staticmethod
    def models_list() -> list[Model]:
        return GoogleLLMClient.models_list()
