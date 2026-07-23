"""Minimal lossless TEI intake for Sanskrit Library/SARIT-style editions."""
from __future__ import annotations
import hashlib
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

TEI = "{http://www.tei-c.org/ns/1.0}"

@dataclass(frozen=True)
class TeiUnit:
    xml_id: str
    kind: str
    text: str
    path: str

@dataclass(frozen=True)
class TeiDocument:
    raw_hash: str
    title: str | None
    units: list[TeiUnit]

def read_tei(path: str | Path) -> TeiDocument:
    raw = Path(path).read_bytes()
    root = ET.fromstring(raw)
    title = root.findtext(f".//{TEI}title") or root.findtext(".//title")
    units = []
    sequence = 0
    for element in root.iter():
        local = element.tag.rsplit("}", 1)[-1]
        if local not in {"ab", "l", "p"}:
            continue
        text = " ".join("".join(element.itertext()).split())
        if not text:
            continue
        xml_id = element.attrib.get("{http://www.w3.org/XML/1998/namespace}id", f"tei.{sequence}")
        units.append(TeiUnit(xml_id, local, text, f"/{local}[{sequence}]"))
        sequence += 1
    return TeiDocument(hashlib.sha256(raw).hexdigest(), title, units)
