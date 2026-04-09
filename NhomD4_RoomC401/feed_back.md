# Feedback — Demo round Day 6

## Nhóm Vinfast_C1

| Tiêu chí | Điểm (1-5) |
|----------|-----------|
| Problem-solution fit | 4 |
| AI product thinking | 4 |
| Demo quality | 3 |

**Điều làm tốt:** 
- **Trải nghiệm đàm thoại mượt mà:** Chatbot trả lời đầy đủ, chi tiết các thông tin do người dùng yêu cầu. Văn phong tự nhiên, giao tiếp lưu loát tạo cảm giác thân thiện và dễ chịu.
- **Có tầm nhìn dài hạn:** Nhóm có định hướng rõ ràng trong việc liên tục cập nhật và cải thiện mô hình AI ở các giai đoạn tiếp theo.

**Gợi ý cải thiện:** 
- **Tăng cường cơ chế kiểm chứng thông tin:** Hiện tại hệ thống dễ "nhẹ dạ" chấp nhận thông tin từ người dùng mà không có validation rõ ràng. Ví dụ nổi cộm: Khi người dùng muốn mua xe VF 5 và tự bịa ra việc đang sở hữu voucher trị giá 20 triệu, chatbot ngay lập tức truy xuất giá và tự động trừ tiền mua xe mà không hề có bước đối chiếu hoặc gọi API kiểm chứng xem voucher đó có hợp lệ/tồn tại hay không.
- **Kiểm soát ảo giác (Hallucination):** Cần trang bị thêm các cơ chế kiểm soát chặt chẽ hơn để giảm thiểu các câu trả lời bịa đặt không có cơ sở.
- **Cải thiện độ chính xác truy xuất:** Phản hồi nhiều lúc chưa bám sát ý định (Hỏi về dòng xe VF 5 nhưng bot lại đi truy xuất thông số và trả lời về VF e34). Việc này cho thấy hệ thống Retrieval và phân tích Intent cần được tối ưu lại.

---

## Nhóm Vinfast_D3

| Tiêu chí | Điểm (1-5) |
|----------|-----------|
| Problem-solution fit | 4 |
| AI product thinking | 4 |
| Demo quality | 3 |

**Điều làm tốt:** 
- **Cơ chế truy xuất tốt:** Ý tưởng truy xuất thông tin của nhóm rất bài bản, chứng tỏ có sự đầu tư trong logic tìm kiếm dữ liệu.

**Gợi ý cải thiện:** 
- **Thiếu tính năng lưu lịch sử (Log History):** Bot hiện chưa có khả năng nhớ context của các lượt nói trước đó, làm giảm trải nghiệm cá nhân hóa. Nhóm nên xây dựng hệ thống lưu log và quản lý biến session.
- **Tính chọn lọc của thông tin:** Câu trả lời đưa ra đôi khi chưa hoàn toàn đáp ứng được đúng yêu cầu trọng tâm, hoặc bị lan man đưa ra các thông tin nằm ngoài phạm vi (out of scope). Cần định nghĩa rõ rào cản (guardrails).
- **Phát triển kịch bản Fallback:** Hệ thống chưa được trang bị cơ chế xử lý dự phòng (fallback) hiệu quả cho các trường hợp bot không hiểu câu hỏi hoặc không tìm được dữ liệu.

---

## Nhóm Vinfast_D2 (Vinfast_D1)

| Tiêu chí | Điểm (1-5) |
|----------|-----------|
| Problem-solution fit | 3 |
| AI product thinking | 4 |
| Demo quality | 4 |

**Điều làm tốt:** 
- **Trình bày chuyên nghiệp:** Phần demo gây ấn tượng nhờ giao diện đẹp, trực quan; các luồng thao tác được thể hiện mượt mà.
- **Tính thực tiễn cao:** Ý tưởng dự án rất tốt, đánh trúng bài toán thực tế và sở hữu nhiều tiềm năng phát triển, mở rộng trong tương lai gần.
- **Quản trị rủi ro tốt:** Nhóm thể hiện khả năng dự đoán vấn đề (AI product thinking) đáng khen khi đã lường trước và tính toán được nhiều cách xử lý cho những trường hợp AI bị sai sót.

**Gợi ý cải thiện:** 
- **Đầu tư thêm cho Chatbot:** Nhóm nên mở rộng các khối module và tập trung phát triển sâu hơn các chức năng tương tác của chatbot để cải tiến toàn diện sản phẩm.
- **Triển khai kiến trúc RAG (Retrieval-Augmented Generation):** Dự án sẽ hoàn thiện và có thông tin chính xác, cập nhật liên tục hơn nếu nhóm nghiên cứu, đưa công nghệ RAG vào luồng xử lý.