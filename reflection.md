# Individual Reflection — Nguyễn Trần Hải Ninh (2A202600221)

## 1. Role (Vai trò)
Evaluation Engineer & Roadmap Designer — Chịu trách nhiệm thiết kế bộ tiêu chí đánh giá hiệu suất hệ thống AI và xây dựng định hướng phát triển dài hạn cho sản phẩm. Vai trò này đòi hỏi hiểu toàn bộ luồng hệ thống để đưa ra các metrics đo lường có ý nghĩa thực tiễn.

## 2. Phần phụ trách cụ thể
- **Thiết kế bộ Eval metrics:** Xây dựng các tiêu chí Precision/Recall cho module Triage, xác định ngưỡng chấp nhận và cách đo lường độ chính xác phân loại yêu cầu của người dùng. Output: `spec/spec-final.md`
- **Phân tích kịch bản ROI:** Tính toán và trình bày các kịch bản Return on Investment cho sản phẩm, hỗ trợ nhóm lập luận về tính khả thi kinh tế khi pitch. Output: phần ROI trong `spec/spec-final.md`
- **Xây dựng Roadmap phát triển:** Phác thảo lộ trình các giai đoạn tiếp theo của sản phẩm (short-term / mid-term / long-term), bao gồm các tính năng cần bổ sung và hướng mở rộng. Output: `demo/slides.pdf`

## 3. SPEC mạnh/yếu
- **Mạnh nhất:** Phần định nghĩa bài toán (Problem Statement) và phân tích đối tượng người dùng được viết rõ ràng, có dẫn chứng cụ thể. Đây là nền tảng giúp cả nhóm giữ đúng hướng trong suốt quá trình build.
- **Yếu nhất:** Phần kỹ thuật mô tả kiến trúc hệ thống còn sơ sài. 

## 4. Đóng góp cụ thể khác (ngoài mục 2)
- **Hỗ trợ chuẩn bị demo:** Tham gia sắp xếp kịch bản demo, đề xuất thứ tự trình bày các tính năng theo logic từ vấn đề → giải pháp → kết quả để người xem dễ theo dõi.
- **Review và test prompt:** Chạy thử một số prompt của module Triage để đối chiếu với metrics đã định nghĩa, phát hiện một vài trường hợp phân loại sai và báo lại cho người phụ trách Prompt Engineering.

## 5. Điều học được
Trước hackathon, tôi nghĩ Eval chỉ là bước cuối cùng sau khi xây xong hệ thống. Thực tế, việc định nghĩa metrics từ sớm (trước khi code) mới là đúng — vì nó buộc cả nhóm thống nhất về "thế nào là đúng" trước khi bắt tay làm, tránh tình trạng mỗi người có một tiêu chí khác nhau khi đánh giá kết quả.

## 6. Nếu làm lại, đổi gì?
Tôi sẽ xây dựng một bộ test case nhỏ (khoảng 20–30 câu hỏi mẫu với expected output) ngay từ ngày đầu và chia sẻ với toàn nhóm. Như vậy, mỗi người build module nào cũng có thể tự chạy kiểm tra nhanh thay vì phải chờ đến giai đoạn tổng hợp mới biết hệ thống chạy đúng hay không.

## 7. AI giúp gì / AI sai (mislead) gì?
- **Giúp ích:** AI hỗ trợ rất tốt trong việc phác thảo cấu trúc SPEC ban đầu — chỉ cần mô tả bài toán, AI đề xuất được các mục cần có trong tài liệu, giúp tiết kiệm đáng kể thời gian khởi đầu. Ngoài ra, AI cũng giúp tính toán nhanh các con số trong kịch bản ROI khi thay đổi giả định đầu vào.
- **Sai / Mislead:** Khi nhờ AI đề xuất ngưỡng Precision/Recall phù hợp cho bài toán Triage xe điện, AI đưa ra con số khá chung chung (thường là 0.8/0.8) mà không có cơ sở từ dữ liệu thực tế của hệ thống. Tôi đã phải tự điều chỉnh lại dựa trên kết quả chạy thử thực tế thay vì tin hoàn toàn vào gợi ý đó.