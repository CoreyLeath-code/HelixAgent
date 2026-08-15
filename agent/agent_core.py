""""HelixAgent compatibility facade and honest vector-operation backends."""

from __future__ import annotations

import ctypes
import logging
import math
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

try:
    import numpy as np
except ImportError:  # pragma: no cover - NumPy is a declared runtime dependency.
    np = None

log = logging.getLogger(__name__)

VectorBackend = Literal["auto", "numpy", "cpp"]
VectorInput = Iterable[float]

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


def _coerce_numpy_vectors(left: object, right: object) -> tuple[object, object]:
    """Return validated, one-dimensional, contiguous float64 NumPy buffers."""
    if np is None:
        raise RuntimeError("NumPy is unavailable; use the Python fallback instead")
    try:
        left_array = np.ascontiguousarray(left, dtype=np.float64)
        right_array = np.ascontiguousarray(right, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            "Vectors must be coercible to one-dimensional float64 arrays"
        ) from exc
    if left_array.ndim != 1 or right_array.ndim != 1:
        raise ValueError("Vectors must be one-dimensional")
    if left_array.size == 0 or left_array.size != right_array.size:
        raise ValueError("Vectors must be non-empty and have equal dimensions")
    return left_array, right_array


def _coerce_python_vectors(
    left: VectorInput, right: VectorInput
) -> tuple[list[float], list[float]]:
    """Validate iterable inputs without requiring NumPy."""
    try:
        left_values = [float(value) for value in left]
        right_values = [float(value) for value in right]
    except (TypeError, ValueError) as exc:
        raise TypeError("Vectors must be iterable numeric values") from exc
    if not left_values or len(left_values) != len(right_values):
        raise ValueError("Vectors must be non-empty and have equal dimensions")
    return left_values, right_values


def cosine_similarity_numpy(left: object, right: object) -> float:
    """Return cosine similarity through contiguous float64 NumPy arrays."""
    left_array, right_array = _coerce_numpy_vectors(left, right)
    denominator = np.linalg.norm(left_array) * np.linalg.norm(right_array)
    if denominator == 0.0:
        return 0.0
    return float(np.dot(left_array, right_array) / denominator)


def cosine_similarity_cpp(left: object, right: object) -> float:
    """Return cosine similarity through the opt-in C++ ctypes demonstration."""
    if _lib_vec is None:
        raise RuntimeError(
            "C++ vector backend is unavailable; build agent/cpp/libvector.so first"
        )
    left_array, right_array = _coerce_numpy_vectors(left, right)
    # C++ reads raw double pointers: float32 or non-contiguous buffers would make it
    # read the wrong bytes, so coercion above is a required FFI boundary guarantee.
    pointer_type = ctypes.POINTER(ctypes.c_double)
    return float(
        _lib_vec.cosine_similarity(
            left_array.ctypes.data_as(pointer_type),
            right_array.ctypes.data_as(pointer_type),
            left_array.size,
        )
    )


def cosine_similarity_python(left: VectorInput, right: VectorInput) -> float:
    """Return a scale-stable pure-Python cosine similarity."""
    left_values, right_values = _coerce_python_vectors(left, right)
    left_magnitude = math.hypot(*left_values)
    right_magnitude = math.hypot(*right_values)
    if not left_magnitude or not right_magnitude:
        return 0.0

    normalized_dot = math.fsum(
        (first / left_magnitude) * (second / right_magnitude)
        for first, second in zip(left_values, right_values, strict=True)
    )
    return max(-1.0, min(1.0, normalized_dot))


def cpp_backend_available() -> bool:
    """Return whether the optional C++ shared library loaded successfully."""
    return _lib_vec is not None


def cosine_sim(
    left: object, right: object, *, backend: VectorBackend | None = None
) -> float:
    """Return cosine similarity with an explicit, evidence-based dispatch order.

    NumPy is the default because it is a declared dependency and uses the platform's
    BLAS-backed vector operations. The C++ backend is opt-in via backend="cpp" or
    HELIXAGENT_VECTOR_BACKEND=cpp to demonstrate safe native interop; it is not
    selected as a performance optimization. The pure-Python implementation is used
    only when NumPy is unavailable, preserving a last-resort degradation path.
    """
    selected = backend or os.getenv("HELIXAGENT_VECTOR_BACKEND", "auto").lower()
    if selected not in {"auto", "numpy", "cpp"}:
        raise ValueError("Vector backend must be one of: auto, numpy, cpp")
    if selected == "cpp":
        return cosine_similarity_cpp(left, right)
    if np is None:
        return cosine_similarity_python(left, right)
    return cosine_similarity_numpy(left, right)


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
