import os
import json
import gradio as gr
from typing import Annotated, List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from tavily import TavilyClient

# --- 1. CẤU HÌNH API KEYS TRƯỚC KHI IMPORT ---
os.environ["GEOAPIFY_API_KEY"] = ""
TAVILY_KEY = os.environ.get("TAVILY_API_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

try:
    from agent import car_agent_app
    from tools import create_planner, Vehicle, Stop, BatteryState
except ImportError:
    from src.agent import car_agent_app
    from src.tools import create_planner, Vehicle, Stop, BatteryState


tavily = TavilyClient(api_key=TAVILY_KEY)
# GPT-4o-mini đóng vai trò tương tự GPT-5.4 Nano
model_fast = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_KEY, temperature=0.1)
# GPT-4o đóng vai trò tổng hợp như GPT-5.4 Pro
model_final = ChatOpenAI(model="gpt-4o", api_key=OPENAI_KEY, temperature=0.2)

# Khởi tạo Planner
planner = create_planner()

# --- 2. ĐỊNH NGHĨA TRẠNG THÁI ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "Lịch sử chat"]
    car_list: List[str]
    processed_reports: str

memory = MemorySaver()

# --- 3. CỐT LÕI GRAPH ---
def router_node(state: AgentState):
    """Phân loại ý định người dùng bằng Ranh giới Từ (Word Boundaries)"""
    import re
    last_msg = state["messages"][-1].content.lower()
    
    trip_keywords = [r"đi từ", r"đến", r"lộ\s*trình", r"quãng\s*đường", r"dừng", r"chặng", r"chuyến\s*đi", r"hành\s*trình"]
    if any(re.search(r"\b" + k + r"\b", last_msg) for k in trip_keywords) and ("đến" in last_msg or "đi" in last_msg):
        return "trip_planner"
        
    vf_keywords = [r"xe", r"vf(?:e\d+|\d+)?", r"giá", r"thông\s*số", r"pin", r"sạc", r"trụ\s*sạc", r"trạm", r"vinfast", r"ô\s*tô", r"oto", r"mua"]
    if any(re.search(r"\b" + k + r"\b", last_msg) for k in vf_keywords):
        return "researcher"
        
    greetings = [r"^chào", r"^hello", r"^hi", r"^hey", r"^alo", r"^xin\s*chào", r"tạm\s*biệt", r"cảm\s*ơn", r"ok", r"^dạ", r"^vâng"]
    if any(re.search(k, last_msg.strip()) for k in greetings) and len(last_msg.split()) < 5:
        return "chat_normal"
        
    return "out_of_scope"

def out_of_scope_node(state: AgentState):
    """Từ chối mọi câu hỏi ngoài phạm vi hệ sinh thái VinFast"""
    from langchain_core.messages import AIMessage
    return {"messages": [AIMessage(content="Xin lỗi, câu hỏi của bạn không trong phạm vi liên quan. Tôi chỉ hỗ trợ các thông tin về Xe VinFast, Trạm sạc hoặc Lên lộ trình di chuyển.")], "car_list": [], "processed_reports": ""}

def chat_normal_node(state: AgentState):
    """Trả lời các câu hỏi chào hỏi thông thường"""
    # Gửi cả history
    response = model_fast.invoke([
        {"role": "system", "content": "Bạn là trợ lý ảo VinFast thân thiện. Trả lời ngắn gọn."}
    ] + state["messages"][-4:])
    return {"messages": [response]}

