# Individual reflection — Lê Đình Việt (2A202600469)

## 1. Role

Xây dựng hệ thống **EV Trip Planner**, bao gồm thiết kế tools và luồng tính toán hành trình tối ưu cho xe điện.
---

## 2. Đóng góp cụ thể

- Thiết kế và triển khai **các tools chính**:
  - Tính thời gian di chuyển  
  - Tính tiêu thụ năng lượng  
  - Tính thời gian sạc  
  - Tính chi phí sạc  
  - Chọn trạm sạc phù hợp  

- Xây dựng **planner tổng** để kết hợp các tools và đưa ra hành trình hoàn chỉnh  
- Thiết kế **các chế độ tối ưu (policy)**: nhanh nhất, rẻ nhất, ít dừng nhất, cân bằng  
- Chuẩn hóa **data model và output format** cho toàn hệ thống  
- Xây dựng test case cho nhiều kịch bản thực tế  

---

## 3. SPEC mạnh/yếu  

### Điểm mạnh nhất
- **Thiết kế system rõ ràng, modular**
  - Mỗi tool giải quyết 1 bài toán → dễ mở rộng và debug  

- **Tư duy product tốt**
  - Có nhiều mode (time/cost/stops) → phù hợp nhiều nhu cầu user  

- **Flow hợp lý**
  - Từ input → route → energy → charging → output rõ ràng  

- **Bám sát thực tế**
  - Có xét tới pin, trạm sạc, chi phí → không phải toy problem  

---

### Điểm yếu nhất
- **Fail handling chưa hoàn chỉnh**
  - Khi không tìm được route hoặc thiếu data → chưa có hướng dẫn rõ cho user  

- **Chưa có learning loop**
  - System chưa học từ user (chọn route, hành vi…) để improve dần  

---

## 4. Đóng góp khác

- Debug các lỗi hệ thống (routing, input format)  
- Thiết kế test case cho các tình huống dễ fail  
- Hỗ trợ tìm edge cases (thiếu trạm, pin không đủ, route không khả thi)  

---

## 5. Điều học được  

- **System design quan trọng hơn model**
  - Planner tốt = kết hợp đúng các tools  

- **Real-world problem luôn có constraint**
  - Không chỉ tính đúng, mà phải “tính được trong thực tế”  

- **Trade-off là trung tâm của product**
  - Không có route “tốt nhất”, chỉ có route “phù hợp”  

- **Data & reliability quan trọng ngang logic**
  - Data sai hoặc thiếu → hệ thống sai  

- **Failure là bình thường**
  - Quan trọng là xử lý fail như thế nào để user vẫn tin tưởng  

---

## 6. Nếu làm lại  

- Tối ưu số lần gọi API để giảm latency  
- Bổ sung data thực tế về trạm sạc  
- Thiết kế fail UX rõ hơn (gợi ý route khác, cảnh báo sớm)  
- Test nhiều hơn với use case thực tế  

---

## 7. AI giúp gì / AI sai gì  

- **Giúp:**
  - Gợi ý cách tách system thành tools + planner  
  - Brainstorm các edge case và flow  

- **Sai/mislead:**
  - Đưa ra nhiều hướng phức tạp không cần thiết  
  - Cần chọn lọc để phù hợp với scope project  
