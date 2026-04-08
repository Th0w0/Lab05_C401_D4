## 6. Mini AI spec — VinFast AI

### 1) Product giải gì, cho ai?
VinFast AI là một agent tra cứu + tổng hợp giúp người dùng (khách hàng đang cân nhắc mua xe, tư vấn bán hàng/CSKH, nhân viên marketing/sales) nhanh chóng có “hồ sơ” đầy đủ của các dòng **ô tô điện VinFast** mà không cần tự mở nhiều tab và chắp vá thông tin.

Hiện tại, khi cần tra cứu/so sánh, user thường phải tự Google, đọc nhiều bài PR–tin tức–bảng giá rời rạc (thậm chí khác năm, khác khu vực), dễ thiếu mục, và dễ nhầm lẫn giữa xe máy điện/xe xăng/xe concept.

### 2) AI làm gì? (automation hay augmentation)
**Augmentation.** Hệ thống tạo báo cáo cấu trúc để user đọc và dùng ngay, không “tự quyết” thay user. User có thể kiểm tra và chỉnh nếu thấy sai/thiếu.

Luồng chính:
- **Discover (quét danh mục)**: dùng Tavily web search để tìm danh sách phương tiện VinFast và lọc ra **nhóm ô tô (4 bánh trở lên)**. Có rule loại bỏ xe máy điện (Klara, Feliz, Vento, Theon, Evo...) và xe xăng (Fadil, Lux A, Lux SA, President).
- **Research detail (lặp theo từng xe)**: với mỗi xe trong danh sách, tiếp tục search và trích xuất đúng **10 mục**:
  1) Tên xe
  2) Hạng xe
  3) Phiên bản
  4) Tốc độ tối đa
  5) Pin (dung lượng, quãng đường)
  6) Sạc (tại nhà, sạc nhanh, thời gian)
  7) Giá niêm yết (kèm pin/thuê pin nếu có)
  8) Giá lăn bánh KV1 (HN/HCM), KV2 (tỉnh)
  9) Bảo hành (xe & pin)
  10) Giới thiệu chung
- **Summarize (trình bày cuối)**: tổng hợp và trình bày đẹp, mỗi xe một khối, đúng cấu trúc 10 mục.

Ngoài ra, sản phẩm có thêm **tính năng tối ưu lộ trình sạc A → B** dựa trên dữ liệu bản đồ trạm sạc:
- **Input**: điểm xuất phát A, điểm đến B, mẫu xe (để suy ra dung lượng pin/hiệu suất), % pin hiện tại, % pin tối thiểu muốn giữ (reserve), tuỳ chọn (ưu tiên nhanh nhất/ít dừng nhất/chi phí thấp).
- **AI/engine output**: lộ trình gồm các chặng + danh sách trạm sạc đề xuất (tên trạm/toạ độ), mức pin dự kiến khi đến trạm, **thời gian sạc khuyến nghị ở mỗi điểm** (đến % nào thì đi), ETA tổng.
- **Cách AI tham gia**: thuật toán tối ưu (đồ thị/shortest path theo thời gian) tính phương án; LLM chỉ dùng để giải thích lựa chọn, hỏi lại khi thiếu input, và trình bày kế hoạch rõ ràng.

Thiết kế mô hình:
- Dùng model “nhanh/tiết kiệm” để trích xuất từng xe (giảm token/cost khi xử lý nhiều xe).
- Dùng model “chất lượng hơn” cho bước tổng hợp trình bày cuối.

### 3) Quality: tối ưu gì và đo thế nào?
Trong bài toán này, nên **ưu tiên precision hơn recall** ở các mục nhạy cảm (giá, bảo hành, pin/sạc). Lý do: sai các mục này gây mất niềm tin và có thể dẫn đến tư vấn sai; còn thiếu một vài chi tiết user vẫn có thể bổ sung sau.

Các thước đo chất lượng đề xuất:
- **Field accuracy (theo từng mục)**: % mục quan trọng (giá/giá lăn bánh/bảo hành/pin/sạc) đúng so với nguồn tin cậy.
- **Coverage**: % xe có đủ 10 mục; nếu không đủ dữ liệu thì trả “Chưa công bố/Không rõ” thay vì bịa.
- **Freshness**: nguồn/ thông tin gần hiện tại; cảnh báo nếu dữ liệu cũ.
- **Format compliance**: luôn ra đúng 10 mục, không trộn xe máy/xe xăng.

