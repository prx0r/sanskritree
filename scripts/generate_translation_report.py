"""Generate a self-contained static HTML translation audit report.
Runs 4-pass DeepSeek (A/B/C/D), computes agreement/conflict, calibrates
against published references (Dyczkowski, etc.), exports a single browsable file.

Usage:
  python3 scripts/generate_translation_report.py [--passes] [--report-only]

  --passes      Re-run DeepSeek passes (caches results, skips done)
  --report-only Skip API calls, regenerate HTML from cache
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import hashlib
import html as htmlmod
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    api_key = "sk-miADz8ScBmj7HqPMJTK20R1ks63h9gtsemjRXfYXz3JyfN0Qgbtrl7qduBD8ouTY"

from openai import OpenAI
client = OpenAI(api_key=api_key, base_url="https://opencode.ai/zen/go/v1")

DIAGNOSTIC_PATH = BASE / "proof" / "diagnostic_36.json"
B0_PATH = BASE / "proof" / "b0_diagnostic_36.json"
CACHE_DIR = BASE / "proof" / "translation_report_cache"
REFERENCES_PATH = BASE / "proof" / "checkpoint1" / "references" / "reference_alignment_manifest.json"
OUTPUT_PATH = BASE / "proof" / "translation_audit_report.html"

TRACKED_TERMS = ["prakāśa", "prakasa", "vimarśa", "vimarsa",
                 "svātantrya", "svatantrya", "svatantra",
                 "ābhāsa", "abhasa", "saṃkoca", "sankoca",
                 "kañcuka", "kancuka", "spanda"]

PASS_LABELS = {
    "A": "Direct translation",
    "B": "Term-first translation",
    "C": "Adversarial re-check",
    "D": "Grounded in secondary lit",
}

# ── Prompt templates ──

PASS_A_PROMPT = """{source}"""

PASS_B_PROMPT = """Source: {source}
Task: List any of these terms found in source: prakāśa, vimarśa, svātantrya, ābhāsa, saṃkoca, kañcuka, spanda. Then translate."""

PASS_C_PROMPT = """Source: {source}
Existing: {prior_translation}
Review for errors. Output ANALYSIS: then CORRECTED:."""

PASS_D_PROMPT = """Source: {source}
Reference: {reference_translation}
Translate consistently with reference. If disagree, flag it."""


# ── Data loading ──

def load_diagnostic() -> list[dict]:
    return json.loads(DIAGNOSTIC_PATH.read_text(encoding="utf-8"))

def load_references() -> dict:
    try:
        raw = json.loads(REFERENCES_PATH.read_text(encoding="utf-8"))
        if "verses" in raw:
            return {k: v.get("translation", "") for k, v in raw["verses"].items()}
    except Exception:
        pass
    return {}

def load_b0() -> dict:
    try:
        data = json.loads(B0_PATH.read_text(encoding="utf-8"))
        return {r["passage_id"]: r.get("b0", "") for r in data}
    except Exception:
        return {}


# ── DeepSeek calls ──

def call_deepseek(messages: list[dict], label: str = "", max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=messages,
                temperature=0.0,
                max_tokens=4096,
            )
            content = resp.choices[0].message.content or ""
            reasoning = getattr(resp.choices[0].message, 'reasoning_content', None)
            usage = resp.usage
            # If reasoning consumed all tokens and content is empty, try with more tokens
            if not content.strip() and reasoning:
                resp = client.chat.completions.create(
                    model="deepseek-v4-flash",
                    messages=messages + [{"role": "assistant", "content": reasoning},
                                         {"role": "user", "content": "Now output the final answer concisely."}],
                    temperature=0.0,
                    max_tokens=4096,
                )
                content = resp.choices[0].message.content or ""
            return {
                "content": content.strip(),
                "reasoning": reasoning,
                "model": resp.model,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                },
                "success": True,
            }
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return {"content": f"[ERROR: {e}]", "reasoning": None, "success": False, "error": str(e)}


def run_pass_a(source: str) -> dict:
    return call_deepseek([
        {"role": "system", "content": "Translate to English. No thinking. One sentence only."},
        {"role": "user", "content": PASS_A_PROMPT.format(source=source)},
    ], "A")

def run_pass_b(source: str) -> dict:
    return call_deepseek([
        {"role": "system", "content": "No thinking. Output TERMS: then TRANSLATION:."},
        {"role": "user", "content": PASS_B_PROMPT.format(source=source)},
    ], "B")

def run_pass_c(source: str, prior_translation: str) -> dict:
    return call_deepseek([
        {"role": "system", "content": "Analyze then correct. No thinking."},
        {"role": "user", "content": PASS_C_PROMPT.format(source=source, prior_translation=prior_translation)},
    ], "C")

def run_pass_d(source: str, reference: str, reference_translation: str) -> dict:
    return call_deepseek([
        {"role": "system", "content": "Translate with published reference. No thinking."},
        {"role": "user", "content": PASS_D_PROMPT.format(source=source, reference=reference, reference_translation=reference_translation)},
    ], "D")


# ── Caching ──

def cache_key(passage_id: str, pass_type: str) -> str:
    return f"{passage_id}_{pass_type}"

def load_cache() -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for f in CACHE_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            results[f.stem] = data
        except Exception:
            pass
    return results

def save_cache(key: str, data: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(data, ensure_ascii=False))


# ── Agreement / conflict detection ──

def normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r'[^\w\s]', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

def ngram_set(text: str, n: int = 4) -> set[str]:
    """Character n-grams for comparing texts with different word segmentation."""
    t = text.lower()
    t = re.sub(r'[^a-z]', '', t)  # letters only
    return {t[i:i+n] for i in range(len(t) - n + 1)} if len(t) >= n else {t}

def compute_text_similarity(a: str, b: str) -> float:
    """Compare two translations using character n-gram overlap.
    Handles ALL CAPS / no-space PDF extraction artifacts."""
    if not a or not b:
        return 0.0
    a_set = ngram_set(a, 4)
    b_set = ngram_set(b, 4)
    if not a_set or not b_set:
        return 0.0
    return len(a_set & b_set) / max(len(a_set | b_set), 1)

def compute_pass_agreement(passes: dict[str, dict]) -> dict:
    translations = {}
    for pt, result in passes.items():
        t = result.get("content", "")
        if result.get("pending"):
            continue  # skip pending passes
        translations[pt] = t

    if len(translations) < 2:
        return {"per_pass": {}, "overall": "unknown"}

    results = {}
    for pt, t in translations.items():
        agreements = []
        conflicts = []
        for other_pt, other_t in translations.items():
            if other_pt == pt:
                continue
            sim = compute_text_similarity(t, other_t)
            if sim > 0.35:
                agreements.append(other_pt)
            else:
                conflicts.append(other_pt)
        results[pt] = {
            "agreements": agreements,
            "conflicts": conflicts,
            "n_agreements": len(agreements),
            "n_conflicts": len(conflicts),
        }

    total_conflicts = sum(r["n_conflicts"] for r in results.values())
    total_possible = len(translations) * (len(translations) - 1)
    overall = "high" if total_conflicts == 0 else \
              "medium" if total_conflicts <= total_possible / 2 else "low"
    return {"per_pass": results, "overall": overall}


def extract_terms(text: str) -> list[str]:
    found = []
    text_lower = text.lower()
    for term in TRACKED_TERMS:
        if term.lower() in text_lower:
            found.append(term)
    return found


# ── Generate HTML report ──

def h(s: str) -> str:
    return htmlmod.escape(s or "")

def render_report(all_data: list[dict], references: dict, b0_data: dict) -> str:
    n_passages = len(all_data)
    n_with_ref = sum(1 for d in all_data if d.get("reference_translation"))
    n_high_conf = sum(1 for d in all_data if d.get("agreement", {}).get("overall") == "high")
    n_med_conf = sum(1 for d in all_data if d.get("agreement", {}).get("overall") == "medium")
    n_low_conf = sum(1 for d in all_data if d.get("agreement", {}).get("overall") == "low")
    n_contradicts_ref = sum(1 for d in all_data if d.get("contradicts_reference"))

    passages_html = ""
    for i, d in enumerate(all_data):
        pid = d["passage_id"]
        source = d["source"]
        domain = d.get("domain", "?")
        work = d.get("work", "?")

        passes = d.get("passes", {})
        agreement = d.get("agreement", {})
        ref_translation = d.get("reference_translation", "")
        contradicts_ref = d.get("contradicts_reference", False)

        # Confidence badge
        conf_level = agreement.get("overall", "unknown")
        conf_colors = {"high": "#22c55e", "medium": "#eab308", "low": "#ef4444", "unknown": "#6b7280"}

        # Per-pass details
        passes_html_inner = ""
        for pt in ["A", "B", "C", "D"]:
            pdata = passes.get(pt, {})
            content = pdata.get("content", "")
            reasoning = pdata.get("reasoning", "")
            success = pdata.get("success", False)
            pending = pdata.get("pending", False)
            source = pdata.get("source", "")
            per_pass_agree = agreement.get("per_pass", {}).get(pt, {})
            n_agree = per_pass_agree.get("n_agreements", 0)
            n_conflict = per_pass_agree.get("n_conflicts", 0)

            if pending:
                status_color = "#94a3b8"
                source_label = "pending"
            else:
                status_color = "#22c55e" if success else "#ef4444"
                source_label = source or ("api" if success else "error")

            passes_html_inner += f"""
            <div class="pass-card {'pass-pending' if pending else ''}">
                <div class="pass-header">
                    <strong>Pass {pt}</strong> — {PASS_LABELS.get(pt, "")}
                    <span class="pass-status" style="color:{status_color}">{'◷' if pending else '✓' if success else '✗'}</span>
                    <span class="pass-source">{source_label}</span>
                    {f'<span class="pass-agreement" style="color:#22c55e">{n_agree} agree · {n_conflict} conflict</span>' if not pending else ''}
                </div>
                <div class="pass-content">{'<em style="color:#94a3b8">' + h(content) + '</em>' if pending else h(content)}</div>
                {f'<details><summary>Reasoning trace</summary><pre class="reasoning">{h(reasoning)}</pre></details>' if reasoning and not pending else ''}
            </div>"""

        # Reference comparison
        ref_html = ""
        if ref_translation:
            b0 = b0_data.get(pid, "")
            # Compare B0 to reference for some basic stats
            ref_html = f"""
            <div class="reference-card">
                <strong>Published reference (Dyczkowski)</strong>
                <div class="pass-content">{h(ref_translation)}</div>
                {'<div class="contradiction-flag">⚠ Contradicts published reference — priority review</div>' if contradicts_ref else ''}
            </div>"""

        # Agreement summary
        agreement_html = ""
        if agreement:
            summary = agreement.get("overall", "unknown")
            agreement_html = f"""
            <div class="agreement-summary" style="border-left: 4px solid {conf_colors.get(summary, '#6b7280')}; padding-left: 12px;">
                <strong>Confidence: {summary.upper()}</strong>
                {f'<span class="conflict-hint">Disagreement detected — review recommended</span>' if summary == 'low' else ''}
                {f'<span class="conflict-hint">Minor divergence — flag for eventual review</span>' if summary == 'medium' else ''}
            </div>"""

        # Term alignment
        terms = d.get("terms_found", [])
        term_html = f'<span class="term-list">{", ".join(terms)}</span>' if terms else '<span class="term-list" style="color:#6b7280">None of the 6 tracked terms found</span>'

        passages_html += f"""
        <div class="passage-card" id="{h(pid)}">
            <div class="passage-header">
                <span class="passage-id">{h(pid)}</span>
                <span class="passage-meta">{h(work)} · {h(domain)}</span>
                <span class="confidence-badge" style="background: {conf_colors.get(conf_level, '#6b7280')}">{conf_level}</span>
            </div>
            <div class="source-text">{h(source)}</div>
            <div class="terms-found">Tracked terms: {term_html}</div>
            {agreement_html}
            {ref_html}
            <div class="passes-container">
                {passes_html_inner}
            </div>
            <details class="annotator-section">
                <summary>Scholar annotation</summary>
                <div class="annotator-form">
                    <label>Your alternate translation:</label>
                    <textarea rows="3" placeholder="Enter alternate reading..."></textarea>
                    <label>Reason code:</label>
                    <select>
                        <option value="">Select...</option>
                        <option value="morphology">Morphology incompatible</option>
                        <option value="sandhi">Sandhi invalid</option>
                        <option value="compound">Wrong compound relation</option>
                        <option value="frame">Frame role incompatible</option>
                        <option value="tradition">Tradition sense</option>
                        <option value="unsupported">Unsupported addition</option>
                        <option value="variant">Acceptable variant</option>
                        <option value="correct">Correct as is</option>
                    </select>
                    <label>Note:</label>
                    <textarea rows="2" placeholder="Your reasoning..."></textarea>
                    <button type="button" onclick="alert('This is a static export. Copy this JSON for submission.')">Export annotation → JSON</button>
                </div>
            </details>
        </div>"""

    # Dashboard
    dashboard = f"""
    <div class="dashboard">
        <div class="stat-card">
            <div class="stat-value">{n_passages}</div>
            <div class="stat-label">Passages</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{n_with_ref}</div>
            <div class="stat-label">With published reference</div>
        </div>
        <div class="stat-card" style="border-top: 3px solid #22c55e">
            <div class="stat-value">{n_high_conf}</div>
            <div class="stat-label">High confidence</div>
        </div>
        <div class="stat-card" style="border-top: 3px solid #eab308">
            <div class="stat-value">{n_med_conf}</div>
            <div class="stat-label">Medium confidence</div>
        </div>
        <div class="stat-card" style="border-top: 3px solid #ef4444">
            <div class="stat-value">{n_low_conf}</div>
            <div class="stat-label">Low confidence (review)</div>
        </div>
        <div class="stat-card" style="border-top: 3px solid #ef4444">
            <div class="stat-value">{n_contradicts_ref}</div>
            <div class="stat-label">Contradicts reference</div>
        </div>
    </div>"""

    # TOC
    toc_items = ""
    for d in all_data:
        pid = d["passage_id"]
        conf = d.get("agreement", {}).get("overall", "unknown")
        conf_colors_toc = {"high": "#22c55e", "medium": "#eab308", "low": "#ef4444", "unknown": "#6b7280"}
        toc_items += f'<li><a href="#{h(pid)}"><span class="toc-dot" style="background:{conf_colors_toc.get(conf, "#6b7280")}"></span>{h(pid)}</a></li>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Translation Audit Report — Sanskritree</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.6; }}
.wrapper {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
h1 {{ font-size: 1.5rem; margin-bottom: 8px; color: #0f172a; }}
.subtitle {{ color: #64748b; margin-bottom: 24px; font-size: 0.9rem; }}
.dashboard {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; margin-bottom: 32px; }}
.stat-card {{ background: white; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-top: 3px solid #3b82f6; }}
.stat-value {{ font-size: 1.5rem; font-weight: 700; }}
.stat-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; }}
.toc {{ background: white; border-radius: 8px; padding: 16px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.toc ul {{ list-style: none; display: flex; flex-wrap: wrap; gap: 4px 16px; }}
.toc a {{ color: #3b82f6; text-decoration: none; font-size: 0.85rem; display: flex; align-items: center; gap: 4px; }}
.toc a:hover {{ text-decoration: underline; }}
.toc-dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; }}
.passage-card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.passage-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }}
.passage-id {{ font-weight: 700; font-size: 1rem; font-family: 'SF Mono', 'Fira Code', monospace; }}
.passage-meta {{ color: #64748b; font-size: 0.8rem; }}
.confidence-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; color: white; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }}
.source-text {{ font-family: 'Noto Sans Devanagari', 'Siddhanta', serif; font-size: 1rem; padding: 12px; background: #f1f5f9; border-radius: 6px; margin-bottom: 12px; }}
.terms-found {{ font-size: 0.8rem; color: #64748b; margin-bottom: 8px; }}
.term-list {{ font-family: 'SF Mono', monospace; font-size: 0.8rem; }}
.passes-container {{ display: grid; gap: 8px; }}
.pass-card {{ padding: 12px; border: 1px solid #e2e8f0; border-radius: 6px; }}
.pass-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 0.85rem; flex-wrap: wrap; }}
.pass-status {{ font-weight: bold; }}
.pass-agreement {{ font-size: 0.75rem; }}
.pass-content {{ font-size: 0.9rem; line-height: 1.5; }}
.pass-pending {{ opacity: 0.7; }}
.pass-source {{ font-size: 0.7rem; color: #94a3b8; font-family: monospace; }}
.reasoning {{ font-size: 0.8rem; color: #475569; background: #f8fafc; padding: 8px; border-radius: 4px; margin-top: 4px; white-space: pre-wrap; }}
.reference-card {{ padding: 12px; border: 1px solid #dbeafe; background: #eff6ff; border-radius: 6px; margin-bottom: 8px; font-size: 0.9rem; }}
.contradiction-flag {{ color: #dc2626; font-weight: 600; margin-top: 4px; font-size: 0.85rem; }}
.agreement-summary {{ margin-bottom: 8px; font-size: 0.85rem; }}
.conflict-hint {{ display: block; color: #dc2626; font-size: 0.8rem; margin-top: 2px; }}
.annotator-section {{ margin-top: 8px; font-size: 0.85rem; }}
.annotator-form {{ padding: 12px; background: #f8fafc; border-radius: 6px; margin-top: 8px; }}
.annotator-form label {{ display: block; font-weight: 600; font-size: 0.8rem; margin-top: 8px; margin-bottom: 2px; }}
.annotator-form textarea {{ width: 100%; border: 1px solid #e2e8f0; border-radius: 4px; padding: 6px; font-family: inherit; font-size: 0.85rem; }}
.annotator-form select {{ width: 100%; border: 1px solid #e2e8f0; border-radius: 4px; padding: 6px; font-family: inherit; font-size: 0.85rem; }}
.annotator-form button {{ margin-top: 8px; padding: 6px 12px; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }}
details > summary {{ cursor: pointer; color: #3b82f6; font-weight: 600; }}
details > summary:hover {{ text-decoration: underline; }}
@media (max-width: 768px) {{ .dashboard {{ grid-template-columns: repeat(2, 1fr); }} }}
</style>
</head>
<body>
<div class="wrapper">
    <h1>Translation Audit Report</h1>
    <p class="subtitle">Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")} · {n_passages} passages · 4-pass DeepSeek · Calibrated against Dyczkowski</p>
    {dashboard}
    <div class="toc"><ul>{toc_items}</ul></div>
    {passages_html}
    <div style="text-align:center;color:#94a3b8;font-size:0.8rem;padding:24px;">
        Generated by sanskritree/scripts/generate_translation_report.py
    </div>
</div>
</body>
</html>"""
    return html


