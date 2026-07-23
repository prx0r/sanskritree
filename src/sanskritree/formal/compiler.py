from __future__ import annotations
import json
import re
import uuid
from ..semantics.schema import SemanticFrame

COMPILER_VERSION = "v2.0.0a1"
_SAFE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _identifier(label: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_]", "_", label).strip("_") or "Entity"
    if value[0].isdigit():
        value = "E_" + value
    return value


def compile_frame(frame: SemanticFrame) -> tuple[str, str, list[str]]:
    """Compile only registered IR patterns; no text or LLM-supplied Lean is accepted."""
    subject, obj = _identifier(frame.subject.label), _identifier(frame.object.label)
    if frame.relation == "IDENTITY":
        proposition, template = f"{subject} = {obj}", "identity.v1"
    elif frame.relation == "QUALIFICATION":
        proposition, template = f'Sanskritree.Relation "QUALIFICATION" {subject} {obj}', "qualification.v1"
    elif frame.relation in {"PRESCRIPTION", "PROHIBITION"}:
        proposition, template = f'Sanskritree.Relation "{frame.relation}" {subject} {obj}', "modality.v1"
    else:
        proposition, template = f'Sanskritree.Relation "{frame.relation}" {subject} {obj}', "binary_relation.v1"
    assumptions = ["InterpretationContext", f"textual frame {frame.frame_id}"]
    code = "import Sanskritree.Semantics.Relation\n\n" + f"-- Generated deterministically from {frame.frame_id}; formal_role: textual_axiom\n" + f"axiom frame_{_identifier(frame.frame_id)} {{α : Type}} ({subject} {obj} : α) : {proposition}\n"
    return code, template, assumptions


def persist_formalization(conn, frame: SemanticFrame) -> str:
    code, template, assumptions = compile_frame(frame)
    if "sorry" in code or "admit" in code or "unsafe" in code:
        raise ValueError("unsafe Lean is forbidden")
    formalization_id = str(uuid.uuid4())
    conn.execute("INSERT INTO formalizations VALUES (?,?,?,?,?,?,?,?)", (formalization_id, frame.frame_id, code, template, "textual_axiom", "uncompiled", json.dumps(assumptions), COMPILER_VERSION))
    conn.commit()
    return formalization_id
