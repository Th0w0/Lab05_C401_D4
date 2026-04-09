# ⚡ VinFast Smart Assistant 2026

> **Nhóm:** NhomD4 — Room C401  
> **Track:** VinFast AI Hackathon  
> **Mô tả:** Trợ lý AI 2-trong-1 giúp người dùng tra cứu thông tin xe VinFast và lập lộ trình sạc thông minh cho hành trình xa.

---

## 🎯 Problem Statement

Người dùng gặp hai pain-point lớn trong hệ sinh thái xe điện VinFast:

1. **Nhiễu thông tin** — Giá lăn bánh, chính sách ưu đãi thay đổi liên tục, khó xác định nguồn tin cậy.
2. **Range Anxiety (nỗi lo hết pin)** — Không tự tin lập lịch trình đi xa vì không biết trạm sạc ở đâu, còn hoạt động hay không.

**Giải pháp:** Một Agent AI duy nhất xử lý cả hai luồng — tra cứu thông số/giá chính xác từ Knowledge Base nội bộ, đồng thời tự động lập lộ trình sạc tối ưu dựa trên model xe và tình trạng pin.

---

## 🏗️ Kiến trúc hệ thống

```
User Input
    │
    ▼
┌─────────────┐
│ router_node │  ← Phân loại ý định bằng Regex + Từ khóa
└──────┬──────┘
       │
  ┌────┴────────────────────┬──────────────────┐
  ▼                         ▼                  ▼
trip_planner_node      researcher_node    chat_normal_node / out_of_scope_node
  │                         │
  │  (EVTripPlanner         │  (car_agent_app: Local JSON)
  │   + Geoapify API        │   (Tavily Search: Trạm sạc)
  │   + Dijkstra)           │
  └────────────┬────────────┘
               ▼
       final_summarizer_node
       (GPT-4o — Viết lại chuyên nghiệp)
               │
               ▼
          Gradio UI
```

**Stack công nghệ:**

