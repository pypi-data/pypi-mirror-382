"""Common pytest fixtures for PyBenchX tests."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pybench import bench_model as bench_mod  # noqa: E402


@pytest.fixture(autouse=True)
def _isolate_global_registry():
    """Isolate global bench registry per test; keep DEFAULT_BENCH."""
    saved_benches = list(bench_mod._ALL_BENCHES)
    saved_default_cases = list(bench_mod.DEFAULT_BENCH._cases)

    bench_mod._ALL_BENCHES.clear()
    bench_mod._ALL_BENCHES.append(bench_mod.DEFAULT_BENCH)
    bench_mod.DEFAULT_BENCH._cases.clear()
    try:
        yield
    finally:
        bench_mod._ALL_BENCHES.clear()
        bench_mod._ALL_BENCHES.extend(saved_benches)
        bench_mod.DEFAULT_BENCH._cases.clear()
        bench_mod.DEFAULT_BENCH._cases.extend(saved_default_cases)
