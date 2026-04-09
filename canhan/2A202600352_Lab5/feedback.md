# Feedback — Demo round Day 6

## Nhóm Vinfast_D1

| Tiêu chí | Điểm (1-5) |
|----------|-----------|
| Problem-solution fit | 3 |
| AI product thinking | 3 |
| Demo quality | 4 |

Điểm chính:
- Demo chưa làm rõ agent giúp gì trong use case thực tế
- Giá trị AI chưa rõ, thiên về rule-based / pipeline
- Problem–solution fit chưa đủ sắc, chưa vượt trội so với solution truyền thống
- AI product thinking còn thiếu chiều sâu (flow, edge case, decision logic)

Hướng cải thiện:
- Làm rõ vai trò reasoning của agent
- Thiết kế flow user rõ ràng hơn
- Tách agent theo chức năng nếu mở rộng (planner, optimizer, validator)

---

## Nhóm Vinfast_D3

| Tiêu chí | Điểm (1-5) |
|----------|-----------|
| Problem-solution fit | 3 |
| AI product thinking | 3 |
| Demo quality | 3 |

Điểm chính:
- Hệ thống truy xuất ở mức cơ bản, dùng mock data
- Chưa có dữ liệu thực tế, chưa phản ánh production
- Chưa phân tích nhiều use case
- Chưa xử lý được nhiều condition (ambiguity, multi-turn, fallback)

Hướng cải thiện:
- Kết nối dữ liệu thật (API / DB / RAG)
- Mở rộng coverage use case
- Thêm log history, feedback loop
- Thêm OOD detection và kiểm soát hallucination

---

## Nhóm Vinfast_C1

| Tiêu chí | Điểm (1-5) |
|----------|-----------|
| Problem-solution fit | 3 |
| AI product thinking | 4 |
| Demo quality | 4 |

Điểm chính:
- Nhận diện đúng các vấn đề: trust, OOD, hallucination
- Domain rõ ràng, gần với use case thực tế
- Có cơ chế cảnh báo khi không chắc chắn

Hướng cải thiện:
- Kết nối dữ liệu thật (RAG / database)
- Thiết kế flow hỏi–đáp như tư vấn viên
- Thêm feedback loop
- Cải thiện xử lý OOD và cập nhật dữ liệu định kỳ
