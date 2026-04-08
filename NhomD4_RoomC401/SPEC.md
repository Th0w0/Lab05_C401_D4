Dựa trên yêu cầu từ ảnh **SPEC draft — 6 items** bạn vừa gửi, mình sẽ thiết lập khung tài liệu (draft) cho con chatbot VinFast (mảng AI cho ô tô/hậu mãi) của bạn. Đây là cách tiếp cận chuẩn "product mindset" cho một dự án AI:

---
# 1. AI Product Canvas
## Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì? |
| **Trả lời** | User: người quan tâm đến xe VinFast (tìm hiểu, mua xe, support sau mua)

Pain:

- Khó tìm thông tin chính xác, cập nhật (giá, chính sách, xe)
- Phải đọc nhiều nguồn hoặc hỏi nhân viên
- Câu hỏi lặp lại (range, sạc, giá, ưu đãi)
- Phải kết nối với nhân viên nhiều lần trong thời gian ngắn khi muốn nhắn với nhân viên
- Không có chỗ tạo đoạn chat mới

Auto hay Aug?

- Augmentation (chatbot hỗ trợ, không tự quyết định)

Value khi AI đúng

- Trả lời nhanh 24/7 thay vì chờ nhân viên
- Giảm friction trong tìm hiểu sản phẩm
Hỗ trợ user trong funnel mua hàng
Giảm tải CSKH |

Precision hay recall?

- Ưu tiên precision (trả lời đúng hơn là trả lời nhiều)
- Nhưng thực tế precision chưa ổn (trả lời sai / thiếu / outdated)

Khi sai → user biết/sửa thế nào?

User phát hiện qua:
- Thông tin mâu thuẫn
- Không khớp thực tế (giá, chính sách)
- Không có cảnh báo “AI có thể sai”
- User không sửa được AI (chỉ có thể hỏi lại)

Trust recovery?

Có:
- Escalate sang nhân viên khi không trả lời được
- Hỏi lại khi câu hỏi mơ hồ
Thiếu:
- Show confidence|

Cost: thấp, khoảng $0.001/GPT-4o

Latency: ~2–4s (chat response)

Risk chính:

- Hallucination → đưa thông tin sai
- Outdated info (pricing, policy)
- Mất trust → ảnh hưởng trực tiếp conversion
- Legal risk nếu tư vấn sai chính sách

Dependency

- Knowledge base nội bộ (pricing, sản phẩm, policy)
- Cập nhật data liên tục
- LLM / chatbot system
- CRM / CSKH system |

---

## Automation hay augmentation?

☐ Automation — AI làm thay, user không can thiệp
☐ Augmentation — AI gợi ý, user quyết định cuối cùng

**Justify:** ___

Hiện tại VinFast chatbot:

- Chỉ trả lời thông tin, không tự hành động
- Có thể từ chối câu hỏi ngoài phạm vi
- Có escalation sang nhân viên

=> Augmentation

Tuy nhiên vấn đề:

- Nếu trả lời sai → user không biết ngay
- Không có cơ chế verify

Hướng cải thiện:

- Thêm source + timestamp (“cập nhật ngày…”)
- Show confidence level
- Cho phép “xác nhận với nhân viên” ngay trong UI
---

## Learning signal

| # | Câu hỏi | Trả lời |
|---|---------|---------|
| 1 | User correction đi vào đâu? | Hiện tại gần như không rõ ràng; nếu có thì thông qua escalation sang nhân viên (human-in-the-loop), chưa thấy learning trực tiếp từ user|
| 2 | Product thu signal gì để biết tốt lên hay tệ đi? | 
- Tỷ lệ escalate sang nhân viên
- Tỷ lệ user hỏi lại cùng 1 câu
- Session drop (user rời chat)
- CSAT sau chat|
| 3 | Data thuộc loại nào? ☐ User-specific · ☐ Domain-specific · ☐ Real-time · ☐ Human-judgment · ☐ Khác: ___ | - User-specific
- Domain-specific (xe, pricing, policy)
- Real-time (giá, ưu đãi thay đổi)
- Human-judgment (CSKH sửa / trả lời lại)|

**Có marginal value không?** (Model đã biết cái này chưa? Có, nhưng trung bình (không quá mạnh)

Lý do:

1. Domain-specific nhưng không độc quyền
- Thông tin xe, giá, chính sách có thể public
- Đối thủ cũng có thể thu thập
2. Value phụ thuộc vào freshness (độ mới của data)
- Nếu không update liên tục → AI mất giá trị
3. Learning loop chưa mạnh
- Chưa tận dụng tốt feedback từ user
- Phụ thuộc nhiều vào human support

Kết luận:

- Moat không nằm ở model
- Mà nằm ở: Data cập nhật nhanh và integration với hệ thống CSKH
___

# 2. User Stories
---
Dùng framework 4 paths để mổ xẻ sản phẩm:

| Path | Câu hỏi |
|------|---------|
| 1. Khi AI **đúng** | -Nhận được câu trả lời nhanh, rõ ràng
- Thông tin có vẻ hợp lý (giá xe, thông số, chính sách)
- Không cần tìm thêm nguồn khác |
| 2. Khi AI **không chắc** | - Có hỏi lại khi câu hỏi mơ hồ (điểm tốt)
- Có thể: từ chối câu hỏi ngoài phạm vi
- Nhưng:
+ Không show alternatives
+ Không nói “tôi không chắc”
+ Không hiển thị mức độ confidence |
| 3. Khi AI **sai** | - So sánh với thực tế (giá, chính sách)
- Nhận ra thông tin:
+ outdated
+ thiếu
+ mâu thuẫn
User sửa bằng cách nào?
- Không thể sửa trực tiếp AI
- Chỉ có thể:
+ hỏi lại
+ hoặc hỏi nhân viên
- Bao nhiêu bước?
+ Nhiều bước:
- Nhận ra sai
- Hỏi lại / đổi cách hỏi
- Nếu vẫn sai → escalate |
| 4. Khi user **mất tin** | - Có exit không?
- Có: dừng chat, chuyển kênh khác
- Có fallback, chuyển sang nhân viên (điểm mạnh)
- Dễ tìm không: Bình thường |

**Tự phân tích:**
- Path nào sản phẩm xử lý tốt nhất? Tại sao?
Path 1 xử lý tốt nhất
Lý do:

+ Core strength của chatbot
+ Đáp ứng tốt use case FAQ đơn giản
+ Tốc độ + tiện lợi

- Path nào yếu nhất hoặc không tồn tại?
+ Path 3 là path yếu nhất
Lý do vì Không có:
+ error detection
+ correction flow
+ explainability
- User phải tự “debug AI”

- Kỳ vọng từ marketing khớp thực tế không? Gap ở đâu?
Marketing kỳ vọng:
+ Chatbot thông minh
+ Trả lời chính xác
+ Hỗ trợ toàn diện
Reality:
Tốt ở:
+ câu hỏi đơn giản
Yếu ở:
+ câu hỏi cần thông tin cập nhật
+ câu hỏi phức tạp





## Cách dùng

1. Điền Value trước — chưa rõ pain thì chưa điền Trust/Feasibility
2. Trust: trả lời 4 câu UX (đúng → sai → không chắc → user sửa)
3. Feasibility: ước lượng cost, không cần chính xác — order of magnitude đủ
4. Learning signal: nghĩ về vòng lặp dài hạn, không chỉ demo ngày mai
5. Đánh [?] cho chỗ chưa biết — Canvas là hypothesis, không phải đáp án

---

*AI Product Canvas — Ngày 5 — VinUni A20 — AI Thực Chiến · 2026*
