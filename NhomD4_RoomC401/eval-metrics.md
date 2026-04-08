# Eval metrics + threshold
**Tại sao precision?**
Chatbot trả lời về giá xe, chi phí sạc, chính sách bảo hành của VinFast — nếu sai sẽ làm mất niềm tin và ảnh hưởng trực tiếp đến quyết định mua. Sai thông tin (false positive) nguy hiểm hơn không trả lời.

Nếu sai ngược lại thì sao? Nếu optimize recall, chatbot trả lời nhiều hơn nhưng dễ hallucinate (bịa thông tin), user thấy nói linh tinh thì mất trust và không sử dụng chat bot nữa.

## Metrics table

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| Precision | ≥90% | <80% trong 1 tuần |
| Latency | <2s | >5s |
| Escalation rate | <30% | >50% |
| User satisfaction | ≥4/5 | <3/5 trong 2 tuần |

**Nguyên tắc thiết kế:**  
Hệ thống cần tối ưu độ chính xác cao để duy trì niềm tin, độ trễ thấp để đảm bảo trải nghiệm người dùng tốt, và tỷ lệ chuyển sang nhân viên thấp để tạo ra giá trị kinh doanh thực sự.