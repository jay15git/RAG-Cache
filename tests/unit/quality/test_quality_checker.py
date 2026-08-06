import pytest

from app.quality.quality_checker import QualityChecker
from app.quality.background_checker import BackgroundQualityChecker, QualityReview


def test_quality_checker_detects_overlap_and_false_hits():
    checker = QualityChecker(min_overlap=0.5)
    assert checker.compare("Paris is the capital of France", "The capital of France is Paris").false_hit is False
    assert checker.compare("Paris", "Quantum mechanics and particle physics").false_hit is True


@pytest.mark.asyncio
async def test_background_checker_processes_outside_request_path():
    checker = BackgroundQualityChecker()
    await checker.submit(QualityReview("Paris", "Quantum physics", "acme"))
    result = await checker.process_one()
    assert result is not None and result.false_hit is True
    assert checker.pending == 0
