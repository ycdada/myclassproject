"""
iFlytek Spark (星火) Large Model API Client

Supports:
- Spark Pro (generalv3.5): Core reasoning & dialogue
- Spark Max (generalv4.0): Long-form content generation
- Spark Pro 128K (pro-128k): Ultra-long context understanding
- Function calling for structured data extraction
- Streaming response via WebSocket
"""

import asyncio
import json
import logging
import time
import hmac
import hashlib
import base64
from urllib.parse import urlencode, urlparse
from typing import AsyncGenerator, Optional, List, Dict, Any, Callable

import httpx
import websockets

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SparkClient:
    """WebSocket-based client for iFlytek Spark API."""

    BASE_URL = "wss://spark-api.xf-yun.com"

    DOMAIN_URLS = {
        "generalv3.5": f"{BASE_URL}/v3.5/chat",       # Spark Pro
        "generalv4.0": f"{BASE_URL}/v4.0/chat",       # Spark Max
        "pro-128k": f"{BASE_URL}/chat/pro-128k",       # Spark Pro 128K
    }

    def __init__(
        self,
        app_id: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        domain: str = "generalv3.5",
    ):
        self.app_id = app_id or settings.SPARK_APP_ID
        self.api_key = api_key or settings.SPARK_API_KEY
        self.api_secret = api_secret or settings.SPARK_API_SECRET
        self.domain = domain

    def _build_auth_url(self) -> str:
        """Build authenticated WebSocket URL with HMAC-SHA256 signature."""
        host = urlparse(self.DOMAIN_URLS[self.domain]).netloc
        path = urlparse(self.DOMAIN_URLS[self.domain]).path
        now = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

        signature_origin = f"host: {host}\ndate: {now}\nGET {path} HTTP/1.1"
        signature_sha = hmac.new(
            self.api_secret.encode(),
            signature_origin.encode(),
            digestmod=hashlib.sha256,
        ).digest()
        signature = base64.b64encode(signature_sha).decode()

        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        authorization = base64.b64encode(authorization_origin.encode()).decode()

        params = {
            "authorization": authorization,
            "date": now,
            "host": host,
        }
        return f"{self.DOMAIN_URLS[self.domain]}?{urlencode(params)}"

    def _build_payload(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.5,
        max_tokens: int = 4096,
        functions: Optional[List[Dict]] = None,
    ) -> Dict:
        """Build request payload for Spark API."""
        payload = {
            "header": {
                "app_id": self.app_id,
                "uid": "dsa_learning_system",
            },
            "parameter": {
                "chat": {
                    "domain": self.domain,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            },
            "payload": {
                "message": {
                    "text": messages,
                }
            },
        }

        if functions:
            payload["payload"]["functions"] = {"text": functions}

        return payload

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.5,
        max_tokens: int = 4096,
        functions: Optional[List[Dict]] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion via WebSocket."""
        url = self._build_auth_url()
        payload = self._build_payload(messages, temperature, max_tokens, functions)

        try:
            async with websockets.connect(url, ping_interval=30) as ws:
                await ws.send(json.dumps(payload))

                while True:
                    response = await ws.recv()
                    data = json.loads(response)

                    header = data.get("header", {})
                    code = header.get("code", 0)

                    if code != 0:
                        logger.error(f"Spark API error: code={code}, message={header.get('message')}")
                        yield f"[ERROR] API error code {code}: {header.get('message')}"
                        break

                    payload_data = data.get("payload", {})
                    choices = payload_data.get("choices", {})
                    status = choices.get("status", 2)

                    text_list = choices.get("text", [])
                    for text_item in text_list:
                        content = text_item.get("content", "")
                        if content:
                            yield content

                    # Also check for function call response
                    if "function_call" in choices:
                        func_call = choices["function_call"]
                        yield json.dumps({"function_call": func_call})

                    if status == 2:  # Completed
                        break

        except Exception as e:
            logger.error(f"Spark WebSocket error: {e}")
            yield f"[ERROR] Connection failed: {str(e)}"

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.5,
        max_tokens: int = 4096,
        functions: Optional[List[Dict]] = None,
    ) -> str:
        """Non-streaming chat completion. Collects all chunks."""
        full_response = []
        async for chunk in self.chat_stream(messages, temperature, max_tokens, functions):
            full_response.append(chunk)
        return "".join(full_response)

    async def chat_with_function_calling(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict],
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """Chat completion with structured function calling output."""
        raw = await self.chat(messages, temperature, max_tokens=2048, functions=functions)
        # Try to parse function call from response
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw_response": raw}


class SparkProClient(SparkClient):
    """Spark Pro - core reasoning & dialogue."""
    def __init__(self, **kwargs):
        super().__init__(domain="generalv3.5", **kwargs)


class SparkMaxClient(SparkClient):
    """Spark Max - long-form content generation."""
    def __init__(self, **kwargs):
        super().__init__(domain="generalv4.0", **kwargs)


class Spark128KClient(SparkClient):
    """Spark Pro 128K - ultra-long context."""
    def __init__(self, **kwargs):
        super().__init__(domain="pro-128k", **kwargs)
