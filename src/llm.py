"""Single place for Gemini model choice, pricing, and client construction."""

import os
from typing import Optional

# gemini-2.5-flash is retired on 2026-12-01 (auto-redirected to 3.5 Flash-Lite).
# Override with GEMINI_MODEL in .env if needed.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Optional: "minimal" (model default), "low", "medium", "high".
# Gemini 3.x ignores temperature/top_p/top_k, so thinking level is the main knob.
GEMINI_THINKING_LEVEL = os.getenv("GEMINI_THINKING_LEVEL") or None

# USD per 1K tokens (Gemini 3.5 Flash-Lite: $0.30 / 1M input, $2.50 / 1M output).
INPUT_COST_PER_1K = 0.0003
OUTPUT_COST_PER_1K = 0.0025


def calculate_cost(input_tokens: int, output_tokens: int) -> tuple:
    """Return (input_cost, output_cost, total_cost) in USD."""
    input_cost = (input_tokens / 1000) * INPUT_COST_PER_1K
    output_cost = (output_tokens / 1000) * OUTPUT_COST_PER_1K
    return input_cost, output_cost, input_cost + output_cost


def response_text(result) -> str:
    """Plain text of a model reply.

    Gemini 3.x replies arrive as a list of content blocks (text plus
    thought-signature blocks) rather than a single string.
    """
    content = getattr(result, "content", result)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts)
    return str(content)


def make_llm(api_key: Optional[str] = None):
    """Build the chat model. No temperature: Gemini 3.x ignores sampling params."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    kwargs = {"model": GEMINI_MODEL, "google_api_key": api_key}
    if GEMINI_THINKING_LEVEL:
        kwargs["thinking_level"] = GEMINI_THINKING_LEVEL
    return ChatGoogleGenerativeAI(**kwargs)
