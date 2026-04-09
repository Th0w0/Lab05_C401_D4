# Individual reflection — Lê Đình Việt (2A202600469)

## 1. Role

Xây dựng luồng hoạt động chatbot, crawl và clean data. Xây dựng spec

## 2. Đóng góp cụ thể

- Xây dựng pipeline crawl và clean data thành dạng json
- Xây dựng luồng hoạt động của chatbot, cách truy xuất trong chatbot để tối ưu thời gian
- Xây dựng test case cho hệ thống

## 3. SPEC mạnh/yếu
Điểm mạnh nhất
- Problem & pain rất rõ ràng → bám sát thực tế user (search + CSKH friction)  
- Thiết kế Augmentation đúng hướng → có fallback CSKH, giảm risk  
- Quality thinking tốt:
  - Ưu tiên precision (rất đúng domain)
  - Có metrics, threshold, kill criteria rõ  
- Nhận diện risk sâu (hallucination, legal, route failure) → mindset product tốt  
Điểm yếu nhất
- Learning loop chưa cụ thể: Có signal nhưng chưa rõ: update model / retrieval như thế nào  
- Chưa có data moat rõ ràng: Data chủ yếu public → khó tạo lợi thế dài hạn  
- UX fail handling chưa fully systemized: Chưa có cơ chế “fail nhiều → đổi behavior” rõ ràng  
- Execution gap: Spec rất tốt nhưng thiếu phần “triển khai cụ thể” (pipeline, infra, update data)

## 4. Đóng góp khác
- Giúp Tuấn debug hệ thống chatbot, tìm những test case hệ thống sẽ sai


## 5. Điều học được
- AI product không chỉ là model: Quan trọng nhất là UX + trust + fallback, không phải chỉ accuracy
- Precision > Recall trong domain nhạy cảm: Sai thông tin (giá, policy) nguy hiểm hơn không trả lời
- Trust = core metric, không phải nice-to-have: 1 lần sai có thể ảnh hưởng trực tiếp đến conversion
- Augmentation thường thực tế hơn Automation: Cho user kiểm soát + có CSKH fallback giúp giảm risk
- Learning signal là tài sản lớn nhất: Escalate, correction, CSAT = nền tảng để system tốt lên
- Failure không tránh được, nhưng phải thiết kế để recover tốt: Fail UX quan trọng không kém việc tránh fail
- Freshness của data quan trọng ngang model quality: Data outdated = AI sai dù model tốt
- Spec tốt = nghĩ trước các failure modes: Những lỗi nguy hiểm nhất là lỗi user không nhận ra
- AI chỉ tạo moat khi có learning loop + proprietary data: Nếu không, đối thủ dễ replicate

## 6. Nếu làm lại
- Test prompt sớm hơn (ngay từ D5 tối): Tránh dồn việc vào cuối, có thêm 2–3 vòng iterate
- Test theo use case thật, không chỉ happy path: Bao gồm: câu mơ hồ, thiếu data, edge cases
- Thiết kế prompt song song với UX flow: Không tách rời spec và implementation
- Log & review failure sớm: Tập trung fix các lỗi “nguy hiểm” (user không nhận ra)
- Chốt format output ngay từ đầu: Tránh sửa nhiều lần khi đã build downstream

## 7. AI giúp gì / AI sai gì
- **Giúp:** dùng Claude để brainstorm failure modes — nó gợi ý được "drug interaction"
  mà nhóm không nghĩ ra. Dùng Gemini để test prompt nhanh qua AI Studio.
- **Giúp**: ChatGPT giúp brainstorm failure modes, gợi ý và phản biện những trường hợp ít khi xảy ra. 
- **Sai/mislead:** ChatGPT sinh ra quá nhiều idea, nếu làm hết thì không đủ thời gian -> Phải lựa chọn idea phù hợp trong thời gian cho phép