"""LLM client with explicit run states, deterministic retries, and infrastructure error handling.
Every call returns a structured result with a status field — never a blank string.
"""
from __future__ import annotations
import json
import os
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Any


class RunState(str, Enum):
    SUCCESS = "SUCCESS"
    EMPTY_OUTPUT = "EMPTY_OUTPUT"
    TRUNCATED_REASONING = "TRUNCATED_REASONING"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    PARSE_ERROR = "PARSE_ERROR"
    AUDIT_REJECTED = "AUDIT_REJECTED"


@dataclass
class LLMResult:
    state: RunState
    translation: str = ""
    reasoning: str | None = None
    model: str = ""
    usage: dict = field(default_factory=dict)
    time_s: float = 0.0
    attempts: list[dict] = field(default_factory=list)


class LLMClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://opencode.ai/zen/go/v1"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def translate(self, source: str, lemmas: list[str], frame: str = "",
                  max_retries: int = 3) -> LLMResult:
        attempts = []
        configs = [
            {"max_tokens": 4096, "prompt_style": "normal"},
            {"max_tokens": 8192, "prompt_style": "simplified"},
            {"max_tokens": 8192, "prompt_style": "minimal"},
        ]

        for attempt_num in range(min(max_retries, len(configs))):
            cfg = configs[attempt_num]
            prompt = self._build_prompt(source, lemmas, frame, style=cfg["prompt_style"])

            t0 = time.time()
            try:
                resp = self.client.chat.completions.create(
                    model="deepseek-v4-flash",
                    messages=[
                        {"role": "system", "content": "You are a Sanskrit translation engine. Output ONLY the English translation."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.0,
                    max_tokens=cfg["max_tokens"],
                )
                elapsed = time.time() - t0
                content = resp.choices[0].message.content or ""
                if isinstance(content, list):
                    content = ""
                content = content.strip()
                reasoning = getattr(resp.choices[0].message, 'reasoning_content', None)
                finish = resp.choices[0].finish_reason or ""

                usage = {}
                if resp.usage:
                    reasoning_tokens = 0
                    if resp.usage.completion_tokens_details:
                        reasoning_tokens = resp.usage.completion_tokens_details.reasoning_tokens or 0
                    usage = {
                        "prompt_tokens": resp.usage.prompt_tokens or 0,
                        "completion_tokens": resp.usage.completion_tokens or 0,
                        "reasoning_tokens": reasoning_tokens,
                    }

                if content:
                    return LLMResult(
                        state=RunState.SUCCESS,
                        translation=content,
                        reasoning=reasoning,
                        model=resp.model,
                        usage=usage,
                        time_s=round(elapsed, 1),
                        attempts=attempts + [{"attempt": attempt_num, "state": "SUCCESS", "usage": usage}],
                    )
                else:
                    state = RunState.TRUNCATED_REASONING if usage.get("reasoning_tokens", 0) >= usage.get("completion_tokens", 0) else RunState.EMPTY_OUTPUT
                    attempts.append({"attempt": attempt_num, "state": state.value, "usage": usage, "finish_reason": finish})

            except Exception as e:
                elapsed = time.time() - t0
                attempts.append({"attempt": attempt_num, "state": "PROVIDER_ERROR", "error": str(e)[:100]})
                time.sleep(1 * (attempt_num + 1))

        return LLMResult(
            state=RunState.PROVIDER_ERROR,
            translation="",
            attempts=attempts,
        )

    def _build_prompt(self, source: str, lemmas: list[str], frame: str, style: str = "normal") -> str:
        evidence_lines = []
        lemma_glosses = {
            "tad": "that", "Sakti": "Sakti/power", "cakra": "wheel",
            "viBava": "manifestation", "prabhava": "source",
            "SaMkara": "Sankara/Siva", "vand": "to praise", "hfd": "heart",
            "nATa": "lord", "anATa": "helpless", "saraRya": "refuge",
            "ca": "and", "na": "not", "api": "also/even", "eva": "indeed",
            "nitya": "eternal", "paramam": "supreme", "pada": "state",
        }
        for lemma in lemmas[:10]:
            gloss = lemma_glosses.get(lemma, f"[unrecognized: {lemma}]")
            evidence_lines.append(f"  {lemma}: {gloss}")
        evidence = "\n".join(evidence_lines) or "[No lexical evidence available]"

        if style == "minimal":
            return f"Translate to English:\n{source}"
        elif style == "simplified":
            return f"Translate this Sanskrit verse to English.\n\nSANSKRIT: {source}\n\nKEY WORDS: {', '.join(lemmas[:8])}"
        else:
            return f"Translate the following Sanskrit verse using the lexical evidence provided.\n\nSANSKRIT: {source}\n\nLEXICAL EVIDENCE:\n{evidence}\n\nFRAME: {frame}"
