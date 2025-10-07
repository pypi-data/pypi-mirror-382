import pytest
from pydantic import BaseModel

import promptbuilder.llm_client.openai_client as openai_mod
from promptbuilder.llm_client.openai_client import OpenaiLLMClient, OpenaiLLMClientAsync
from promptbuilder.llm_client.types import Content, Part


class _FakeResponses:
    def __init__(self, recorder: dict):
        self.recorder = recorder

    def create(self, **kwargs):
        self.recorder["create_kwargs"] = kwargs
        class U:
            def __init__(self):
                self.output_tokens = 0
                self.input_tokens = 0
                self.total_tokens = 0
        class R:
            def __init__(self):
                self.output = []
                self.usage = U()
        return R()

    def parse(self, text_format=None, **kwargs):
        self.recorder["parse_kwargs"] = kwargs
        class R2:
            def __init__(self):
                class U:
                    def __init__(self):
                        self.output_tokens = 0
                        self.input_tokens = 0
                        self.total_tokens = 0
                self.output = []
                self.usage = U()
                self.output_parsed = {"ok": True}
        return R2()


class _FakeOpenAIClient:
    def __init__(self, recorder: dict):
        self.responses = _FakeResponses(recorder)


def test_openai_timeout_forwarded_sync(monkeypatch):
    rec: dict = {}
    # Patch the constructor used inside the client to return our fake with recorder
    monkeypatch.setattr(openai_mod, "OpenAI", lambda api_key=None: _FakeOpenAIClient(rec))
    cli = OpenaiLLMClient(model="dummy", api_key="test-key")

    _ = cli.create(
        messages=[Content(parts=[Part(text="hi")], role="user")],
        timeout=2.5,
    )

    assert rec.get("create_kwargs") is not None
    assert rec["create_kwargs"]["timeout"] == 2.5

    # structured parse path (pydantic model)
    class M(BaseModel):
        x: int | None = None

    _ = cli.create(
        messages=[Content(parts=[Part(text="hi")], role="user")],
        result_type=M,
        timeout=1.0,
    )
    assert rec.get("parse_kwargs") is not None
    assert rec["parse_kwargs"]["timeout"] == 1.0


class _FakeAsyncResponses:
    def __init__(self, recorder: dict):
        self.recorder = recorder

    async def create(self, **kwargs):
        self.recorder["create_kwargs_async"] = kwargs
        class U:
            def __init__(self):
                self.output_tokens = 0
                self.input_tokens = 0
                self.total_tokens = 0
        class R:
            def __init__(self):
                self.output = []
                self.usage = U()
        return R()

    async def parse(self, text_format=None, **kwargs):
        self.recorder["parse_kwargs_async"] = kwargs
        class R2:
            def __init__(self):
                class U:
                    def __init__(self):
                        self.output_tokens = 0
                        self.input_tokens = 0
                        self.total_tokens = 0
                self.output = []
                self.usage = U()
                self.output_parsed = {"ok": True}
        return R2()


class _FakeAsyncOpenAIClient:
    def __init__(self, recorder: dict):
        self.responses = _FakeAsyncResponses(recorder)


@pytest.mark.asyncio
async def test_openai_timeout_forwarded_async(monkeypatch):
    rec: dict = {}
    monkeypatch.setattr(openai_mod, "AsyncOpenAI", lambda api_key=None: _FakeAsyncOpenAIClient(rec))
    cli = OpenaiLLMClientAsync(model="dummy", api_key="test-key")

    _ = await cli.create(
        messages=[Content(parts=[Part(text="hi")], role="user")],
        timeout=3.3,
    )

    assert rec.get("create_kwargs_async") is not None
    assert rec["create_kwargs_async"]["timeout"] == 3.3

    class M(BaseModel):
        x: int | None = None

    _ = await cli.create(
        messages=[Content(parts=[Part(text="hi")], role="user")],
        result_type=M,
        timeout=4.0,
    )
    assert rec.get("parse_kwargs_async") is not None
    assert rec["parse_kwargs_async"]["timeout"] == 4.0
