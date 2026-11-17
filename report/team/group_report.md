# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: 4Seasons
- Lớp: L3B
- Repo nhóm: `https://github.com/phihoang1709/K5-L3B-DAY08-4Seasons-FromWorkflowsToAgents`
- Thành viên: xem `TEAM.md` (Nguyễn Phi Hoàng - 2A202603952, Quách Ngọc Huy - 2A202603956, Trần Xuân Lộc - 2A202603951, Nguyễn Công Hoàn - 2A202603972)
- Commit chốt (trùng `report/team/decision_adr.md`): `631fe8a`

## 2. Mục tiêu và cách tiếp cận

Bài toán yêu cầu xử lý quy trình yêu cầu bồi thường (claims refund) của công ty vận tải giả lập LogiX-VN theo 4 hình thái kiến trúc (*shapes*):
- **A `workflow`**: Pipeline xác định viết bằng Python thuần túy.
- **B `single`**: Tác nhân đơn theo mô hình ReAct (tối đa 8 bước).
- **C `orchestrator`**: Kiến trúc điều phối trung tâm kết hợp các investigator chỉ đọc độc lập.
- **D `swarm`**: Mạng lưới tác nhân ngang hàng (tham chiếu).

Nhóm tiếp cận theo nguyên tắc **Defense in Depth** và **Zero Trust**:
1. **Tách biệt ranh giới model và tiền bạc**: Model chỉ đọc dữ liệu hoặc soạn thảo phản hồi; toàn bộ việc tính toán bồi thường do code (`compute_compensation`) và thẩm quyền ghi nhận giao dịch hoàn tiền thuộc duy nhất về host (`durability.issue_refund`).
2. **Idempotency & Crash Resilience**: Đảm bảo an toàn tuyệt đối khi chạy lại (retry) hoặc gặp crash tại bất kỳ điểm nào (trước ghi, sau ghi trước checkpoint, sau checkpoint).
3. **Bảo mật ranh giới & Sanitize Handoff**: Chỉ cho phép các trường trong allowlist đi qua ranh giới giữa các agent; tuyệt đối không rò rỉ `CANARY_SECRET_*`, PII hay raw rows vào trace hoặc kết quả.

## 3. Giải pháp

### 3.1. Shape A — Deterministic Workflow (`workflow.py`)
- **Luồng xử lý:** Đọc claim qua `get_claim_view`. Nếu thiếu `order_id` trả `needs_info`. Tra cứu đơn qua `lookup_order`, nếu không nhìn thấy trả `escalated`. Tính báo giá bằng `compute_compensation(conn, order)`.
- **Ra quyết định:** Nếu quote $\le 0$ trả `denied` (không gọi host). Nếu quote $> 0$, truyền **quote đầy đủ** vào `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` để host tự kiểm tra approval và trừ các lần hoàn tiền trước của đơn đó (T13, T14).
- **Ranh giới:** Hoàn toàn bằng code xác định, 0 model call trong money path. Trace ghi nhận đầy đủ sự kiện `quote` và `decision`.

### 3.2. Shape B — Single ReAct Agent (`single.py`)
- **Luồng xử lý:** Khởi tạo ReAct loop với ngân sách và số bước tối đa là 8. Agent tuần tự gọi các công cụ chỉ đọc (`get_claim_view`, `lookup_order`, `lookup_policy`, `compute_compensation`).
- **Ranh giới:** Agent tuyệt đối không có quyền gọi ghi tiền. Sau khi hoàn thành việc thu thập thông tin và tính toán quote, host bên ngoài vòng lặp mới thực hiện thẩm định và gọi `issue_refund`.

### 3.3. Shape C — Orchestrator & Read-only Investigators (`orchestrator.py`)
- **Luồng xử lý:** Orchestrator nhận claim, đóng gói yêu cầu điều tra thông qua `make_handoff` với danh sách công cụ được phép (`allowed_tools`: `lookup_order`, `lookup_policy`, `compute_compensation`).
- **Ranh giới bảo mật:** Handoff chỉ chứa dữ liệu whitelist (`request_id`, `claim_id`, `task`, `facts`, `allowed_tools`), không mang parent context hay secret. Các investigator được chạy qua `run_readonly_investigators` trong môi trường chỉ đọc. Sau khi nhận báo cáo từ investigator, orchestrator thực hiện gọi `issue_refund`.

## 4. Kết quả

### 4.1. Bảng số liệu Benchmark 4 Shapes (trên 14 claims × 5 seeds = 70 trials/shape)
Dữ liệu trích xuất trực tiếp từ `src/reports/benchmark.json`:

