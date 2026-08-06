"""Smoke test for the deterministic benchmark."""

import asyncio

from scripts.load_test import run


def test_load_smoke_is_reproducible():
    first = asyncio.run(run(100, 0.6, 2, 0, 42))
    second = asyncio.run(run(100, 0.6, 2, 0, 42))
    assert first["hit_rate"] == second["hit_rate"]
    assert first["hits"] > 0
    assert first["estimated_tokens_saved"] > 0
