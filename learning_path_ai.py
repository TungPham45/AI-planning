import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
from datetime import datetime, timedelta

class LearningPathAI:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.label_encoders = {
            'subject': LabelEncoder(),
            'learning_style': LabelEncoder(),
            'grade': LabelEncoder()
        }
        self.is_trained = False
        
    def train(self, training_data_path='training_data.csv'):
        """Huấn luyện mô hình với dữ liệu đã có"""
        # Đọc dữ liệu huấn luyện
        df = pd.read_csv(training_data_path)
        
        # Tiền xử lý dữ liệu
        X = self._preprocess_features(df)
        y = df['success_rate']
        
        # Chia dữ liệu thành tập huấn luyện và tập kiểm tra
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Huấn luyện mô hình
        self.model.fit(X_train, y_train)
        
        # Đánh giá mô hình
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"\nKết quả huấn luyện:")
        print(f"Độ chính xác trên tập huấn luyện: {train_score:.2f}")
        print(f"Độ chính xác trên tập kiểm tra: {test_score:.2f}")
        
        self.is_trained = True
        
        # Lưu mô hình
        self.save_model()
        
    def _preprocess_features(self, df):
        """Tiền xử lý các đặc trưng đầu vào"""
        # Mã hóa các biến phân loại
        for col, encoder in self.label_encoders.items():
            df[col] = encoder.fit_transform(df[col])
        
        # Chọn các đặc trưng cần thiết
        features = [
            'subject', 'grade', 'current_score', 'target_score',
            'duration_weeks', 'daily_study_hours', 'learning_style'
        ]
        
        return df[features]
    
    def save_model(self, model_path='learning_path_model.joblib'):
        """Lưu mô hình đã huấn luyện"""
        if self.is_trained:
            joblib.dump(self.model, model_path)
            print(f"\nĐã lưu mô hình vào {model_path}")
    
    def load_model(self, model_path='learning_path_model.joblib'):
        """Tải mô hình đã huấn luyện"""
        try:
            self.model = joblib.load(model_path)
            self.is_trained = True
            print(f"\nĐã tải mô hình từ {model_path}")
        except:
            print("\nKhông tìm thấy mô hình đã lưu. Vui lòng huấn luyện mô hình trước.")
    
    def predict_success_rate(self, subject, current_score, target_score, 
                           duration_weeks, daily_study_hours, learning_style, grade):
        """Dự đoán tỷ lệ thành công cho một học sinh mới"""
        if not self.is_trained:
            print("\nMô hình chưa được huấn luyện. Vui lòng huấn luyện trước.")
            return None
        
        # Tạo dữ liệu đầu vào
        input_data = pd.DataFrame([{
            'subject': subject,
            'grade': grade,
            'current_score': current_score,
            'target_score': target_score,
            'duration_weeks': duration_weeks,
            'daily_study_hours': daily_study_hours,
            'learning_style': learning_style
        }])
        
        # Tiền xử lý dữ liệu
        X = self._preprocess_features(input_data)
        
        # Dự đoán
        success_rate = self.model.predict(X)[0]
        
        return round(success_rate, 2)
    
    def generate_learning_path(self, subject, current_score, target_score, 
                             duration_weeks, daily_study_hours, learning_style, grade):
        """Tạo lộ trình học tập dựa trên đầu vào và dự đoán tỷ lệ thành công"""
        # Dự đoán tỷ lệ thành công
        success_rate = self.predict_success_rate(
            subject, current_score, target_score,
            duration_weeks, daily_study_hours, learning_style, grade
        )
        
        if success_rate is None:
            return None
        
        # Xác định cấp độ học dựa trên điểm số và tỷ lệ thành công dự đoán
        level = self._determine_level(current_score, target_score, success_rate)
        
        # Tạo lộ trình học tập
        learning_path = []
        current_date = datetime.now()
        
        # Phân bổ thời gian học theo tuần
        for week in range(duration_weeks):
            week_plan = {
                'week_number': week + 1,
                'start_date': current_date.strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=6)).strftime('%Y-%m-%d'),
                'level': level,
                'grade': grade,
                'predicted_success_rate': success_rate,
                'daily_plans': []
            }
            
            # Tạo kế hoạch cho từng ngày trong tuần
            for day in range(7):
                if day < 5:  # Chỉ học 5 ngày/tuần
                    daily_plan = self._create_daily_plan(
                        subject=subject,
                        learning_style=learning_style,
                        daily_hours=daily_study_hours,
                        week_number=week + 1,
                        total_weeks=duration_weeks,
                        level=level,
                        grade=grade
                    )
                    week_plan['daily_plans'].append(daily_plan)
            
            current_date += timedelta(days=7)
            learning_path.append(week_plan)
        
        return learning_path
    
    def _determine_level(self, current_score, target_score, success_rate):
        """Xác định cấp độ học dựa trên điểm số và tỷ lệ thành công dự đoán"""
        if current_score < 5 or success_rate < 50:
            return 'basic'
        elif current_score < 7 or success_rate < 75:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _create_daily_plan(self, subject, learning_style, daily_hours, week_number, total_weeks, level, grade):
        """Tạo kế hoạch học tập cho một ngày"""
        if learning_style == 'practical':
            theory_hours = daily_hours * 0.3
            practice_hours = daily_hours * 0.7
        elif learning_style == 'theory':
            theory_hours = daily_hours * 0.7
            practice_hours = daily_hours * 0.3
        else:  # combined
            theory_hours = daily_hours * 0.5
            practice_hours = daily_hours * 0.5
            
        return {
            'theory_topics': self._get_theory_topics(subject, week_number, total_weeks, level, grade),
            'practice_exercises': self._get_practice_exercises(subject, week_number, total_weeks, level, grade),
            'theory_hours': theory_hours,
            'practice_hours': practice_hours,
            'learning_resources': self._get_learning_resources(subject, level, grade)
        }
    
    def _get_theory_topics(self, subject, week_number, total_weeks, level, grade):
        """Lấy danh sách chủ đề lý thuyết dựa trên môn học, tuần, cấp độ và lớp"""
        topics = {
            'math': {
                'thcs': {
                    'basic': [
                        'Số tự nhiên và số nguyên',
                        'Phân số và số thập phân',
                        'Tỷ lệ và phần trăm',
                        'Phương trình bậc nhất',
                        'Hình học cơ bản',
                        'Thống kê đơn giản'
                    ],
                    'intermediate': [
                        'Phương trình bậc hai',
                        'Hàm số bậc nhất',
                        'Lượng giác cơ bản',
                        'Hình học phẳng',
                        'Xác suất cơ bản',
                        'Thống kê mô tả'
                    ],
                    'advanced': [
                        'Phương trình bậc cao',
                        'Hàm số bậc hai',
                        'Lượng giác nâng cao',
                        'Hình học không gian',
                        'Xác suất nâng cao',
                        'Thống kê suy luận'
                    ]
                },
                'thpt': {
                    'basic': [
                        'Hàm số và đồ thị',
                        'Phương trình và hệ phương trình',
                        'Lượng giác',
                        'Hình học phẳng',
                        'Xác suất thống kê',
                        'Số phức'
                    ],
                    'intermediate': [
                        'Hàm số mũ và logarit',
                        'Phương trình lượng giác',
                        'Hình học không gian',
                        'Tích phân',
                        'Xác suất nâng cao',
                        'Thống kê suy luận'
                    ],
                    'advanced': [
                        'Hàm số phức tạp',
                        'Phương trình vi phân',
                        'Hình học giải tích',
                        'Tích phân nâng cao',
                        'Xác suất thống kê nâng cao',
                        'Số phức nâng cao'
                    ]
                }
            },
            'physics': {
                'thcs': {
                    'basic': [
                        'Đo lường và đơn vị',
                        'Chuyển động cơ bản',
                        'Lực và chuyển động',
                        'Năng lượng cơ bản',
                        'Nhiệt độ và nhiệt lượng',
                        'Điện học cơ bản'
                    ],
                    'intermediate': [
                        'Chuyển động nâng cao',
                        'Định luật Newton',
                        'Năng lượng và công',
                        'Nhiệt động lực học',
                        'Điện từ học cơ bản',
                        'Sóng cơ học'
                    ],
                    'advanced': [
                        'Cơ học nâng cao',
                        'Định luật bảo toàn',
                        'Nhiệt động lực học nâng cao',
                        'Điện từ học nâng cao',
                        'Quang học cơ bản',
                        'Sóng và âm thanh'
                    ]
                },
                'thpt': {
                    'basic': [
                        'Cơ học chất điểm',
                        'Điện trường',
                        'Từ trường',
                        'Quang hình học',
                        'Nhiệt động lực học',
                        'Sóng cơ học'
                    ],
                    'intermediate': [
                        'Cơ học vật rắn',
                        'Điện từ trường',
                        'Quang học sóng',
                        'Nhiệt động lực học nâng cao',
                        'Sóng điện từ',
                        'Vật lý hạt nhân cơ bản'
                    ],
                    'advanced': [
                        'Cơ học lượng tử',
                        'Thuyết tương đối',
                        'Vật lý hạt nhân nâng cao',
                        'Điện từ học nâng cao',
                        'Quang học lượng tử',
                        'Vật lý hiện đại'
                    ]
                }
            },
            'chemistry': {
                'thcs': {
                    'basic': [
                        'Cấu trúc nguyên tử',
                        'Bảng tuần hoàn',
                        'Liên kết hóa học cơ bản',
                        'Phản ứng hóa học đơn giản',
                        'Dung dịch và nồng độ',
                        'Axit và bazơ cơ bản'
                    ],
                    'intermediate': [
                        'Liên kết hóa học nâng cao',
                        'Phản ứng oxi hóa khử',
                        'Cân bằng hóa học',
                        'Hóa học hữu cơ cơ bản',
                        'Điện hóa học cơ bản',
                        'Hóa học môi trường'
                    ],
                    'advanced': [
                        'Hóa học vô cơ nâng cao',
                        'Hóa học hữu cơ nâng cao',
                        'Cân bằng hóa học nâng cao',
                        'Điện hóa học nâng cao',
                        'Hóa học môi trường nâng cao',
                        'Hóa học thực nghiệm'
                    ]
                },
                'thpt': {
                    'basic': [
                        'Cấu trúc nguyên tử nâng cao',
                        'Liên kết hóa học',
                        'Phản ứng hóa học',
                        'Dung dịch điện li',
                        'Hóa học hữu cơ',
                        'Hóa học vô cơ'
                    ],
                    'intermediate': [
                        'Hóa học lượng tử',
                        'Hóa học hữu cơ nâng cao',
                        'Hóa học vô cơ nâng cao',
                        'Điện hóa học',
                        'Hóa học phân tích',
                        'Hóa học môi trường'
                    ],
                    'advanced': [
                        'Hóa học lượng tử nâng cao',
                        'Hóa học hữu cơ chuyên sâu',
                        'Hóa học vô cơ chuyên sâu',
                        'Hóa học phân tích nâng cao',
                        'Hóa sinh học'
                    ]
                }
            }
        }
        
        subject_topics = topics.get(subject.lower(), {}).get(grade, {}).get(level, [])
        topics_per_week = len(subject_topics) // total_weeks
        start_idx = (week_number - 1) * topics_per_week
        end_idx = start_idx + topics_per_week
        
        return subject_topics[start_idx:end_idx]
    
    def _get_practice_exercises(self, subject, week_number, total_weeks, level, grade):
        """Lấy danh sách bài tập thực hành"""
        exercises = {
            'math': {
                'thcs': {
                    'basic': [
                        'Bài tập số học cơ bản',
                        'Bài tập phân số',
                        'Bài tập phương trình bậc nhất',
                        'Bài tập hình học cơ bản',
                        'Bài tập thống kê đơn giản'
                    ],
                    'intermediate': [
                        'Bài tập phương trình bậc hai',
                        'Bài tập hàm số',
                        'Bài tập lượng giác',
                        'Bài tập hình học phẳng',
                        'Bài tập xác suất'
                    ],
                    'advanced': [
                        'Bài tập phương trình bậc cao',
                        'Bài tập hàm số nâng cao',
                        'Bài tập lượng giác nâng cao',
                        'Bài tập hình học không gian',
                        'Bài tập xác suất nâng cao'
                    ]
                },
                'thpt': {
                    'basic': [
                        'Bài tập hàm số và đồ thị',
                        'Bài tập phương trình',
                        'Bài tập lượng giác',
                        'Bài tập hình học phẳng',
                        'Bài tập xác suất thống kê'
                    ],
                    'intermediate': [
                        'Bài tập hàm số mũ và logarit',
                        'Bài tập phương trình lượng giác',
                        'Bài tập hình học không gian',
                        'Bài tập tích phân',
                        'Bài tập xác suất nâng cao'
                    ],
                    'advanced': [
                        'Bài tập hàm số phức tạp',
                        'Bài tập phương trình vi phân',
                        'Bài tập hình học giải tích',
                        'Bài tập tích phân nâng cao',
                        'Bài tập xác suất thống kê nâng cao'
                    ]
                }
            },
            'physics': {
                'thcs': {
                    'basic': [
                        'Bài tập chuyển động cơ bản',
                        'Bài tập lực và chuyển động',
                        'Bài tập năng lượng cơ bản',
                        'Bài tập nhiệt học cơ bản',
                        'Bài tập điện học cơ bản'
                    ],
                    'intermediate': [
                        'Bài tập chuyển động nâng cao',
                        'Bài tập định luật Newton',
                        'Bài tập năng lượng và công',
                        'Bài tập nhiệt động lực học',
                        'Bài tập điện từ học'
                    ],
                    'advanced': [
                        'Bài tập cơ học nâng cao',
                        'Bài tập định luật bảo toàn',
                        'Bài tập nhiệt động lực học nâng cao',
                        'Bài tập điện từ học nâng cao',
                        'Bài tập quang học'
                    ]
                },
                'thpt': {
                    'basic': [
                        'Bài tập cơ học chất điểm',
                        'Bài tập điện trường',
                        'Bài tập từ trường',
                        'Bài tập quang hình học',
                        'Bài tập nhiệt động lực học'
                    ],
                    'intermediate': [
                        'Bài tập cơ học vật rắn',
                        'Bài tập điện từ trường',
                        'Bài tập quang học sóng',
                        'Bài tập nhiệt động lực học nâng cao',
                        'Bài tập sóng điện từ'
                    ],
                    'advanced': [
                        'Bài tập cơ học lượng tử',
                        'Bài tập thuyết tương đối',
                        'Bài tập vật lý hạt nhân',
                        'Bài tập điện từ học nâng cao',
                        'Bài tập quang học lượng tử'
                    ]
                }
            },
            'chemistry': {
                'thcs': {
                    'basic': [
                        'Bài tập cấu trúc nguyên tử',
                        'Bài tập bảng tuần hoàn',
                        'Bài tập liên kết hóa học',
                        'Bài tập phản ứng hóa học',
                        'Bài tập dung dịch'
                    ],
                    'intermediate': [
                        'Bài tập liên kết hóa học nâng cao',
                        'Bài tập phản ứng oxi hóa khử',
                        'Bài tập cân bằng hóa học',
                        'Bài tập hóa học hữu cơ',
                        'Bài tập điện hóa học'
                    ],
                    'advanced': [
                        'Bài tập hóa học vô cơ nâng cao',
                        'Bài tập hóa học hữu cơ nâng cao',
                        'Bài tập cân bằng hóa học nâng cao',
                        'Bài tập điện hóa học nâng cao',
                        'Bài tập hóa học thực nghiệm'
                    ]
                },
                'thpt': {
                    'basic': [
                        'Bài tập cấu trúc nguyên tử nâng cao',
                        'Bài tập liên kết hóa học',
                        'Bài tập phản ứng hóa học',
                        'Bài tập dung dịch điện li',
                        'Bài tập hóa học hữu cơ'
                    ],
                    'intermediate': [
                        'Bài tập hóa học lượng tử',
                        'Bài tập hóa học hữu cơ nâng cao',
                        'Bài tập hóa học vô cơ nâng cao',
                        'Bài tập điện hóa học',
                        'Bài tập hóa học phân tích'
                    ],
                    'advanced': [
                        'Bài tập hóa học lượng tử nâng cao',
                        'Bài tập hóa học hữu cơ chuyên sâu',
                        'Bài tập hóa học vô cơ chuyên sâu',
                        'Bài tập hóa học phân tích nâng cao',
                        'Bài tập hóa sinh học'
                    ]
                }
            }
        }
        
        subject_exercises = exercises.get(subject.lower(), {}).get(grade, {}).get(level, [])
        exercises_per_week = len(subject_exercises) // total_weeks
        start_idx = (week_number - 1) * exercises_per_week
        end_idx = start_idx + exercises_per_week
        
        return subject_exercises[start_idx:end_idx]
    
    def _get_learning_resources(self, subject, level, grade):
        """Lấy danh sách tài liệu học tập phù hợp"""
        resources = {
            'math': {
                'thcs': {
                    'basic': [
                        'Sách giáo khoa Toán THCS',
                        'Video bài giảng cơ bản',
                        'Bài tập trắc nghiệm cơ bản',
                        'Tài liệu ôn tập cơ bản'
                    ],
                    'intermediate': [
                        'Sách nâng cao THCS',
                        'Video bài giảng nâng cao',
                        'Bài tập tự luận',
                        'Đề thi thử'
                    ],
                    'advanced': [
                        'Sách chuyên sâu THCS',
                        'Video bài giảng chuyên sâu',
                        'Bài tập Olympic',
                        'Tài liệu nghiên cứu'
                    ]
                },
                'thpt': {
                    'basic': [
                        'Sách giáo khoa Toán THPT',
                        'Video bài giảng cơ bản',
                        'Bài tập trắc nghiệm cơ bản',
                        'Tài liệu ôn tập cơ bản'
                    ],
                    'intermediate': [
                        'Sách nâng cao THPT',
                        'Video bài giảng nâng cao',
                        'Bài tập tự luận',
                        'Đề thi thử'
                    ],
                    'advanced': [
                        'Sách chuyên sâu THPT',
                        'Video bài giảng chuyên sâu',
                        'Bài tập Olympic',
                        'Tài liệu nghiên cứu'
                    ]
                }
            },
            'physics': {
                'thcs': {
                    'basic': [
                        'Sách giáo khoa Vật lý THCS',
                        'Video thí nghiệm cơ bản',
                        'Bài tập trắc nghiệm cơ bản',
                        'Tài liệu ôn tập cơ bản'
                    ],
                    'intermediate': [
                        'Sách nâng cao THCS',
                        'Video thí nghiệm nâng cao',
                        'Bài tập tự luận',
                        'Đề thi thử'
                    ],
                    'advanced': [
                        'Sách chuyên sâu THCS',
                        'Video thí nghiệm chuyên sâu',
                        'Bài tập Olympic',
                        'Tài liệu nghiên cứu'
                    ]
                },
                'thpt': {
                    'basic': [
                        'Sách giáo khoa Vật lý THPT',
                        'Video thí nghiệm cơ bản',
                        'Bài tập trắc nghiệm cơ bản',
                        'Tài liệu ôn tập cơ bản'
                    ],
                    'intermediate': [
                        'Sách nâng cao THPT',
                        'Video thí nghiệm nâng cao',
                        'Bài tập tự luận',
                        'Đề thi thử'
                    ],
                    'advanced': [
                        'Sách chuyên sâu THPT',
                        'Video thí nghiệm chuyên sâu',
                        'Bài tập Olympic',
                        'Tài liệu nghiên cứu'
                    ]
                }
            },
            'chemistry': {
                'thcs': {
                    'basic': [
                        'Sách giáo khoa Hóa học THCS',
                        'Video thí nghiệm cơ bản',
                        'Bài tập trắc nghiệm cơ bản',
                        'Tài liệu ôn tập cơ bản'
                    ],
                    'intermediate': [
                        'Sách nâng cao THCS',
                        'Video thí nghiệm nâng cao',
                        'Bài tập tự luận',
                        'Đề thi thử'
                    ],
                    'advanced': [
                        'Sách chuyên sâu THCS',
                        'Video thí nghiệm chuyên sâu',
                        'Bài tập Olympic',
                        'Tài liệu nghiên cứu'
                    ]
                },
                'thpt': {
                    'basic': [
                        'Sách giáo khoa Hóa học THPT',
                        'Video thí nghiệm cơ bản',
                        'Bài tập trắc nghiệm cơ bản',
                        'Tài liệu ôn tập cơ bản'
                    ],
                    'intermediate': [
                        'Sách nâng cao THPT',
                        'Video thí nghiệm nâng cao',
                        'Bài tập tự luận',
                        'Đề thi thử'
                    ],
                    'advanced': [
                        'Sách chuyên sâu THPT',
                        'Video thí nghiệm chuyên sâu',
                        'Bài tập Olympic',
                        'Tài liệu nghiên cứu'
                    ]
                }
            }
        }
        
        return resources.get(subject.lower(), {}).get(grade, {}).get(level, [])

