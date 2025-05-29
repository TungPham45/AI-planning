import pandas as pd
import numpy as np
from datetime import datetime

def generate_training_data():
    # Tạo dữ liệu cơ bản
    subjects = ['math', 'physics', 'chemistry']
    grades = ['10', '11', '12']
    learning_styles = ['practical', 'theory', 'combined']
    
    # Tạo các mẫu dữ liệu đa dạng
    data = []
    
    # 1. Mẫu cho học sinh có điểm số thấp (3.0 - 5.0)
    for subject in subjects:
        for grade in grades:
            for style in learning_styles:
                # Thời gian học ngắn (1-2 giờ/ngày)
                data.append({
                    'subject': subject,
                    'grade': grade,
                    'current_score': round(np.random.uniform(3.0, 4.0), 1),
                    'target_score': round(np.random.uniform(5.0, 6.0), 1),
                    'duration_weeks': np.random.choice([12, 14, 16]),
                    'daily_study_hours': round(np.random.uniform(1.0, 2.0), 1),
                    'learning_style': style,
                    'success_rate': round(np.random.uniform(45.0, 55.0), 1)
                })
                
                # Thời gian học trung bình (2-3 giờ/ngày)
                data.append({
                    'subject': subject,
                    'grade': grade,
                    'current_score': round(np.random.uniform(3.5, 4.5), 1),
                    'target_score': round(np.random.uniform(5.5, 6.5), 1),
                    'duration_weeks': np.random.choice([10, 12, 14]),
                    'daily_study_hours': round(np.random.uniform(2.0, 3.0), 1),
                    'learning_style': style,
                    'success_rate': round(np.random.uniform(55.0, 65.0), 1)
                })
    
    # 2. Mẫu cho học sinh có điểm số trung bình (5.0 - 7.0)
    for subject in subjects:
        for grade in grades:
            for style in learning_styles:
                # Thời gian học trung bình (2-3 giờ/ngày)
                data.append({
                    'subject': subject,
                    'grade': grade,
                    'current_score': round(np.random.uniform(5.0, 6.0), 1),
                    'target_score': round(np.random.uniform(7.0, 8.0), 1),
                    'duration_weeks': np.random.choice([8, 10, 12]),
                    'daily_study_hours': round(np.random.uniform(2.0, 3.0), 1),
                    'learning_style': style,
                    'success_rate': round(np.random.uniform(65.0, 75.0), 1)
                })
                
                # Thời gian học nhiều (3-4 giờ/ngày)
                data.append({
                    'subject': subject,
                    'grade': grade,
                    'current_score': round(np.random.uniform(5.5, 6.5), 1),
                    'target_score': round(np.random.uniform(7.5, 8.5), 1),
                    'duration_weeks': np.random.choice([6, 8, 10]),
                    'daily_study_hours': round(np.random.uniform(3.0, 4.0), 1),
                    'learning_style': style,
                    'success_rate': round(np.random.uniform(75.0, 85.0), 1)
                })
    
    # 3. Mẫu cho học sinh có điểm số khá (7.0 - 8.5)
    for subject in subjects:
        for grade in grades:
            for style in learning_styles:
                # Thời gian học trung bình (2-3 giờ/ngày)
                data.append({
                    'subject': subject,
                    'grade': grade,
                    'current_score': round(np.random.uniform(7.0, 7.5), 1),
                    'target_score': round(np.random.uniform(8.5, 9.0), 1),
                    'duration_weeks': np.random.choice([6, 8, 10]),
                    'daily_study_hours': round(np.random.uniform(2.0, 3.0), 1),
                    'learning_style': style,
                    'success_rate': round(np.random.uniform(80.0, 90.0), 1)
                })
                
                # Thời gian học nhiều (3-4 giờ/ngày)
                data.append({
                    'subject': subject,
                    'grade': grade,
                    'current_score': round(np.random.uniform(7.5, 8.0), 1),
                    'target_score': round(np.random.uniform(9.0, 9.5), 1),
                    'duration_weeks': np.random.choice([4, 6, 8]),
                    'daily_study_hours': round(np.random.uniform(3.0, 4.0), 1),
                    'learning_style': style,
                    'success_rate': round(np.random.uniform(85.0, 95.0), 1)
                })
    
    # 4. Mẫu cho học sinh có điểm số giỏi (8.5 - 10.0)
    for subject in subjects:
        for grade in grades:
            for style in learning_styles:
                # Thời gian học trung bình (2-3 giờ/ngày)
                data.append({
                    'subject': subject,
                    'grade': grade,
                    'current_score': round(np.random.uniform(8.5, 9.0), 1),
                    'target_score': round(np.random.uniform(9.5, 10.0), 1),
                    'duration_weeks': np.random.choice([4, 6, 8]),
                    'daily_study_hours': round(np.random.uniform(2.0, 3.0), 1),
                    'learning_style': style,
                    'success_rate': round(np.random.uniform(90.0, 95.0), 1)
                })
                
                # Thời gian học nhiều (3-4 giờ/ngày)
                data.append({
                    'subject': subject,
                    'grade': grade,
                    'current_score': round(np.random.uniform(9.0, 9.5), 1),
                    'target_score': 10.0,
                    'duration_weeks': np.random.choice([2, 4, 6]),
                    'daily_study_hours': round(np.random.uniform(3.0, 4.0), 1),
                    'learning_style': style,
                    'success_rate': round(np.random.uniform(95.0, 100.0), 1)
                })
    
    # 5. Thêm một số trường hợp đặc biệt
    special_cases = [
        # Trường hợp học cấp tốc (thời gian ngắn, cường độ cao)
        {
            'subject': 'math',
            'grade': '12',
            'current_score': 7.0,
            'target_score': 9.0,
            'duration_weeks': 4,
            'daily_study_hours': 4.0,
            'learning_style': 'combined',
            'success_rate': 85.0
        },
        # Trường hợp học từ từ (thời gian dài, cường độ thấp)
        {
            'subject': 'physics',
            'grade': '10',
            'current_score': 4.0,
            'target_score': 6.0,
            'duration_weeks': 20,
            'daily_study_hours': 1.5,
            'learning_style': 'theory',
            'success_rate': 60.0
        },
        # Trường hợp học thực hành nhiều
        {
            'subject': 'chemistry',
            'grade': '11',
            'current_score': 6.0,
            'target_score': 8.0,
            'duration_weeks': 12,
            'daily_study_hours': 3.0,
            'learning_style': 'practical',
            'success_rate': 75.0
        }
    ]
    data.extend(special_cases)
    
    # Tạo DataFrame và lưu vào file CSV
    df = pd.DataFrame(data)
    
    # Sắp xếp dữ liệu theo subject, grade và current_score
    df = df.sort_values(['subject', 'grade', 'current_score'])
    
    # Lưu file với timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'training_data_{timestamp}.csv'
    df.to_csv(filename, index=False)
    print(f"Đã tạo file {filename} với {len(df)} mẫu dữ liệu")
    
    # In thống kê cơ bản
    print("\nThống kê dữ liệu:")
    print(f"Số lượng mẫu theo môn học:\n{df['subject'].value_counts()}")
    print(f"\nSố lượng mẫu theo lớp:\n{df['grade'].value_counts()}")
    print(f"\nSố lượng mẫu theo phong cách học:\n{df['learning_style'].value_counts()}")
    print("\nThống kê điểm số:")
    print(df[['current_score', 'target_score', 'success_rate']].describe())
    
    return filename  # Trả về tên file đã tạo

if __name__ == "__main__":
    filename = generate_training_data()
    print(f"\nFile đã được tạo: {filename}") 