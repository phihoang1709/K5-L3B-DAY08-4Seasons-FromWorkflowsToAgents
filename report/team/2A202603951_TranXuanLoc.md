# Báo cáo cá nhân — 2A202603951_TranXuanLoc

## 1. Thông tin thành viên

- Họ tên: Trần Xuân Lộc
- MSSV: 2A202603951
- Lớp: L3B
- Email: 26ai.loctx2@vinuni.edu.vn
- GitHub: Kaylez-TXL

## 2. Phần việc phụ trách

Em phụ trách triển khai shape C — Orchestrator và investigator trong `src/lab8/shapes/orchestrator.py`, đồng thời bổ sung kiểm thử về handoff và bảo mật dữ liệu.

## 3. Đóng góp cụ thể

- Em xây dựng luồng đọc claim, tạo handoff bằng `make_handoff` và giao investigator sử dụng các tool chỉ đọc.
- Em tích hợp tính bồi thường bằng code và truyền quote đầy đủ vào `issue_refund` để host kiểm tra approval, giới hạn hoàn tiền và chống ghi trùng.
- Em xử lý các nhánh kết quả, ghi trace an toàn và truyền `crash_at` mà không bắt `InjectedCrash`.
- Em bổ sung ba ca kiểm thử trong `src/tests/test_handoff_secret.py`, kiểm tra handoff, dữ liệu nhạy cảm và trace khi trả kết quả sớm.
- Commit đóng góp: `a33ee1e` — `shape C`.

## 4. Bằng chứng

Các lệnh kiểm tra đã được thực hiện trong thư mục `src/` sau khi chỉnh sửa phần C:

| Kiểm tra | Kết quả |
| --- | --- |
| `python -m lab8.smoke` | Pass |
| `python -m pytest -q -m student -o addopts= -k orchestrator` | 62 passed, gồm T11 và T12 |
| `python -m pytest -q` | 57 passed, gồm ba ca kiểm thử mới |

Các hàm kiểm thử em bổ sung gồm `test_orchestrator_handoff_and_trace_exclude_untrusted_ticket` và `test_orchestrator_early_return_writes_trace_without_handoff`; hàm thứ hai được tham số hóa thành hai ca.

Kết quả trên được ghi nhận tại thời điểm hoàn thành phần C, trên Python 3.14.6. Nhóm cần kiểm tra lại bằng Python 3.11–3.13 theo yêu cầu đề bài. Kết quả này chưa đại diện cho hidden test hoặc crash suite chung 20 điểm.

## 5. Công cụ AI đã dùng

Em sử dụng ChatGPT/Codex để hỗ trợ phân tích yêu cầu, triển khai shape C và bổ sung kiểm thử. Kết quả được kiểm chứng bằng các lệnh smoke, test student của orchestrator và test mặc định; số liệu trong báo cáo lấy từ kết quả chạy thực tế.

## 6. Tự đánh giá

Phần C đã vượt qua các kiểm thử public được thực hiện, bao gồm gọi lại claim và phục hồi sau crash. Qua phần việc này, em hiểu rõ hơn vai trò của handoff theo allowlist, giới hạn quyền investigator và trách nhiệm của host khi ghi tiền. Phần kiểm thử toàn dự án, benchmark và đánh giá hidden cần tiếp tục phối hợp với các thành viên trong nhóm.
