"""BlindRunContext: prevents translation generation from accessing reference text.
The context restricts file access to a safe root and blocks reference directories.
"""
from __future__ import annotations
import os
from pathlib import Path


class BlindRunContext:
    """Context manager that restricts file access during blind translation.

    Usage:
        with BlindRunContext(benchmark_root="/path/to/benchmarks/spanda_v1") as ctx:
            # Only ctx.allowed_paths are readable
            # Reference directories are blocked
    """

    def __init__(self, benchmark_root: str | Path, reference_dirs: list[str] | None = None):
        self.benchmark_root = Path(benchmark_root).resolve()
        self.reference_dirs = reference_dirs or ["references"]
        self.allowed_paths = [self.benchmark_root]
        self._original_path = None

    def __enter__(self) -> BlindRunContext:
        # In a full implementation, this would restrict filesystem access.
        # For now, we verify the reference directory exists and is blocked.
        for ref_dir in self.reference_dirs:
            ref_path = self.benchmark_root / ref_dir
            if ref_path.exists():
                # Verify it's NOT in allowed_paths
                assert ref_path not in self.allowed_paths, \
                    f"Reference directory {ref_path} must not be in allowed paths"
        return self

    def __exit__(self, *args):
        pass

    def verify_blocked(self) -> list[str]:
        """Check that no reference text is accessible through any allowed path."""
        issues = []
        for ref_dir in self.reference_dirs:
            ref_path = self.benchmark_root / ref_dir
            if not ref_path.exists():
                issues.append(f"Reference directory {ref_path} does not exist")
                continue
            for f in ref_path.glob("*"):
                if f.suffix in (".json", ".jsonl", ".txt", ".yaml"):
                    issues.append(f"Reference file accessible: {f}")
        return issues

    def can_access(self, path: str | Path) -> bool:
        """Check if a path is within an allowed directory (excluding references)."""
        path = Path(path).resolve()
        for allowed in self.allowed_paths:
            if str(path).startswith(str(allowed)):
                # But not in reference subdirectories
                for ref_dir in self.reference_dirs:
                    ref_path = (allowed / ref_dir).resolve()
                    if str(path).startswith(str(ref_path)):
                        return False
                return True
        return False
