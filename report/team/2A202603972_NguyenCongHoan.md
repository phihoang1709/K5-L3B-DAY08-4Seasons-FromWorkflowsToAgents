# Báo cáo cá nhân — 2A202603972_NguyenCongHoan

## 1. Thông tin thành viên

- Họ tên: Nguyễn Công Hoàn
- MSSV: 2A202603972
- Lớp: L3B
- Email: 26ai.hoannc@vinuni.edu.vn
- GitHub: hoan11052004

## 2. Phần việc phụ trách

Em phụ trách vai trò **Evaluation, Benchmark, Testing & Research ** của nhóm:

- Thiết lập kế hoạch và thực hiện quy trình kiểm thử (Testing), đo lường chuẩn hóa (Benchmark) và đánh giá độ bền vững (Durability & Crash Safety) trên cả 4 kiến trúc (*shapes*): `workflow`, `single`, `orchestrator`, `swarm`.
- Thực hiện kiểm chứng cổng host gate (`pytest -q`), ma trận kiểm thử sinh viên T01–T14 (`pytest -m student`) và bộ kịch bản sự cố crash suite 20 điểm (`lab8.crash_test`).
- chạy benchmark 4 shapes × 5 seeds trên 14 claims public, trích xuất dữ liệu và phân tích chuyên sâu các metrics: Pass rate, Pass^5, Seed variance, Cost per success, Mean/p95 steps, Secret leakage và Approval bypass.
- Hoàn thiện tài liệu (`report/team/decision_adr.md`), phiếu (`report/team/research_card.md`), đồng thời tích hợp bảng số liệu thực nghiệm vào báo cáo nhóm (`report/team/group_report.md`).
- Chạy công cụ kiểm tra hợp lệ nộp bài `python -m lab8.check_submission`, đưa toàn bộ dự án về trạng thái **0 FAIL, 0 WARN**.

## 3. Đóng góp cụ thể

### 3.1. Thực thi & Xác thực Kiểm thử (Testing Phase)
- **Cổng Host (`pytest -q`):** Thực thi và giám sát cổng kiểm định chất lượng cốt lõi, bảo đảm 61 test luôn xanh (bao gồm hợp đồng host, MockLLM, chính sách phê duyệt, idempotency và các test mở rộng của nhóm).
- **Ma trận Sinh viên T01–T14 (`pytest -m student`):** Kiểm thử toàn bộ 248 ca kiểm thử trên cả 4 kiến trúc với 5 seeds (`11, 22, 33, 44, 55`), xác thực hành vi của từng shape trên các tình huống đặc biệt (T11 gọi lại giữ nguyên 1 refund, T12 crash trước checkpoint không trả tiền hai lần, T13/T14 hoàn tiền theo hạn mức đơn hàng).
- **Crash Safety Suite (`crash_test.py`):** Kiểm tra 20 điểm crash mô phỏng sự cố (trước effect, sau effect chưa checkpoint, sau checkpoint, xung đột số tiền, thiếu approval). Xác thực hệ thống đạt chuẩn an toàn tuyệt đối **20/20**, đảm bảo chỉ có đúng 1 dòng ledger và 1 dòng audit `refund_committed`.

### 3.2. Đo chuẩn & Đánh giá Đa kiến trúc (Benchmark & Evaluation)
- Chạy toàn diện bộ benchmark:
  ```powershell
  python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
  ```
  Quản lý việc thực thi $4 \times 14 \times 5 = 280$ trials độc lập trên các file SQLite riêng biệt.
- **Phân tích đối chứng:**
  - Phát hiện và ghi nhận bản chất điểm yếu của `swarm` tại seed 55 ở claim `C-002`: swarm tin vào số ngày trễ ghi trong claim ticket (5 ngày) thay vì dữ liệu thực tế trong order (2 ngày), dẫn đến việc bồi thường 20.000 VND trái quy định thay vì từ chối (`status resolved != denied`).
  - Chứng minh sự suy giảm của Swarm: Pass rate giảm xuống 0.9857 (69/70), Pass^5 giảm xuống 0.9286 (13/14), làm bộc lộ phương sai `seed_variance = 0.000816`.
  - Chứng minh ưu thế tuyệt đối của `workflow`: Pass rate = 1.0, Pass^5 = 1.0, phương sai = 0.0, chi phí thấp nhất (27.86 VND/success, rẻ hơn ~44% so với Swarm 49.57 VND và Orchestrator 47.44 VND).

