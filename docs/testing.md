# Testing & Verification Guide: MailMind (InboxGuard)

## 1. Automated Test Suite

InboxGuard includes comprehensive unit and integration tests covering:
- Mathematical scoring formulas
- Commitment FSM state transitions
- Redundancy and cosine similarity
- Safety Policy Guard and prompt-injection neutralization
- Full end-to-end pipeline execution

### Running Tests
```powershell
cd backend
python -m pytest tests -v
```

### Verified Test Cases
1. `tests/test_scoring.py`:
   - `test_storage_waste_scorer_low_waste`: Verifies low score for active, recent emails with tasks.
   - `test_storage_waste_scorer_high_waste`: Verifies high score ($\ge 80$) for large, old duplicate marketing emails.
2. `tests/test_job_matching.py`:
   - `test_job_matcher_high_alignment`: Verifies 85%+ score for candidate possessing required skills.
   - `test_job_matcher_low_alignment`: Verifies low score when key skills are missing.
3. `tests/test_commitments.py`:
   - `test_commitment_fsm_valid_transitions`: Verifies allowed transitions and terminal states.
   - `test_commitment_state_overdue_evaluation`: Tests automated transition to `OVERDUE` when deadline passes.
   - `test_commitment_fulfillment_detection`: Validates evidence detection in reply emails.
4. `tests/test_safety.py`:
   - `test_safety_policy_action_risk_tiers`: Validates gating of destructive actions.
   - `test_prompt_injection_neutralization`: Tests adversarial prompt override containment.
5. `tests/test_redundancy.py`:
   - `test_subject_normalization`: Strips `Re:`, `Fwd:`, and ticket brackets.
   - `test_duplicate_detection_similarity`: Identifies duplicates using cosine threshold $\ge 0.88$.
6. `tests/test_pipeline_e2e.py`:
   - Full integration test: Seed $\to$ Ingest $\to$ Score $\to$ LangGraph $\to$ Policy Gate $\to$ User Approval $\to$ Action Execution $\to$ Audit Trail.

---

## 2. Frontend Build Verification
```powershell
cd frontend
npm run build
```
Verifies zero TypeScript errors and compiles production static assets.
