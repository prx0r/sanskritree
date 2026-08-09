"""Batch OCR of Jīvānanda PDFs using Google Vision API.
Usage: screen -dmS batch_ocr bash -c 'export API_KEY="KEY" && python3 -u scripts/batch_ocr.py'
"""
import os, subprocess, base64, json, requests, time, re, sys
from pathlib import Path

API_KEY = os.environ.get("API_KEY", "")
if not API_KEY:
    print("FATAL: API_KEY not set"); sys.exit(1)

# Texts to OCR: (pdf_path, output_path, pages_to_try)
TARGETS = [
    ("corpus/nyaya/classical/tarkasamgraha.pdf", "sources/Tarkasamgraha_sk.txt", 30),
    ("corpus/nyaya/classical/tarkasamgraha_dipika.pdf", "sources/Tarkasamgraha_Dipika_sk.txt", 50) if Path("corpus/nyaya/classical/tarkasamgraha_dipika.pdf").exists() else None,
    ("corpus/nyaya/classical/bhasapariccheda.pdf", "sources/Bhasapariccheda_sk.txt", 40),
]

def ocr_pdf(pdf_path, out_path, max_pages=30):
    if Path(out_path).exists():
        print(f"  SKIP {Path(pdf_path).name} (already exists)")
        return True
    
    print(f"\nOCR: {Path(pdf_path).name} → {Path(out_path).name}")
    os.makedirs("/tmp/batch_ocr", exist_ok=True)
    all_text = []
    
    for page in range(1, max_pages + 1):
        png_base = f"/tmp/batch_ocr/p{int(time.time())}_{page}"
        subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-r", "250", pdf_path, png_base],
                       timeout=30, stderr=subprocess.DEVNULL)
        
        for fname in [f"{png_base}-01.png", f"{png_base}.png"]:
            if os.path.exists(fname):
                with open(fname, "rb") as f:
                    img = base64.b64encode(f.read()).decode()
                try:
                    resp = requests.post(f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}",
                        json={"requests": [{"image": {"content": img}, "features": [{"type": "TEXT_DETECTION"}]}]},
                        timeout=30)
                    result = resp.json()
                    if resp.status_code == 200 and result.get("responses")[0].get("textAnnotations"):
                        text = result["responses"][0]["textAnnotations"][0]["description"]
                        if re.search(r'[\u0900-\u097F]', text):
                            all_text.append(f"--- Page {page} ---\n{text}")
                            print(f"  {Path(pdf_path).name} page {page}: {len(text)} chars ✅", flush=True)
                except Exception as e:
                    print(f"  Page {page}: error {str(e)[:40]}")
                break
        
        time.sleep(0.25)
    
    if all_text:
        with open(out_path, "w") as f:
            f.write("\n\n".join(all_text))
        size = sum(len(t) for t in all_text)
        print(f"  ✅ Saved {size:,} chars to {out_path}", flush=True)
        return True
    else:
        print(f"  ❌ No Sanskrit text found in {Path(pdf_path).name}")
        return False

for target in [t for t in TARGETS if t]:
    pdf, out, pages = target
    if Path(pdf).exists():
        ocr_pdf(pdf, out, pages)

print("\n=== Batch OCR complete ===")
