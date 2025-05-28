# Hệ thống AI Tạo Lộ Trình Học Tập

Hệ thống AI này giúp tạo lộ trình học tập tùy chỉnh cho các môn Toán, Lý và Hóa dựa trên nhu cầu và khả năng của người học.

## Cài đặt

1. Cài đặt Python 3.8 trở lên
2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## Cách sử dụng

1. Chạy file `learning_path_ai.py`:
```bash
python learning_path_ai.py
```

2. Hoặc import và sử dụng trong code của bạn:
```python
from learning_path_ai import LearningPathAI

ai = LearningPathAI()
learning_path = ai.generate_learning_path(
    subject='math',  # 'math', 'physics', hoặc 'chemistry'
    current_score=6.5,  # Điểm số hiện tại (thang điểm 10)
    target_score=8.5,  # Mục tiêu điểm số
    duration_weeks=8,  # Số tuần học
    daily_study_hours=2,  # Số giờ học mỗi ngày
    learning_style='combined'  # 'theory', 'practical', hoặc 'combined'
)
```

## Các tham số đầu vào

- `subject`: Môn học ('math', 'physics', 'chemistry')
- `current_score`: Điểm số hiện tại (thang điểm 10)
- `target_score`: Mục tiêu điểm số muốn đạt được
- `duration_weeks`: Số tuần học
- `daily_study_hours`: Số giờ học mỗi ngày
- `learning_style`: Phong cách học ('theory', 'practical', 'combined')

## Đầu ra

Hệ thống sẽ tạo ra một lộ trình học tập chi tiết theo tuần và ngày, bao gồm:
- Các chủ đề lý thuyết cần học
- Các bài tập thực hành
- Thời gian phân bổ cho lý thuyết và thực hành
- Ngày bắt đầu và kết thúc của mỗi tuần 