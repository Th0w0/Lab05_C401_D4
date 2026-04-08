Dựa trên yêu cầu từ ảnh **SPEC draft — 6 items** bạn vừa gửi, mình sẽ thiết lập khung tài liệu (draft) cho con chatbot VinFast (mảng AI cho ô tô/hậu mãi) của bạn. Đây là cách tiếp cận chuẩn "product mindset" cho một dự án AI:

## Problem state
Người dùng tìm kiếm thông tin về sản phẩm và chính sách của VinFast thông qua chatbot, nhưng hệ thống thường cung cấp thông tin sai, thiếu hoặc không cập nhật, trong khi không có cơ chế giúp người dùng nhận biết độ tin cậy của câu trả lời.

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

# 3. Eval-metric
## Eval metrics + threshold
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

# 4. ROI ANALYSIS: 

**Chủ đề:** Tra cứu sản phẩm & Lập kế hoạch di chuyển thông minh (Charging Route Planner).
**Chiến lược:** Độ chính xác dữ liệu (Thông số/Giá) + Tính khả thi của lộ trình (Trạm sạc).

| Kịch bản | **Assumption** | **Cost** | **Benefit** | **Net** |
| :--- | :--- | :--- | :--- | :--- |
| **Conservative** | 100 user. AI trả lời đúng giá, lập lộ trình cơ bản (chưa tối ưu trạm sạc theo pin). | $70/ngày (API LLM + Map cơ bản) | Tiết kiệm 4h tư vấn/ngày. Giảm nỗi lo đi xa cho người mới dùng xe điện. | **+$180** |
| **Realistic** | 500 user. AI tư vấn sâu về dòng xe + Lập lộ trình Hà Nội - Đà Nẵng khớp 99% trạm sạc thực. | $250/ngày (RAG + Real-time Map API) | Thay thế 3 nhân sự trực chat. Tăng 10% tỷ lệ khách để lại thông tin đặt cọc (Lead). | **+$1,350** |
| **Optimistic** | 2000 user. Tự động hóa hoàn toàn bán hàng & dẫn đường. Gợi ý điểm nghỉ theo sở thích. | $650/ngày (Premium Model + High-scale Infra) | Cắt giảm 80% chi phí CSKH. Thu phí Affiliate từ các điểm dừng nghỉ đối tác trên lộ trình. | **+$5,500** |

---

### Kill Criteria (Tiêu chí dừng dự án)
1. **Critical Hallucination:** Sai lệch thông tin giá xe hoặc vị trí trạm sạc > 2 lần/tuần (Gây rủi ro pháp lý hoặc sự cố hết pin giữa đường).
12. **Technical Lag:** Thời gian xử lý lộ trình phức tạp (Hà Nội - Đà Nẵng) > 1 phút.
3. **Adoption Failure:** > 60% khách hàng không hài lòng với lộ trình được gợi ý sau 1 tháng thử nghiệm.

### Ghi chú Logic
* **Investment (Cost):** Chi phí xử lý
* **Return (Benefit):** * *Trực tiếp:* Giảm nhân sự và chi phí vận hành tổng đài.
    * *Gián tiếp:* Giải quyết "Range Anxiety" (Nỗi lo về pin) - rào cản lớn nhất khiến khách hàng chưa xuống tiền mua xe điện VinFast.
* **Safety First:** Hệ thống sử dụng cơ chế kiểm tra chéo (Cross-check): Thông tin trạm sạc được lấy trực tiếp từ Database API của VinFast thay vì để AI tự suy luận.

# 5. Top 3 failure modes

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


# 6. Mini AI spec — VinFast AI

## 1. Product giải gì, cho ai?
VinFast AI là một agent tra cứu + tổng hợp giúp người dùng (khách hàng đang cân nhắc mua xe, tư vấn bán hàng/CSKH, nhân viên marketing/sales) nhanh chóng có “hồ sơ” đầy đủ của các dòng **ô tô điện VinFast** mà không cần tự mở nhiều tab và chắp vá thông tin.

Hiện tại, khi cần tra cứu/so sánh, user thường phải tự Google, đọc nhiều bài PR–tin tức–bảng giá rời rạc (thậm chí khác năm, khác khu vực), dễ thiếu mục, và dễ nhầm lẫn giữa xe máy điện/xe xăng/xe concept.

## 2. AI làm gì? (automation hay augmentation)
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

## 3. Quality: tối ưu gì và đo thế nào?
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

## 4. Rủi ro chính & mitigation
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

## 5. Data & flywheel học tập (learning signal)
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



# Phân công
- Việt: Canvas + User stories
- Tuấn: code agent
- Đạt: Failure modes
- Thư: Eval-metrics
- Hải Ninh: ROI
- Hiếu: Mini AI Spec

## Cách dùng

1. Điền Value trước — chưa rõ pain thì chưa điền Trust/Feasibility
2. Trust: trả lời 4 câu UX (đúng → sai → không chắc → user sửa)
3. Feasibility: ước lượng cost, không cần chính xác — order of magnitude đủ
4. Learning signal: nghĩ về vòng lặp dài hạn, không chỉ demo ngày mai
5. Đánh [?] cho chỗ chưa biết — Canvas là hypothesis, không phải đáp án

---

*AI Product Canvas — Ngày 5 — VinUni A20 — AI Thực Chiến · 2026*
