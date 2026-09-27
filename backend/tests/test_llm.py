import logging

import httpx
import pytest

from app.core.config import Settings, settings
from app.rag import llm


def test_llm_model_can_be_loaded_from_environment(monkeypatch):
    model = "nvidia/nemotron-3-ultra-550b-a55b:free"
    monkeypatch.setenv("LLM_MODEL", model)

    configured = Settings(
        _env_file=None,
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        JWT_SECRET_KEY="test-secret",
    )

    assert configured.LLM_MODEL == model


@pytest.mark.asyncio
async def test_llm_logs_technical_result_without_sensitive_content(
    monkeypatch, caplog
):
    api_key = "ci-only-fake-llm-key"
    system_prompt = "private system prompt"
    user_prompt = "private user prompt"
    model_response = "private model response"

    class StubResponse:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": model_response}}]}

    class StubAsyncClient:
        def __init__(self, *, timeout):
            assert timeout == 30.0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, _url, *, headers, json):
            assert headers["Authorization"] == f"Bearer {api_key}"
            assert json["model"] == settings.LLM_MODEL
            assert json["max_tokens"] == 2048
            assert json["messages"][0]["content"] == system_prompt
            assert json["messages"][1]["content"] == user_prompt
            return StubResponse()

    monkeypatch.setattr(settings, "LLM_API_KEY", api_key)
    monkeypatch.setattr(llm.httpx, "AsyncClient", StubAsyncClient)
    caplog.set_level(logging.INFO, logger="app.rag.llm")

    result = await llm.call_llm(system_prompt, user_prompt)

    assert result == model_response
    assert "LLM request completed" in caplog.text
    for sensitive_value in (api_key, system_prompt, user_prompt, model_response):
        assert sensitive_value not in caplog.text


@pytest.mark.asyncio
async def test_llm_failure_logs_do_not_expose_api_key(monkeypatch, caplog):
    api_key = "ci-only-fake-llm-key"

    class StubAsyncClient:
        def __init__(self, *, timeout):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, *_args, **_kwargs):
            request = httpx.Request("POST", "https://llm.test/chat/completions")
            response = httpx.Response(402, request=request)
            raise httpx.HTTPStatusError(api_key, request=request, response=response)

    monkeypatch.setattr(settings, "LLM_API_KEY", api_key)
    monkeypatch.setattr(llm.httpx, "AsyncClient", StubAsyncClient)
    caplog.set_level(logging.WARNING, logger="app.rag.llm")

    with pytest.raises(httpx.HTTPStatusError):
        await llm.call_llm("system", "user")

    assert "LLM request failed" in caplog.text
    assert api_key not in caplog.text
