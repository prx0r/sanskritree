import subprocess, sys, os, time
from pathlib import Path
import pytesseract
from PIL import Image

PDF = "/tmp/mbt_extract/Manthanabhairavatantram, Kumarikakhandah -- Mark Dyczkowski/Text and Translation.pdf"
OUT = Path("/root/sanskritree/sources/mbt_sanskrit/mbt_sanskrit_full.txt")

def get_sanskrit_pages():
    import fitz
    doc = fitz.open(PDF)
    pages = [pn+1 for pn in range(len(doc))
             if any("Khalnayak" in f[3] for f in doc[pn].get_fonts())]
    doc.close()
    return pages

pages = get_sanskrit_pages()
print(f"Processing {len(pages)} Sanskrit pages")

start = time.time()
out_lines = []
for i, pn in enumerate(pages):
    t0 = time.time()
    prefix = f"/tmp/mbt_{pn}"
    subprocess.run(["pdftoppm", "-f", str(pn), "-l", str(pn),
                    "-r", "200", "-png", PDF, prefix],
                   capture_output=True, timeout=120)
    png = f"{prefix}-{pn:04d}.png"
    img = Image.open(png)
    text = pytesseract.image_to_string(img, lang="san")
    img.close()
    os.remove(png)
    out_lines.append(f"\n{'='*60}\n[Page {pn}]\n{'='*60}\n{text.strip()}\n")
    sec = time.time() - t0
    rate = (i+1)/(time.time()-start)
    rem = (len(pages)-i-1)/rate
    print(f"[{i+1}/{len(pages)}] p{pn} {len(text)}c {sec:.1f}s | "
          f"{rate:.1f}pg/min | {rem/60:.0f}min left", flush=True)
    if (i+1)%25 == 0:
        OUT.write_text("".join(out_lines))

OUT.write_text("".join(out_lines))
print(f"\nDone in {(time.time()-start)/60:.1f} min → {OUT}")