Với tính năng **tối ưu lộ trình sạc**, quality tập trung vào “đi được thật” và “tối ưu đúng mục tiêu”:
- **Route feasibility**: không có chặng nào vượt quá range khả dụng (tính theo reserve + sai số).
- **ETA error**: sai số ETA tổng và thời gian sạc (so với thực tế/benchmark).
- **Success rate**: % chuyến đi hoàn thành mà không phải “replan khẩn cấp”.
- **User satisfaction**: user chọn “dùng theo kế hoạch” vs chỉnh trạm/đổi phương án.

### 4) Rủi ro chính & mitigation
- **Hallucination / suy diễn theo năm mới**: prompt có yêu cầu “ước lượng theo chính sách mới nhất 2026” → rủi ro bịa dữ liệu, user khó phát hiện.
  - Mitigation: bắt buộc kèm **nguồn + thời điểm** cho các mục nhạy cảm; nếu không đủ chứng cứ thì trả “Chưa xác thực”; tách rõ “ước lượng” vs “thông tin xác nhận”.
- **Nhiễu search dẫn đến trộn domain** (lọt xe máy điện/xe xăng hoặc nhầm tên xe).
  - Mitigation: validator theo taxonomy (ô tô vs 2 bánh; concept vs thương mại) + allowlist/denylist.
- **Giá lăn bánh theo khu vực** thay đổi theo phí/thuế/ưu đãi.
  - Mitigation: hiển thị như **khoảng giá + giả định** (khu vực, biển số, ưu đãi) và cho user chỉnh tham số.
- **Sai kế hoạch sạc khiến user “kẹt pin”** (failure mode nguy hiểm nhất vì có thể không biết sai cho đến khi quá muộn).
  - Mitigation: luôn có **reserve**, mô hình tiêu thụ điện có biên an toàn, ưu tiên trạm “chắc chắn hoạt động”, và cung cấp **replan real-time** khi pin/traffic lệch dự kiến; hiển thị rõ giả định (tốc độ, điều hoà, tải, thời tiết).
- **Dữ liệu trạm sạc lỗi thời** (trạm hỏng/đầy/giới hạn công suất).
  - Mitigation: gắn nhãn độ tin cậy theo nguồn + thời gian cập nhật; cho user report “trạm không dùng được”; ưu tiên trạm có tín hiệu live (nếu có).

### 5) Data & flywheel học tập (learning signal)
Tín hiệu học chủ yếu là **human-judgment + domain-specific**:
- User có thể sửa:
  - **Danh sách xe** (thêm/bớt/chuẩn hoá tên: “VF e34” vs “VFe34”).
  - **Từng mục thông tin** (giá/pin/sạc/bảo hành…) và đánh dấu “đúng/sai/thiếu”.
- Hệ thống nên thu:
  - Log “accepted vs corrected” theo từng mục và theo nguồn.
  - Tỷ lệ “Unknown” hợp lý vs bịa.
  - Source quality score (nguồn nào hay gây sai) để ưu tiên nguồn tốt.

Với tối ưu lộ trình sạc, learning signal đến từ hành vi thực tế:
- User chỉnh trạm/đổi thời gian sạc/đổi mục tiêu (nhanh nhất ↔ ít dừng) → dùng làm nhãn preference.
- Sai lệch giữa dự báo và thực tế (SoC khi đến trạm, thời gian sạc thực) → hiệu chỉnh model tiêu thụ và tốc độ sạc theo trạm.
- Report trạm “hỏng/đầy/không tương thích” → cải thiện chất lượng dữ liệu trạm sạc.

Marginal value: mô hình nền có kiến thức chung, nhưng các thông tin theo thị trường VN (giá/khuyến mãi/chính sách) biến động theo thời gian và địa phương, nên feedback + đánh giá nguồn có **giá trị biên cao** để tăng độ tin cậy.

