import pytest

import promptbuilder.llm_client.google_client as google_mod
from promptbuilder.llm_client.google_client import GoogleLLMClient, GoogleLLMClientAsync
from promptbuilder.llm_client.types import Content, Part, ThinkingConfig


class _FakeGoogleModels:
    def __init__(self, recorder):
        self.recorder = recorder
    def generate_content(self, *, model, contents, config):
        self.recorder["last_config"] = config
        class R:
            def __init__(self):
                self.candidates = []
                self.usage_metadata = None
                self.text = ""
        return R()

class _FakeGoogleClient:
    def __init__(self, recorder):
        self.models = _FakeGoogleModels(recorder)


def test_google_timeout_forwarded_sync(monkeypatch):
    rec = {}
    monkeypatch.setattr(google_mod, "Client", lambda api_key=None: _FakeGoogleClient(rec))

    cli = GoogleLLMClient(model="gemini-1.5-flash", api_key="k")
    _ = cli.create(
        messages=[Content(parts=[Part(text="hi")], role="user")],
        timeout=12.0,
        thinking_config=ThinkingConfig(),
    )

    cfg = rec.get("last_config")
    assert cfg is not None
    assert cfg.http_options is not None
    assert int(cfg.http_options.timeout) == 12


class _FakeAioGoogleModels:
    def __init__(self, recorder):
        self.recorder = recorder
    async def generate_content(self, *, model, contents, config):
        self.recorder["last_config_async"] = config
        class R:
            def __init__(self):
                self.candidates = []
                self.usage_metadata = None
                self.text = ""
        return R()

class _FakeAioWrapper:
    def __init__(self, recorder):
        self.models = _FakeAioGoogleModels(recorder)

class _FakeGoogleClientAsync:
    def __init__(self, recorder):
        self.aio = _FakeAioWrapper(recorder)


@pytest.mark.asyncio
async def test_google_timeout_forwarded_async(monkeypatch):
    rec = {}
    monkeypatch.setattr(google_mod, "Client", lambda api_key=None: _FakeGoogleClientAsync(rec))

    cli = GoogleLLMClientAsync(model="gemini-1.5-flash", api_key="k")
    _ = await cli.create(
        messages=[Content(parts=[Part(text="hi")], role="user")],
        timeout=8.5,
        thinking_config=ThinkingConfig(),
    )

    cfg = rec.get("last_config_async")
    assert cfg is not None
    assert cfg.http_options is not None
    assert int(cfg.http_options.timeout) == 8
