"""Google Gemini LLM provider using the public REST API."""

import httpx

from app.config import config
from app.exceptions import LLMProviderError
from app.llm.provider import BaseLLMProvider
from app.llm.rate_limiter import RateLimitConfig, RateLimiter
from app.llm.retry import RetryHandler
from app.models.llm import LLMResponse
from app.models.query import QueryRequest
from app.utils.logger import get_logger, log_llm_call

logger = get_logger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Async Gemini provider compatible with existing provider interface."""

    def __init__(self, api_key: str, rate_limiter=None, retry_handler=None):
        self._api_key = api_key
        self._rate_limiter = rate_limiter or RateLimiter(
            RateLimitConfig(requests_per_minute=60)
        )
        self._retry_handler = retry_handler or RetryHandler()

    async def complete(self, request: QueryRequest) -> LLMResponse:
        await self._rate_limiter.acquire()
        try:
            return await self._retry_handler.execute(lambda: self._make_api_call(request))
        except Exception as exc:
            logger.error("Gemini API call failed", error=str(exc))
            raise LLMProviderError(f"Gemini API call failed: {type(exc).__name__} - {exc}") from exc

    async def _make_api_call(self, request: QueryRequest) -> LLMResponse:
        model = request.get_model(config.default_model)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        payload = {"contents": [{"role": "user", "parts": [{"text": request.query}]}],
                   "generationConfig": {"temperature": request.get_temperature(config.default_temperature),
                                        "maxOutputTokens": request.get_max_tokens(config.default_max_tokens)}}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers={"x-goog-api-key": self._api_key},
                json=payload,
            )
            if response.status_code >= 400 and response.status_code not in (429, 500, 502, 503, 504):
                raise LLMProviderError(
                    f"Gemini API rejected request with HTTP {response.status_code}"
                )
            response.raise_for_status()
            data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})
        result = LLMResponse(content=text, prompt_tokens=usage.get("promptTokenCount", 0),
                             completion_tokens=usage.get("candidatesTokenCount", 0), model=model)
        log_llm_call(provider="gemini", model=model, tokens=result.total_tokens)
        return result

    def get_name(self) -> str:
        return "gemini"
