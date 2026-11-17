# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | [HO_TEN] | [MSSV] | phih5066@gmail.com | phihoang1709 | Workflow (Shape A) + Integration |
|   2 | Trần Xuân Lộc | 2A202603951 | 26ai.loctx2@vinuni.edu.vn | Kaylez-TXL | Orchestrator (Shape C) |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| phihoang1709 | Workflow (Shape A) + Integration | `e4fb449`, `167f4e2` | `src/tests/test_workflow_extra.py` (4 test mới: fail-closed, anti-injection ticket-vs-order, leak scan, idempotency) |
| Kaylez-TXL | Orchestrator (Shape C) | `a33ee1e` | `src/tests/test_handoff_secret.py` (bổ sung 3 test handoff/worker) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## phihoang1709

### Phần việc phụ trách

- Shape A — deterministic workflow (`src/lab8/shapes/workflow.py`) + Integration Lead.

### Đóng góp cụ thể

- Implement `run_claim` deterministic (commit `e4fb449`, PR #1); commit bằng chứng crash `src/reports/crash.json` 20/20 (`167f4e2`); review PR Shape C và chạy kiểm tra tích hợp sau merge.

### Bằng chứng

- `python -m pytest -q -m student -o addopts= -k workflow` → 62 passed; host gate sau merge → 61 passed; `check_submission`: `[ OK ] shape workflow: 12/12 claim public pass ở seed 11`. Chi tiết: `report/team/phihoang1709.md`.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
