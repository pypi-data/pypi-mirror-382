import pytest
from pydantic import BaseModel

import promptbuilder.llm_client.litellm_client as litellm_mod
from promptbuilder.llm_client.litellm_client import LiteLLMClient, LiteLLMClientAsync
from promptbuilder.llm_client.types import Content, Part


def test_litellm_timeout_forwarded_sync(monkeypatch):
    recorded = {}
    def fake_completion(**kwargs):
        recorded.update(kwargs)
        class R:
            def __init__(self):
                self.choices = []
                self.usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        return R()
    monkeypatch.setattr(litellm_mod, "completion", fake_completion)

    cli = LiteLLMClient(full_model_name="ollama:llama3.1", api_key=None)
    _ = cli.create([Content(parts=[Part(text="hi")], role="user")], timeout=7.5)

    assert "request_timeout" in recorded
    assert recorded["request_timeout"] == 7.5


@pytest.mark.asyncio
async def test_litellm_timeout_forwarded_async(monkeypatch):
    recorded = {}
    async def fake_acompletion(**kwargs):
        recorded.update(kwargs)
        class R:
            def __init__(self):
                self.choices = []
                self.usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        return R()
    monkeypatch.setattr(litellm_mod, "acompletion", fake_acompletion)

    cli = LiteLLMClientAsync(full_model_name="ollama:llama3.1", api_key=None)
    _ = await cli.create([Content(parts=[Part(text="hi")], role="user")], timeout=5.0)

    assert "request_timeout" in recorded
    assert recorded["request_timeout"] == 5.0