def main():
    # Khởi tạo AI
    ai = LearningPathAI()
    
    # Huấn luyện mô hình
    print("Bắt đầu huấn luyện mô hình...")
    ai.train()
    
    # Ví dụ sử dụng với một học sinh mới
    print("\nTạo lộ trình học tập cho học sinh mới:")
    learning_path = ai.generate_learning_path(
        subject='math',
        current_score=6.5,
        target_score=8.5,
        duration_weeks=8,
        daily_study_hours=2,
        learning_style='combined',
        grade='thpt'
    )
    
    if learning_path:
        # In kết quả
        for week in learning_path:
            print(f"\nTuần {week['week_number']} ({week['start_date']} - {week['end_date']}):")
            print(f"Cấp độ: {week['level']}")
            print(f"Cấp học: {week['grade']}")
            print(f"Tỷ lệ thành công dự đoán: {week['predicted_success_rate']}%")
            for day, plan in enumerate(week['daily_plans'], 1):
                print(f"\nNgày {day}:")
                print(f"Lý thuyết ({plan['theory_hours']} giờ):")
                for topic in plan['theory_topics']:
                    print(f"- {topic}")
                print(f"\nThực hành ({plan['practice_hours']} giờ):")
                for exercise in plan['practice_exercises']:
                    print(f"- {exercise}")
                print("\nTài liệu học tập:")
                for resource in plan['learning_resources']:
                    print(f"- {resource}")

if __name__ == "__main__":
    main() 