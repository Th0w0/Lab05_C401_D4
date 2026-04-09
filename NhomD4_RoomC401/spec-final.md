# SPEC — AI Product Hackathon

**Nhóm:** NhomD4_RoomC401

**Track:** 
☑ VinFast 

**Problem statement:** Người dùng gặp khó khăn trong việc tra cứu thông tin xe VinFast chính xác và lo lắng về phạm vi di chuyển (range anxiety) khi lập kế hoạch đi xa, AI giúp cung cấp thông tin chuẩn xác và lộ trình sạc thông minh.

---
## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | User: người quan tâm đến xe VinFast (tìm hiểu, mua xe, support sau mua)

Pain:

- Khó tìm thông tin chính xác, cập nhật (giá, chính sách, xe)
- Phải đọc nhiều nguồn hoặc hỏi nhân viên
- Câu hỏi lặp lại (range, sạc, giá, ưu đãi)
- Phải kết nối với nhân viên nhiều lần trong thời gian ngắn khi muốn nhắn với nhân viên
- Không có chỗ tạo đoạn chat mới

AI giải gì

- Trả lời nhanh 24/7 thay vì chờ nhân viên
- Giảm friction trong tìm hiểu sản phẩm
- Hỗ trợ user trong funnel mua hàng
- Giảm tải CSKH| 
Khi AI sai, có thể gọi nhân viên CSKH.
User của thế sửa sai bằng cách:
- Có dấu tích, khi đánh dấu thì xác định đấy là trả lời sai
- Yêu cầu nhắn tin hoặc gọi cho nhân viên CSKH| ost: thấp, khoảng $0.001/GPT-4o

Latency: ~2–4s (chat response)

Risk chính:

- Hallucination → đưa thông tin sai
- Outdated info (pricing, policy)
- Mất trust → ảnh hưởng trực tiếp conversion
- Legal risk nếu tư vấn sai chính sách
 |

**Automation hay augmentation?** ☐ Automation · ☐ Augmentation
Justify: *Augmentation — user thấy gợi ý và chấp nhận/từ chối, cost of reject = 0*

- Chỉ trả lời thông tin, không tự hành động
- Có thể từ chối câu hỏi ngoài phạm vi
- Có escalation sang nhân viên

=> Augmentation

- Khi không tin không chắc chắn, thông báo user thông tin không chắc hoặc chuyển sang cho nhân viên CSKH
- Đưa ra cảnh báo khi không chắc chắn

**Learning signal:**

1. User correction đi vào đâu? 
- Hệ thống thu thập số lần user raise ticket, số lần phải gọi nhân viên CSKH, số lần và câu hỏi phải hỏi lại nhiều lần
2. Product thu signal gì để biết tốt lên hay tệ đi? 
- Tỷ lệ escalate sang nhân viên
- Tỷ lệ user hỏi lại cùng 1 câu
- Tỷ lệ hỏi lại câu hỏi
- Session drop (user rời chat)
- CSAT sau cha
3. Data thuộc loại nào? ☐ User-specific · ☐ Domain-specific · ☐ Real-time · ☐ Human-judgment · ☐ Khác:
- User-specific
- Domain-specific (xe, pricing, policy)
- Real-time (giá, ưu đãi thay đổi)
- Human-judgment (CSKH sửa / trả lời lại)

Có marginal value không? (Model đã biết cái này chưa?) 
Có, nền tảng rất tốt nhưng chưa fully unlock

Điểm mạnh
- Giải đúng pain (tìm info xe, giảm friction)
- Thiết kế Augmentation hợp lý (có fallback CSKH)
- Có sẵn learning signals (escalate, CSAT, repeat)

Hạn chế
- Data không độc quyền → moat yếu  
- Phụ thuộc freshness (giá, chính sách)  
- Learning loop chưa tận dụng → chưa “tự học”  

Kết luận
- Value có thật, setup rất đúng hướng  
- Chỉ thiếu learning loop + data moat để scale thành lợi thế cạnh tranh
---

## 2. User Stories — 4 paths

Mỗi feature chính = 1 bảng. AI trả lời xong → chuyện gì xảy ra?

### Feature: *Tìm kiếm thông tin xe*

**Trigger:** User nhập câu hỏi về xe (giá, thông số, chính sách) trong chatbot

