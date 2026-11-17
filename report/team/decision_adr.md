# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 631fe8a
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / [1.000, 1.000] / 0.0
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Shape `workflow` (Shape A) tuân thủ triệt để nguyên tắc kim chỉ nam của bài lab: "ít tự chủ nhất mà vẫn làm được việc". Trên toàn bộ 14 claims public chạy qua 5 seeds (tổng cộng 70 trials độc lập trên các SQLite database riêng biệt), `workflow` đạt thành tích tối đa tuyệt đối: pass rate = 1.0 (70/70), pass^5 = 1.0 (14/14 claim pass 5/5 seed), và phương sai seed_variance = 0.0 (tuyệt đối ổn định, min = max = 1.0). Toàn bộ luồng tiền và logic thẩm định được thực hiện bằng mã nguồn xác định (deterministic code với `compute_compensation` và `durability.issue_refund`), không có bất kỳ lời gọi model nào can thiệp vào money path, loại bỏ hoàn toàn rủi ro prompt injection, ảo giác (hallucination) hay chênh lệch do seed ngẫu nhiên. Về mặt kinh tế, chi phí mô phỏng của `workflow` chỉ đạt 27.86 VND/success, tiết kiệm 41.3% so với `orchestrator` (47.44 VND) và 43.8% so với `swarm` (49.57 VND).

## Có đáng đổi lấy multi-agent không

Nhóm quyết định giữ nguyên kiến trúc `workflow` và **không đánh đổi** lấy mô hình multi-agent (orchestrator hay swarm) cho bài toán xử lý claim vận chuyển này. Kết quả thực nghiệm cho thấy việc tăng mức độ tự chủ và bổ sung các agent cộng tác không mang lại bất kỳ sự cải thiện nào về độ chính xác (pass rate của workflow đã đạt 1.0 hoàn hảo, trong khi swarm giảm xuống 0.9857 và pass^5 chỉ đạt 0.9286 do lỗi tin lời ticket ở seed 55), nhưng lại làm tăng chi phí gần gấp đôi và làm phát sinh phương sai lớn (seed_variance của swarm là 0.000816).

Quyết định kiến trúc chỉ nên đảo ngược sang multi-agent hoặc orchestrator khi hội tụ các điều kiện sau:
1. Nhiệm vụ đòi hỏi phân tích dữ liệu phi cấu trúc phức tạp từ nhiều nguồn đa phương tiện (ví dụ: thẩm định ảnh chụp bưu kiện bị móp méo, trích xuất hóa đơn VAT scan, hoặc phân tích sentiment tranh chấp) vượt quá khả năng xử lý của code luật cố định;
2. Yêu cầu phân quyền và cách ly bảo mật theo nguyên tắc Zero Trust giữa các bộ phận độc lập, nơi một tiến trình đơn lẻ không được phép truy cập toàn bộ dữ liệu đơn hàng mà bắt buộc phải giao nhiệm vụ qua các read-only investigator có allowlist nghiêm ngặt;
3. Quy trình nghiệp vụ thay đổi liên tục hàng ngày theo nhiều kịch bản động mà việc cập nhật code pipeline gây chậm trễ hơn việc tinh chỉnh agent role và context handoff.

## Trace và bằng chứng

Trace của nhóm tuân thủ nghiêm ngặt chuẩn Trace contract v1 (`docs/contracts.md`):
- Các event được ghi nhận: `quote` (chứa `amount_vnd`, `reason`, `clause_ids`), `decision` (chứa `status`, `reason`, `amount_vnd`), và `crash` (khi gặp `InjectedCrash`). Mọi event đều gắn liền với `run_id` duy nhất và danh sách sự kiện tuyến tính.
- Các field cố ý **không ghi** vào trace: Toàn bộ thông tin định danh cá nhân (PII) gồm số điện thoại (`phone`), địa chỉ (`address`), tên hàng hóa (`item`), ghi chú nội bộ (`internal_note`), mã `CANARY_SECRET_*`, mã `CANARY_INTERNAL_*`, cũng như raw row từ bảng `claims` và `orders`.
- Lý do: Trace là nhật ký kiểm toán và bằng chứng nộp bài công khai; việc rò rỉ secret hay PII vào trace vi phạm trực tiếp tiêu chí Must-pass của lab và chuẩn mực an toàn thông tin doanh nghiệp.
- Cách chứng minh hệ thống không lộ secret:
  1. Static analysis: Kiểm tra code đảm bảo các đối tượng đưa vào trace dictionary chỉ gồm các trường nguyên thủy được lọc sạch qua view layer (`get_claim_view`, `lookup_order`), không serialize raw tuple/dict.
  2. Dynamic scanning: Sử dụng bộ quét tự động tích hợp trong `lab8.metrics` quét qua file trace JSON và output của `RunResult`, đối chiếu với danh mục `forbid_substrings` và `LEAK_MARKERS` trên tất cả 70 trials (`secret_leak_count == 0`).
  3. Security boundaries: Cổng host (`durability.issue_refund`) và module handoff (`make_handoff`) đóng vai trò rào chắn bảo mật độc lập, từ chối mọi trường ngoài allowlist trước khi ghi log.

## Giới hạn

- MockLLM trong môi trường lab là mô hình giả lập ánh xạ qua seed/prompt, phục vụ đo lường độ dao động và phân loại hành vi; nó không phản ánh đầy đủ độ trễ mạng thực tế, chi phí thực của LLM thương mại, hay bản chất stochastic phức tạp của các mô hình LLM production lớn.
- Trường độ trễ (`latency`) được giữ nguyên giá trị `unavailable` theo chuẩn của hệ thống đo lường của lab.
- Nhóm cam kết không chỉnh sửa thủ công bất kỳ số liệu nào trong các file JSON bằng chứng (`src/reports/benchmark.json`, `src/reports/crash.json`).
