import os
from typing import Annotated, List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

# --- 1. CẤU HÌNH ---
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", )
model_final = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_KEY, temperature=0.2)
# Khuyến nghị dùng gpt-4o-mini để xử lý context dài nhanh và tiết kiệm.

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "Lịch sử"]

# --- 2. NODES XỬ LÝ ---

def read_local_knowledge_node(state: AgentState):
    """Trích xuất và đọc file dữ liệu nội bộ về xe VinFast"""
    print("--- ĐANG ĐỌC FILE DỮ LIỆU NỘI BỘ (JSON) ---")
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Danh_Sach_Xe_Toi_Uu.json")
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        content = "{}"
        print(f"Error reading JSON: {e}")
        
    history_str = "\n".join([f"{'Khách' if m.type=='human' else 'Bot'}: {m.content}" for m in state["messages"][-4:]])
    
    prompt = f"""
    Bạn là hệ thống trích xuất thông tin xe điện VinFast. Dưới đây là CƠ SỞ DỮ LIỆU NỘI BỘ 2026:
    
    {content}
    
    -------------------
    CHIẾN LƯỢC TRÍCH XUẤT (RAW DATA ONLY):
    Dựa vào lịch sử người dùng hỏi, HÃY TRÍCH XUẤT CÁC THÔNG SỐ VÀ GIÁ TRỊ TƯƠNG ỨNG DƯỚI DẠNG DỮ LIỆU THÔ.
    - KHÔNG thêm các câu chào hỏi, diễn giải dài dòng.
    - KHÔNG định dạng đẹp mắt, chỉ cần liệt kê Fact (Sự thật/Thông số).
    - Ví dụ: "VF 3: Giá Pin 240tr, Kích thước 3190x1679x1622..."
    - Nếu câu hỏi chung chung, trích xuất danh sách tên xe hỗ trợ.
    - Nếu nằm ngoài dữ liệu, trả về "NOT_FOUND".
    
    Lịch sử hội thoại gần nhất:
    {history_str}
    
    HÃY TRẢ VỀ DỮ LIỆU THÔ NGAY BÂY GIỜ.
    """
    
    response = model_final.invoke(prompt)
    return {"messages": [response]}

# --- 3. XÂY DỰNG GRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("answer", read_local_knowledge_node)

workflow.set_entry_point("answer")
workflow.add_edge("answer", END)

car_agent_app = workflow.compile()

# --- 4. CHẠY TEST ---
if __name__ == "__main__":
    inputs = {"messages": [HumanMessage(content="Giá lăn bánh của VF 3 tại Hà Nội là bao nhiêu?")]}
    result = car_agent_app.invoke(inputs)
    print("\n" + result["messages"][-1].content)