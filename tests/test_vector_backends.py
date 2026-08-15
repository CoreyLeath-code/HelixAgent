""""Unit contracts for the honest cosine-similarity backends."""

from __future__ import annotations

import math

import numpy as np
import pytest

from agent import agent_core

KNOWN_CASES = [
    ([1.0, 2.0], [1.0, 2.0], 1.0),
    ([1.0, 0.0], [0.0, 1.0], 0.0),
    ([0.0, 0.0], [1.0, -1.0], 0.0),
    ([1.0, 2.0], [-1.0, -2.0], -1.0),
]


class RecordingVectorLibrary:
    """Small ctypes-compatible stand-in that observes the raw FFI buffers."""

    def cosine_similarity(self, left_pointer, right_pointer, length) -> float:
        left = np.ctypeslib.as_array(left_pointer, shape=(int(length),))
        right = np.ctypeslib.as_array(right_pointer, shape=(int(length),))
        left_norm = np.linalg.norm(left)
        right_norm = np.linalg.norm(right)
        if left_norm == 0.0 or right_norm == 0.0:
            return 0.0
        return float(np.dot(left, right) / (left_norm * right_norm))


@pytest.fixture
def fake_cpp_backend(monkeypatch) -> RecordingVectorLibrary:
    library = RecordingVectorLibrary()
    monkeypatch.setattr(agent_core, "_lib_vec", library)
    return library


@pytest.mark.parametrize(("left", "right", "expected"), KNOWN_CASES)
@pytest.mark.parametrize(
    "backend",
    [agent_core.cosine_similarity_numpy, agent_core.cosine_similarity_python],
)
def test_numpy_and_python_backends_cover_known_cases(
    backend, left, right, expected
) -> None:
    assert backend(left, right) == pytest.approx(expected, abs=1e-12)


@pytest.mark.parametrize(("left", "right", "expected"), KNOWN_CASES)
def test_cpp_backend_covers_known_cases(
    fake_cpp_backend, left, right, expected
) -> None:
    assert agent_core.cosine_similarity_cpp(left, right) == pytest.approx(
        expected, abs=1e-12
    )


@pytest.mark.skipif(
    not agent_core.cpp_backend_available(),
    reason="optional C++ shared library is not available on this runner",
)
@pytest.mark.parametrize(("left", "right", "expected"), KNOWN_CASES)
def test_loaded_cpp_backend_covers_known_cases(left, right, expected) -> None:
    assert agent_core.cosine_similarity_cpp(left, right) == pytest.approx(
        expected, abs=1e-12
    )


def test_available_backends_agree_on_seeded_vectors() -> None:
    generator = np.random.default_rng(8_675_309)
    left = generator.normal(size=257)
    right = generator.normal(size=257)
    results = [
        agent_core.cosine_similarity_numpy(left, right),
        agent_core.cosine_similarity_python(left, right),
    ]
    if agent_core.cpp_backend_available():
        results.append(agent_core.cosine_similarity_cpp(left, right))

    for result in results[1:]:
        assert math.isclose(results[0], result, rel_tol=1e-9, abs_tol=1e-9)


def test_cpp_coerces_float32_and_non_contiguous_arrays(fake_cpp_backend) -> None:
    left = np.arange(12, dtype=np.float32)[::2]
    right = np.arange(12, dtype=np.float32)[1::2]
    assert not left.flags.c_contiguous
    assert left.dtype == np.float32

    expected = agent_core.cosine_similarity_numpy(left, right)
    actual = agent_core.cosine_similarity_cpp(left, right)

    assert actual == pytest.approx(expected, abs=1e-12)


def test_cpp_boundary_rejects_mismatched_and_uncoercible_inputs(
    fake_cpp_backend,
) -> None:
    with pytest.raises(ValueError, match="equal dimensions"):
        agent_core.cosine_similarity_cpp([1.0], [1.0, 2.0])
    with pytest.raises(TypeError, match="coercible"):
        agent_core.cosine_similarity_cpp(["not-a-number"], [1.0])


def test_compatibility_facade_defaults_to_numpy(monkeypatch) -> None:
    monkeypatch.delenv("HELIXAGENT_VECTOR_BACKEND", raising=False)

    assert agent_core.cosine_sim([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_compatibility_facade_selects_cpp_only_when_opted_in(
    monkeypatch, fake_cpp_backend
) -> None:
    monkeypatch.setenv("HELIXAGENT_VECTOR_BACKEND", "cpp")

    assert agent_core.cosine_sim([1.0, 2.0], [1.0, 2.0]) == pytest.approx(1.0)


def test_compatibility_facade_uses_python_only_without_numpy(monkeypatch) -> None:
    monkeypatch.setattr(agent_core, "np", None)

    assert agent_core.cosine_sim([1.0, 2.0], [-1.0, -2.0]) == pytest.approx(-1.0)
