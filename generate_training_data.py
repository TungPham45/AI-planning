import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_student_data(num_students=50):
    """Tạo dữ liệu huấn luyện cho 50 học sinh"""
    data = []
    
    # Các giá trị có thể có cho mỗi trường
    subjects = ['math', 'physics', 'chemistry']
    grades = ['thcs', 'thpt']
    learning_styles = ['theory', 'practical', 'combined']
    
    for _ in range(num_students):
        # Tạo dữ liệu ngẫu nhiên cho mỗi học sinh
        student = {
            'subject': random.choice(subjects),
            'grade': random.choice(grades),
            'current_score': round(random.uniform(4.0, 9.0), 1),
            'target_score': round(random.uniform(7.0, 10.0), 1),
            'duration_weeks': random.randint(4, 12),
            'daily_study_hours': random.randint(1, 4),
            'learning_style': random.choice(learning_styles),
            'success_rate': 0.0  # Tỷ lệ thành công sẽ được tính sau
        }
        
        # Tính toán tỷ lệ thành công dựa trên các yếu tố
        score_gap = student['target_score'] - student['current_score']
        time_factor = student['duration_weeks'] * student['daily_study_hours']
        
        # Công thức tính tỷ lệ thành công
        base_success = 0.5
        score_factor = 1 - (score_gap / 10)  # Điểm càng gần mục tiêu càng tốt
        time_factor = min(time_factor / 40, 1)  # Thời gian học càng nhiều càng tốt
        
        # Điều chỉnh theo phong cách học
        style_factor = {
            'theory': 0.9,
            'practical': 0.85,
            'combined': 1.0
        }[student['learning_style']]
        
        # Tính tỷ lệ thành công cuối cùng
        success_rate = (base_success + score_factor + time_factor) * style_factor / 3
        student['success_rate'] = round(success_rate * 100, 2)
        
        data.append(student)
    
    return pd.DataFrame(data)

def save_training_data(df, filename='training_data.csv'):
    """Lưu dữ liệu huấn luyện vào file CSV"""
    df.to_csv(filename, index=False)
    print(f"Đã lưu dữ liệu huấn luyện vào {filename}")

def main():
    # Tạo dữ liệu huấn luyện
    training_data = generate_student_data(50)
    
    # Hiển thị thống kê cơ bản
    print("\nThống kê dữ liệu huấn luyện:")
    print(f"Tổng số mẫu: {len(training_data)}")
    print("\nPhân bố theo môn học:")
    print(training_data['subject'].value_counts())
    print("\nPhân bố theo cấp học:")
    print(training_data['grade'].value_counts())
    print("\nPhân bố theo phong cách học:")
    print(training_data['learning_style'].value_counts())
    print("\nThống kê điểm số:")
    print(training_data[['current_score', 'target_score']].describe())
    print("\nThống kê tỷ lệ thành công:")
    print(training_data['success_rate'].describe())
    
    # Lưu dữ liệu
    save_training_data(training_data)

if __name__ == "__main__":
    main() 