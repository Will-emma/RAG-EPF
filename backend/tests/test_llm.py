import logging

import pytest

from app.core.config import settings
from app.rag import llm


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