def trip_planner_node(state: AgentState):
    """Lập lộ trình di chuyển cho xe điện qua EVTripPlanner"""
    user_input = state["messages"][-1].content
    print(f"--- ĐANG LẬP LỘ TRÌNH: {user_input} ---")
    
    extract_prompt = f"""
    Trích xuất các thông tin sau từ yêu cầu lập lộ trình xe điện của người dùng: '{user_input}'
    
    Trả về ĐÚNG định dạng JSON sau, KHÔNG có markdown, KHÔNG thêm bất kỳ chữ nào khác:
    {{
        "origin": "Điểm xuất phát (Ví dụ: Hà Nội)",
        "destination": "Điểm đến (Ví dụ: Hội An)",
        "vehicle_name": "Tên xe (Ví dụ: VF 8)",
        "start_soc": 100
    }}
    Lưu ý: Nếu không rõ điểm xuất phát, hãy gán "Hà Nội". Nếu không rõ xe, hãy gán "VF 8". Nếu không rõ pin hiện tại, gán 100.
    """
    try:
        raw_res = model_fast.invoke(extract_prompt).content
        clean_res = raw_res.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_res)
        
        origin = data.get("origin", "Hà Nội")
        destination = data.get("destination", "Hội An")
        vh = data.get("vehicle_name", "VF 8")
        start_soc = float(data.get("start_soc", 100))
        
        # Khai báo thông số mặc định của Vinfast
        if "VF 3" in vh: bat, eff = 18.64, 0.08
        elif "VF 5" in vh: bat, eff = 37.23, 0.12
        elif "VF e34" in vh: bat, eff = 42.0, 0.14
        elif "VF 6" in vh: bat, eff = 59.6, 0.15
        elif "VF 7" in vh: bat, eff = 75.3, 0.17
        elif "VF 9" in vh: bat, eff = 92.0, 0.22
        else: bat, eff = 78.0, 0.19 # VF 8 mặc định
        
        vehicle = Vehicle(model=vh, usable_battery_kwh=bat, efficiency_kwh_per_km=eff)
        battery = BatteryState(start_soc_percent=start_soc)
        stops = [Stop(name=destination)]
        
        print(f"Params: {origin} -> {destination} | Xe: {vh}")
        result = planner.plan_trip(origin, stops, vehicle, battery)
        
        if result.status == "success":
            report = f"### BÁO CÁO LỘ TRÌNH THÀNH CÔNG\n"
            report += f"- **Tổng khoảng cách**: {result.summary.total_distance_km:.1f} km\n"
            report += f"- **Tổng thời gian lái**: {result.summary.total_drive_time_min:.0f} phút\n"
            report += f"- **Số lần dừng sạc**: {result.summary.total_stops} lần\n"
            report += f"- **Tổng thời gian sạc**: {result.summary.total_charging_time_min:.0f} phút\n"
            report += f"- **Tổng chi phí sạc**: {result.summary.total_charging_cost_vnd:,.0f} Đ\n"
            report += "\n### CHI TIẾT CÁC CHẶNG & BIỂU ĐỒ NĂNG LƯỢNG\n"
            for step in result.itinerary:
                if step["type"] == "drive":
                    soc = step['end_soc_percent']
                    bars = int(soc / 10)
                    progress = "█" * bars + "░" * (10 - bars)
                    report += f"🚗 **{step['origin']}** ➔ **{step['destination']}** ({step['distance_km']:.1f} km)\n> 🔋 Mức pin tới nơi: `{progress} {soc:.1f}%`\n\n"
                elif step["type"] == "charge":
                    soc = step['target_soc_percent']
                    bars = int(soc / 10)
                    progress = "█" * bars + "░" * (10 - bars)
                    report += f"🔌 **SẠC TẠI:** {step['station_name']} ({step['charging_time_min']:.0f} phút - {step['charging_cost_vnd']:,.0f} Đ)\n> ⚡ Sạc đầy lên: `{progress} {soc:.1f}%`\n\n"
        else:
            report = f"Lập lộ trình thất bại. Lý do: {', '.join(result.errors)}"
            
    except Exception as e:
        report = f"Lỗi không xác định khi xử lý thông tin lộ trình GPS: {str(e)}"
        
    return {"processed_reports": report, "car_list": []}