| Path | Câu hỏi thiết kế | Mô tả |
|------|------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | - Trả lời nhanh, rõ ràng, đúng trọng tâm  
- Có thể kèm context (giá, ưu đãi, range…)  
- User không cần hỏi thêm → kết thúc flow |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | - AI nói rõ: “Thông tin có thể chưa chính xác / đã thay đổi”  
- Hỏi lại để clarify nếu câu hỏi mơ hồ  
- Gợi ý chuyển CSKH khi liên quan giá/policy nhạy cảm |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | - User phát hiện qua thông tin thực tế (giá/policy lệch)  
- AI nên cho phép escalate nhanh → CSKH  
- Gợi ý kiểm tra lại hoặc cung cấp nguồn chính thức |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | - User hỏi lại hoặc đánh dấu câu trả lời sai  
- Log vào system: câu hỏi, response sai, escalation  
- Dùng để cải thiện knowledge & retrieval |

*Lặp lại cho feature thứ 2-3 nếu có.*

### Feature: *Tìm kiếm đường đi phù hợp*

**Trigger:** User nhập câu hỏi tuyến đường từ A đến B

| Path | Câu hỏi thiết kế | Mô tả |
|------|------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | - Hiển thị route rõ ràng (khoảng cách, thời gian)  
- Gợi ý trạm sạc phù hợp trên đường  
- Có thể kèm số lần sạc cần thiết  
- User đủ thông tin để di chuyển → kết thúc |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | - Yêu cầu trả lời rõ điểm A/B nếu mơ hồ  
- Báo: “Route có thể chưa tối ưu / thiếu trạm sạc”  
- Gợi ý kiểm tra Google Maps |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | - Route bất hợp lý (vòng, xa, thiếu trạm sạc)  
- ETA / khoảng cách sai lệch rõ  
- Recover: user hỏi lại hoặc dùng app map ngoài |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | - User nhập lại điểm chính xác hơn hoặc route khác  
- Log lại query + route bị reject  
- Dùng để cải thiện routing & placement trạm sạc |

## Mở rộng (optional — bonus)

### Transition flow giữa các path

Vẽ diagram hoặc mô tả: user chuyển từ path này sang path khác thế nào?

```
Happy → Failure: User tin AI đúng → sau đó phát hiện sai (giá/route lệch)
→ UX nên: luôn kèm disclaimer nhẹ + link verify

Low-confidence → Happy: AI hỏi lại → user clarify → trả lời đúng
→ UX nên: giữ context + học từ query đã clarify

Failure → Correction → Happy: User hỏi lại / sửa → AI trả lời đúng hơn
→ UX nên: log correction + ưu tiên pattern này lần sau

Failure → Bỏ dùng: Sai nhiều lần → user mất trust
→ UX nên: sau 2–3 lần fail → auto đề xuất CSKH / nguồn chính thức
```

- Mỗi mũi tên = 1 điểm thiết kế UX. Bao nhiêu lần failure trước khi user bỏ dùng?
- Transition nào product đang không hỗ trợ?

### Edge cases

Liệt kê 3-5 tình huống biên mà AI sẽ gặp khó:

| Edge case | Dự đoán AI sẽ xử lý | UX nên phản ứng |
|-----------|---------------------|----------------|
| Input tiếng Anh / viết tắt | Hiểu sai hoặc không map đúng intent | Normalize + detect language → hỏi lại nhẹ |
| Địa điểm mơ hồ (VD: “đi Hà Nội”) | Route sai / thiếu điểm cụ thể | Yêu cầu rõ A/B (quận, địa chỉ) |
| Input quá ngắn (“giá VF8”) | Thiếu context (phiên bản, pin…) | Hỏi lại + đưa option chọn nhanh |
| Input quá dài / nhiều ý | Trả lời lan man / thiếu trọng tâm | Tách intent → trả lời từng phần |
| Không có trạm sạc trên route | AI vẫn cố trả lời | Báo rõ “không đủ dữ liệu” + gợi ý route khác |

### Câu hỏi mở rộng

- Nếu user sửa AI 10 lần liên tiếp, UI có nên thay đổi hành vi không? (VD: tắt auto, chuyển sang gợi ý)
Có — nên đổi behavior:
- Sau 2–3 lần fail:
  - Giảm auto-answer  
  - Tăng clarify  
  - Gợi ý CSKH mạnh hơn 
- User mới vs user cũ: 4 paths có cần thiết kế khác nhau không?
Có — nên khác:
- User mới:
  - Nhiều hướng dẫn + clarify  
- User cũ:
  - Trả lời nhanh hơn, ít hỏi lại  
  - Dựa vào history 
