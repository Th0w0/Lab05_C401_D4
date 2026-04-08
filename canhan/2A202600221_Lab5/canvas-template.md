# AI Product Canvas — template


---

## Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì? |
| **Trả lời** |User: Hành khách cần tra cứu thông tin bay nhanh — không muốn gọi tổng đài hoặc tự tìm trên web. Pain: Tổng đài chờ lâu, website nhiều bước, không biết hỏi ai ngoài giờ hành chính. AI giải quyết gì? Trả lời 24/7 tức thì cho các câu hỏi lặp lại (giờ bay, giá vé, quy định hành lý) — thứ mà tổng đài tốn người và web tốn thời gian tìm. |Khi AI sai: User nhận thông tin sai về giá/chuyến bay → đặt sai vé → thiệt hại tài chính thực. User biết bằng cách nào? Hầu như không có signal rõ — NEO không nói "tôi không chắc", chỉ trả lời hoặc im. User sửa thế nào? Phải tự hỏi lại, tự đối chiếu web, hoặc gọi hotline — không có flow sửa lỗi trong bot. |Cost/request: Ước lượng thấp — câu hỏi đơn giản, context ngắn, ~$0.001–0.005/request với LLM phổ thông. Latency: Chấp nhận được, <3s với câu thông thường. Risk chính: Trả lời sai thông tin bay/giá vé → user đặt nhầm → khiếu nại, hoàn vé, mất trust thương hiệu hàng không. |

---

## Automation hay augmentation?

☑ Automation — NEO hiện tại trả lời thẳng, không hỏi user có muốn confirm không

**Justify:** NEO đang chạy theo mode automation — đưa ra thông tin giá vé, lịch bay như sự thật tuyệt đối mà không có disclaimer "vui lòng kiểm tra lại trên website". Với domain hàng không (giá vé thay đổi theo giờ, chính sách hoàn/đổi phức tạp), automation ở đây tiềm ẩn rủi ro cao. Nên chuyển sang augmentation — NEO gợi ý + luôn kèm link xác nhận chính thức để user quyết định cuối.

Gợi ý: nếu AI sai mà user không biết → automation nguy hiểm, cân nhắc augmentation.

---

## Learning signal

| # | Câu hỏi | Trả lời |
|---|---------|---------|
| 1 | User correction đi vào đâu? | [?] Không rõ — NEO không có nút "Sai rồi / Không đúng ý tôi". User correction chỉ xảy ra ngầm khi user hỏi lại câu khác, không được thu thập có cấu trúc.|
| 2 | Product thu signal gì để biết tốt lên hay tệ đi? | [?] Không quan sát được từ ngoài — Có thể có log nội bộ, nhưng không có rating, thumbs up/down, hay bất kỳ explicit feedback nào sau mỗi câu trả lời.|
| 3 | Data thuộc loại nào? ☐ User-specific · ☑ Domain-specific · ☑ Real-time · ☐ Human-judgment · ☐ Khác: ___ | |

**Có marginal value không?** (Model đã biết cái này chưa? Ai khác cũng thu được data này không?)
Dữ liệu lịch bay và chính sách là domain-specific của VNA — model chung không có, đây là lợi thế thực sự. Tuy nhiên phần real-time pricing là thách thức lớn: nếu không sync liên tục với hệ thống đặt vé, NEO sẽ trả lời giá cũ → mất trust. Marginal value cao nếu data pipeline được giữ fresh — thấp nếu chỉ dùng data tĩnh.
___

---

*AI Product Canvas — Ngày 5 — VinUni A20 — AI Thực Chiến · 2026*
