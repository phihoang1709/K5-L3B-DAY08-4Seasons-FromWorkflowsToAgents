"""Extra workflow-shape tests contributed by the Shape A owner.

Runs in the default host gate (no student marker). Complements the student
matrix with fail-closed, anti-injection, leak-scan, and idempotency checks
written directly against the workflow shape.
"""

from __future__ import annotations

import json
from pathlib import Path

from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.config_loader import repo_path
from lab8.shapes import SHAPES

WORLD = load_json(repo_path("data", "public_world_state.json"))
CLAIMS = load_jsonl(repo_path("data", "public_claims.jsonl"))
BY_ID = {row["claim_id"]: row for row in CLAIMS}


def _store(tmp_path: Path, name: str) -> Path:
    store = tmp_path / name
    init_store(store, WORLD, CLAIMS).close()
    return store


def _artifact_blob(result) -> str:
    """Same surface the grader scans: result JSON + the trace file it points to."""
    trace_text = Path(result.trace_path).read_text(encoding="utf-8")
    return json.dumps(result.as_dict(), ensure_ascii=False) + trace_text


def test_workflow_unknown_claim_fails_closed(tmp_path):
    store = _store(tmp_path, "wf-unknown.sqlite")
    result = SHAPES["workflow"]("C-999", seed=11, store_path=str(store))
    conn = connect(store)
    try:
        rows = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-999'").fetchone()["n"]
    finally:
        conn.close()
    assert result.status == "failed"
    assert result.error_reason == "unknown_claim"
    assert result.proposal_amount == 0
    assert rows == 0
    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert trace["run_id"] == result.run_id
    assert isinstance(trace["events"], list)


def test_workflow_quote_uses_order_row_not_ticket(tmp_path):
    # T02 at the swarm's variance seed: the ticket claims 5 days, the order row says 2.
    # The deterministic workflow must deny on every seed, including 55.
    store = _store(tmp_path, "wf-ticket-lie.sqlite")
    result = SHAPES["workflow"]("C-002", seed=55, store_path=str(store))
    conn = connect(store)
    try:
        rows = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-002'").fetchone()["n"]
    finally:
        conn.close()
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert rows == 0


def test_workflow_no_forbidden_substrings_in_artifacts(tmp_path):
    # C-005 (foreign order with PII) and C-010 (PII-heavy owned order): nothing
    # from the claim's forbid list may appear in the result or its trace.
    for claim_id, name in (("C-005", "wf-leak-c005.sqlite"), ("C-010", "wf-leak-c010.sqlite")):
        store = _store(tmp_path, name)
        result = SHAPES["workflow"](claim_id, seed=11, store_path=str(store))
        blob = _artifact_blob(result)
        for token in BY_ID[claim_id]["expected"]["forbid_substrings"]:
            assert token not in blob, f"{claim_id} leaked {token!r}"


def test_workflow_retry_is_idempotent(tmp_path):
    store = _store(tmp_path, "wf-retry.sqlite")
    first = SHAPES["workflow"]("C-011", seed=11, store_path=str(store))
    second = SHAPES["workflow"]("C-011", seed=11, store_path=str(store))
    conn = connect(store)
    try:
        rows = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-011'"
        ).fetchone()["n"]
        audits = conn.execute(
            "SELECT COUNT(*) AS n FROM audit_events WHERE claim_id = 'C-011' AND event_type = 'refund_committed'"
        ).fetchone()["n"]
    finally:
        conn.close()
    assert first.status == "resolved"
    assert second.status == "resolved"
    assert second.proposal_amount == first.proposal_amount == 35000
    assert rows == 1
    assert audits == 1