- Nếu 2 user sửa AI theo 2 hướng ngược nhau, hệ thống ưu tiên ai?
Ưu tiên theo:
- Nguồn chính thức (policy, pricing)  
- Tần suất + consistency  
- CSKH confirm  


---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** ☑ Precision · ☐ Recall
Tại sao? Trong tư vấn giá xe và trạm sạc, sai sót (False Positive) có thể dẫn đến rủi ro pháp lý hoặc rủi ro an toàn (hết pin giữa đường). Ưu tiên trả lời đúng tuyệt đối hơn là cố trả lời nhiều.

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| Accuracy (Giá & Thông số) | ≥95% | <85% trong 3 ngày liên tiếp |
| Success Route Feasibility | 100% | Có ≥1 case người dùng bị kẹt pin do AI tính sai range |
| Latency (Route Planning) | <5s | >10s cho các chặng dài (>500km) |
| User Satisfaction (CSAT) | ≥4.2/5 | <3.5/5 |

---

## 4. Top 3 failure modes

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | Truy xuất dữ liệu cũ/thiếu về phiên bản xe mới | User nhận thông tin sai, đưa ra quyết định mua sai lầm, mất trust nghiêm trọng. | Luôn hiển thị timestamp "Dữ liệu cập nhật ngày..." và link nguồn. |
| 2 | Sai lệch dự báo tiêu thụ pin (do thời tiết/tải trọng/tốc độ) | Lộ trình AI gợi ý khiến xe không tới được trạm tiếp theo. | Luôn giữ biên an toàn (Reserve) ≥15-20% pin. Cho phép user điều chỉnh "phong cách lái". |
| 3 | Trạm sạc trên lộ trình bị đầy hoặc hỏng đột xuất | User đến trạm nhưng phải chờ lâu hoặc không sạc được, gây hỏng kế hoạch di chuyển. | Tích hợp dữ liệu Live Status của trạm sạc. Gợi ý thêm các trạm "Surrounding stations" để dự phòng. |

---

## 5. ROI 3 kịch bản

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 100 user/ngày, AI trả lời đúng giá, lộ trình cơ bản. | 500 user/ngày, tư vấn sâu, lộ trình khớp 99% thực tế. | 2000 user/ngày, tự động hóa CSKH & Lead gen, gợi ý dịch vụ đối tác. |
| **Cost** | $70/ngày (API + Bản đồ) | $250/ngày (RAG + Real-time Map) | $650/ngày (Premium Models + Scale) |
| **Benefit** | Tiết kiệm 4h tư vấn/ngày. Giảm nỗi lo đi xa. | Thay thế 3 nhân sự chat. Tăng 10% Lead đặt cọc. | Cắt giảm 80% chi phí CSKH. Thu phí Affiliate từ điểm nghỉ. |
| **Net** | **+$180** | **+$1,350** | **+$5,500** |

**Kill criteria:** Tỷ lệ lỗi tính toán lộ trình (Route Error) khiến khách hàng phàn nàn > 5% trong 1 tháng.

---

## 6. Mini AI spec (1 trang)

Chatbot VinFast "Smart EV Assistant" là một Agent hỗ trợ toàn diện người dùng trong hệ sinh thái xe điện.

- **Mục tiêu**: Giải quyết pain-point về "nhiễu thông tin" khi tìm hiểu xe và "nỗi lo hết pin" khi di chuyển xa.
- **AI Core**: 
    - Hiện tại chỉ sử dụng Tavily để search các thông tin mới nhất từ các sản phẩm nhưng tương lai sẽ sử dụng **RAG (Retrieval-Augmented Generation)** để truy xuất thông tin từ Knowledge Base chính thức của VinFast (giá, thông số, chính sách).
    - Sử dụng **Optimization Engine** kết hợp LLM để lập lộ trình sạc. AI tính toán dựa trên: mẫu xe, dung lượng pin, hiệu suất tiêu thụ và mạng lưới trạm sạc VinFast.
- **Tính năng an toàn pin**: Kiểm tra các trạm sạc xung quanh (surrounding stations) và đảm bảo dung lượng pin dự phòng (reserve) giúp người dùng yên tâm.
- **Triết lý thiết kế**: Ưu tiên **Precision** (độ chính xác). Bot sẽ báo "Chưa rõ" hoặc "Chuyển nhân viên" thay vì tự ý bịa số liệu nhạy cảm.
- **Data Flywheel**: Càng nhiều người dùng report về tình trạng trạm sạc và chỉnh sửa lộ trình, AI càng học được các điểm dừng ưa thích và các khu vực thiếu trạm để tối ưu khuyến nghị trong tương lai.
