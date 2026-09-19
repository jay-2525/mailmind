from datetime import datetime, timezone
from typing import Dict, Any, List
from app.core.config import settings


class StorageWasteScorer:
    """
    Computes an explainable, configurable decision-support Storage Waste Score (0-100).
    Explicitly provides itemized point contributions for academic transparency and user review.
    """

    def __init__(
        self,
        weight_size: float = settings.WEIGHT_STORAGE_SIZE,
        weight_promo: float = settings.WEIGHT_PROMOTIONAL,
        weight_redundancy: float = settings.WEIGHT_REDUNDANCY,
        weight_age: float = settings.WEIGHT_AGE,
        weight_low_action: float = settings.WEIGHT_LOW_ACTIONABILITY,
    ):
        self.w_size = weight_size
        self.w_promo = weight_promo
        self.w_redundancy = weight_redundancy
        self.w_age = weight_age
        self.w_low_action = weight_low_action

    def compute_waste_score(
        self,
        size_bytes: int,
        is_promotional: bool,
        redundancy_score: float,  # 0.0 to 1.0 (cosine similarity to duplicate)
        received_at: datetime,
        has_tasks: bool,
        has_commitments: bool,
        category: str = "Other",
        future_value_indicators: bool = False,
    ) -> Dict[str, Any]:
        breakdown: List[Dict[str, Any]] = []
        raw_score = 0.0

        # 1. Attachment / payload size factor (up to 30 points)
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > 15:
            pts = 30.0
            breakdown.append({"factor": f"Very Large Payload ({size_mb:.1f} MB)", "points": +30})
        elif size_mb > 5:
            pts = 20.0
            breakdown.append({"factor": f"Large Attachment ({size_mb:.1f} MB)", "points": +20})
        elif size_mb > 1:
            pts = 10.0
            breakdown.append({"factor": f"Moderate Payload ({size_mb:.1f} MB)", "points": +10})
        else:
            pts = 0.0
        raw_score += pts * (self.w_size / 0.25)

        # 2. Promotional / Newsletter category factor (up to 25 points)
        if is_promotional or category.lower() in ["promotion", "promotional", "newsletter", "shopping"]:
            pts = 25.0
            breakdown.append({"factor": "Promotional / Marketing Content", "points": +25})
            raw_score += pts * (self.w_promo / 0.25)

        # 3. Redundancy / duplicate similarity (up to 25 points)
        if redundancy_score >= 0.88:
            pts = 25.0
            breakdown.append({"factor": f"High Content Redundancy ({int(redundancy_score*100)}% match)", "points": +25})
            raw_score += pts * (self.w_redundancy / 0.20)
        elif redundancy_score >= 0.70:
            pts = 15.0
            breakdown.append({"factor": f"Moderate Thread Redundancy ({int(redundancy_score*100)}% match)", "points": +15})
            raw_score += pts * (self.w_redundancy / 0.20)

        # 4. Inactivity / Age factor (up to 20 points)
        now = datetime.now(timezone.utc)
        if received_at.tzinfo is None:
            received_at = received_at.replace(tzinfo=timezone.utc)
        age_days = max(0, (now - received_at).days)
        if age_days > 180:
            pts = 20.0
            breakdown.append({"factor": f"Old Email ({age_days} days inactive)", "points": +20})
        elif age_days > 60:
            pts = 12.0
            breakdown.append({"factor": f"Aging Content ({age_days} days old)", "points": +12})
        elif age_days > 30:
            pts = 5.0
            breakdown.append({"factor": f"Inactive ({age_days} days old)", "points": +5})
        else:
            pts = 0.0
        raw_score += pts * (self.w_age / 0.15)

        # 5. Low Actionability factor (up to 15 points)
        if not has_tasks and not has_commitments:
            pts = 15.0
            breakdown.append({"factor": "No Pending Tasks or Commitments", "points": +15})
            raw_score += pts * (self.w_low_action / 0.15)
        else:
            # Active tasks reduce waste score significantly
            breakdown.append({"factor": "Contains Active Task/Commitment", "points": -20})
            raw_score -= 20.0

        # 6. Future Value Protection (Discounts waste score)
        if future_value_indicators or category.lower() in ["finance", "receipt", "contract", "security", "education"]:
            breakdown.append({"factor": "Potential Future Value / Important Category", "points": -15})
            raw_score -= 15.0

        final_score = max(0.0, min(100.0, round(raw_score, 1)))

        # Recommended action based on score thresholds
        if final_score >= 80:
            recommended_action = "DELETE"
        elif final_score >= 50:
            recommended_action = "ARCHIVE"
        else:
            recommended_action = "KEEP"

        return {
            "waste_score": final_score,
            "recommended_action": recommended_action,
            "breakdown": breakdown,
            "evaluated_at": now.isoformat()
        }


storage_waste_scorer = StorageWasteScorer()