| Layer | Công nghệ |
|---|---|
| Orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) `StateGraph` |
| LLM (Fast) | GPT-4o-mini — Routing, Trích xuất JSON, Tóm tắt nhanh |
| LLM (Final) | GPT-4o — Tổng hợp phản hồi chuyên nghiệp |
| Web Search | [Tavily](https://tavily.com/) — Tìm thông tin trạm sạc realtime |
| Route API | [Geoapify](https://www.geoapify.com/) — Tính khoảng cách, thời gian thực tế |
| UI | [Gradio](https://gradio.app/) `gr.Blocks` với dark-mode glassmorphism |
| Memory | LangGraph `MemorySaver` — Lưu lịch sử hội thoại theo session |
| Cache | In-Memory `SESSION_CACHE` — Tránh gọi API lặp lại |

---

## 🗂️ Cấu trúc thư mục

```
Lab05_C401_D4/
├── app.py                  # Entry point — khởi chạy Gradio UI
├── src/
│   ├── agent.py            # Car Knowledge Agent (LangGraph đơn node, đọc JSON nội bộ)
│   ├── tools.py            # EVTripPlanner — Dijkstra routing Engine + Data Models
│   ├── toolsCS.py          # Main Agent — Multi-node LangGraph + Gradio UI
│   ├── .env                # API Keys (OPENAI, TAVILY, GEOAPIFY)
│   └── .gitignore
├── data/
│   ├── Danh_Sach_Xe_Toi_Uu.json   # Knowledge Base xe VinFast nội bộ
│   └── data_update.json            # Trạm sạc do user đóng góp (Data Flywheel)
├── NhomD4_RoomC401/
│   ├── spec-final.md       # AI Product Canvas, User Stories, Eval Metrics
│   └── spec-draft.md       # Tài liệu nháp
└── README.md
```

---

## 🤖 Chi tiết các Agent Nodes

### 1. `router_node` — Bộ định tuyến
Phân loại ý định người dùng bằng Regex + Word Boundary matching. Gồm 4 nhánh:

| Route | Kích hoạt khi |
|---|---|
| `trip_planner` | Nhắc đến "đi từ", "đến", "lộ trình", "chặng"... |
| `researcher` | Nhắc đến "xe", "VF", "giá", "thông số", "pin"... |
| `chat_normal` | Lời chào ngắn < 5 từ ("chào", "hello", "cảm ơn"...) |
| `out_of_scope` | Không khớp bất kỳ nhóm nào (từ chối lịch sự) |

### 2. `trip_planner_node` — Lập lộ trình sạc
- Dùng GPT-4o-mini để trích xuất `origin`, `destination`, `vehicle_name`, `start_soc` từ câu hỏi tự nhiên
- Gọi `EVTripPlanner` (Dijkstra graph-based) với Geoapify API để tính lộ trình tối ưu
- Hiển thị biểu đồ pin từng chặng bằng ký tự `█░`
- Hỗ trợ các policy: `min_time`, `min_cost`, `min_stops`, `balanced`

### 3. `researcher_node` — Tra cứu sản phẩm (Hybrid RAG)
- **Luồng Xe:** Gọi `car_agent_app` (đọc JSON nội bộ `Danh_Sach_Xe_Toi_Uu.json`). Nếu `NOT_FOUND` thì trả về hướng dẫn nhập đúng tên xe — không fallback sang nguồn ngoài.
- **Luồng Trạm sạc:** Dùng Tavily để tìm kiếm realtime, tóm tắt bằng GPT-4o-mini.
- **Chặn hãng xe khác:** Tự động từ chối nếu phát hiện Toyota, Honda, Tesla, BYD...

### 4. `final_summarizer_node` — Tổng hợp phản hồi
Nhận raw data từ researcher hoặc trip_planner, viết lại thành câu trả lời lịch sự, Markdown sạch sẽ, dùng GPT-4o.

### 5. `car_agent_app` (`agent.py`) — Car Knowledge Sub-Agent
Agent đơn node riêng biệt: đọc toàn bộ JSON nội bộ, dùng LLM để trích xuất thông số thô (giá, kích thước, pin...) theo yêu cầu. Trả về raw data format để `researcher_node` và `final_summarizer_node` xử lý tiếp.

---

## 🛣️ EVTripPlanner — Routing Engine

File `src/tools.py` chứa thuật toán Dijkstra lập lộ trình sạc, bao gồm:

- **Data Models:** `Vehicle`, `BatteryState`, `Charger`, `RouteInfo`, `PlannerPolicy`, `PlannerResult`
- **TravelTimeTool:** Gọi Geoapify API để geocode địa điểm và tính khoảng cách/thời gian thực tế
- **EnergyConsumptionTool:** Ước tính tiêu thụ năng lượng (kWh) theo quãng đường và xe
- **ChargingTimeTool:** Tính thời gian sạc từ SOC hiện tại đến target
- **ChargingCostTool:** Tính chi phí sạc theo giá điện từng trạm (VND/kWh)
- **ChargingStationSelector:** Tìm trạm sạc trong hành lang route (corridor) dựa trên polyline
- **EVTripPlanner:** Xây dựng đồ thị, chạy Dijkstra với các policy khác nhau

**Charging Stations đã có sẵn:** Hà Nội → Thanh Hóa → Vinh → Hà Tĩnh → Quảng Bình → Huế → Đà Nẵng

---

## 🖥️ Giao diện (Gradio UI)

- **Dark Mode glassmorphism** với custom CSS
- **2 cột:**
  - *Trái:* Form đóng góp trạm sạc mới (Google Maps embed preview, kiểm tra trùng lặp, lưu vào `data_update.json`)
  - *Phải:* ChatInterface với streaming token-by-token và semantic cache
- **Streaming output:** Phản hồi hiển thị realtime từng token thay vì chờ toàn bộ

---

## 🚀 Cài đặt & Chạy

### 1. Cài đặt môi trường

```bash
pip install langchain-openai langgraph gradio tavily-python requests python-dotenv
```

### 2. Cấu hình API Keys

Tạo file `src/.env`:

```env
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
GEOAPIFY_API_KEY=your_geoapify_key
```

### 3. Chạy ứng dụng

```bash
python app.py
```

Mở trình duyệt tại `http://localhost:7860` hoặc sử dụng link Gradio Share được tạo tự động.

### 4. Chạy standalone (chỉ Trip Planner)

```bash
python src/tools.py
```

---

## 💬 Ví dụ sử dụng

| Câu hỏi | Agent xử lý |
|---|---|
| `Giá lăn bánh VF 8 tại Hà Nội là bao nhiêu?` | researcher → car_agent_app → summarize |
| `Tôi muốn đi từ Hà Nội đến Đà Nẵng bằng VF 8, pin 80%` | trip_planner → summarize |
| `Trạm sạc VinFast gần Bãi Cháy ở đâu?` | researcher → Tavily → summarize |
| `Chào bạn!` | chat_normal |
| `Giá xe Toyota Camry bao nhiêu?` | researcher (⛔ chặn hãng khác) |

---

## 📊 Eval Metrics & Ngưỡng an toàn

| Metric | Target | Red Flag |
|---|---|---|
| Accuracy (Giá & Thông số) | ≥ 95% | < 85% trong 3 ngày liên tiếp |
| Route Feasibility | 100% | ≥ 1 case kẹt pin do AI tính sai |
| Latency (Route Planning) | < 5s | > 10s với chặng > 500 km |
| CSAT | ≥ 4.2/5 | < 3.5/5 |

---

## 🔮 Future Improvements

### Ngắn hạn

- [ ] **Live Charging Station Status** — Tích hợp API thời gian thực tình trạng trạm (đầy/hỏng/bảo trì) thay vì dữ liệu tĩnh
- [ ] **RAG thay thế JSON đọc thẳng** — Dùng vector store (FAISS/Chroma) với embedding để tra cứu chính xác hơn khi KB lớn dần
- [ ] **Driving Profile** — Cho phép user chọn phong cách lái (bình thường / tiết kiệm / sport) để tính tiêu thụ pin sát thực tế hơn
- [ ] **Multi-destination routing** — Hỗ trợ hành trình nhiều điểm dừng (A → B → C) thay vì chỉ điểm đầu → điểm cuối

### Trung hạn

- [ ] **User Correction Logging** — Lưu phản hồi "Báo lỗi dữ liệu" của người dùng, phân loại để Admin review và cập nhật KB
- [ ] **Preference Learning** — Ghi nhận việc người dùng đổi trạm sạc để học pattern (ưu tiên trạm có tiện ích, tránh trạm hay đầy)
- [ ] **Weather & Load Adjustment** — Điều chỉnh ước tính tiêu hao pin theo nhiệt độ, số người, điều hòa
- [ ] **Persistent Multi-session Memory** — Thay MemorySaver bằng Redis/PostgreSQL để lưu lịch sử qua nhiều phiên

### Dài hạn

- [ ] **Data Flywheel** — Vòng lặp: User report trạm sạc → Cập nhật KB → AI gợi ý tốt hơn → Nhiều user hơn sử dụng
- [ ] **Escalation to Human** — Tự động chuyển sang nhân viên CSKH khi AI low-confidence thay vì trả lời mù
- [ ] **Affiliate Integration** — Gợi ý điểm dừng nghỉ (khách sạn, nhà hàng) gần trạm sạc, tạo nguồn doanh thu mới
- [ ] **Push to Vehicle** — Gửi lộ trình sạc trực tiếp lên hệ thống navigation của xe VinFast

---

## 📋 Failure Modes & Mitigations

| # | Trigger | Hậu quả | Mitigation hiện tại |
|---|---|---|---|
| 1 | Dữ liệu xe cũ/thiếu (model mới chưa cập nhật) | User nhận thông tin sai → mất trust | Hiển thị timestamp dữ liệu; trả về "NOT_FOUND" thay vì bịa |
| 2 | Sai lệch dự báo tiêu thụ pin (thời tiết/tải trọng) | Lộ trình khiến xe không tới được trạm tiếp theo | Giữ reserve ≥ 10% SOC tối thiểu trong mọi chặng |
| 3 | Trạm sạc đầy hoặc hỏng đột xuất | User đến trạm nhưng không sạc được | Gợi ý charger nearby thông qua corridor threshold |