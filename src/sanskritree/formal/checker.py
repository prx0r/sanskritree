"""Lean type-checking for deterministic V2 declarations."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def _lake() -> str | None:
    return shutil.which("lake") or str(Path.home() / ".elan/bin/lake") if (Path.home() / ".elan/bin/lake").exists() else None


def typecheck(code: str, project_root: str | Path) -> tuple[bool, str]:
    """Check generated code without proving its textual axiom."""
    if any(term in code for term in ("sorry", "admit", "unsafe")):
        return False, "forbidden placeholder or unsafe declaration"
    lake = _lake()
    if lake is None:
        return False, "lake executable unavailable"
    with tempfile.NamedTemporaryFile("w", suffix=".lean", dir=project_root, encoding="utf-8", delete=False) as handle:
        handle.write(code)
        path = handle.name
    try:
        result = subprocess.run([lake, "env", "lean", path], cwd=project_root, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return False, "Lean type-check timeout"
    finally:
        Path(path).unlink(missing_ok=True)


def check_persisted(conn, formalization_id: str, project_root: str | Path) -> tuple[bool, str]:
    row = conn.execute("SELECT lean_code FROM formalizations WHERE formalization_id=?", (formalization_id,)).fetchone()
    if row is None:
        raise KeyError(formalization_id)
    ok, output = typecheck(row[0], project_root)
    conn.execute("UPDATE formalizations SET lean_status=? WHERE formalization_id=?", ("typechecked" if ok else "rejected", formalization_id))
    conn.commit()
    return ok, output
