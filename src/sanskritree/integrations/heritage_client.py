"""Hardened Heritage API client with explicit failure classification and long timeout."""
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import Any
import time


class HeritageFailure(str, Enum):
    TRANSPORT_FAILURE = "TRANSPORT_FAILURE"
    TIMEOUT = "TIMEOUT"
    EMPTY_RESPONSE = "EMPTY_RESPONSE"
    PARSE_FAILURE = "PARSE_FAILURE"
    NO_ANALYSIS = "NO_ANALYSIS"
    PARTIAL_ANALYSIS = "PARTIAL_ANALYSIS"
    SUCCESS = "SUCCESS"


@dataclass
class HeritageResult:
    status: HeritageFailure
    words: list[str] = field(default_factory=list)
    attempts: list[dict] = field(default_factory=list)
    time_s: float = 0.0


class HeritageClient:
    """Wrapper around HeritagePlatform with explicit failure handling."""

    def __init__(self, timeout: int = 120, max_attempts: int = 3):
        self.timeout = timeout
        self.max_attempts = max_attempts

    def analyze(self, devanagari_text: str, iast_text: str = "") -> HeritageResult:
        from heritage.heritage import HeritagePlatform, SolutionAnalysis

        attempts = []
        t0 = time.time()

        for attempt in range(self.max_attempts):
            try:
                platform = HeritagePlatform(method="web", request_timeout=self.timeout)
                analysis = platform.get_analysis(devanagari_text, sentence=True, structured=True)
                elapsed = time.time() - t0

                if analysis is None:
                    attempts.append({"attempt": attempt, "status": "EMPTY_RESPONSE", "time_s": round(elapsed, 1)})
                    continue

                found_words = False
                for sol_id in sorted(analysis.keys()):
                    sol = analysis[sol_id]
                    if isinstance(sol, SolutionAnalysis) and sol.words:
                        words = [str(w.text) for w in sol.words]
                        attempts.append({"attempt": attempt, "status": "SUCCESS", "n_words": len(words), "time_s": round(elapsed, 1)})
                        return HeritageResult(
                            status=HeritageFailure.SUCCESS,
                            words=words,
                            attempts=attempts,
                            time_s=round(elapsed, 1),
                        )

                if not found_words:
                    attempts.append({"attempt": attempt, "status": "NO_ANALYSIS", "time_s": round(elapsed, 1)})

            except Exception as e:
                err_str = str(e)
                elapsed = time.time() - t0
                if "timeout" in err_str.lower() or "timed out" in err_str.lower():
                    status = "TIMEOUT"
                else:
                    status = "TRANSPORT_FAILURE"
                attempts.append({"attempt": attempt, "status": status, "error": err_str[:100], "time_s": round(elapsed, 1)})

            if attempt < self.max_attempts - 1:
                time.sleep(2 ** attempt)

        return HeritageResult(
            status=HeritageFailure.TIMEOUT,
            attempts=attempts,
            time_s=round(time.time() - t0, 1),
        )

    def analyze_with_fallback(self, iast_text: str) -> HeritageResult:
        """IAST → Devanagari → Heritage analysis with fallback."""
        from vidyut.lipi import transliterate, Scheme
        try:
            deva = transliterate(iast_text, Scheme.Iast, Scheme.Devanagari)
        except Exception as e:
            return HeritageResult(status=HeritageFailure.PARSE_FAILURE, attempts=[{"error": f"IAST→Deva failed: {str(e)[:80]}"}])

        result = self.analyze(deva, iast_text)
        return result