### 3.3. Soạn thảo Hồ sơ Báo cáo & Nghiên cứu (Reports & ADR)
- **Hoàn thiện `report/team/decision_adr.md`:** Khẳng định lựa chọn kiến trúc `workflow` theo nguyên tắc *"ít tự chủ nhất mà vẫn làm được việc"*, trích xuất chính xác `run_id` dẫn chứng (`R-workflow-C-001-s11`), phân tích ranh giới trace bảo mật không rò rỉ PII/Secret, và giải trình điều kiện đảo ngược quyết định.
- **Hoàn thiện `report/team/research_card.md`:** Triển khai câu hỏi nghiên cứu R2 (Failure taxonomy - MAST NeurIPS 2025), thiết kế và phân tích ablation thực nghiệm giữa Workflow A và Swarm D.
- **Cập nhật `report/team/group_report.md`:** Tổng hợp bảng số liệu thực nghiệm 4 shapes, ranh giới an toàn của hệ thống và giải pháp khắc phục sự cố môi trường.

### 3.4. Commit đóng góp chính
- `631fe8a` — `docs: complete decision ADR, research card, group report and benchmark`
- `4939ece` — `docs: record final commit hash in ADR, group report, and TEAM.md`

## 4. Bằng chứng

Toàn bộ các lệnh kiểm tra và đo lường được thực thi trực tiếp trong thư mục `src/`:

| Hạng mục kiểm tra | Lệnh thực hiện | Kết quả thực tế | Ý nghĩa kiểm chứng |
| :--- | :--- | :---: | :--- |
| **Cổng Host** | `python -m pytest -q` | **61 passed** | Không regression, vượt qua toàn bộ rào chắn bảo mật và hợp đồng host |
| **Ma trận Student** | `python -m pytest -q -m student -o addopts=` | **248 passed** | 100% tests T01–T14 xanh trên cả 4 shapes qua 5 seeds |
| **Độ bền Crash** | `python -m lab8.crash_test --count 20 --out reports/crash.json` | **20/20** | Đạt chỉ tiêu Must-pass C3, không duplicate refund khi resume |
| **Benchmark** | `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm ...` | **280/280 trials** | Sinh ra `src/reports/benchmark.json` hợp lệ, đầy đủ dữ liệu so sánh 4 shapes |
| **Hợp lệ Nộp bài** | `python -m lab8.check_submission` | **0 FAIL, 0 WARN** | Toàn bộ code, reports và docs khớp định dạng chấm điểm tự động |

- **Bằng chứng file lưu trữ:** `src/reports/benchmark.json`, `src/reports/crash.json`.
- **Run ID mẫu:** `R-workflow-C-001-s11` (Workflow thành công), `R-swarm-C-002-s55` (Swarm bộc lộ lỗi ở seed 55).

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity AI Agent (DeepMind / Gemini 3.8 Flash).
- **Mục đích sử dụng:**
  - Hỗ trợ lập kế hoạch tổng thể quy trình kiểm thử và đánh giá (/plan).
  - Đối soát cấu trúc JSON và trích xuất số liệu thống kê từ `benchmark.json` sang bảng Markdown.
  - Tra cứu tài liệu nghiên cứu tham khảo (MAST NeurIPS 2025) phục vụ điền phiếu `research_card.md`.
  - Hỗ trợ rà soát cú pháp regex kiểm tra của `check_submission.py` để đảm bảo bài nộp chuẩn định dạng máy đọc.
- **Quy trình kiểm tra kết quả:**
  - Tự tay thực thi tất cả các lệnh kiểm thử và benchmark trong terminal PowerShell; toàn bộ số liệu đưa vào báo cáo đều trích xuất trực tiếp từ file JSON do công cụ lab sinh ra, không sử dụng số liệu suy đoán.
  - Kiểm tra độc lập mã nguồn các file báo cáo Markdown đảm bảo không làm mất hoặc sai lệch các dòng nhãn bắt buộc của hệ thống chấm điểm.

## 6. Tự đánh giá

- **Điểm làm tốt:**
  - Kiểm thử và benchmark bài bản, kiểm soát trọn vẹn 280 trials và 248 student tests mà không gặp lỗi dừng đột ngột.
  - Phân tích sâu sắc bản chất toán học của các chỉ số (Pass rate, Pass^5, phương sai seed, cost/success) và cơ chế phát sinh lỗi của Swarm tại seed 55, làm nổi bật tính thuyết phục của quyết định lựa chọn Workflow trong ADR.
  - Đưa toàn bộ dự án về trạng thái hoàn hảo `0 FAIL, 0 WARN` trên hệ thống kiểm tra tự động `check_submission`.
- **Điểm còn hạn chế / Bài học kinh nghiệm:**
  - Trong quá trình chạy ban đầu trên môi trường Windows, cần chú ý luôn kích hoạt và sử dụng Python trong virtual environment (`.\.venv\Scripts\python.exe`) để tránh việc trình thông dịch nhận nhầm module `conftest` từ global site-packages.
- **Thời gian thực tế dành cho phần việc:** Khoảng 1 giờ (chạy benchmark, kiểm thử ma trận, phân tích dữ liệu và hoàn thiện hồ sơ báo cáo).
