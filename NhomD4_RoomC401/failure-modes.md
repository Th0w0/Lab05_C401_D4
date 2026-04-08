# Top 3 failure modes

Liệt kê cách product có thể fail, không phải list features.

> **"Failure mode nào user KHÔNG BIẾT bị sai? Đó là cái nguy hiểm nhất."**

---

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | User ra chỉ thị rõ ràng: "Đưa ra top 10 xe của VinFast" nhưng model không tuân thủ ràng buộc số lượng và chỉ trả về top 5 | User không nhận đủ phương án để so sánh, có thể tưởng hệ thống đã trả lời đầy đủ. Lỗi khó bị phát hiện nếu user không đếm kỹ, làm giảm trust vào chatbot tư vấn mua xe | Nhấn mạnh explicit constraints trong prompt hệ thống. Thêm bước self-check trước khi trả lời: kiểm tra số item có đúng với yêu cầu hay không. Nếu không đủ 10 thì bot phải nói rõ "hiện chỉ tìm thấy X mẫu" thay vì tự cắt ngắn |
| 2 | User hỏi "VF3 có mấy phiên bản?" nhưng hệ thống RAG truy xuất thiếu hoặc dùng dữ liệu cũ nên chỉ lấy ra 1 phiên bản trong khi thực tế có 2 | Chatbot trả lời sai nhưng nghe vẫn rất hợp lý, khiến khách hiểu sai về sản phẩm và ra quyết định dựa trên thông tin thiếu. Đây là lỗi âm thầm vì user thường không biết để phản biện | Viết lại prompt để ưu tiên truy xuất facts từ KB trước khi trả lời. Gắn thời gian cập nhật của dữ liệu vào câu trả lời. Nếu tài liệu truy xuất không đủ rõ hoặc có xung đột, bot phải báo chưa chắc chắn và chuyển sang nguồn chính thức / nhân viên hỗ trợ |
| 3 | User hỏi "So sánh VF 7 với Hyundai Tucson giúp tôi" — chatbot chỉ liệt kê ưu điểm VinFast mà lược bỏ nhược điểm, tạo bảng so sánh thiên vị một chiều | Khách hàng ra quyết định mua dựa trên bảng so sánh không khách quan. Nếu sau mua phát hiện thông tin sai lệch, thiệt hại uy tín thương hiệu lớn hơn nhiều so với mất một đơn hàng. Đặc biệt nguy hiểm vì dạng bảng so sánh khiến user tin rằng dữ liệu đã được kiểm chứng | Giới hạn scope: chỉ so sánh bằng dữ liệu có trong Knowledge Base chính thức, thông số đối thủ phải ghi rõ nguồn và ngày cập nhật. Nếu không có dữ liệu đối thủ thì bot phải từ chối so sánh và gợi ý user kiểm tra trang chính hãng. Thêm disclaimer tự động: "Thông số đối thủ có thể thay đổi, vui lòng xác nhận tại hãng" |

---

## Kết luận

**Failure #2 — RAG truy xuất sai/thiếu thông tin sản phẩm — là nguy hiểm nhất.**

Lý do:

1. **User không thể tự phát hiện lỗi.** Với failure #1 (thiếu số lượng), user có thể đếm lại. Với failure #3 (so sánh thiên vị), user có thể tra cứu đối thủ để kiểm chứng. Nhưng failure #2 thì chatbot trả lời rất tự tin, nghe hoàn toàn hợp lý — khách hàng không có lý do gì để nghi ngờ và cũng không biết phải kiểm tra ở đâu.
2. **Ảnh hưởng trực tiếp đến quyết định mua.** Khách hàng chọn phiên bản xe dựa trên thông tin sai → mua xong mới biết có phiên bản phù hợp hơn → khiếu nại, mất lòng tin thương hiệu.
3. **Khó phát hiện ở quy mô lớn.** Lỗi chỉ xảy ra khi dữ liệu KB lỗi thời hoặc thiếu, không có pattern rõ ràng để monitor — khác với failure #1 (đếm được) hay #3 (detect bằng keyword matching).

