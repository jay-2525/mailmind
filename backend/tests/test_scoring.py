from datetime import datetime, timedelta, timezone
from app.scoring.waste_scorer import StorageWasteScorer


def test_storage_waste_scorer_low_waste():
    scorer = StorageWasteScorer()
    now = datetime.now(timezone.utc)
    # An email received today, small size, not promotional, with tasks
    result = scorer.compute_waste_score(
        size_bytes=10240,  # 10 KB
        is_promotional=False,
        redundancy_score=0.0,
        received_at=now,
        has_tasks=True,
        has_commitments=False,
        category="Work"
    )

    assert result["waste_score"] <= 20.0
    assert result["recommended_action"] == "KEEP"
    assert any(b["points"] < 0 for b in result["breakdown"])


def test_storage_waste_scorer_high_waste():
    scorer = StorageWasteScorer()
    old_date = datetime.now(timezone.utc) - timedelta(days=200)
    # A 25 MB promotional email from 200 days ago with high redundancy and no tasks
    result = scorer.compute_waste_score(
        size_bytes=25 * 1024 * 1024,
        is_promotional=True,
        redundancy_score=0.92,
        received_at=old_date,
        has_tasks=False,
        has_commitments=False,
        category="Promotion"
    )

    assert result["waste_score"] >= 80.0
    assert result["recommended_action"] == "DELETE"
    assert len(result["breakdown"]) >= 4
