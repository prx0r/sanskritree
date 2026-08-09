"""Render fluent English for Pass 1 using DeepSeek V4 Flash via opencode API.
Reads evidence bundles from blind_pass_1.jsonl, calls LLM, saves augmented records."""
from __future__ import annotations
import json, os, time, sys
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("FATAL: OPENAI_API_KEY not set")
    sys.exit(1)

from openai import OpenAI
client = OpenAI(api_key=api_key, base_url="https://opencode.ai/zen/go/v1")

# Load pass 1 records
jsonl_path = BASE / "proof" / "checkpoint1" / "runs" / "pass_1" / "blind_pass_1.jsonl"
records = [json.loads(l) for l in jsonl_path.read_text().strip().split("\n") if l.strip()]

B2_PROMPT_TEMPLATE = """You are a Sanskrit translation assistant. You have been given lexical and grammatical evidence to support your translation. Use the evidence provided below, but produce a natural English translation. If the evidence is insufficient for any part of the verse, state "Uncertain: [your best attempt]" rather than inventing a meaning.

SANSKRIT: {source}

LEXICAL EVIDENCE:
{evidence}

FRAME: {frame}

Translate the verse using the provided evidence. Do not add unsupported content."""

def call_llm(source, lemmas, frame, max_retries=3):
    evidence_lines = []
    lemma_gloss = {
        "vand": "to praise", "hfd": "heart", "nATa": "lord",
        "anATa": "helpless", "saraRya": "refuge", "tvanmaya": "consisting of you",
        "citta": "mind", "BErava": "Bhairava",
        "tad": "that", "Sakti": "Sakti/power", "cakra": "wheel",
        "viBava": "manifestation", "prabhava": "source",
        "SaMkara": "Sankara/Siva", "ca": "and", "na": "not",
        "api": "also/even", "eva": "indeed", "aham": "I",
        "Atman": "self", "deva": "god/lord", "Siva": "Siva",
        "nAtha": "lord", "paramArtha": "ultimate reality",
        "phala": "fruit", "karma": "action",
        "nitya": "eternal", "sarvatra": "everywhere",
        "sat": "being/true", "para": "other/supreme", "sva": "self",
    }
    for lemma in lemmas[:10]:
        gloss = lemma_gloss.get(lemma, f"[unrecognized: {lemma}]")
        evidence_lines.append(f"  {lemma}: {gloss}")
    evidence = "\n".join(evidence_lines) if evidence_lines else "[No lexical evidence available]"

    prompt = B2_PROMPT_TEMPLATE.format(source=source, evidence=evidence, frame=frame)

    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": "You are a Sanskrit translation engine. Output ONLY the English translation. No thinking, no notes, no commentary. If uncertain, start with 'Uncertain:'"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=2048,
            )
            content = resp.choices[0].message.content or ""
            reasoning = getattr(resp.choices[0].message, 'reasoning_content', None)
            return {
                "translation": content.strip(),
                "reasoning": reasoning,
                "model": resp.model,
                "usage": {
                    "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                    "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
                    "reasoning_tokens": resp.usage.completion_tokens_details.reasoning_tokens if resp.usage and resp.usage.completion_tokens_details else 0,
                },
                "finish_reason": resp.choices[0].finish_reason,
            }
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return {"translation": f"[LLM_ERROR: {str(e)}]", "error": str(e)}

print(f"Rendering {len(records)} verses with DeepSeek V4 Flash\n")
results = []
total_cost = 0
errors = 0

for i, rec in enumerate(records):
    seq = rec["sequence_index"]
    source = rec["source_clean"]
    lemmas = rec["pipeline"]["factor_graph"]["lemmas"]
    frame = rec["pipeline"]["factor_graph"]["frame"]

    result = call_llm(source, lemmas, frame)
    rec["pipeline"]["llm_rendering"] = result
    rec["reference_blind"] = True  # still blind

    translation = result["translation"]
    usage = result.get("usage", {})
    pt = usage.get("prompt_tokens", 0)
    ct = usage.get("completion_tokens", 0)
    rt = usage.get("reasoning_tokens", 0)
    cost = (pt * 0.15 + ct * 0.60) / 1_000_000  # approximate DeepSeek V4 pricing
    total_cost += cost

    status = "OK"
    if result.get("error"):
        status = "ERR"
        errors += 1
    elif not translation:
        status = "EMPTY"
        errors += 1

    print(f"  [{seq:2d}] {status} | {pt:4d}+{ct:4d}+{rt:4d}tok | ${cost:.4f} | {translation[:70]}...")
    results.append(rec)

    # Rate limiting
    if (i + 1) % 5 == 0:
        time.sleep(0.5)

# Re-save augmented records
jsonl_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in results))
print(f"\n{'='*50}")
print(f"Rendered: {len(results)}/{len(records)} verses")
print(f"Errors: {errors}")
print(f"Total cost: ${total_cost:.4f}")

# Update manifest
manifest_path = BASE / "proof" / "checkpoint1" / "runs" / "pass_1" / "blind_pass_1_manifest.json"
manifest = json.loads(manifest_path.read_text())
manifest["llm_rendering"] = {
    "model": "deepseek-v4-flash",
    "provider": "opencode.ai/zen/go/v1",
    "temperature": 0.0,
    "max_tokens": 2048,
    "completed_at": datetime.now(timezone.utc).isoformat(),
    "total_cost": round(total_cost, 4),
    "total_errors": errors,
    "prompt_version": "B2",
}
manifest_path.write_text(json.dumps(manifest, indent=2))
print(f"Manifest updated")
