from app.scoring.redundancy_detector import RedundancyDetector


def test_subject_normalization():
    assert RedundancyDetector.normalize_subject("Re: Fwd: [Ticket-123] Server Outage Report") == "server outage report"
    assert RedundancyDetector.normalize_subject("  FW: Weekly Update  ") == "weekly update"
    assert RedundancyDetector.normalize_subject("Hello World") == "hello world"


def test_duplicate_detection_similarity():
    cand_sub = "Mega Cloud Hosting Clearance - 80% OFF"
    existing = [{
        "id": "e_orig",
        "subject": "Fwd: Mega Cloud Hosting Clearance - 80% OFF",
        "sender": "deals@cloudhoster-specials.com",
        "embedding": [0.8] * 384
    }]

    result = RedundancyDetector.check_duplicate(
        candidate_subject=cand_sub,
        candidate_sender="deals@cloudhoster-specials.com",
        candidate_embedding=[0.8] * 384,
        existing_emails=existing
    )

    assert result["is_duplicate"] is True
    assert result["canonical_email_id"] == "e_orig"
