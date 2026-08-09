"""OCR Tarkasaṃgraha Khemraj edition with Google Vision API."""
import os, subprocess, base64, json, requests, time, re, sys

API_KEY = "AIzaSyA7-ZK5BGBxDwGCGx1Wiro0fB7NfX68KIc"
os.makedirs("/tmp/ts_ocr_v2", exist_ok=True)
all_text = []

for page in range(1, 11):
    png = f"/tmp/ts_ocr_v2/p{page}"
    subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-r", "250",
                    "/tmp/khemraj.pdf", png], timeout=30, stderr=subprocess.DEVNULL)
    for fname in [f"{png}-01.png", f"{png}.png"]:
        if os.path.exists(fname):
            with open(fname, "rb") as f:
                img = base64.b64encode(f.read()).decode()
            try:
                resp = requests.post(f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}",
                    json={"requests": [{"image": {"content": img}, "features": [{"type": "TEXT_DETECTION"}]}]},
                    timeout=30)
                result = resp.json()
                if resp.status_code == 200 and result.get("responses")[0].get("textAnnotations"):
                    t = result["responses"][0]["textAnnotations"][0]["description"]
                    if re.search(r'[\u0900-\u097F]', t):
                        all_text.append(f"--- Page {page} ---\n{t}")
                        sys.stdout.write(f"Page {page}: {len(t)} chars\n")
                        sys.stdout.flush()
            except Exception as e:
                sys.stdout.write(f"Page {page}: error {str(e)[:40]}\n")
                sys.stdout.flush()
            break
    time.sleep(0.3)

if all_text:
    out = "/root/projects/sanskritree/sources/Tarkasamgraha_Khemraj_Vision.txt"
    with open(out, "w") as f:
        f.write("\n\n".join(all_text))
    total = sum(len(t) for t in all_text)
    sys.stdout.write(f"\n✅ Done: {total:,} chars from {len(all_text)} pages → {out}\n")
else:
    sys.stdout.write("No Sanskrit text found\n")
