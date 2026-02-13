"""
LLM interface — pluggable (Groq / OpenAI / Ollama).
"""

import json
from typing import List, Dict, Any

from rag.config import (
    LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL,
    OPENAI_API_KEY, OPENAI_LLM_MODEL,
    OLLAMA_MODEL, OLLAMA_BASE_URL,
)


def _build_messages(system: str, history: List[Dict], user_msg: str) -> List[Dict]:
    msgs = [{"role": "system", "content": system}]
    msgs.extend(history)
    msgs.append({"role": "user", "content": user_msg})
    return msgs


def call_llm(
    system_prompt: str,
    user_message: str,
    history: List[Dict] = None,
    temperature: float = 0.0,
    max_tokens: int = 2048,
) -> str:
    """Call the configured LLM and return the response text."""
    history = history or []
    messages = _build_messages(system_prompt, history, user_message)

    if LLM_PROVIDER == "groq":
        return _call_groq(messages, temperature, max_tokens)
    elif LLM_PROVIDER == "openai":
        return _call_openai(messages, temperature, max_tokens)
    elif LLM_PROVIDER == "ollama":
        return _call_ollama(messages, temperature, max_tokens)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")


def _call_groq(messages, temperature, max_tokens) -> str:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content


def _call_openai(messages, temperature, max_tokens) -> str:
    import openai
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=OPENAI_LLM_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content


def _call_ollama(messages, temperature, max_tokens) -> str:
    import requests
    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]
