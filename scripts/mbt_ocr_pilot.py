"""OCR pilot: first chunk of MBT Chapter 1 Sanskrit pages via Google Vision API."""
from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

import fitz
import requests

VISION_KEY = os.environ.get("VISION_API_KEY", "AIzaSyA7-ZK5BGBxDwGCGx1Wiro0fB7NfX68KIc")
VISION_URL = f"https://vision.googleapis.com/v1/images:annotate?key={VISION_KEY}"

BASE = Path(__file__).parents[1]
SOURCES = BASE / "sources"
OUTPUT = BASE / "data" / "ocr"
OUTPUT.mkdir(parents=True, exist_ok=True)

MBT_FILE = list(SOURCES.glob("Manthānabhairavatantram _*"))[0]


def ocr_page(pdf_path: str, page_num: int, dpi: int = 300) -> tuple[int, str, float]:
    doc = fitz.open(pdf_path)
    page = doc[page_num - 1]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes("png")
    doc.close()

    img_b64 = base64.b64encode(img_bytes).decode()
    payload = {
        "requests": [{
            "image": {"content": img_b64},
            "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
            "imageContext": {"languageHints": ["sa", "hi"]},
        }]
    }

    t0 = time.time()
    r = requests.post(VISION_URL, json=payload, timeout=120)
    elapsed = time.time() - t0

    if r.status_code != 200:
        return page_num, f"HTTP {r.status_code}: {r.text[:200]}", elapsed

    resp = r.json()
    api_err = resp.get("responses", [{}])[0].get("error")
    if api_err:
        return page_num, f"API error: {api_err}", elapsed

    text = resp["responses"][0].get("textAnnotations", [{}])[0].get("description", "")
    return page_num, text, elapsed


def main():
    doc = fitz.open(str(MBT_FILE))
    khalnayak_pages = []
    for pn in range(len(doc)):
        fonts = doc[pn].get_fonts()
        if any("Khalnayak" in f[3] for f in fonts):
            khalnayak_pages.append(pn + 1)
    doc.close()

    # Pilot: first ~10 Sanskrit pages (Chapter 1 opening)
    pilot_pages = khalnayak_pages[:10]
    print(f"Pilot OCR: {len(pilot_pages)} pages")
    print(f"Page numbers: {pilot_pages}")

    results = {}
    total_cost_est = 0
    for i, pn in enumerate(pilot_pages):
        print(f"\n[{i+1}/{len(pilot_pages)}] OCR page {pn}...", end=" ", flush=True)
        page_num, text, sec = ocr_page(str(MBT_FILE), pn)
        print(f"({sec:.1f}s, {len(text)} chars)")
        if text.startswith("HTTP") or text.startswith("API error"):
            print(f"  ERROR: {text[:100]}")
        else:
            print(f"  First 80 chars: {text[:80].replace(chr(10), ' ')}")
            results[page_num] = text

        # Save incrementally
        out = OUTPUT / "mbt_ocr_pilot.json"
        out.write_text(json.dumps({
            "source": MBT_FILE.name,
            "pages_processed": i + 1,
            "pilot_page_range": pilot_pages,
            "results": results,
            "page_order": pilot_pages,
        }, indent=2, ensure_ascii=False))

    print(f"\n\n=== Pilot complete ===")
    total_chars = sum(len(t) for t in results.values())
    print(f"Pages: {len(results)} | Total chars: {total_chars}")
    print(f"Saved to: {OUTPUT / 'mbt_ocr_pilot.json'}")

    # Print all text
    print(f"\n{'='*60}")
    print("FULL OCR TEXT")
    print(f"{'='*60}")
    for pn in pilot_pages:
        if pn in results:
            print(f"\n--- Page {pn} ---")
            print(results[pn])


if __name__ == "__main__":
    main()
