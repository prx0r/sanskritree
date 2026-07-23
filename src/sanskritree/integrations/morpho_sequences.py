"""Read-only candidate lookup for the audited Vidyut-verified morphology data."""
from __future__ import annotations
from pathlib import Path
from ..philology.analysis_lattice import Analysis


def lookup(surface_slp1: str, dataset_dir: str | Path, limit: int = 8) -> list[Analysis]:
    """Return observed analyses without converting the corpus or selecting a winner."""
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("pyarrow is required for Parquet morphology lookup") from exc
    paths = sorted(Path(dataset_dir).glob("*.parquet"))
    if not paths:
        raise FileNotFoundError(f"no Parquet shards in {dataset_dir}")
    results = []
    columns = ["id", "tokens", "lemmas", "pos_tags", "vibhakti", "vacana", "purusha", "prayoga", "linga", "verification"]
    for path in paths:
        for batch in pq.ParquetFile(path).iter_batches(columns=columns, batch_size=4096):
            for row in batch.to_pylist():
                for index, token in enumerate(row["tokens"]):
                    if token != surface_slp1:
                        continue
                    features = {key: row[key][index] for key in ("pos_tags", "vibhakti", "vacana", "purusha", "prayoga", "linga")}
                    results.append(Analysis("dcs_vidyut_verified", row["lemmas"][index], features, None, {"dataset_id": "CodeIsAbstract/sanskrit-morpho-sequences", "revision": "5ec125edf915b1c7edfebd7c048e27a17f2260c3", "source_sentence_id": row["id"], "verification": row["verification"]}))
                    if len(results) >= limit:
                        return results
    return results
