

# Prototype — VinFast Smart Assistant 2026 (Pro Version)

## Mô tả

Hệ thống Agentic Chatbot thông minh cho xe điện VinFast, tích hợp 3 tính năng cốt lõi:

1.  **AI Triage:** Phân loại ý định người dùng (Tra cứu xe / Hỏi đường / Chat / Chặn hãng xe khác).
2.  **Hybrid RAG:** Truy vấn dữ liệu xe chính xác 100% từ file JSON nội bộ.
3.  **EV Trip Planner:** Sử dụng thuật toán Dijkstra để lập lộ trình dừng sạc tối ưu (từ VF 3 đến VF Wild).

## Level: Fully-Functional Prototype

  * **UI build bằng Gradio** (Python), tích hợp Chat Streaming và hiển thị ProgressBar mức pin xe.
  * **Hệ thống Multi-Agent chạy thật với LangGraph** và Google Gemini 2.0 Flash (hoặc GPT-4o).

## Links

  * **Demo Link (Gradio URL):** [https://vf-smart-assistant-2026.gradio.app](https://www.google.com/search?q=https://vf-smart-assistant-2026.gradio.app)
  * **Prompt test log:** xem file `extras/prompt-test-logs.md`.
  * **Video demo:** [https://drive.google.com/xxx](https://drive.google.com/xxx)

## Tools

  * **Framework:** LangGraph (Điều phối Agent Workflow).
  * **UI:** Gradio (Web Interface).
  * **AI:** Google Gemini 2.0 Flash (hoặc GPT-4o).
  * **Data:** `Danh_Sach_Xe_Toi_Uu.json` (Knowledge Base).

## Phân công

| Thành viên | Phần | Output |
|:---:|:---|:---|
| **Trần Văn Tuấn** | **AI Agent Architect**: Thiết kế sơ đồ đa tác vụ (LangGraph), cấu trúc Graph State, Router, Researcher, Summarizer và Guardrails Node. | `agent.py`, `toolsCS.py` |
| **[Tên của bạn]** | **UX & Prompt Engineer**: Thiết kế conversation flow, viết System Prompt cho các Node và xây dựng ít nhất 3 bộ few-shot examples. | `extras/prompt-test-logs.md` |
| **Lê Đình Việt** | **Data Engineering (RAG)**: Làm sạch và cấu trúc dữ liệu từ định dạng văn bản sang `Danh_Sach_Xe_Toi_Uu.json`, đảm bảo chính xác 100%. | `Danh_Sach_Xe_Toi_Uu.json` |
| **[Hồ Bảo Thư]** | **EV Trip Planner & Dijkstra**: Phát triển thuật toán `EVTripPlanner` dựa trên Dijkstra để tính toán điểm dừng sạc tối ưu. | `tools.py` |
| **[Nguyễn Đình Hiếu]** | **UI Prototype (Gradio)**: Xây dựng giao diện Web Demo bằng Gradio, tích hợp Chat Streaming và ProgressBar hiển thị pin. | `toolsCS.py`, Link Gradio Demo |
| **[Thành viên 6]** | **Evaluation & Roadmapping**: Thiết kế bộ Eval metrics (Precision/Recall cho Triage), kịch bản ROI và định hướng phát triển. | `spec/spec-final.md`, `demo/slides.pdf` |
