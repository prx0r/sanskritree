import fitz
import pytesseract
from PIL import Image, ImageFilter
import subprocess
import os
import sys
import time
from pathlib import Path

PDF_PATH = "/tmp/mbt_extract/Manthanabhairavatantram, Kumarikakhandah -- Mark Dyczkowski/Text and Translation.pdf"
OUTPUT_DIR = Path("/root/sanskritree/sources/mbt_sanskrit")
OUTPUT_TXT = OUTPUT_DIR / "mbt_sanskrit_full.txt"

def find_sanskrit_pages(pdf_path, max_pages=None):
    doc = fitz.open(pdf_path)
    total = len(doc)
    if max_pages:
        total = min(total, max_pages)
    sanskrit_pages = []
    for pn in range(total):
        page = doc[pn]
        fonts = page.get_fonts()
        if any("Khalnayak" in f[3] for f in fonts):
            sanskrit_pages.append(pn + 1)
        pass
    doc.close()
    return sanskrit_pages

def ocr_page(pdf_path, page_num, dpi=300):
    out_path = f"/tmp/mbt_page_{page_num}.png"
    subprocess.run(
        ["pdftoppm", "-f", str(page_num), "-l", str(page_num),
         "-r", str(dpi), "-png", pdf_path, f"/tmp/mbt_page_{page_num}"],
        capture_output=True, timeout=60
    )
    img_path = f"/tmp/mbt_page_{page_num}-{page_num:04d}.png"
    if not os.path.exists(img_path):
        img_path = f"/tmp/mbt_page_{page_num}-{page_num:04d}.png"
        alt = f"/tmp/mbt_page_{page_num}.png"
        if os.path.exists(alt):
            img_path = alt
        else:
            return ""
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img, lang="san")
    os.remove(img_path)
    return text.strip()

def main():
    print("Finding Sanskrit pages...")
    pages = find_sanskrit_pages(PDF_PATH)
    print(f"Found {len(pages)} Sanskrit pages")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_text = []
    total = len(pages)
    for i, pn in enumerate(pages):
        print(f"[{i+1}/{total}] OCR page {pn}...", end=" ", flush=True)
        text = ocr_page(PDF_PATH, pn)
        all_text.append(f"\n{'='*60}\n[Page {pn}]\n{'='*60}\n{text}\n")
        print(f"{len(text)} chars")
        if (i + 1) % 10 == 0:
            with open(OUTPUT_TXT, "w") as f:
                f.write("\n".join(all_text))
    with open(OUTPUT_TXT, "w") as f:
        f.write("\n".join(all_text))
    print(f"\nDone! Saved to {OUTPUT_TXT}")

if __name__ == "__main__":
    main()
