# Báo cáo cá nhân — phihoang1709

> **Lưu ý:** đổi tên file này thành `MSSV_HoTen.md` (ví dụ `2A202604567_NguyenHoangPhi.md`) và thay `[HO_TEN]` / `[MSSV]` sau khi điền.

## 1. Thông tin thành viên

- Họ tên: [HO_TEN]
- MSSV: [MSSV]
- Email: phih5066@gmail.com
- GitHub: [phihoang1709](https://github.com/phihoang1709)

## 2. Phần việc phụ trách

**Shape A — Deterministic Workflow** (`src/lab8/shapes/workflow.py`) và vai trò **Integration Lead** của nhóm.

- Implement `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult` theo đúng output contract (`docs/contracts.md`) và trace contract v1.
- Workflow hoàn toàn deterministic: tiền do code tính (`compute_compensation`), không có lời gọi model nào trong money path — model không chọn số tiền, không commit refund.
- Integration Lead: review PR của thành viên khác, chạy kiểm tra tích hợp sau merge (host gate + student matrix + `check_submission`).

## 3. Đóng góp cụ thể

**Commit chính:**

- `e4fb449` — `feat(workflow): implement deterministic Shape A run_claim` (implement `workflow.py` + thêm 4 test; PR #1 đã merge vào main).
- `167f4e2` — `feat: commit crash file` (commit bằng chứng CP4 `src/reports/crash.json` 20/20 + bổ sung `.gitignore` cho `.mimosa/`).

**Test đã thêm:** `src/tests/test_workflow_extra.py` — 4 test chạy trong host gate (không cần marker `student`):

| Test | Kiểm chứng |
| --- | --- |
| `test_workflow_unknown_claim_fails_closed` | Claim lạ → `failed`/`unknown_claim`, 0 tiền, 0 dòng ledger, trace hợp lệ (run_id + events) |
| `test_workflow_quote_uses_order_row_not_ticket` | T02 seed 55 (seed variance của swarm): quote từ order row, không tin số ngày trễ trong ticket |
| `test_workflow_no_forbidden_substrings_in_artifacts` | C-005/C-010: quét result JSON + trace file, không token nào trong danh sách `forbid_substrings` rò rỉ |
| `test_workflow_retry_is_idempotent` | C-011 chạy 2 lần: 1 dòng ledger, 1 audit `refund_committed`, cùng proposal 35000 |

**Quyết định kỹ thuật:**

1. **Truyền full quote vào `durability.issue_refund`, không tự trừ** — host tự cap theo per-order và approval (T13/T14). Tự trừ trước sẽ bị host trừ hai lần.
2. **`crash_at` được truyền thẳng vào `issue_refund`, không bắt `InjectedCrash`** — chỉ flush trace (`trace.add("crash", ...)`, `trace.write()`) rồi re-raise để T12 xác nhận crash có xảy ra thật.
3. **Quote chỉ từ order row** — số ngày trễ trong ticket (kể cả câu "ignore policy" trong T09) là dữ liệu người dùng, không phải lệnh; fix luôntrap seed 55 của swarm reference.
4. **Trace chỉ ghi view đã allowlist** (`get_claim_view` chỉ `found/claim_id`, `lookup_order` đã strip PII, quote payload) — không bao giờ ghi raw claim/order row, không in gì ra stdout.
5. **Mọi return path đi qua `common.finish()`** — `refund_effects`/`committed_audit_count` lấy từ ledger, trace contract v1 hợp lệ kể cả các nhánh early-return.

## 4. Bằng chứng

- **Commit:** [e4fb449](https://github.com/phihoang1709/K5-L3B-DAY08-4Seasons-FromWorkflowsToAgents/commit/e4fb449), [167f4e2](https://github.com/phihoang1709/K5-L3B-DAY08-4Seasons-FromWorkflowsToAgents/commit/167f4e2); PR #1 merge vào main (`ced4344`).
- **Student matrix (workflow):** `python -m pytest -q -m student -o addopts= -k workflow` → **62 passed** (12 claims T01–T14 × 5 seed + T11 retry + T12 crash/resume).
- **Host gate sau merge main:** `python -m pytest -q` → **61 passed** (54 gốc + 4 test của tôi + 3 test bổ sung của Shape C), không regression.
- **check_submission:** `[ OK ] shape workflow: format đúng, 12/12 claim public pass ở seed 11`.
- **Crash safety:** `src/reports/crash.json` — `crash_safety: 20/20` (bằng chứng CP4, commit `167f4e2`).
- **Run id mẫu:** `R-workflow-C-001-s11` (trace JSON tương ứng trong `src/traces/`, bị gitignore đúng theo repo).
- **Diff scope:** chỉ 2 file thuộc phạm vi (`workflow.py`, `test_workflow_extra.py`); không đụng `metrics.py`, `durability.py`, `policy.py`, `src/config/`, `src/data/`; diff đã quét — không có `CANARY_SECRET_*`/PII.

## 5. Công cụ AI đã dùng

- **Công cụ:** ZCode (model GLM) — dùng như trợ lý AI theo cho phép của [RULES.md](../../RULES.md).
- **Dùng vào việc:** đọc và tóm tắt contract/docs (`docs/contracts.md`, `docs/business_rules.md`), tra cứu API host (`durability.py`, `policy.py`, `tools.py`), nháp bản implement đầu, chạy toàn bộ test suite và tổng hợp bằng chứng.
- **Tự kiểm tra kết quả thế nào:**
  - Chạy lại bằng tay toàn bộ gate: host `pytest -q`, student `-k workflow` (62/62), full student matrix, `check_submission` — mọi số liệu trong báo cáo này lấy trực tiếp từ output lệnh đã chạy, không có số nào do AI sinh ra.
  - Tự review diff trước khi commit: chỉ 2 file đúng phạm vi, không sửa file bảo vệ, không có secret/PII trong diff.
  - Đối chiếu implementation với output contract từng dòng trong bảng `docs/contracts.md` (7 tình huống → status/proposal/ledger).

## 6. Tự đánh giá

*(Mục tự đánh giá — theo RULES.md phần này do thành viên tự viết, không dùng AI bịa. Gợi ý điền:)*

- Điểm làm tốt: ...
- Điểm còn hạn chế / sẽ làm khác: ...
- Thời gian thực tế dành cho phần việc: ...
