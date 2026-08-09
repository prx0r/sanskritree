#!/usr/bin/env python3
"""Freeze the corpus substrate: sha256 of every source e-text we hold.

The reference map's Phase-1 deliverable: source hashes frozen, so every
passage is traceable to an immutable snapshot. Prints the hash table.
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# id → relative path (the works in our corpus, with their e-texts)
WORKS = {
    # the bundle
    "kaulajnananirnaya": "sources/muktabodha-lib/kaulajJAnanirNaya-M00027-IAST.txt",
    "akulavira": "sources/muktabodha-lib/akulavIratantra-M00003-IAST.txt",
    "jnanakarika": "sources/muktabodha-lib/jJAnakArikA-M00024-IAST.txt",
    "kulananda": "sources/muktabodha-lib/kulAnanda-M00513-IAST.txt",
    # the kula-manuals
    "kaularahasya": "sources/muktabodha-lib/kaularahasya-M00326-IAST.txt",
    "kulapradipa": "sources/muktabodha-lib/kulapradIpa-M00068-IAST.txt",
    "kulalashastra": "sources/muktabodha-lib/kulAlazAstra-M00274-IAST.txt",
    "kaularcanadipika": "sources/muktabodha-lib/kaulArcanadIpikA zrIjJAnatantra-M00633-IAST.txt",
    "kuladipika": "sources/muktabodha-lib/kuladIpikA-M0230-IAST.txt",
    "nityakaulatantra": "sources/muktabodha-lib/nityAkaulatantra-M00316-IAST.txt",
    # the Kubjikā
    "kubjikamata": "sources/gretil2/raw_kubjikamata.txt",
    "kubjikatantra": "sources/muktabodha-lib/kubjikAtantra-M00030-IAST.txt",
    # the Krama
    "mahanayaprakasha": "sources/muktabodha-lib/mahAnayaprakAza-M00033-IAST.txt",
    "maharthamanjari": "sources/gretil2/raw_maharthamanjari.itx",
    # the Trika / Spanda / Pratyabhijñā
    "tantraloka": "sources/gretil_tantraloka.txt",
    "tantrasara": "sources/gretil_tantrasara.txt",
    "spandakarika": "sources/gretil2/raw_spandakarika.txt" if Path("sources/gretil2/raw_spandakarika.txt").exists() else "SPANDAKARIKA_TRANSLATION_V1.md",
    "sivasutra": "sources/Aphorisms oF Siva -- Dyczkowski, Mark S_ G_ -- 2011 -- fea2150a50095642a616be780cfc4d29 -- Anna's Archive.pdf",
    "ajadapramatrsiddhi": "sources/muktabodha-lib/ajaDapramAtRsiddhiH-M00658-IAST.txt",
    # the Nyāya
    "tarkasamgraha": "sources/gretil_tarkasamgraha.txt",
    "nyayasutra": "sources/gretil_nyayasutra.txt",
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

print("id|path|sha256")
for wid, rel in WORKS.items():
    p = ROOT / rel
    if p.exists():
        print(f"{wid}|{rel}|{sha256(p)}")
    else:
        print(f"{wid}|{rel}|MISSING")
