"""HelixAgent compatibility facade and optional native vector integration."""

from __future__ import annotations

import ctypes
import logging
import math
from pathlib import Path

log = logging.getLogger(__name__)

_lib_vec = None
_LIB_PATH = Path(__file__).parent / "cpp" / "libvector.so"
try:
    if _LIB_PATH.exists():
        _lib_vec = ctypes.cdll.LoadLibrary(str(_LIB_PATH))
        _lib_vec.cosine_similarity.restype = ctypes.c_double
        _lib_vec.cosine_similarity.argtypes = (
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
        )
except OSError as exc:
    log.warning("Native vector library unavailable: %s", exc)


def cosine_sim(left: list[float], right: list[float]) -> float:
    """Return cosine similarity using the native library when available."""
    if not left or len(left) != len(right):
        raise ValueError("Vectors must be non-empty and have equal dimensions")
    if _lib_vec is not None:
        array_type = ctypes.c_double * len(left)
        return float(_lib_vec.cosine_similarity(array_type(*left), array_type(*right), len(left)))
    dot = sum(a * b for a, b in zip(left, right))
    magnitude = math.sqrt(sum(value * value for value in left)) * math.sqrt(
        sum(value * value for value in right)
    )
    return dot / magnitude if magnitude else 0.0


class AgenticAssistant:
    """Backward-compatible synchronous interface over the durable autonomous runtime."""

    def __init__(self, runtime=None) -> None:
        if runtime is None:
            from agent.autonomy.runtime import AutonomousRuntime

            runtime = AutonomousRuntime()
        self.runtime = runtime

    def run(self, prompt: str) -> str:
        run = self.runtime.submit(prompt)
        completed = self.runtime.run(run.id)
        if completed.final_output:
            return completed.final_output
        if completed.error:
            raise RuntimeError(completed.error)
        return f"Run {completed.id} paused with status {completed.status.value}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(AgenticAssistant().run("Compare vectors and summarize the result"))
