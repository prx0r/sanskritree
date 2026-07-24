import pytesseract
from PIL import Image
import subprocess
import os
import sys
from pathlib import Path
from multiprocessing import Pool, cpu_count
import time

PDF_PATH = "/tmp/mbt_extract/Manthanabhairavatantram, Kumarikakhandah -- Mark Dyczkowski/Text and Translation.pdf"
OUTPUT_DIR = Path("/root/sanskritree/sources/mbt_sanskrit")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def find_sanskrit_pages():
    import fitz
    doc = fitz.open(PDF_PATH)
    pages = []
    for pn in range(len(doc)):
        page = doc[pn]
        fonts = page.get_fonts()
        if any("Khalnayak" in f[3] for f in fonts):
            pages.append(pn + 1)
        page.clean_contents()
    doc.close()
    return pages

def ocr_single_page(page_num):
    out_path = f"/tmp/mbt_p{page_num}"
    subprocess.run(
        ["pdftoppm", "-f", str(page_num), "-l", str(page_num),
         "-r", "200", "-png", PDF_PATH, out_path],
        capture_output=True, timeout=120
    )
    img_path = f"{out_path}-{page_num:04d}.png"
    if not os.path.exists(img_path):
        img_path = f"{out_path}.png"
    if not os.path.exists(img_path):
        return page_num, ""
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img, lang="san")
    img.close()
    os.remove(img_path)
    return page_num, text.strip()

def main():
    print("Finding Sanskrit pages...")
    pages = find_sanskrit_pages()
    print(f"Found {len(pages)} pages")

    n_workers = min(cpu_count(), 8)
    print(f"Using {n_workers} workers")

    start = time.time()
    results = []
    with Pool(n_workers) as pool:
        for i, (pn, text) in enumerate(pool.imap_unordered(ocr_single_page, pages)):
            results.append((pn, text))
            elapsed = time.time() - start
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            remaining = (len(pages) - i - 1) / rate if rate > 0 else 0
            print(f"[{i+1}/{len(pages)}] Page {pn}: {len(text)} chars | "
                  f"{rate:.1f} pg/min | ETA: {remaining/60:.0f}min", flush=True)
            if (i + 1) % 20 == 0:
                results.sort()
                out = "\n".join(
                    f"\n{'='*60}\n[Page {pn}]\n{'='*60}\n{t}\n"
                    for pn, t in results
                )
                (OUTPUT_DIR / "mbt_sanskrit_partial.txt").write_text(out)

    results.sort()
    out = "\n".join(
        f"\n{'='*60}\n[Page {pn}]\n{'='*60}\n{t}\n"
        for pn, t in results
    )
    (OUTPUT_DIR / "mbt_sanskrit_full.txt").write_text(out)
    elapsed = time.time() - start
    print(f"\nDone! {len(pages)} pages in {elapsed/60:.1f} min")
    print(f"Saved to {OUTPUT_DIR / 'mbt_sanskrit_full.txt'}")

if __name__ == "__main__":
    main()