def researcher_node(state: AgentState):
    """Tìm kiếm thông tin tổng hợp về Xe hoặc Trạm sạc tĩnh (Hybrid RAG)"""
    user_input = state["messages"][-1].content
    lower_input = user_input.lower()
    print(f"--- ĐANG NGHIÊN CỨU TĨNH: {user_input} ---")
    
    # 0. CHẶN HÃNG XE KHÁC
    other_cars = ["toyota", "honda", "ford", "hyundai", "kia", "mazda", "mercedes", "bmw", "audi", "porsche", "lexus", "byd", "wuling", "tesla"]
    if any(c in lower_input for c in other_cars):
        print("-> ⛔ Phát hiện hỏi về xe hãng khác. Bơm dữ liệu loại trừ...")
        return {"processed_reports": "Xin lỗi, tôi là trợ lý ảo chuyên trách thuộc hệ sinh thái VinFast. Tôi không được phép cung cấp, đánh giá hay tham chiếu thông tin liên quan đến các dòng xe hoặc thương hiệu của hãng khác.", "car_list": []}
    
    # 1. XE -> Dùng Local Car Agent
    if any(k in lower_input for k in ["xe", "vf", "giá", "thông số", "pin", "vinfast", "mua"]) and not ("trạm" in lower_input or "sạc" in lower_input):
        print("-> Phân luồng: Tìm kiếm thông tin Xe trong Dữ liệu Nội bộ...")
        result = car_agent_app.invoke({"messages": [HumanMessage(content=user_input)]})
        report = result["messages"][-1].content
        if "NOT_FOUND" not in report:
            return {"processed_reports": report, "car_list": []}
        
        print("-> ⛔ NOT_FOUND trong Dữ liệu Nội bộ Xe. Chặn Fallback Trạm Sạc.")
        return {"processed_reports": "Xin lỗi, dòng xe bạn hỏi hiện không có trong hệ thống dữ liệu nhận diện của tôi. Vui lòng cung cấp chính xác tên dòng VinFast (Ví dụ: VF 8, VF 5, VF 3).", "car_list": []}

    # 2. TRẠM SẠC -> Tavily Online Search
    print("-> Phân luồng: Tìm kiếm trạm sạc...")
    print("-> Kích hoạt Tavily Search theo yêu cầu ưu tiên độ chính xác...")
    search_query = user_input
    if "bãi cháy" in lower_input:
        search_query += " Hạ Long Quảng Ninh trạm sạc VinFast công suất"
    
    search_data = tavily.search(query=search_query, search_depth="basic", max_results=3)
    
    extract_prompt = f"""
    Dựa trên dữ liệu mạng: {str(search_data)}
    Hãy trả lời chính xác và trực tiếp cho câu hỏi: '{user_input}'.
    Dữ liệu thô, ngắn gọn (Fact check).
    """
    summary = model_fast.invoke(extract_prompt).content
    return {"processed_reports": summary, "car_list": []}

def final_summarizer_node(state: AgentState):
    """Trình bày kết quả cuối cùng chuyên nghiệp"""
    print("--- ĐANG TỔNG HỢP PHẢN HỒI ---")
    prompt = f"""
    Bạn là VinFast AI Assistant chuyên nghiệp (GPT-5.4 Pro Tier).
    Dưới đây là DỮ LIỆU THÔ hệ thống đã trích xuất:
    
    {state.get('processed_reports', '')}
    
    CHIẾN LƯỢC TRẢ LỜI THEO YÊU CẦU:
    1. Dùng Dữ liệu thô trên để viết lại thành câu trả lời LỊCH SỰ, CHUẨN XÁC, NGẮN GỌN (Nhằm giảm thiểu thời gian đọc).
    2. Nếu là Báo Cáo Lộ Trình hoặc Trạm sạc chi tiết, trình bày Markdown sạch sẽ.
    3. Không dài dòng, không suy diễn thêm thông tin.
    """
    response = model_final.invoke(prompt)
    return {"messages": [response]}

# --- 4. XÂY DỰNG GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("chat_normal", chat_normal_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("trip_planner", trip_planner_node)
workflow.add_node("summarize", final_summarizer_node)
workflow.add_node("out_of_scope", out_of_scope_node)

workflow.set_conditional_entry_point(router_node, {
    "trip_planner": "trip_planner",
    "researcher": "researcher",
    "chat_normal": "chat_normal",
    "out_of_scope": "out_of_scope"
})

workflow.add_edge("researcher", "summarize")
workflow.add_edge("trip_planner", "summarize")
workflow.add_edge("summarize", END)
workflow.add_edge("chat_normal", END)
workflow.add_edge("out_of_scope", END)

bot_app = workflow.compile(checkpointer=memory)

# --- 5. GIAO DIỆN CHAT STREAMING & CACHING ---
SESSION_CACHE = {}

def chat_function(message, history):
    lower_msg = message.strip().lower()
    
    # 1. Semantic Cache (In-Memory Dictionary)
    if lower_msg in SESSION_CACHE:
        print(f"⚡ [CACHE HIT] Tìm thấy câu trả lời cho: '{lower_msg}'")
        yield SESSION_CACHE[lower_msg]
        return

    config = {"configurable": {"thread_id": "session_fptu_001"}}
    inputs = {"messages": [HumanMessage(content=message)], "car_list": [], "processed_reports": ""}
    
    try:
        final_output = ""
        # 2. Xử lý Streaming Output từ LangGraph Token-by-Token
        for chunk, metadata in bot_app.stream(inputs, config, stream_mode="messages"):
            node = metadata.get("langgraph_node")
            # Chỉ thu thập stream từ node summary hoặc normal
            if node in ["summarize", "chat_normal", "out_of_scope"] and chunk.content:
                final_output += chunk.content
                yield final_output
                
        # Cache kết quả sau khi sinh xong để dùng cho lần sau
        if final_output:
            SESSION_CACHE[lower_msg] = final_output
            
    except Exception as e:
        yield f"Xin lỗi, tôi đang bị gián đoạn hệ thống. ({str(e)})"

