# Báo cáo cá nhân — 2A202603956_QuachNgocHuy

## 1. Thông tin thành viên

- Họ tên: Quách Ngọc Huy
- MSSV: 2A202603956
- Email: zellsed123@gmail.com
- GitHub: Huy Quach

## 2. Phần việc phụ trách

- **Shape phụ trách:** Shape B — **Single Agent** (`src/lab8/shapes/single.py`).
- **Phạm vi trách nhiệm:** 
  - Thiết kế và cài đặt toàn bộ chu trình giải quyết khiếu nại (claim resolution) cho Single Agent theo đúng đặc tả hợp đồng (Contract v1) của Checkpoint 2 & Checkpoint 3.
  - Tích hợp các công cụ tra cứu nghiệp vụ an toàn (`get_claim_view`, `lookup_order`, `lookup_policy`).
  - Đảm bảo tính toán bồi thường tất định qua hàm `compute_compensation`, không để mô hình tự suy diễn tiền bồi hoàn.
  - Đảm bảo tính bền vững dữ liệu, idempotency và khả năng phục hồi khi gặp sự cố (`crash_at` / InjectedCrash) thông qua `durability.issue_refund`.

## 3. Đóng góp cụ thể

- **Commit chính:**
  - `ee5b2ac` (`update: single`): Cài đặt hoàn thiện luồng xử lý `run_claim` cho Single Agent trong `src/lab8/shapes/single.py`.
- **Chi tiết kỹ thuật đã thực hiện:**
  1. **Khởi tạo và đóng tài nguyên an toàn:** Kết nối SQLite store qua `connect(store_path)` và luôn đóng kết nối trong khối `finally: conn.close()`.
  2. **Truy cập dữ liệu có kiểm soát:** Sử dụng `get_claim_view` để lấy thông tin claim an toàn, không để lộ dữ liệu nhạy cảm.
  3. **Xử lý thiếu thông tin (`needs_info`):** Kiểm tra `order_id` trong claim. Nếu thiếu, ghi sự kiện quyết định vào `trace` và kết thúc với trạng thái `needs_info`, `error_reason="missing_order_id"`.
  4. **Kiểm tra quyền truy cập và hiển thị (`escalated`):** Gọi `lookup_order(conn, order_id, principal_id)` và cộng chi phí `tool_cost()` vào `budget`. Nếu `visible` là False (truy cập trái phép hoặc đơn hàng bị ẩn), ghi nhận `trace` và chuyển trạng thái `escalated`.
  5. **Tra cứu chính sách & tính bồi hoàn tất định (`quote`):**
     - Gọi `lookup_policy(conn)` và `compute_compensation(conn, order_view["order"])`, ghi nhận chi phí budget cho từng lần gọi tool.
     - Số tiền bồi hoàn hoàn toàn do mã nguồn tính toán, không phó mặc cho LLM.
     - Ghi nhận thông tin báo giá (`amount_vnd`, `reason`, `clause_ids`) vào `trace`.
  6. **Xử lý từ chối bồi hoàn (`denied`):** Nếu `amount_vnd <= 0`, trả trạng thái `denied` kèm lý do giải thích.
  7. **Thực hiện bồi hoàn an toàn & chuyển tiếp sự cố (`resolved` / `failed`):**
     - Gọi `durability.issue_refund(conn, claim_id, amount_vnd, crash_at=crash_at)`.
     - Chuyển tiếp nguyên vẹn tham số `crash_at` và không bắt/nuốt ngoại lệ `InjectedCrash`, đảm bảo hệ thống có thể kiểm thử khả năng chịu lỗi (fault tolerance).
     - Dựa vào kết quả trả về để kết luận trạng thái `resolved` (thành công) hoặc `failed` / `denied` (khi có xung đột hay từ chối).
     - Định dạng kết quả trả về chuẩn `RunResult` qua hàm `finish`.

## 4. Bằng chứng

- **Test học viên (Student Matrix Tests):**
  - Chạy lệnh kiểm thử dành riêng cho Shape Single:
    ```bash
    python -m pytest -q -m student -o addopts= -k 'single and not workflow and not orchestrator and not swarm'
    ```
  - Kết quả: **62/62 passed (100% PASS)**:
    - Vượt qua toàn bộ các ca kiểm thử T01–T10, T13, T14 trên cả 5 seeds (11, 22, 33, 44, 55).
    - Vượt qua T11 (`test_t11_retry_keeps_one_refund[single]`): Kiểm tra tính Idempotent, gọi lại cùng claim ID không phát sinh ghi trùng sổ cái.
    - Vượt qua T12 (`test_t12_crash_before_checkpoint_does_not_double_pay[single]`): Kiểm tra an toàn sự cố trước checkpoint.
- **Kiểm thử cổng Host & Smoke:**
  - `python -m lab8.smoke`: **PASS** (`lab8.smoke pass | MockLLM seeded | swarm C-001 refund 35000 | trace clean`).
  - `python -m pytest -q`: **61 passed, 0 failed** (xanh toàn bộ các test kiểm tra hợp đồng, bảo mật và hồi quy).
- **Kiểm thử Crash Safety:**
  - `reports/crash.json`: Đạt điểm tuyệt đối **20/20** kịch bản an toàn sự cố (`"crash_safety": "20/20"`).
- **Trình kiểm tra nộp bài tự động (`check_submission`):**
  - `[ OK ] shape single: format đúng, 12/12 claim public pass ở seed 11`.

## 5. Công cụ AI đã dùng

- **Công cụ:** Trợ lý AI (Google Gemini / Antigravity Assistant).
- **Mục đích sử dụng:**
  - Tra cứu và đối chiếu các schema trong `lab8/schemas.py`, các hàm tiện ích trong `lab8/tools.py` và quy định giao ước vết chạy trong `docs/contracts.md`.
  - Phân tích luồng nghiệp vụ rẽ nhánh trạng thái (`needs_info`, `escalated`, `denied`, `resolved`, `failed`) để đảm bảo không bỏ sót trường hợp biên.
  - Gợi ý câu lệnh pytest và cách cấu hình môi trường kiểm thử tương thích.
- **Phương thức tự kiểm tra kết quả:**
  - Tự đọc, phân tích và làm chủ toàn bộ mã nguồn `src/lab8/shapes/single.py`.
  - Thực thi kiểm thử thực tế trên PowerShell bằng các bộ test chính thức: `pytest -m student`, `pytest -q`, `python -m lab8.smoke`, `python -m lab8.check_submission`.
  - Trực tiếp kiểm tra nội dung log và trace data để đảm bảo không có rò rỉ secret hoặc PII (như `parent_secret`, số điện thoại, ghi chú bảo mật).

## 6. Tự đánh giá

- **Mức độ hoàn thành:** **100%** yêu cầu đối với Shape Single Agent.
- **Chất lượng mã nguồn:** Tuân thủ chuẩn mực thiết kế an toàn, tối ưu chi phí công cụ, đảm bảo tính toàn vẹn dữ liệu và khả năng chịu lỗi cao.
