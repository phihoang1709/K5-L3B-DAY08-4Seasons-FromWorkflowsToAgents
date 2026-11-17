# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST: Why Do Multi-Agent LLM Systems Fail?, NeurIPS 2025, https://arxiv.org/abs/2503.13657, benchmark & empirical failure taxonomy |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Hệ thống Multi-Agent LLM thường phát sinh lỗi do thông tin sai lệch từ trao đổi tự do (unverified communication) lấn át các ràng buộc thực tế từ môi trường (ground truth verification failure). |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Áp dụng trên bài toán ra quyết định theo quy tắc nghiệp vụ cố định có cơ sở dữ liệu xác thực (ground truth DB) và các agent trao đổi ngang hàng không qua trung tâm kiểm duyệt chặt chẽ. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi chuyển từ Workflow xác định (Shape A) sang Swarm (Shape D), việc tin cậy lời trao đổi không kiểm chứng trong ticket sẽ làm phát sinh failure ở các seed nhạy cảm (seed 55), khiến pass rate giảm khoảng 1.4% (từ 1.0 xuống ~0.986), pass^5 giảm từ 1.0 xuống ~0.929, và seed_variance tăng từ 0.0 lên > 0.0008. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, bộ công cụ đọc/tính tiền, danh sách 5 seeds (11, 22, 33, 44, 55), 14 claims public, bảng giá pricing.yaml, evaluator/host gate. Biến duy nhất thay đổi: Topology/Architecture (Deterministic Workflow A vs Peer-to-peer Swarm D). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Đo lường bằng tỷ lệ Pass rate tổng thể, Pass^5, Seed variance, Cost per success (mô phỏng VND) và kiểm tra lỗi sai lệch trạng thái tại trial C-002 seed 55 (status resolved != denied). |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
- Run id / file report: src/reports/benchmark.json (so sánh trials R-workflow-C-002-s55 và R-swarm-C-002-s55)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng. Kết quả benchmark thực tế chứng minh chính xác giả thuyết: Swarm ở seed 55 bị failure do tin vào số ngày trễ ghi trong ticket (5 ngày) thay vì dữ liệu thực tế trong order (2 ngày), dẫn đến hoàn tiền 20.000 VND trái quy định thay vì từ chối (status resolved != denied). Hậu quả: Pass rate của Swarm giảm từ 1.000 xuống 0.9857 (69/70), Pass^5 giảm từ 1.000 xuống 0.9286 (13/14), Seed variance tăng từ 0.0 lên 0.000816, và chi phí/thành công tăng từ 27.86 VND lên 49.57 VND (+77.9%). Workflow đạt 1.000 pass rate, 1.000 pass^5 và 0.0 variance.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