def save_charger(name, charger_types, address):
    if not name or not charger_types or not address:
        return "⚠️ Vui lòng nhập đầy đủ thông tin!"
    
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "data_update.json")
    
    # Read existing DB
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    else:
        data = []
        
    # Append
    data.append({
        "station_name": str(name),
        "charger_types": charger_types,
        "address": str(address)
    })
    
    # Write back
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    return f"✅ Đã lưu trạm '{name}' thành công!"

custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="indigo",
).set(
    button_primary_background_fill="*primary_500",
    button_primary_background_fill_hover="*primary_600",
)

def validate_station(name):
    if not name: return ""
    try:
        from src.tools import build_mock_chargers
        cdict = build_mock_chargers()
        for _, lst in cdict.items():
            for c in lst:
                if name.lower() in c.station_name.lower():
                    return f"⚠️ Cảnh báo: Trạm '{name}' dường như đã tồn tại!"
    except: pass
    return "✅ Có vẻ là trạm mới! Hợp lệ."

def generate_map_html(addr):
    if not addr.strip(): return ""
    import urllib.parse
    enc = urllib.parse.quote(addr)
    return f'<iframe width="100%" height="250" src="https://maps.google.com/maps?q={enc}&t=&z=14&ie=UTF8&iwloc=&output=embed" frameborder="0" style="border:0; border-radius:10px;"></iframe>'

custom_css = """
body { background-color: #0f172a !important; color: #f8fafc !important; }
.gradio-container { background: transparent !important; }
.panel-box { background: rgba(30, 41, 59, 0.7) !important; backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; }
h1 { background: -webkit-linear-gradient(45deg, #3b82f6, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
"""

with gr.Blocks(title="VinFast Smart Assistant 2026", theme=custom_theme, css=custom_css) as demo:
    gr.Markdown("<h1 style='text-align: center;'>⚡ VinFast Smart Assistant 2026 (Pro Version)</h1>")
    gr.Markdown("<p style='text-align: center; font-size: 16px; color: #94a3b8;'>Phiên bản siêu tốc 2026 với AI Streaming, Hệ thống Offline Routing và Data Fine-Tuning.</p>")
    
    with gr.Row():
        # LEFT COLUMN (Data entry)
        with gr.Column(scale=1, elem_classes="panel-box"):
            with gr.Accordion("🔋 Đóng Góp Hệ Sinh Thái", open=True):
                gr.Markdown("Thêm trạm sạc mới vào `data_update.json` để phục vụ công tác Fine-tune AI.")
                t_name = gr.Textbox(label="Tên Trạm / Mã Trạm", placeholder="VD: Trạm sạc Vincom Đồng Khởi")
                val_msg = gr.Markdown("")
                
                t_types = gr.CheckboxGroup(
                    choices=["AC (11kW)", "DC (30kW)", "DC (60kW)", "DC (80kW)", "DC (120kW)", "DC (150kW)", "DC (250kW - 300kW)"],
                    label="Loại Trụ Sạc Hiện Có"
                )
                t_addr = gr.Textbox(label="Địa chỉ chi tiết", placeholder="VD: 72 Lê Thánh Tôn, Quận 1, TPHCM", lines=2)
                map_view = gr.HTML(label="Bản đồ mô phỏng")
                
                submit_btn = gr.Button("💾 Cập nhật Database", variant="primary")
                out_msg = gr.Textbox(label="Trạng thái", interactive=False)
            
            # Event Listeners
            t_name.change(fn=validate_station, inputs=[t_name], outputs=[val_msg])
            t_addr.change(fn=generate_map_html, inputs=[t_addr], outputs=[map_view])
            submit_btn.click(
                fn=save_charger,
                inputs=[t_name, t_types, t_addr],
                outputs=[out_msg]
            )

        # RIGHT COLUMN (Chatbot)
        with gr.Column(scale=2, elem_classes="panel-box"):
            gr.ChatInterface(
                fn=chat_function, 
                examples=None
            )

if __name__ == "__main__":
    demo.launch(share=True)
