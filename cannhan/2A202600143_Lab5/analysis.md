# UX exercise — MoMo Moni AI

## Sản phẩm: MoMo — Moni AI Assistant (phân loại chi tiêu)

---

## 4 paths

### 1. AI đúng
- User chi tiêu 50k tại Circle K → Moni gợi ý "Ăn uống"
- User thấy tag đúng, không cần làm gì thêm
- UI: hiện tag + icon category, không hỏi confirm

---

### 2. AI không chắc
- User chuyển tiền 200k cho bạn → Moni không tag hoặc tag "Khác"
- UI: không hiện gợi ý nào, user phải tự vào chỉnh

**Vấn đề:**
- Không có cơ chế hỏi: "Bạn muốn phân loại giao dịch này không?"
- Bỏ lỡ cơ hội thu thập feedback từ user

---

### 3. AI sai
- User mua sách trên Shopee → Moni tag "Mua sắm" thay vì "Học tập"
- User phát hiện khi xem báo cáo hoặc lịch sử giao dịch
- Sửa: vào chi tiết giao dịch → đổi category → nhiều bước

**Vấn đề:**
- Recovery flow dài, tốn effort
- Không rõ AI có học từ correction này không

---

### 4. User mất niềm tin
- Sau nhiều lần phân loại sai, user không còn tin vào auto-tag
- User bắt đầu ignore hoặc không dùng feature nữa

**Vấn đề:**
- Không có option:
  - "Tắt auto-tag"
  - Hoặc chuyển sang chế độ manual
- Không có fallback rõ ràng ngoài việc sửa từng giao dịch

---

## Path yếu nhất: Path 3 + 4
- Khi AI sai → sửa rất mất công
- Không có feedback loop rõ ràng
- User không biết AI có học hay không
- Không có cơ chế khôi phục niềm tin (trust)

---

## Gap marketing vs thực tế
- Marketing: "Moni giúp quản lý chi tiêu thông minh, tự động"
- Thực tế:
  - Auto-tag chỉ chính xác tốt với case phổ biến
  - Các edge case (chuyển tiền, mua online) thường sai hoặc không tag

**Gap lớn nhất:**
- Marketing không nói về failure case
- User kỳ vọng gần 100% chính xác → dễ thất vọng

---

## Sketch

- As-is:
  giao dịch → auto-tag → user thấy kết quả → nếu sai phải vào sửa thủ công

- To-be:
  giao dịch → auto-tag  
  → nếu confidence thấp: hiện "Bạn muốn phân loại?"  
  → user chọn category  
  → AI ghi nhận correction  
  → hiển thị: "Đã học, lần sau sẽ chính xác hơn"