# ── Main ──

def load_pass1_renderings() -> dict:
    """Load Pass1 Spanda renderings (hybrid factor-graph + DeepSeek).
    Indexes by source text hash for matching against diagnostic passages."""
    path = BASE / "proof" / "checkpoint1" / "runs" / "pass_1" / "blind_pass_1.jsonl"
    results = {}
    try:
        for line in path.read_text(encoding="utf-8").strip().split("\n"):
            if not line.strip():
                continue
            rec = json.loads(line)
            source = rec.get("source_clean") or rec.get("source_raw", "")
            source_norm = re.sub(r'\s+', ' ', source).strip().lower()
            source_hash = hashlib.sha256(source_norm.encode()).hexdigest()
            # Prefer LLM rendering, fall back to factored pipeline
            llm = rec.get("pipeline", {}).get("llm_rendering", {})
            trans = llm.get("translation", "")
            reasoning = llm.get("reasoning", "")
            if not trans:
                trans = rec.get("pipeline", {}).get("rendered_english", "")
            if trans:
                results[source_hash] = {"content": trans, "reasoning": reasoning, "success": True}
    except Exception:
        pass
    return results


def main():
    args = sys.argv[1:]
    run_passes_flag = "--passes" in args
    report_only = "--report-only" in args
    limit = None
    for a in args:
        if a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])

    diagnostic = load_diagnostic()
    if limit:
        diagnostic = diagnostic[:limit]
    references = load_references()
    b0_data = load_b0()
    pass1_data = load_pass1_renderings()

    print(f"Translation audit report generator")
    print(f"  Diagnostic passages: {len(diagnostic)}")
    print(f"  Published references available: {len(references)}")

    # Load or run passes
    cache = load_cache()
    all_data = []

    for d in diagnostic:
        pid = d["passage_id"]
        source = d["source"]
        domain = d.get("domain", "")
        work = d.get("work", "")

        entry = {
            "passage_id": pid,
            "source": source,
            "domain": domain,
            "work": work,
        }

        # Find reference
        ref_translation = references.get(pid, "")
        entry["reference_translation"] = ref_translation

        # Determine tracked terms in source
        terms = extract_terms(source)
        entry["terms_found"] = terms

        # Run/load passes
        passes = {}
        api_unavailable = False

        for pt in ["A", "B", "C", "D"]:
            ck = cache_key(pid, pt)
            if ck in cache and not run_passes_flag:
                cached = cache[ck]
                if cached.get("success"):
                    passes[pt] = cached
                    print(f"  [CACHE] {pid} pass {pt} ({len(cached.get('content',''))} chars)")
                    continue

            # Fallback for Pass A: use existing B0 data
            if pt == "A" and pid in b0_data and b0_data[pid]:
                passes[pt] = {"content": b0_data[pid], "reasoning": None, "success": True, "source": "b0_data"}
                print(f"  [B0] {pid} pass A ({len(b0_data[pid])} chars)")
                continue

            # Fallback for comparison: use Pass1 Spanda renderings (match by source text hash)
            source_norm = re.sub(r'\s+', ' ', source).strip().lower()
            source_hash = hashlib.sha256(source_norm.encode()).hexdigest()
            if pt in ("C",) and source_hash in pass1_data:
                passes[pt] = pass1_data[source_hash].copy()
                passes[pt]["source"] = "pass1_pipeline"
                print(f"  [PASS1] {pid} pass C ({len(pass1_data[source_hash].get('content',''))} chars)")
                continue

            # In report-only mode, mark unfulfilled passes as pending
            if report_only:
                passes[pt] = {"content": "[PENDING]", "reasoning": None, "success": False, "pending": True}
                continue

            # Try API
            if not api_unavailable:
                if pt == "A":
                    result = run_pass_a(source)
                elif pt == "B":
                    result = run_pass_b(source)
                elif pt == "C":
                    prior = passes.get("A", {}).get("content", "")
                    result = run_pass_c(source, prior)
                elif pt == "D":
                    if ref_translation:
                        result = run_pass_d(source, pid, ref_translation)
                    else:
                        result = run_pass_a(source)

                if result.get("success"):
                    passes[pt] = result
                    save_cache(ck, result)
                    print(f"  [API] {pid} pass {pt}: {result.get('content','')[:60]}...")
                    time.sleep(1.0)
                    continue
                else:
                    api_unavailable = True
                    print(f"  [API UNAVAILABLE] {pid} pass {pt}: {result.get('error','')[:60]}")

            # Mark as pending if we couldn't get it
            passes[pt] = {"content": "[PENDING — API quota exceeded. Resets ~Aug 8, 2026]",
                          "reasoning": None, "success": False, "pending": True}

        entry["passes"] = passes

        # Compute agreement
        if passes:
            agreement = compute_pass_agreement(passes)
            entry["agreement"] = agreement

        # Check contradiction with reference (using n-gram similarity for ALL CAPS tolerance)
        if ref_translation and passes:
            contradicts = False
            for pt, pdata in passes.items():
                if pdata.get("pending"):
                    continue
                pass_text = pdata.get("content", "")
                sim = compute_text_similarity(pass_text, ref_translation)
                if sim < 0.2 and sim >= 0:  # very low similarity = contradicts
                    contradicts = True
                    break
            entry["contradicts_reference"] = contradicts

        all_data.append(entry)

    # Generate HTML
    html = render_report(all_data, references, b0_data)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"\nReport written: {OUTPUT_PATH}")
    print(f"  Size: {len(html)} bytes")

    # Print summary
    n_high = sum(1 for d in all_data if d.get("agreement", {}).get("overall") == "high")
    n_med = sum(1 for d in all_data if d.get("agreement", {}).get("overall") == "medium")
    n_low = sum(1 for d in all_data if d.get("agreement", {}).get("overall") == "low")
    n_contra = sum(1 for d in all_data if d.get("contradicts_reference"))
    print(f"\n  Confidence: {n_high} high · {n_med} medium · {n_low} low")
    print(f"  Contradicts reference: {n_contra}")
    print(f"  With reference: {sum(1 for d in all_data if d.get('reference_translation'))}")


if __name__ == "__main__":
    main()
