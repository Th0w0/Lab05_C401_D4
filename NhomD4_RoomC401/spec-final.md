# SPEC — AI Product Hackathon

**Nhóm:** NhomD4_RoomC401

**Track:** 
☑ VinFast 

**Problem statement:** Người dùng gặp khó khăn trong việc tra cứu thông tin xe VinFast chính xác và lo lắng về phạm vi di chuyển (range anxiety) khi lập kế hoạch đi xa, AI giúp cung cấp thông tin chuẩn xác và lộ trình sạc thông minh.

---

## 1. AI Product Canvas


## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | Nhóm 1 — Người đang cân nhắc mua xe: Pain là nhiễu thông tin — giá lăn bánh, chính sách ưu đãi thay đổi liên tục, không biết nguồn nào đáng tin. Nhóm 2 — Người đã có xe VinFast: Pain là range anxiety — không tự tin lập lịch trình đi xa vì không biết trạm sạc ở đâu, còn hoạt động không.AI giải: Agent 2-trong-1 — (1) tra cứu thông số/giá/chính sách từ Knowledge Base mới nhất; (2) lập lộ trình sạc thông minh dựa trên mẫu xe, dung lượng pin, mạng lưới trạm VinFast. | AI sai (giá cũ, trạm hỏng): Gây mất niềm tin hoặc kẹt pin. User sửa: Report lỗi dữ liệu, yêu cầu nhân viên xác nhận, hoặc điều chỉnh trạm sạc thủ công. | ~$0.002/request, latency <3s. Risk: Hallucination về giá/chính sách thương mại và dữ liệu trạm sạc không live (đang bảo trì). |

**Automation hay augmentation?** ☐ Automation · ☑ Augmentation
Justify: AI gợi ý thông tin và lộ trình, người dùng là người ra quyết định cuối cùng (đặt cọc xe hoặc chọn dừng ở trạm nào).

**Learning signal:**

1. User correction đi vào đâu?
   - **Sai giá/thông số** → Correction log phân loại → Admin review và cập nhật Knowledge Base. [?] Review cycle chưa xác định — hàng ngày hay hàng tuần?
   - **Đổi trạm sạc** → Preference log ghi nhận pattern (ưu tiên trạm có tiện ích, tránh trạm hay đầy) → dùng để cải thiện gợi ý lộ trình về sau.

2. Product thu signal gì để biết tốt lên hay tệ đi?
   - **Tỷ lệ escalate sang nhân viên** (%): Tăng liên tục 3 ngày → dấu hiệu KB lỗi thời hoặc prompt cần review.
   - **Tỷ lệ user theo lộ trình AI** (%): Dưới 60% user không đổi trạm sau khi nhận gợi ý → xem lại logic tính range.
   - **Session drop rate** (%): Trên 40% user rời đi giữa chừng → xem lại UX hoặc chất lượng trả lời.

3. Data thuộc loại nào? ☐ User-specific · ☑ Domain-specific · ☑ Real-time · ☐ Human-judgment · ☐ Khác
   Có marginal value không? Có — model nền không biết chính sách VinFast 2026 và tình trạng trạm sạc thời gian thực. Đây là lợi thế cạnh tranh duy nhất so với ChatGPT thông thường; nếu KB không được cập nhật liên tục thì lợi thế mất đi.

**Vòng lặp dài hạn (Data Flywheel):** Càng nhiều user report tình trạng trạm + điều chỉnh lộ trình → AI học được điểm dừng ưa thích và khu vực thiếu trạm → lộ trình ngày càng khớp thực tế hơn.


## 2. User Stories — 4 paths

### Feature 1: Tra cứu sản phẩm
**Trigger:** User hỏi về thông số, giá lăn bánh hoặc ưu đãi của một dòng xe (e.g., VF 3, VF 7).

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Bot đưa bảng thông số/giá chính xác, kèm nguồn xác thực. User hài lòng và có thể hỏi thêm về trả góp. |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | Bot báo "Thông tin về ưu đãi này có thể thay đổi tùy đại lý", gợi ý user để lại SĐT để nhân viên tư vấn gọi lại. |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | AI đưa giá cũ -> User thấy mâu thuẫn với web chính thức -> Click nút "Báo lỗi dữ liệu" hoặc "Chat với nhân viên". |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User comment: "Giá này là đời 2024 rồi" -> Log lưu lại để Admin cập nhật Knowledge Base. |

### Feature 2: Lập lộ trình & Trạm sạc (Charging Route Planner)
**Trigger:** User hỏi "Tôi muốn đi từ Hà Nội tới Vinh bằng VF 8, hãy lập lịch trình sạc." hoặc "Trạm sạc gần nhất ở đâu?".

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Lộ trình chi tiết: Các chặng dừng tại trạm sạc VinFast, thời gian sạc ước tính, mức pin dự kiến. User chọn "Gửi đến xe". |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | Trạm sạc tại điểm dừng đang có báo cáo bảo trì -> AI gợi ý 2 trạm dự phòng xung quanh để user lựa chọn. |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | AI gợi ý lộ trình quá xa so với dung lượng pin thực tế -> User thấy cảnh báo "Phạm vi không khả thi" hoặc nhận ra khi đi giữa đường -> Yêu cầu tìm trạm khẩn cấp. |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User chọn đổi trạm dừng khác -> AI ghi nhận preference (ưu tiên trạm dừng có quán cafe/nhà hàng). |

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
