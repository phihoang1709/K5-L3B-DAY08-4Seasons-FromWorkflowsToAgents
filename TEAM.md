# Team

## Thông tin nhóm

- Tên nhóm: 4Seasons
- Lớp: L3B
- Repo nhóm: `https://github.com/phihoang1709/K5-L3B-DAY08-4Seasons-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/phihoang1709/K5-L3B-DAY08-4Seasons-FromWorkflowsToAgents, main, 631fe8a

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --- | --- | --- | --- | --- | --- |
|   1 | Nguyễn Phi Hoàng | 2A202603952 | 26ai.hoangnp2@vinuni.edu.vn | phihoang1709 | Workflow (Shape A) + Integration |
|   2 | Quách Ngọc Huy | 2A202603956 | zellsed123@gmail.com | Huy Quach | Single Agent (Shape B) |
|   3 | Trần Xuân Lộc | 2A202603951 | 26ai.loctx2@vinuni.edu.vn | Kaylez-TXL | Orchestrator (Shape C) |
|   4 | Nguyễn Công Hoàn | 2A202603972 | 26ai.hoannc@vinuni.edu.vn | hoan11052004 | Evaluation, Benchmark & Testing |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| phihoang1709 | Workflow (Shape A) + Integration | `e4fb449`, `167f4e2` | `src/tests/test_workflow_extra.py` (4 test mới: fail-closed, anti-injection ticket-vs-order, leak scan, idempotency) |
| Quách Ngọc Huy | single agent | ee5b2ac | test_public_single_run_cases[single], test_t11_retry_keeps_one_refund[single], test_t12_crash_before_checkpoint_does_not_double_pay[single] |
| Kaylez-TXL | Orchestrator (Shape C) | `a33ee1e` | `src/tests/test_handoff_secret.py` (bổ sung 3 test handoff/worker) |
| 2A202603972_NguyenCongHoan | Evaluation, Benchmark & Testing | `631fe8a`, `4939ece` | Chạy và kiểm chứng benchmark 4 shapes x 5 seeds, crash suite 20/20, student matrix 248 tests |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603952_NguyenPhiHoang

### Phần việc phụ trách

- Shape A — deterministic workflow (`src/lab8/shapes/workflow.py`) + Integration Lead.

### Đóng góp cụ thể

- Implement `run_claim` deterministic (commit `e4fb449`, PR #1); commit bằng chứng crash `src/reports/crash.json` 20/20 (`167f4e2`); review PR Shape C và chạy kiểm tra tích hợp sau merge.

### Bằng chứng

- `python -m pytest -q -m student -o addopts= -k workflow` → 62 passed; host gate sau merge → 61 passed; `check_submission`: `[ OK ] shape workflow: 12/12 claim public pass ở seed 11`. Chi tiết: `report/team/2A202603952_NguyenPhiHoang.md`.

## 2A202603956_QuachNgocHuy

### Phần việc phụ trách

- Shape B: Single Agent (`src/lab8/shapes/single.py`).

### Đóng góp cụ thể

- Commit `ee5b2ac` (`update: single`): Hoàn thiện triển khai xử lý khiếu nại cho Single Agent, đọc view an toàn không lộ secret, tra cứu order & tính bồi hoàn tự động bằng `compute_compensation`, ghi ledger qua `durability.issue_refund` với cơ chế chống ghi trùng (idempotency key `refund:{claim_id}`) và cơ chế fault injection `crash_at`.

### Bằng chứng

- 62/62 test student shape single passed (`pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"`).
- `reports/crash.json` đạt điểm tuyệt đối 20/20.
- `python -m lab8.smoke` pass, host test `pytest -q` pass 61/61.

## 2A202603951_TranXuanLoc

### Phần việc phụ trách

- Shape C: Orchestrator và investigator (`src/lab8/shapes/orchestrator.py`).

### Đóng góp cụ thể

- Xây dựng luồng đọc claim, tạo handoff bằng `make_handoff` và giao investigator sử dụng các tool chỉ đọc; tích hợp tính bồi thường bằng code và truyền quote đầy đủ vào `issue_refund`; xử lý các nhánh kết quả, ghi trace an toàn và truyền `crash_at` mà không bắt `InjectedCrash`. Bổ sung ba ca kiểm thử trong `src/tests/test_handoff_secret.py`. Commit: `a33ee1e`.

### Bằng chứng

- `python -m pytest -q -m student -o addopts= -k orchestrator` → 62 passed; `python -m lab8.smoke` pass. Chi tiết: `report/team/2A202603951_TranXuanLoc.md`.

## 2A202603972_NguyenCongHoan

### Phần việc phụ trách

- Evaluation, Benchmark, Testing & Research.

### Đóng góp cụ thể

- Thực thi benchmark 4 shapes × 5 seeds (280 trials); kiểm thử crash 20/20; thẩm định 248 student tests T01–T14; hoàn thiện decision ADR, research card R2, và group report đạt 0 FAIL, 0 WARN.

### Bằng chứng

- `src/reports/benchmark.json` (280 trials), `src/reports/crash.json` (20/20), `python -m lab8.check_submission` → 0 FAIL, 0 WARN. Chi tiết: `report/team/2A202603972_NguyenCongHoan.md`.
