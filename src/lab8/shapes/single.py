from __future__ import annotations

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import (
    compute_compensation,
    get_claim_view,
    lookup_order,
    lookup_policy,
    tool_cost,
)
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    run_id = make_run_id("single", claim_id, seed)
    trace = Trace(run_id)
    budget = Budget()

    conn = connect(store_path)

    try:
        claim = get_claim_view(conn, claim_id)

        if not claim.get("order_id"):
            trace.add("decision", {"status": "needs_info", "reason": "missing_order_id"})
            return finish(
                conn=conn,
                shape="single",
                claim_id=claim_id,
                seed=seed,
                status="needs_info",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason="missing_order_id",
            )


        budget.add_tool(tool_cost())
        order_view = lookup_order(conn, claim["order_id"], claim["principal_id"])

        if not order_view.get("visible"):
            trace.add("decision", {"status": "escalated", "reason": order_view.get("reason")})
            return finish(
                conn=conn,
                shape="single",
                claim_id=claim_id,
                seed=seed,
                status="escalated",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason=order_view.get("reason"),
            )

        budget.add_tool(tool_cost())
        lookup_policy(conn)  

        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, order_view["order"])
        amount_vnd = int(quote_payload.get("amount_vnd", 0))

        trace.add("quote", {
            "amount_vnd": amount_vnd,
            "reason": quote_payload.get("reason"),
            "clause_ids": quote_payload.get("clause_ids"),
        })

        if amount_vnd <= 0:
            trace.add("decision", {"status": "denied", "reason": quote_payload.get("reason")})
            return finish(
                conn=conn,
                shape="single",
                claim_id=claim_id,
                seed=seed,
                status="denied",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason=quote_payload.get("reason"),
            )

        outcome = issue_refund(conn, claim_id, amount_vnd, crash_at=crash_at)

        if not outcome["ok"]:
            status = "failed" if outcome.get("conflict") else "denied"
            trace.add("decision", {"status": status, "reason": outcome.get("reason")})
            return finish(
                conn=conn,
                shape="single",
                claim_id=claim_id,
                seed=seed,
                status=status,
                proposal_amount=amount_vnd,
                budget=budget,
                trace=trace,
                error_reason=outcome.get("reason"),
            )

        trace.add("decision", {"status": "resolved", "amount_vnd": amount_vnd})
        return finish(
            conn=conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="resolved",
            proposal_amount=amount_vnd,
            budget=budget,
            trace=trace,
        )

    finally:
        conn.close()
