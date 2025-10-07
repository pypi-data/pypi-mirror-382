import os
import json
import base64
import mimetypes
from typing import Any, Dict, List, Tuple, Optional

import requests
from .base import LLMProvider, search_pricing_data


ANTHROPIC_PRICING = [
    {
      "model_id": "claude-opus-4.1",
      "input_price_per_million_tokens": 15.00,
      "output_price_per_million_tokens": 75.00,
    },
    {
      "model_id": "claude-sonnet-4",
      "input_price_per_million_tokens": 3.00,
      "output_price_per_million_tokens": 15.00,
    },
    {
      "model_id": "claude-haiku-3.5",
      "input_price_per_million_tokens": 0.80,
      "output_price_per_million_tokens": 4.00,
    },
    # Legacy models
    {
      "model_id": "claude-opus-4",
      "input_price_per_million_tokens": 15.00,
      "output_price_per_million_tokens": 75.00,
    },
    {
      "model_id": "claude-opus-3",
      "input_price_per_million_tokens": 15.00,
      "output_price_per_million_tokens": 75.00,
    },
    {
      "model_id": "claude-sonnet-3.7",
      "input_price_per_million_tokens": 3.00,
      "output_price_per_million_tokens": 15.00,
    },
    {
      "model_id": "claude-haiku-3",
      "input_price_per_million_tokens": 0.25,
      "output_price_per_million_tokens": 1.25,
    }
]


class AnthropicProvider(LLMProvider):
    API_URL = "https://api.anthropic.com/v1/messages"
    API_KEY_NAME = "ANTHROPIC_API_KEY"
    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def _check_api_key(self):
        api_key = os.getenv(self.API_KEY_NAME)
        if not api_key:
            raise ValueError(
                f"{self.API_KEY_NAME} environment variable not set. "
                "Please set it to your Anthropic API key."
            )
        return api_key

    def _stream_response(self, response):
        for line in response.iter_lines():
            if not line:
                continue
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith('data:'):
                try:
                    data = json.loads(decoded_line[len('data: '):])
                    if data.get('type') == 'content_block_delta':
                        delta = data.get('delta', {})
                        txt = delta.get('text')
                        if txt:
                            yield {"type": "text", "text": txt}
                except (json.JSONDecodeError, KeyError):
                    continue

    # ---- helpers to transform normalized parts to Anthropic schema ----

    def _read_image_to_base64(self, part: Dict[str, Any]) -> Tuple[str, str]:
        source = part.get("source", {})
        kind = source.get("kind")
        value = source.get("value")
        mime = part.get("mime")

        data: Optional[bytes] = None
        if kind == "bytes":
            data = value if isinstance(value, (bytes, bytearray)) else bytes(value)
        elif kind == "file":
            data = value.read()
        elif kind == "path":
            if not mime and isinstance(value, str):
                mime = mimetypes.guess_type(value)[0] or "image/jpeg"
            with open(value, "rb") as f:
                data = f.read()
        elif kind == "url":
            # Anthropic supports URL sources, but we'll prefer base64 to be consistent
            resp = requests.get(value, timeout=30)
            resp.raise_for_status()
            data = resp.content
            mime = mime or resp.headers.get("Content-Type") or mimetypes.guess_type(value)[0] or "image/jpeg"
        else:
            raise ValueError("Unsupported image source for Anthropic.")

        if not mime:
            mime = "image/jpeg"

        b64 = base64.b64encode(data).decode("utf-8")
        return mime, b64

    def _to_anthropic_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content")
            if isinstance(content, list):
                blocks: List[Dict[str, Any]] = []
                for p in content:
                    if p.get("type") == "text":
                        blocks.append({"type": "text", "text": p.get("text", "")})
                    elif p.get("type") == "image":
                        # Use base64 source (works for both path/bytes/file/url)
                        mime, b64 = self._read_image_to_base64(p)
                        blocks.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime,
                                "data": b64
                            }
                        })
                    else:
                        continue
                out.append({"role": role, "content": blocks})
            else:
                # Fallback: plain string content becomes a single text block
                out.append({"role": role, "content": [{"type": "text", "text": str(content)}]})
        return out

    def get_model_pricing(self, model_id: str) -> Optional[Dict[str, float]]:
        return search_pricing_data(ANTHROPIC_PRICING, model_id)

    def call(self, model, messages, system_prompt=None, stream=False, **kwargs):
        api_key = self._check_api_key()

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        tools = kwargs.pop("tools", None)
        tool_choice = kwargs.pop("tool_choice", None)

        # Extract system messages and combine with system_prompt
        system_parts = []
        filtered_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                content = msg.get("content")
                if isinstance(content, list):
                    for p in content:
                        if p.get("type") == "text":
                            system_parts.append(p.get("text", ""))
                else:
                    system_parts.append(str(content))
            else:
                filtered_messages.append(msg)

        system_text = "\n".join(system_parts)
        if system_prompt:
            if system_text:
                system_text = system_prompt + "\n\n" + system_text
            else:
                system_text = system_prompt

        payload = {
            "model": model or self.DEFAULT_MODEL,
            "messages": self._to_anthropic_messages(filtered_messages),
            "stream": stream,
            "max_tokens": kwargs.get("max_tokens", 1024),
        }

        if system_text:
            payload["system"] = system_text

        if tools:
            anthropic_tools = []
            for tool in tools:
                if tool.get("type") == "function":
                    func = tool.get("function", {})
                    name = func.get("name")
                    description = func.get("description", "")
                    parameters = func.get("parameters", {})
                    # Map OpenAI parameters to Anthropic input_schema
                    input_schema = parameters
                    anthropic_tools.append({
                        "name": name,
                        "description": description,
                        "input_schema": input_schema,
                    })
            payload["tools"] = anthropic_tools

        if tool_choice:
            if tool_choice == "auto":
                payload["tool_choice"] = {"type": "auto"}
            elif tool_choice == "none":
                payload["tool_choice"] = {"type": "any"}
            elif isinstance(tool_choice, dict) and tool_choice.get("type") == "function":
                func = tool_choice.get("function", {})
                name = func.get("name")
                payload["tool_choice"] = {"type": "tool", "name": name}

        payload.update(kwargs)

        response = requests.post(self.API_URL, headers=headers, json=payload, stream=stream)
        response.raise_for_status()

        if stream:
            return self._stream_response(response)

        data = response.json()
        content_blocks = data.get('content') or []
        parts: List[Dict[str, Any]] = []
        tool_calls = None
        for b in content_blocks:
            if b.get("type") == "text":
                parts.append({"type": "text", "text": b.get("text", "")})
            elif b.get("type") == "tool_use":
                # Extract tool call
                if tool_calls is None:
                    tool_calls = []
                tool_calls.append({
                    "id": b.get("id"),
                    "type": "function",
                    "function": {
                        "name": b.get("name"),
                        "arguments": json.dumps(b.get("input", {})),  # Anthropic uses 'input' as dict
                    },
                })
        finish_reason = data.get("stop_reason")
        if tool_calls:
            finish_reason = "tool_calls"
        return {
            "parts": parts,
            "tool_calls": tool_calls,
            "raw": data,
            "finish_reason": finish_reason,
            "usage": data.get("usage"),
        }