import os
from typing import Annotated, List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from tavily import TavilyClient

# --- 1. CẤU HÌNH ---
os.environ["TAVILY_API_KEY"] = "" # Thay key của bạn vào đây
os.environ["OPENAI_API_KEY"] = ""


tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
# Dùng model-mini để tóm tắt từng xe (tiết kiệm token)
model_fast = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# Dùng model chính để trình bày kết quả cuối cùng
model_final = ChatOpenAI(model="gpt-4o", temperature=0.2)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "Lịch sử"]
    car_list: List[str]
    processed_reports: str # Lưu các bản tóm tắt thu gọn

# --- 2. NODES XỬ LÝ ---

def discover_cars_node(state: AgentState):
    """Quét danh mục toàn bộ Ô TÔ ĐIỆN, XE TẢI ĐIỆN và XE BUS ĐIỆN của VinFast"""
    print("--- ĐANG QUÉT TOÀN BỘ HỆ SINH THÁI Ô TÔ ĐIỆN VINFAST ---")
    
    # Mở rộng query để tìm cả các dòng xe Mini và xe chuyên dụng mới
    query = (
        "danh sách các dòng ô tô điện VinFast 2026 chính thức và concept: "
        "VF3, VF5, VFe34, VF6, VF7, VF8, VF9, EC VAN, Mino, Herio, Limo, MPV7, VF Wild, VinBus"
    )
    search = tavily.search(query=query, search_depth="advanced", max_results=12)
    
    # Cấu trúc lại Prompt để LLM phân biệt đúng loại phương tiện
    prompt = f"""
    Dựa trên dữ liệu: {str(search)}
    Hãy liệt kê danh sách các phương tiện thuộc nhóm Ô TÔ (4 bánh trở lên) của VinFast.
    
    DANH SÁCH BẮT BUỘC (Nếu có trong dữ liệu):
    - Dòng VF: VF 3, VF 5, VF e34, VF 6, VF 7, VF 8, VF 9.
    - Dòng Xe tải/Van: EC Van.
    - Dòng Xe mới/Concept: Mino, Herio, Limo, MPV7, VF Wild.
    
    QUY TẮC LOẠI BỎ:
    - Loại bỏ XE MÁY ĐIỆN (Klara, Feliz, Vento, Theon, Evo...).
    - Loại bỏ XE XĂNG (Fadil, Lux A, Lux SA, President).
    
    Chỉ trả về tên các xe cách nhau bằng dấu phẩy.
    """
    
    res = model_fast.invoke(prompt)
    # Làm sạch dữ liệu để tránh lỗi "EC Van." có dấu chấm hoặc khoảng trắng thừa
    cars = [c.strip().replace(".", "") for c in res.content.split(",") if c.strip()]
    
    return {"car_list": cars, "processed_reports": ""}

def detail_research_node(state: AgentState):
    """Tìm đúng 10 mục thông tin cho từng xe"""
    car_name = state["car_list"][0]
    print(f"--- ĐANG SEARCH TAVILY: {car_name} ---")
    
    # Query tập trung vào bảng giá và thông số kỹ thuật Việt Nam
    query = f"thông số kỹ thuật ô tô VinFast {car_name} giá lăn bánh Hà Nội TP.HCM 2026 mới nhất"
    search_result = tavily.search(query=query, search_depth="advanced", max_results=5)
    
    extract_prompt = f"""
    Từ dữ liệu: {str(search_result)}
    Hãy trích xuất chính xác thông tin xe {car_name} theo các mục sau:
    1. Tên xe
    2. Hạng xe (Vd: SUV hạng A, B, C...)
    3. Phiên bản (Vd: Eco, Plus, nâng cao)
    4. Tốc độ tối đa
    5. Pin (Dung lượng, quãng đường di chuyển)
    6. Thông tin sạc (Sạc tại nhà, sạc nhanh tại trạm, thời gian sạc)
    7. Giá niêm yết (Kèm pin và thuê pin nếu có)
    8. Giá lăn bánh KV1 (Hà Nội, HCM), KV2 (Tỉnh)
    9. Bảo hành (Xe và Pin)
    10. Giới thiệu chung (Slogan hoặc mục đích sử dụng)
    
    Yêu cầu: Nếu dữ liệu là của năm cũ, hãy cố gắng ước lượng theo chính sách mới nhất 2026.
    """
    summary = model_fast.invoke(extract_prompt).content
    new_report = f"\n\n### CHI TIẾT XE: {car_name}\n{summary}\n-----------------------"
    
    return {
        "car_list": state["car_list"][1:],
        "processed_reports": state.get("processed_reports", "") + new_report
    }

def final_summarizer_node(state: AgentState):
    """Tổng hợp thành phản hồi cuối cùng chuyên nghiệp"""
    print("--- ĐANG TỔNG HỢP PHẢN HỒI CUỐI CÙNG ---")
    full_context = state["processed_reports"]
    
    final_prompt = f"""
    Bạn là VinFast AI. Dựa trên dữ liệu đã trích xuất:
    {full_context}
    
    Hãy trình bày đầy đủ thông tin của từng xe. Mỗi xe trình bày thành một khối riêng biệt, trình bày đẹp mắt, dễ đọc theo đúng các mục người dùng yêu cầu:
    - Tên xe
    - Hạng xe
    - Phiên bản
    - Tốc độ tối đa
    - Thông tin Pin
    - Thông tin Sạc (Tất cả hình thức)
    - Giá niêm yết
    - Giá lăn bánh (KV1, KV2)
    - Chế độ bảo hành
    - Giới thiệu chung
    """
    
    response = model_final.invoke(final_prompt)
    return {"messages": [response]}

# --- 3. LUỒNG ĐIỀU KHIỂN ---
def should_continue(state: AgentState):
    return "continue" if len(state["car_list"]) > 0 else "end"

# --- 4. XÂY DỰNG GRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("discover", discover_cars_node)
workflow.add_node("research_detail", detail_research_node)
workflow.add_node("summarize", final_summarizer_node)

workflow.set_entry_point("discover")
workflow.add_edge("discover", "research_detail")
workflow.add_conditional_edges("research_detail", should_continue, {"continue": "research_detail", "end": "summarize"})
workflow.add_edge("summarize", END)

app = workflow.compile()

# --- 5. CHẠY ---
if __name__ == "__main__":
    inputs = {"messages": [HumanMessage(content="Thông tin tất cả xe điện VinFast")], "car_list": []}
    result = app.invoke(inputs)
    print("\n" + result["messages"][-1].content)