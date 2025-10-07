# 🧘‍♂️ ZenLLM

[![PyPI version](https://badge.fury.io/py/zenllm.svg)](https://badge.fury.io/py/zenllm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)

The zen, simple, and unified API for LLMs with the best developer experience: two ergonomic entry points and one consistent return type.

> Philosophy: No SDK bloat. Just requests and your API keys. Multimodal in and out. Streaming that’s easy to consume.

## ✨ What’s new (breaking change)

- Two functions: generate() for single-turn, chat() for multi-turn.
- Simple inputs for 95% cases. Escape hatch for advanced parts remains.
- Always returns a structured Response (or a ResponseStream when streaming).
- Image outputs are first-class (bytes or URLs), not lost in translation.
- CLI model picker: when you start the CLI without --model, ZenLLM now prompts you to select a model from the provider (supports OpenAI, Groq, Anthropic, DeepSeek, Gemini, Together, X.ai, and OpenAI-compatible endpoints).

## 🚀 Installation

```bash
pip install zenllm
```

## 💡 Quick start

First, set your provider’s API key (e.g., `export OPENAI_API_KEY="your-key"`).

You can also set a default model via environment:
- export ZENLLM_DEFAULT_MODEL="gpt-4.1"

### Text-only

```python
import zenllm as llm

resp = llm.generate("Why is the sky blue?", model="gpt-4.1")
print(resp.text)
```

### Vision (single image shortcut)

```python
import zenllm as llm

resp = llm.generate(
    "What is in this photo?",
    model="gemini-2.5-pro",
    image="cheeseburger.jpg",  # path, URL, bytes, or file-like accepted
)
print(resp.text)
```

### Vision (image generation output)

Gemini can return image data inline. Save them with one call.

```python
import zenllm as llm

resp = llm.generate(
    "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme",
    model="gemini-2.5-flash-image-preview",
)
resp.save_images(prefix="banana_")  # writes banana_0.png, ...
```

### Multi-turn chat with shorthands

```python
import zenllm as llm

resp = llm.chat(
    [
      ("system", "Be concise."),
      ("user", "Describe this image in one sentence.", "cheeseburger.jpg"),
    ],
    model="claude-sonnet-4-20250514",
)
print(resp.text)
```

### Tool calling (OpenAI-style)

```python
import zenllm as llm

def get_weather(city: str) -> dict:
    """Get current weather for a city.
    
    Args:
        city: The city name.
    """
    # Simulate API call
    return {"temp_c": 21.5, "condition": "sunny"}

# Use in chat or generate
resp = llm.chat(
    [("user", "What's the weather in Paris?")],
    tools=[get_weather],  # or [{"type": "function", "function": {"name": "get_weather", ...}}]
    tool_choice="auto",   # "auto", "none", or {"type": "function", "function": {"name": "get_weather"}}
    model="gpt-4o",
)
print(resp.text)  # Model may respond with tool call instructions
```

ZenLLM automatically derives the tool schema from the function signature, type hints, and docstring. For more control, pass raw dict specs.

#### Handling tool calls (execution loop)

After the model generates tool calls (accessible via `resp.tool_calls`), you can execute them and feed the results back to the LLM for a final response. Use `agent()` for automatic handling, or implement manually for custom logic.

```python
import zenllm as llm
import json

def get_weather(city: str) -> dict:
    """Get current weather for a city.
    
    Args:
        city: The city name.
    """
    # Simulate API call
    return {"temp_c": 21.5, "condition": "sunny"}

# Use agent() for automatic tool execution loop
resp = llm.agent(
    [("user", "What's the weather in Paris?")],
    tools=[get_weather],
    model="gpt-4o",
    auto_run_tools=True,  # Executes tools and feeds results back to the model
)
print(resp.text)
# Output: "The current weather in Paris is sunny with a temperature of 21.5°C."

# Manually handling tool calls (for custom loops)
messages = [("user", "What's the weather in Paris?")]
resp = llm.chat(messages, tools=[get_weather], tool_choice="auto", model="gpt-4o")
print("Tool calls:", resp.tool_calls)  # e.g., [{'id': 'call_abc', 'function': {'name': 'get_weather', 'arguments': '{"city":"Paris"}'}, 'type': 'function'}]

if resp.tool_calls:
    # Execute tools
    tool_results = []
    for call in resp.tool_calls:
        func_name = call["function"]["name"]
        args_str = call["function"]["arguments"]
        args = json.loads(args_str)
        # Assume we have a map of name to function
        if func_name == "get_weather":
            result = get_weather(**args)
            tool_results.append({
                "tool_call_id": call["id"],
                "role": "tool",
                "name": func_name,
                "content": json.dumps(result),
            })
    # Append tool calls and results to messages
    messages.append({"role": "assistant", "tool_calls": resp.tool_calls})
    messages.extend(tool_results)
    # Call again for final response
    final_resp = llm.chat(messages, tools=[get_weather], model="grok-4-fast")
    print("Final response:", final_resp.text)
```

#### Defining tools via Python functions

Tools can be set in the `tools` parameter of each API request (to `chat()`, `generate()`, or `agent()`). The preferred way is to define plain Python functions—ZenLLM automatically derives the OpenAI-compatible tool schema from the function's signature, type hints, and docstring. This approach is simple, type-safe, and leverages your IDE's autocompletion and linting.

##### Structuring your functions

To get the best results, structure your functions with clear signatures, type hints, and docstrings. ZenLLM uses these to generate accurate schemas that help the model understand when and how to call your tools.

For example:

```python
from enum import Enum
from typing import Dict, Optional
import zenllm as llm

class TempUnit(str, Enum):
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"

def get_weather(location: str, units: Optional[TempUnit] = TempUnit.CELSIUS) -> Dict[str, Any]:
    """Retrieves current weather for the given location.
    
    Args:
        location: City and country e.g. Bogotá, Colombia
        units: Units the temperature will be returned in.
    """
    # Simulate API call
    temp = 21.5 if units == TempUnit.CELSIUS else 70.7
    return {"temp": temp, "condition": "sunny"}

# Use in chat or generate
resp = llm.chat(
    [("user", "What's the weather in Paris?")],
    tools=[get_weather],
    tool_choice="auto",
    model="gpt-4o",
)
print(resp.text)
```

ZenLLM inspects the function to. generate a schema like this:

- **name**: Derived from `fn.__name__` (e.g., "get_weather")
- **description**: First line of the docstring
- **parameters**: JSON schema from type hints (e.g., enums become enum arrays, Optional types are not required) and docstring Args: sections for descriptions
- **strict**: Defaults to `true` for better validation (enforced where supported by the provider)

This automatic derivation supports:
- Primitive types (str → "string", int → "integer", float → "number", bool → "boolean")
- Collections (List[T] → array of T, Dict[str, T] → object with additionalProperties T)
- Enums (via `Enum` subclasses)
- Nested structures (dataclasses, TypedDict)
- Optionals (Union[T, None] or Optional[T] → not required, with default if provided)
- Docstring parsing for parameter descriptions (look for "Args:" sections)

For even simpler cases, a basic function with a docstring works:

```python
def simple_calc(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

##### Best practices for structuring functions

Focus on writing clear, well-typed Python functions. ZenLLM handles schema generation, so prioritize readable code over manual JSON. Here are key guidelines to structure your functions effectively:

- **Write clear and detailed function names, parameter descriptions, and instructions.**  
  Use descriptive names and docstrings. Explicitly describe the purpose, each parameter's format, and output in the docstring's first line and Args: section.  
  Use the system prompt to guide when (and when not) to call the function—tell the model exactly what to do.  
  Include examples and edge cases in docstrings if needed, but note that this may impact reasoning models' performance.

- **Apply software engineering best practices.**  
  Make functions obvious and intuitive (principle of least surprise).  
  Use type hints with enums and structures to prevent invalid inputs (e.g., prefer `def toggle_light(state: bool):` over separate on/off params).  
  Pass the intern test: Can someone use the function correctly based only on its signature and docstring? Add clarifications if not.

- **Offload the burden from the model and use code where possible.**  
  Avoid parameters for known values—compute them in code (e.g., no `order_id` param if it's from context; use `submit_refund()` with no args).  
  Combine sequential functions into one (e.g., merge `query_location` and `mark_location` if always paired).

- **Keep the number of tools small for higher accuracy.**  
  Test with varying tool counts. Aim for <20 tools per call to maintain model performance.

- **Leverage ZenLLM resources.**  
  Iterate functions by testing in the CLI or with `chat()`/`generate()`.  
  For advanced workflows, use `agent()` (future autorun support planned).


### Streaming with typed events

```python
import zenllm as llm

stream = llm.generate(
    "Generate an image and a short caption.",
    model="gemini-2.5-flash-image-preview",
    stream=True,
)

caption = []
for ev in stream:
    if ev.type == "text":
        caption.append(ev.text)
        print(ev.text, end="", flush=True)
    elif ev.type == "image":
        if getattr(ev, "bytes", None):
            with open("out.png", "wb") as f:
                f.write(ev.bytes)
        elif getattr(ev, "url", None):
            print(f"\nImage available at: {ev.url}")
final = stream.finalize()  # Response
```

### Using OpenAI-compatible endpoints

Works with local or third-party OpenAI-compatible APIs by passing `base_url`.

```python
import zenllm as llm

# Local model (e.g., Ollama or LM Studio)
resp = llm.generate(
    "Why is the sky blue?",
    model="qwen3:30b",
    base_url="http://localhost:11434/v1",
)
print(resp.text)

# Streaming
stream = llm.generate(
    "Tell me a story.",
    model="qwen3:30b",
    base_url="http://localhost:11434/v1",
    stream=True,
)
for ev in stream:
    if ev.type == "text":
        print(ev.text, end="", flush=True)
```

## 📟 CLI (terminal chat)

Run an interactive chat in your terminal:

```bash
python -m zenllm --model gpt-4o-mini
```

If you omit --model, the CLI will automatically show a model picker populated from your selected provider (OpenAI, Groq, Anthropic, DeepSeek, Gemini, Together, X.ai, or any OpenAI-compatible base_url).

Options (common ones):
- --model MODEL            Model name (defaults to ZENLLM_DEFAULT_MODEL or gpt-4.1)
- --select-model           Force the interactive model picker on startup (by default, the picker appears when you did not pass --model)
- --provider PROVIDER      Force provider (openai/gpt, gemini, claude, deepseek, together, xai, groq)
- --base-url URL           OpenAI-compatible base URL (e.g., http://localhost:11434/v1)
- --api-key KEY            Override API key for this run
- --system TEXT            System prompt for the session
- --no-stream              Disable streaming output
- --temperature FLOAT      Sampling temperature
- --top-p FLOAT            Top-p nucleus sampling
- --max-tokens INT         Limit on generated tokens
- --show-usage             Print usage dict after responses (if available)
- --show-cost              Print cost estimate after responses (if pricing is known)
- --once "PROMPT"          Send a single prompt and exit (non-interactive)

Tip:
- By default, the CLI prompts for model selection when you did not pass --model.
- For OpenAI (provider "openai" or "gpt"): during interactive selection, pressing Enter selects "gpt-5".

Interactive commands:
- /help                 Show help
- /exit | /quit | :q    Exit
- /reset                Reset conversation history
- /system TEXT          Set/replace the system prompt
- /model [NAME]         Switch model; omit NAME to select interactively
- /img PATH [PATH...]   Attach image(s) to the next user message

Examples:
```bash
# Pick a model interactively from Groq
python -m zenllm --provider groq

# Local model via OpenAI-compatible API (e.g., Ollama)
python -m zenllm --base-url http://localhost:11434/v1 --model qwen2.5:7b

# One-off question, streaming, show cost
python -m zenllm --model gpt-4o-mini --show-cost --once "Why is the sky blue?"
```

Note:
- The CLI uses the same env vars as the library (e.g., OPENAI_API_KEY, GEMINI_API_KEY, GROQ_API_KEY, ANTHROPIC_API_KEY, TOGETHER_API_KEY, XAI_API_KEY).
- Fallback chains via ZENLLM_FALLBACK are supported by the underlying API calls.

## 📚 List models programmatically

You can query available models for each provider:

```python
import zenllm as llm

# OpenAI (or other OpenAI-compatible endpoints via base_url)
openai_models = llm.list_models(provider="openai")  # or provider=None with OPENAI_API_KEY set
print([m.id for m in openai_models][:10])

# Groq
groq_models = llm.list_models(provider="groq")

# Anthropic (Claude)
claude_models = llm.list_models(provider="claude")

# DeepSeek
deepseek_models = llm.list_models(provider="deepseek")

# Google Gemini (OpenAI-compatible list endpoint)
gemini_models = llm.list_models(provider="gemini")

# Together AI
together_models = llm.list_models(provider="together")

# X.ai (Grok)
xai_models = llm.list_models(provider="xai")

# OpenAI-compatible custom base (e.g., local)
local_models = llm.list_models(base_url="http://localhost:11434/v1")
```

Each item is a ModelInfo with fields: id, created (if integer), owned_by (if provided), and raw (the full provider response item).

## 🔁 Fallback chains (automatic provider failover)

You can define an ordered chain of providers and models. ZenLLM will try them in order and move on when a provider is down, rate-limiting, or times out. By default, we do not switch mid-stream once tokens start.

Example:
```python
import zenllm as llm
from zenllm import FallbackConfig, ProviderChoice, RetryPolicy

cfg = FallbackConfig(
    chain=[
        ProviderChoice(provider="openai",   model="gpt-4o-mini"),
        ProviderChoice(provider="xai",      model="grok-2-mini"),
        ProviderChoice(provider="together", model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),
    ],
    retry=RetryPolicy(max_attempts=2, initial_backoff=0.5, max_backoff=4.0, timeout=30),
    allow_mid_stream_switch=False,  # recommended
)

# Single-turn
resp = llm.generate("Explain CRDTs vs OT.", fallback=cfg, options={"temperature": 0.2})
print(resp.text)

# Multi-turn
resp = llm.chat([("user", "Help me debug this error…")], fallback=cfg)
print(resp.text)

# Streaming (we only lock in a provider after the first event arrives)
stream = llm.generate("Tell me a haiku about dataclasses.", stream=True, fallback=cfg)
for ev in stream:
    if ev.type == "text":
        print(ev.text, end="")
final = stream.finalize()
```

Environment default:
- You can set a default fallback chain via `ZENLLM_FALLBACK`. Format: `provider:model,provider:model,...`
  Example:
  - `export ZENLLM_FALLBACK="openai:gpt-4o-mini,xai:grok-2-mini,together:meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"`
- When `fallback` is not provided to `generate/chat`, ZenLLM will use the env chain if present.

Notes:
- Per-provider overrides go in `ProviderChoice(..., options={...})`. They override call-level `options`.
- If a provider reports 400/401/403/404/422 errors, we do not retry and we move to the next provider.
- Retryable errors include 408/429/5xx and network timeouts. Exponential backoff with jitter is used.

## 💰 Cost Estimation

ZenLLM automatically estimates the cost of an API call when pricing information is available for the model used.

### After a Call (Most Common)

The `Response` object returned by `generate()` and `chat()` provides methods to access cost information. This is the simplest way to track spending.

```python
import zenllm as llm

resp = llm.generate("Why is the sky blue?", model="gpt-4.1")

# Get total cost as a float
total_cost = resp.cost()
if total_cost is not None:
    print(f"Cost: ${total_cost:.6f}")

# Get a detailed breakdown
breakdown = resp.cost_breakdown()
print(breakdown)
```
This also works in the CLI via the `--show-cost` flag.

### Programmatically Before a Call

To check model pricing before making an API call, you can import the provider class directly and use its `get_model_pricing` method. This is useful for building cost calculators or user-facing UIs.

```python
from zenllm.providers.openai import OpenAIProvider
from zenllm.providers.anthropic import AnthropicProvider

# Create provider instances
openai = OpenAIProvider()
anthropic = AnthropicProvider()

# Get pricing for a specific model
gpt_price = openai.get_model_pricing("gpt-5-mini")
# Returns {'input': 0.25, 'output': 2.0}

claude_price = anthropic.get_model_pricing("claude-haiku-3.5")
# Returns {'input': 0.8, 'output': 4.0}

if gpt_price:
    print(f"GPT-5-mini input cost: ${gpt_price['input']} / 1M tokens")
```

The method returns a dictionary with `input` and `output` prices per million tokens, or `None` if the model's pricing is not available.

## 🧱 API overview

- generate(prompt=None, *, model=..., system=None, image=None, images=None, tools=None, tool_choice=None, stream=False, options=None, provider=None, base_url=None, api_key=None, fallback=None)
- chat(messages, *, model=..., system=None, tools=None, tool_choice=None, stream=False, options=None, provider=None, base_url=None, api_key=None, fallback=None)
- agent(messages, *, tools=None, auto_run_tools=False, model=..., system=None, stream=False, options=None, provider=None, base_url=None, api_key=None, fallback=None)

Inputs:
- prompt: str
- image: single image source (path, URL, bytes, file-like)
- images: list of image sources (same kinds)
- messages shorthands:
  - "hello"
  - ("user"|"assistant"|"system", text[, images])
  - {"role":"user","text":"...", "images":[...]}
  - {"role":"user","parts":[...]}  // escape hatch for experts
- tools: list of tool definitions in OpenAI format (e.g., [{"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}]); also accepts decorated functions from @zenllm.tool or raw dict specs
- tool_choice: tool choice in OpenAI format ("auto", "none", or {"type": "function", "function": {"name": "specific_tool"}})
- options: normalized tuning and passthrough, e.g. {"temperature": 0.7, "max_tokens": 512}.
  These are mapped per provider where needed. Tools/tool_choice can also be passed here for finer control.

Helpers (escape hatch):
- zenllm.text(value) -> {"type":"text","text": "..."}
- zenllm.image(source[, mime, detail]) -> {"type":"image","source":{"kind": "...","value": ...}, ...}

Outputs:
- Always a Response object with:
  - response.text: concatenated text
  - response.parts: normalized parts
    - {"type":"text","text":"..."}
    - {"type":"image","source":{"kind":"bytes"|"url","value":...},"mime":"image/png"}
  - response.images: convenience filtered list
  - response.finish_reason, response.usage, response.raw
  - response.save_images(dir=".", prefix="img_")
  - response.cost(prompt_chars=None, completion_chars=None): total USD cost (None if pricing unknown)
  - response.cost_breakdown(prompt_chars=None, completion_chars=None): detailed dict of pricing inputs and totals
  - response.to_dict() for JSON-safe structure (bytes are base64, kind becomes "bytes_b64")

Streaming:
- Returns a ResponseStream. Iterate events:
  - Text events: ev.type == "text", ev.text
  - Image events: ev.type == "image", either ev.bytes (with ev.mime) or ev.url
- Call stream.finalize() to materialize a Response from the streamed events.

Provider selection:
- Automatic by model prefix: gpt, gemini, claude, deepseek, together, xai, grok, groq
- Override with provider="gpt"|"openai"|"openai-compatible"|"gemini"|"claude"|"deepseek"|"together"|"xai"|"groq"
- OpenAI-compatible: pass base_url (and optional api_key) and we append /chat/completions
- Fallback chains: pass fallback=FallbackConfig(...) or set env ZENLLM_FALLBACK="provider:model,provider:model,..."

## ✅ Supported Providers

| Provider   | Env Var             | Prefix       | Notes                                           | Example Models                                       |
| ---------- | ------------------- | ------------ | ----------------------------------------------- | ---------------------------------------------------- |
| Anthropic  | `ANTHROPIC_API_KEY` | `claude`     | Text + Images (input via base64)                | `claude-sonnet-4-20250514`, `claude-opus-4-20250514` |
| DeepSeek   | `DEEPSEEK_API_KEY`  | `deepseek`   | OpenAI-compatible; image support may vary       | `deepseek-chat`, `deepseek-reasoner`                 |
| Google     | `GEMINI_API_KEY`    | `gemini`     | Text + Images (inline_data base64)              | `gemini-2.5-pro`, `gemini-2.5-flash`                 |
| OpenAI     | `OPENAI_API_KEY`    | `gpt`        | Text + Images (`image_url`, supports data URLs) | `gpt-4.1`, `gpt-4o`                                  |
| TogetherAI | `TOGETHER_API_KEY`  | `together`   | OpenAI-compatible; image support may vary       | `together/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` |
| Groq       | `GROQ_API_KEY`      | `groq`       | OpenAI-compatible; image support may vary       | `llama-3.1-70b-versatile`                            |
| X.ai       | `XAI_API_KEY`       | `xai`, `grok` | OpenAI-compatible; image support may vary       | `grok-code-fast-1`                                   |

Notes:
- For OpenAI-compatible endpoints (like local models), pass `base_url` and optional `api_key`. We’ll route via the OpenAI-compatible provider and append `/chat/completions`.
- Some third-party endpoints don’t support vision. If you pass images to an unsupported model, the upstream provider may return an error.
- DeepSeek and Together may not accept image URLs; prefer path/bytes/file for images with those providers.

## 🧪 Experimental: agent() (preview)

Pass plain Python functions or raw dict specs as tools to the high-level agent() helper. Autorun of tools is disabled by default.

Notes:
- Current preview forwards tool definitions to the provider using an OpenAI-style schema. Automatic execution of tools on the client side (autorun loop) is intentionally off by default and will be expanded in a future release.
- Provider support for tool/function calling varies. OpenAI-compatible endpoints tend to support it; others may ignore the tools field.

Example
```python
import zenllm as llm

def get_weather(city: str):
    """Return current weather for a city.
    
    Args:
        city: The city name.
    """
    # Implement your logic here (e.g., call a REST API)
    return {"temp_c": 21.5, "condition": "sunny"}

# Send tool definitions to the model (no automatic execution by default)
resp = llm.agent(
    messages=[("user", "What's the weather in Paris right now?")],
    tools=[get_weather],           # you can also pass a list of prebuilt dict specs
    model="gpt-4.1",
    # auto_run_tools=False is the default
)

print(resp.text)
```

Passing raw specs (optional)
```python
tool_spec = {
    "name": "get_weather",
    "description": "Get current weather by city",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
        "additionalProperties": False,
    },
}
resp = llm.agent(
    messages=[("user", "What's the weather in Paris right now?")],
    tools=[tool_spec],             # dict specs are accepted too
    model="gpt-4.1",
)
```

Tip:
- Tools and tool_choice can now be passed directly to generate() and chat() for convenience.
- For more advanced usage, pass via options={"tools": [...], "tool_choice": "..."}.

Roadmap:
- Streaming tool-call events, structured JSON output helpers, and an opt-in autorun loop will land in subsequent updates.

## 🧪 Advanced examples

Manual parts with helpers:
```python
from zenllm import text, image
import zenllm as llm

msgs = [
  {"role": "user", "parts": [
    text("Describe this in one sentence."),
    image("cheeseburger.jpg", detail="high"),
  ]},
]
resp = llm.chat(msgs, model="gemini-2.5-pro")
print(resp.text)
```

Provider override:
```python
import zenllm as llm

resp = llm.generate(
  "Hello!",
  model="gpt-4.1",
  provider="openai",  # or "gpt", "openai-compatible", "gemini", "claude", "deepseek", "together", "xai", "groq"
)
print(resp.text)
```

Serialization:
```python
d = resp.to_dict()  # bytes are base64-encoded with kind "bytes_b64"
```

## 📜 License

MIT License — Copyright (c) 2025 Koen van Eijk
[{'id': 'call_87745073', 'function': {'name': 'get_weather', 'arguments': '{"city":"Paris"}'}, 'type': 'function'}]