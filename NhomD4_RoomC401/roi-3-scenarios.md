# ROI ANALYSIS: VINFAST SMART ASSISTANT (INFO & ROUTE)

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