| Chỉ số đo lường | Shape A `workflow` | Shape B `single` | Shape C `orchestrator` | Shape D `swarm` (Ref) |
| :--- | :---: | :---: | :---: | :---: |
| **Pass rate** | **1.000** (70/70) | **1.000** (70/70) | **1.000** (70/70) | 0.9857 (69/70) |
| **Pass^5** (ổn định cả 5 seeds) | **1.000** (14/14) | **1.000** (14/14) | **1.000** (14/14) | 0.9286 (13/14) |
| **Seed variance** | **0.000** | **0.000** | **0.000** | 0.000816 |
| **Seed min / max** | [1.000, 1.000] | [1.000, 1.000] | [1.000, 1.000] | [0.9286, 1.000] |
| **Cost per success (VND)** | **27.86** | **26.43** | 47.44 | 49.57 |
| **Tổng chi phí mô phỏng (VND)**| 1,950.0 | 1,850.0 | 3,321.0 | 3,420.12 |
| **Mean / p95 steps** | 3.79 / 4.0 | 1.86 / 2.0 | 3.71 / 4.0 | 2.80 / 3.0 |
| **Mean Model calls** | 0.0 | 0.0 | 1.0 | 3.0 |
| **Mean Tool calls** | 2.79 | 2.64 | 4.64 | 4.66 |

### 4.2. Độ an toàn Crash & Độ bền vững (Durability)
- File bằng chứng: `src/reports/crash.json`
- Kết quả kiểm thử: **`crash_safety: 20/20`** (vượt qua tất cả 20 kịch bản crash trước effect, sau effect chưa checkpoint, sau checkpoint, xung đột số tiền retry, và thiếu approval).
- Không có bất kỳ hiện tượng duplicate refund hay mất dấu audit `refund_committed`.

### 4.3. Phân tích kết quả
- **Điểm yếu của Swarm:** Swarm bị fail tại `C-002` ở seed 55 do tin vào claim ticket (khách báo trễ 5 ngày) thay vì dữ liệu đối soát thực tế trong order (chỉ trễ 2 ngày), dẫn đến bồi thường 20.000 VND trái luật thay vì từ chối (`status resolved != denied`).
- **So sánh chi phí:** Workflow và Single agent có chi phí chỉ bằng ~55% so với Orchestrator và Swarm do không phát sinh các lượt gọi model trung gian cho việc phối hợp và giao việc.
- Quyết định kiến trúc chính thức: Xem chi tiết tại [report/team/decision_adr.md](decision_adr.md).
- Nghiên cứu cơ chế lỗi và ablation: Xem chi tiết tại [report/team/research_card.md](research_card.md).

## 5. Khó khăn và cách xử lý

1. **Môi trường Windows và xung đột package toàn cục:**
   - *Vấn đề:* Khi chạy pytest bằng lệnh `python -m pytest`, Python trên Windows ưu tiên module `tests.conftest` trong global site-packages thay vì thư mục `src/tests`, gây lỗi import `CLAIMS, WORLD`.
   - *Cách xử lý:* Thống nhất sử dụng trực tiếp Python trong virtual environment: `.\.venv\Scripts\python.exe` từ thư mục `src/`.
2. **Khấu trừ tiền bồi thường đơn hàng đã hoàn trước đó (T13, T14):**
   - *Vấn đề:* Ban đầu có thể nhầm lẫn tự trừ số tiền đã hoàn trước đó trong code của shape trước khi gửi sang host.
   - *Cách xử lý:* Đọc kỹ contract `durability.issue_refund`, chỉ truyền **quote đầy đủ** tính theo order; host sẽ là bên duy nhất thực hiện việc kiểm tra trần và trừ đi các khoản đã hoàn để tránh việc bị trừ 2 lần.
3. **Bảo mật Handoff và Trace:**
   - *Vấn đề:* Rò rỉ context hoặc dữ liệu nhạy cảm vào trace khi serialize dict.
   - *Cách xử lý:* Áp dụng strict allowlist trong `make_handoff` và chỉ ghi các field định nghĩa sẵn vào trace.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân:
- Nguyễn Phi Hoàng: `report/team/2A202603952_NguyenPhiHoang.md` (Workflow Shape A, Integration, Crash safety report).
- Quách Ngọc Huy: `report/team/2A202603956_QuachNgocHuy.md` (Single Agent Shape B).
- Trần Xuân Lộc: `report/team/2A202603951_TranXuanLoc.md` (Orchestrator Shape C, Handoff & Investigator security).
- Nguyễn Công Hoàn: `report/team/2A202603972_NguyenCongHoan.md` (Evaluation, Benchmark, Testing & Research).

## 7. Hạn chế và hướng cải thiện

- **Mô phỏng MockLLM:** MockLLM trong bài lab dựa trên bảng tra cố định và seed, chưa mô phỏng được độ trễ mạng thực tế (`latency: unavailable`) và độ bất định của LLM trong môi trường production.
- **Mở rộng tương lai:** Khi bài toán mở rộng sang các yêu cầu bồi thường bảo hiểm đa phương tiện (ảnh chụp hiện trường, giấy biên nhận viết tay), kiến trúc Orchestrator với các multimodal worker chuyên biệt sẽ phát huy ưu thế vượt trội so với workflow tĩnh.

## 8. Tài liệu tham khảo

1. Google Research (2026), *Towards a Science of Scaling Agent Systems*.
2. MAST Team (NeurIPS 2025), *Why Do Multi-Agent LLM Systems Fail?*.
3. AgentArch (AACL 2026), *Architectural Choices in Agentic Systems*.
4. Tài liệu nội bộ môn học: `docs/contracts.md`, `docs/business_rules.md`, `docs/metrics.md`.
