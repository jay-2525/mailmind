import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_end_to_end_pipeline_flow():
    with TestClient(app) as client:
        # 1. Health check
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "HEALTHY"

        # 2. Reset and verify demo seeding
        reset_res = client.post("/api/v1/demo/reset")
        assert reset_res.status_code == 200

        # 3. Fetch emails
        emails_res = client.get("/api/v1/emails")
        assert emails_res.status_code == 200
        emails = emails_res.json()
        assert len(emails) >= 10

        # 4. Verify Storage Waste analysis
        storage_res = client.get("/api/v1/storage/overview")
        assert storage_res.status_code == 200
        storage_data = storage_res.json()
        assert storage_data["total_emails"] >= 10
        assert storage_data["recoverable_storage_bytes"] > 0

        # 5. Verify Tasks & Commitments
        tasks_res = client.get("/api/v1/tasks")
        assert tasks_res.status_code == 200
        assert len(tasks_res.json()) >= 1

        commitments_res = client.get("/api/v1/tasks/commitments")
        assert commitments_res.status_code == 200
        assert len(commitments_res.json()) >= 1

        # 6. Verify Jobs & Match Scoring
        jobs_res = client.get("/api/v1/jobs")
        assert jobs_res.status_code == 200
        jobs = jobs_res.json()
        assert len(jobs) >= 2
        # Check that Google job has match score calculated
        google_job = next((j for j in jobs if "Google" in j["company"]), None)
        assert google_job is not None
        assert len(google_job["matches"]) > 0
        assert google_job["matches"][0]["match_score"] > 70.0

        # 7. Test Application Preparation on Google Job
        app_prep = client.post(f"/api/v1/jobs/{google_job['id']}/prepare-application", json={})
        assert app_prep.status_code == 200
        prep_data = app_prep.json()
        assert "cover_letter" in prep_data
        assert "recruiter_pitch" in prep_data

        # 8. Test Historical RAG Hybrid Search
        rag_res = client.post("/api/v1/rag/search", json={"query": "distributed systems assignment", "top_k": 3})
        assert rag_res.status_code == 200
        rag_data = rag_res.json()
        assert len(rag_data["results"]) > 0
        assert "reason_for_retrieval" in rag_data["results"][0]

        # 9. Verify Approval Center Queue
        approvals_res = client.get("/api/v1/approvals")
        assert approvals_res.status_code == 200
        approvals = approvals_res.json()
        assert len(approvals) > 0

        # 10. Approve an action and verify execution + audit trail
        first_appr = approvals[0]
        act_res = client.post(f"/api/v1/approvals/{first_appr['id']}/action", json={"action": "APPROVE"})
        assert act_res.status_code == 200
        assert act_res.json()["status"] == "APPROVED"

        # 11. Verify Audit Logs
        audit_res = client.get("/api/v1/audit/logs")
        assert audit_res.status_code == 200
        logs = audit_res.json()
        assert len(logs) >= 5
        assert any(l["event_type"] == "USER_APPROVED" for l in logs)
