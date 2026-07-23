"""
LLM client for Chutes API. One Qwen3.5 call for sayability + formalization + decomposition.
Use CHUTES_API_TOKEN env var. models.md has fallback for dev.
"""

import os
import json
import urllib.request
from typing import Optional

CHUTES_BASE = "https://llm.chutes.ai/v1"
QWEN = "Qwen/Qwen3.5-397B-A17B-TEE"


def _get_token() -> str:
    t = os.environ.get("CHUTES_API_TOKEN")
    if t:
        return t
    try:
        from pathlib import Path
        md = Path(__file__).resolve().parents[1] / "models.md"
        if md.exists():
            for line in md.read_text(encoding="utf-8").splitlines():
                if line.startswith("api = "):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return ""


def chat(messages: list[dict], *, max_tokens: int = 1024, temperature: float = 0.2) -> str:
    token = _get_token()
    if not token:
        return ""
    req = urllib.request.Request(
        f"{CHUTES_BASE}/chat/completions",
        data=json.dumps({
            "model": QWEN,
            "messages": messages,
            "stream": False,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            out = json.loads(r.read().decode())
        if "error" in out:
            return ""
        return out.get("choices", [{}])[0].get("message", {}).get("content") or ""
    except Exception:
        return ""


def process_claim(claim: str, sanskrit: Optional[str] = None, provenance: Optional[dict] = None) -> dict:
    """
    One Qwen3.5 call. Returns {sayable, children}; models cannot author Lean.
    """
    ctx = f"Claim: {claim[:400]}\n"
    if sanskrit:
        ctx += f"Sanskrit (IAST): {sanskrit}\n"
    if provenance:
        ctx += f"Provenance: {json.dumps(provenance)}\n"

    prompt = f"""For this Sanskrit philosophy claim, reply with exactly this JSON (no other text):
{{"sayable": true/false, "children": [{{"statement": "...", "node_type": "FORMAL"}}]}}

Rules: sayable=false if unfalsifiable. Do not write Lean. children: sub-claims if decomposable, else []. node_type: FORMAL|EMPIRICAL|DEFINITION|UNSAYABLE.

{ctx}"""

    resp = chat([{"role": "user", "content": prompt}], max_tokens=600, temperature=0.1)
    if not resp:
        return {"sayable": True, "lean_type": None, "children": []}
    try:
        start = resp.find("{")
        end = resp.rfind("}") + 1
        if start >= 0 and end > start:
            d = json.loads(resp[start:end])
            return {
                "sayable": d.get("sayable", True),
                "children": d.get("children") or [],
            }
    except json.JSONDecodeError:
        pass
    return {"sayable": True, "lean_type": None, "children": []}
