import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
from datetime import datetime, timedelta
import traceback
import os

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
        
        # Giới hạn môn học và cấp lớp
        self.ALLOWED_SUBJECTS = ['math', 'physics', 'chemistry']
        self.ALLOWED_GRADES = ['10', '11', '12']
        
        # Đọc dữ liệu từ các file Excel
        self.excel_data = {}
        try:
            print("\n[DEBUG] Đang đọc dữ liệu từ các file Excel...")
            
            # Đọc file theory.xlsx
            if os.path.exists('theory.xlsx'):
                self.excel_data['theory'] = pd.read_excel('theory.xlsx')
                print("[DEBUG] Đã đọc theory.xlsx")
            
            # Đọc file practice.xlsx
            if os.path.exists('practice.xlsx'):
                self.excel_data['practice'] = pd.read_excel('practice.xlsx')
                print("[DEBUG] Đã đọc practice.xlsx")
            
            # Đọc file topic.xlsx
            if os.path.exists('topic.xlsx'):
                self.excel_data['topic'] = pd.read_excel('topic.xlsx')
                print("[DEBUG] Đã đọc topic.xlsx")
            
            # Đọc file subject.xlsx
            if os.path.exists('subject.xlsx'):
                self.excel_data['subject'] = pd.read_excel('subject.xlsx')
                print("[DEBUG] Đã đọc subject.xlsx")
            
            # Đọc file grade.xlsx
            if os.path.exists('grade.xlsx'):
                self.excel_data['grade'] = pd.read_excel('grade.xlsx')
                print("[DEBUG] Đã đọc grade.xlsx")
            
            print("[DEBUG] Đã đọc xong tất cả các file Excel")
            
        except Exception as e:
            print(f"\n[ERROR] Lỗi khi đọc file Excel: {str(e)}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            self.excel_data = {}
        
    def _validate_input(self, subject, grade):
        """Kiểm tra tính hợp lệ của đầu vào"""
        if subject not in self.ALLOWED_SUBJECTS:
            raise ValueError(f"Môn học không hợp lệ. Chỉ chấp nhận: {', '.join(self.ALLOWED_SUBJECTS)}")
        if grade not in self.ALLOWED_GRADES:
            raise ValueError(f"Cấp lớp không hợp lệ. Chỉ chấp nhận: {', '.join(self.ALLOWED_GRADES)}")
        
    def train(self, training_data_path='training_data.csv'):
        """Huấn luyện mô hình với dữ liệu đã có"""
        try:
            print("\nBắt đầu huấn luyện mô hình...")
            
            # Đọc dữ liệu huấn luyện
            df = pd.read_csv(training_data_path)
            print(f"Đã đọc {len(df)} mẫu dữ liệu huấn luyện")
            
            # Kiểm tra dữ liệu
            required_columns = ['subject', 'grade', 'current_score', 'target_score',
                              'duration_weeks', 'daily_study_hours', 'learning_style', 'success_rate']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Thiếu các cột: {', '.join(missing_columns)}")
            
            # Fit các encoder với dữ liệu huấn luyện
            print("\nĐang fit các encoder...")
            for col, encoder in self.label_encoders.items():
                print(f"Fitting encoder cho {col}...")
                print(f"Unique values: {df[col].unique()}")
                encoder.fit(df[col])
                print(f"Encoder classes: {encoder.classes_}")
            
            # Tiền xử lý dữ liệu
            print("\nĐang tiền xử lý dữ liệu...")
            X = self._preprocess_features(df)
            y = df['success_rate']
            
            # Chia dữ liệu thành tập huấn luyện và tập kiểm tra
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            print("\nĐang huấn luyện mô hình Random Forest...")
            # Huấn luyện mô hình
            self.model.fit(X_train, y_train)
            
            # Đánh giá mô hình
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            
            print(f"\nKết quả huấn luyện:")
            print(f"Độ chính xác trên tập huấn luyện: {train_score:.2f}")
            print(f"Độ chính xác trên tập kiểm tra: {test_score:.2f}")
            
            self.is_trained = True
            
            # Lưu mô hình và encoder
            self.save_model()
            print("Đã lưu mô hình thành công")
            
            return True
            
        except Exception as e:
            print(f"\nLỗi khi huấn luyện mô hình: {str(e)}")
            import traceback
            print("Stack trace:")
            traceback.print_exc()
            self.is_trained = False
            return False
    
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
        """Dự đoán tỷ lệ thành công dựa trên các tham số đầu vào"""
        try:
            print("\n[DEBUG] ====== Bắt đầu dự đoán tỷ lệ thành công ======")
            print("[DEBUG] Input parameters:", {
                'subject': subject,
                'current_score': current_score,
                'target_score': target_score,
                'duration_weeks': duration_weeks,
                'daily_study_hours': daily_study_hours,
                'learning_style': learning_style,
                'grade': grade
            })
            
            # Kiểm tra xem mô hình đã được huấn luyện chưa
            if not self.is_trained:
                print("[DEBUG] Model not trained, attempting to train...")
                if not self.train():
                    print("[ERROR] Failed to train model")
                    return None
                print("[DEBUG] Model trained successfully")
            
            # Kiểm tra tính hợp lệ của đầu vào
            try:
                current_score = float(current_score)
                target_score = float(target_score)
                duration_weeks = float(duration_weeks)
                daily_study_hours = float(daily_study_hours)
                
                print(f"[DEBUG] Converted values: current_score={current_score}, target_score={target_score}, duration_weeks={duration_weeks}, daily_study_hours={daily_study_hours}")
                
                if not (0 <= current_score <= 10 and 0 <= target_score <= 10):
                    print("[ERROR] Scores must be between 0 and 10")
                    return None
                    
                if duration_weeks <= 0 or daily_study_hours <= 0:
                    print("[ERROR] Time values must be greater than 0")
                    return None
                    
            except ValueError as e:
                print(f"[ERROR] Error converting input values: {e}")
                return None
            
            # Chuẩn bị dữ liệu đầu vào
            print("[DEBUG] Preparing input data...")
            input_data = pd.DataFrame({
                'subject': [subject],
                'grade': [grade],
                'current_score': [current_score],
                'target_score': [target_score],
                'duration_weeks': [duration_weeks],
                'daily_study_hours': [daily_study_hours],
                'learning_style': [learning_style]
            })
            print("[DEBUG] Input data prepared:", input_data)
            
            # Mã hóa các biến phân loại
            print("[DEBUG] Encoding categorical features...")
            encoded_data = self._encode_categorical_features(input_data)
            if encoded_data is None:
                print("[ERROR] Failed to encode categorical features")
                return None
            print("[DEBUG] Encoded data:", encoded_data)
            
            # Dự đoán tỷ lệ thành công
            try:
                print("[DEBUG] Making prediction...")
                # Đảm bảo dữ liệu đầu vào là 2D array
                if len(encoded_data) == 0:
                    print("[ERROR] Encoded data is empty")
                    return None
                    
                # Chuyển đổi DataFrame thành numpy array và reshape
                X = encoded_data.values.reshape(1, -1)
                print(f"[DEBUG] Reshaped data shape: {X.shape}")
                
                success_rate = self.model.predict(X)[0]
                # Đảm bảo tỷ lệ thành công nằm trong khoảng 0-1
                success_rate = max(0.0, min(1.0, float(success_rate)))
                print(f"[DEBUG] Success rate predicted: {success_rate}")
                print("[DEBUG] ====== Kết thúc dự đoán tỷ lệ thành công ======\n")
                return success_rate
            except Exception as e:
                print(f"[ERROR] Error making prediction: {e}")
                import traceback
                print("[ERROR] Stack trace:")
                traceback.print_exc()
                return None
            
        except Exception as e:
            print("\n[ERROR] Exception in predict_success_rate:")
            print(f"[ERROR] Error type: {type(e).__name__}")
            print(f"[ERROR] Error message: {str(e)}")
            import traceback
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            print("[DEBUG] ====== Kết thúc dự đoán tỷ lệ thành công với lỗi ======\n")
            return None
    
    def generate_learning_path(self, subject, current_score, target_score, 
                             duration_weeks, daily_study_hours, learning_style, grade):
        """Tạo lộ trình học tập dựa trên đầu vào và dự đoán tỷ lệ thành công"""
        try:
            print("\n[DEBUG] ====== Bắt đầu tạo lộ trình học tập ======")
            print("[DEBUG] Input parameters:", {
                'subject': subject,
                'current_score': current_score,
                'target_score': target_score,
                'duration_weeks': duration_weeks,
                'daily_study_hours': daily_study_hours,
                'learning_style': learning_style,
                'grade': grade
            })
            
            if not self.is_trained:
                print("[DEBUG] Model not trained, attempting to train...")
                if not self.train():
                    print("[ERROR] Failed to train model")
                    return None
                print("[DEBUG] Model trained successfully")
            
            try:
                self._validate_input(subject, grade)
                print("[DEBUG] Input validation successful")
            except ValueError as e:
                print(f"[ERROR] Input validation failed: {e}")
                return None
            
            print("[DEBUG] Predicting success rate...")
            success_rate = self.predict_success_rate(
                subject, current_score, target_score,
                duration_weeks, daily_study_hours, learning_style, grade
            )
            
            if success_rate is None:
                print("[ERROR] Failed to predict success rate")
                return None
            print(f"[DEBUG] Success rate predicted: {success_rate}")
            
            print("[DEBUG] Determining learning level...")
            level = self._determine_level(current_score, target_score, success_rate)
            if level is None:
                print("[ERROR] Failed to determine learning level")
                return None
            print(f"[DEBUG] Learning level determined: {level}")
            
            print("[DEBUG] Generating learning path...")
            weekly_plans = []
            start_date = datetime.now()

            # Lấy thông tin chi tiết về các chủ đề
            topic_breakdown = self.get_topic_breakdown(subject, grade, level)
            if not topic_breakdown:
                print("[ERROR] Failed to get topic breakdown")
                return None

            # Tính toán tổng số bài học cần phân bổ
            total_lessons = sum(len(topic['lessons']) for topic in topic_breakdown['topics'])
            total_days = duration_weeks * 7
            lessons_per_day = max(1, total_lessons // total_days)

            # Khởi tạo biến theo dõi tiến độ
            current_topic_index = 0
            current_lesson_index = 0
            remaining_lessons = total_lessons

            for week in range(1, duration_weeks + 1):
                week_start = start_date + timedelta(days=(week-1)*7)
                week_end = week_start + timedelta(days=6)
                week_plan = {
                    'week_number': week,
                    'start_date': week_start.strftime('%Y-%m-%d'),
                    'end_date': week_end.strftime('%Y-%m-%d'),
                    'level': level,
                    'predicted_success_rate': float(success_rate),
                    'daily_plans': []
                }

                for day in range(7):
                    day_date = week_start + timedelta(days=day)
                    
                    # Tính số giờ học cho ngày
                    if learning_style == 'practical':
                        theory_hours = daily_study_hours * 0.3
                        practice_hours = daily_study_hours * 0.7
                    elif learning_style == 'theory':
                        theory_hours = daily_study_hours * 0.7
                        practice_hours = daily_study_hours * 0.3
                    else:  # combined
                        theory_hours = daily_study_hours * 0.5
                        practice_hours = daily_study_hours * 0.5

                    # Lấy bài học hiện tại
                    if current_topic_index < len(topic_breakdown['topics']):
                        current_topic = topic_breakdown['topics'][current_topic_index]
                        if current_lesson_index < len(current_topic['lessons']):
                            current_lesson = current_topic['lessons'][current_lesson_index]
                            
                            # Tạo kế hoạch cho ngày
                            daily_plan = {
                                'date': day_date.strftime('%Y-%m-%d'),
                                'theory_topics': [f"{current_topic['name']} - {current_lesson}"],
                                'practice_exercises': self._get_practice_exercises(subject, week, duration_weeks, level, grade),
                                'theory_hours': float(theory_hours),
                                'practice_hours': float(practice_hours),
                                'learning_resources': self._get_learning_resources(subject, level, grade),
                                'topic_details': [{
                                    'topic': current_topic['name'],
                                    'lesson': current_lesson,
                                    'estimated_hours': theory_hours,
                                    'completed': False
                                }]
                            }
                            
                            # Cập nhật chỉ số bài học
                            current_lesson_index += 1
                            if current_lesson_index >= len(current_topic['lessons']):
                                current_lesson_index = 0
                                current_topic_index += 1
                            
                            week_plan['daily_plans'].append(daily_plan)
                            remaining_lessons -= 1
                        else:
                            # Nếu đã học hết bài của chủ đề hiện tại, chuyển sang chủ đề tiếp theo
                            current_lesson_index = 0
                            current_topic_index += 1
                            if current_topic_index < len(topic_breakdown['topics']):
                                current_topic = topic_breakdown['topics'][current_topic_index]
                                current_lesson = current_topic['lessons'][0]
                                
                                daily_plan = {
                                    'date': day_date.strftime('%Y-%m-%d'),
                                    'theory_topics': [f"{current_topic['name']} - {current_lesson}"],
                                    'practice_exercises': self._get_practice_exercises(subject, week, duration_weeks, level, grade),
                                    'theory_hours': float(theory_hours),
                                    'practice_hours': float(practice_hours),
                                    'learning_resources': self._get_learning_resources(subject, level, grade),
                                    'topic_details': [{
                                        'topic': current_topic['name'],
                                        'lesson': current_lesson,
                                        'estimated_hours': theory_hours,
                                        'completed': False
                                    }]
                                }
                                
                                current_lesson_index = 1
                                week_plan['daily_plans'].append(daily_plan)
                                remaining_lessons -= 1
                            else:
                                # Nếu đã học hết tất cả chủ đề, tạo kế hoạch ôn tập
                                daily_plan = {
                                    'date': day_date.strftime('%Y-%m-%d'),
                                    'theory_topics': ['Ôn tập và củng cố kiến thức'],
                                    'practice_exercises': self._get_practice_exercises(subject, week, duration_weeks, level, grade),
                                    'theory_hours': float(theory_hours),
                                    'practice_hours': float(practice_hours),
                                    'learning_resources': self._get_learning_resources(subject, level, grade),
                                    'topic_details': [{
                                        'topic': 'Ôn tập',
                                        'lesson': 'Củng cố kiến thức',
                                        'estimated_hours': theory_hours,
                                        'completed': False
                                    }]
                                }
                                week_plan['daily_plans'].append(daily_plan)
                    else:
                        # Nếu đã học hết tất cả chủ đề, tạo kế hoạch ôn tập
                        daily_plan = {
                            'date': day_date.strftime('%Y-%m-%d'),
                            'theory_topics': ['Ôn tập và củng cố kiến thức'],
                            'practice_exercises': self._get_practice_exercises(subject, week, duration_weeks, level, grade),
                            'theory_hours': float(theory_hours),
                            'practice_hours': float(practice_hours),
                            'learning_resources': self._get_learning_resources(subject, level, grade),
                            'topic_details': [{
                                'topic': 'Ôn tập',
                                'lesson': 'Củng cố kiến thức',
                                'estimated_hours': theory_hours,
                                'completed': False
                            }]
                        }
                        week_plan['daily_plans'].append(daily_plan)

                weekly_plans.append(week_plan)

            if not weekly_plans:
                print("[ERROR] Failed to generate learning path")
                return None
            print("[DEBUG] Successfully generated learning path")
            print("[DEBUG] ====== Kết thúc tạo lộ trình học tập ======\n")
            
            # Trả về kết quả theo cấu trúc mong đợi
            return {
                'weekly_plans': weekly_plans,
                'subject': subject,
                'grade': grade,
                'level': level,
                'predicted_success_rate': float(success_rate),
                'total_weeks': duration_weeks,
                'daily_study_hours': daily_study_hours,
                'learning_style': learning_style
            }

        except Exception as e:
            print("\n[ERROR] Exception in generate_learning_path:")
            print(f"[ERROR] Error type: {type(e).__name__}")
            print(f"[ERROR] Error message: {str(e)}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            print("[DEBUG] ====== Kết thúc tạo lộ trình học tập với lỗi ======\n")
            return None
    
    def _determine_level(self, current_score, target_score, success_rate):
        """Xác định cấp độ học dựa trên điểm số hiện tại, mục tiêu và tỷ lệ thành công"""
        try:
            # Chuyển đổi các giá trị thành float
            current_score = float(current_score)
            target_score = float(target_score)
            success_rate = float(success_rate)
            
            # Kiểm tra tính hợp lệ của các giá trị
            if not (0 <= current_score <= 10 and 0 <= target_score <= 10):
                print("Điểm số phải nằm trong khoảng 0-10")
                return "basic"
            
            if not (0 <= success_rate <= 1):
                print("Tỷ lệ thành công không hợp lệ")
                return "basic"
            
            # Tính toán khoảng cách điểm
            score_gap = target_score - current_score
            
            # Xác định cấp độ dựa trên các tiêu chí
            if current_score < 5:
                return "basic"
            elif current_score < 7:
                if score_gap > 2:
                    return "basic"
                else:
                    return "intermediate"
            elif current_score < 8.5:
                if score_gap > 1.5:
                    return "intermediate"
                else:
                    return "advanced"
            else:
                if score_gap > 1:
                    return "advanced"
                else:
                    return "expert"
                    
        except Exception as e:
            print(f"Lỗi khi xác định cấp độ: {e}")
            return "basic"  # Trả về cấp độ cơ bản trong trường hợp lỗi
    
    def _create_daily_plan(self, subject, learning_style, daily_hours, week_number, total_weeks, level, grade):
        """Tạo kế hoạch học tập cho một ngày"""
        try:
            print(f"\n[DEBUG] Creating daily plan for subject={subject}, learning_style={learning_style}, daily_hours={daily_hours}, week={week_number}, level={level}, grade={grade}")
            
            # Tính toán thời gian học cho mỗi ngày
            if learning_style == 'practical':
                theory_hours = daily_hours * 0.3
                practice_hours = daily_hours * 0.7
            elif learning_style == 'theory':
                theory_hours = daily_hours * 0.7
                practice_hours = daily_hours * 0.3
            else:  # combined
                theory_hours = daily_hours * 0.5
                practice_hours = daily_hours * 0.5
            
            print(f"[DEBUG] Calculated hours: theory={theory_hours}, practice={practice_hours}")
            
            # Lấy tất cả chủ đề lý thuyết
            print("[DEBUG] Getting theory topics...")
            all_topics = self._get_theory_topics(subject, 1, total_weeks, level, grade)
            if not all_topics:
                print(f"[ERROR] No theory topics found for subject={subject}, level={level}, grade={grade}")
                return None
            print(f"[DEBUG] Found {len(all_topics)} theory topics")
            
            # Tính toán thời gian cần thiết cho mỗi chủ đề
            topic_time_estimates = {
                'math': {
                    '10': {
                        'Hàm số và đồ thị': 2.0,
                        'Hàm số bậc ba': 3.0,
                        'Phương trình bậc ba': 2.5,
                        'Bất phương trình bậc hai': 2.0,
                        'Hệ phương trình bậc ba': 2.5,
                        'Phương trình chứa căn': 2.0,
                        'Phương trình chứa dấu giá trị tuyệt đối': 2.0
                    },
                    '11': {
                        'Hàm số lượng giác': 3.0,
                        'Phương trình lượng giác cơ bản': 2.5,
                        'Tổ hợp và xác suất': 3.0,
                        'Dãy số và cấp số': 2.5,
                        'Giới hạn của dãy số': 2.0,
                        'Giới hạn của hàm số': 2.0
                    },
                    '12': {
                        'Khảo sát và vẽ đồ thị hàm số': 3.0,
                        'Tích phân và ứng dụng': 3.5,
                        'Số phức': 2.5,
                        'Hình học không gian': 3.0,
                        'Phương pháp tọa độ trong không gian': 2.5,
                        'Mặt cầu và mặt tròn xoay': 2.0
                    }
                },
                # ... (giữ nguyên các phần khác của topic_time_estimates)
            }
            
            # Tính toán tổng số ngày đã học
            total_days = (week_number - 1) * 7 + 1
            
            # Tính toán chủ đề hiện tại dựa trên tổng số ngày đã học
            current_topic_index = 0
            remaining_hours = 0
            total_hours_used = 0
            
            # Tìm chủ đề hiện tại dựa trên tổng số giờ đã học
            for topic in all_topics:
                topic_time = topic_time_estimates.get(subject, {}).get(grade, {}).get(topic['name'], 2.0)
                if total_hours_used + topic_time > total_days * theory_hours:
                    remaining_hours = topic_time - (total_days * theory_hours - total_hours_used)
                    break
                total_hours_used += topic_time
                current_topic_index += 1
            
            # Nếu đã học hết tất cả chủ đề, quay lại chủ đề đầu tiên
            if current_topic_index >= len(all_topics):
                current_topic_index = 0
                total_hours_used = 0
                remaining_hours = topic_time_estimates.get(subject, {}).get(grade, {}).get(all_topics[0]['name'], 2.0)
            
            current_topic = all_topics[current_topic_index]
            
            # Lấy bài tập thực hành tương ứng với chủ đề hiện tại
            print("[DEBUG] Getting practice exercises...")
            practice_exercises = self._get_practice_exercises(subject, week_number, total_weeks, level, grade)
            if not practice_exercises:
                print(f"[ERROR] No practice exercises found for subject={subject}, week={week_number}, level={level}, grade={grade}")
                return None
            print(f"[DEBUG] Found {len(practice_exercises)} practice exercises")
            
            # Lấy tài liệu học tập
            print("[DEBUG] Getting learning resources...")
            learning_resources = self._get_learning_resources(subject, grade, level)
            if not learning_resources:
                print(f"[ERROR] No learning resources found for subject={subject}, level={level}, grade={grade}")
                return None
            print(f"[DEBUG] Found {len(learning_resources)} learning resources")
            
            # Tạo kế hoạch chi tiết cho ngày
            daily_plan = {
                'theory_topics': [],
                'practice_exercises': [],
                'theory_hours': float(theory_hours),
                'practice_hours': float(practice_hours),
                'learning_resources': learning_resources,
                'topic_details': []
            }
            
            # Tính toán thời gian học cho ngày hiện tại
            if remaining_hours <= theory_hours:
                # Học nốt phần còn lại của chủ đề
                daily_plan['theory_topics'].append(f"{current_topic['name']} (Hoàn thành - {remaining_hours:.1f} giờ)")
                daily_plan['topic_details'].append({
                    'topic': f"{current_topic['name']} (Hoàn thành - {remaining_hours:.1f} giờ)",
                    'estimated_hours': remaining_hours,
                    'completed': True
                })
            else:
                # Học một phần của chủ đề
                daily_plan['theory_topics'].append(f"{current_topic['name']} (Còn {remaining_hours - theory_hours:.1f} giờ)")
                daily_plan['topic_details'].append({
                    'topic': f"{current_topic['name']} (Còn {remaining_hours - theory_hours:.1f} giờ)",
                    'estimated_hours': theory_hours,
                    'completed': False
                })
            
            # Phân bổ thời gian cho bài tập
            remaining_practice_hours = practice_hours
            for exercise in practice_exercises:
                # Ước tính thời gian làm bài tập (thường bằng 1/2 thời gian học lý thuyết)
                exercise_time = 1.0  # Mặc định 1 giờ cho mỗi bài tập
                
                if remaining_practice_hours >= exercise_time:
                    daily_plan['practice_exercises'].append(exercise)
                    daily_plan['topic_details'].append({
                        'topic': exercise['name'],
                        'estimated_hours': exercise_time,
                        'completed': False
                    })
                    remaining_practice_hours -= exercise_time
                else:
                    break
            
            print("[DEBUG] Successfully created daily plan")
            return daily_plan
            
        except Exception as e:
            print(f"\n[ERROR] Exception in _create_daily_plan:")
            print(f"[ERROR] Error type: {type(e).__name__}")
            print(f"[ERROR] Error message: {str(e)}")
            import traceback
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            return None
    
    def evaluate_student_profile(self, current_score, target_score, learning_style, daily_study_hours, duration_weeks):
        """Đánh giá hồ sơ học sinh và đề xuất cấp độ học phù hợp"""
        # Tính toán tổng thời gian học có sẵn
        total_available_hours = daily_study_hours * 5 * duration_weeks  # 5 ngày/tuần
        
        # Tính toán khoảng cách điểm số
        score_gap = target_score - current_score
        
        # Đánh giá cấp độ học phù hợp
        if current_score < 5:
            recommended_level = 'basic'
            required_hours = 22.5  # Giờ cần thiết cho cấp độ basic
        elif current_score < 7:
            recommended_level = 'intermediate'
            required_hours = 33.5  # Giờ cần thiết cho cấp độ intermediate
        else:
            recommended_level = 'advanced'
            required_hours = 44.5  # Giờ cần thiết cho cấp độ advanced
            
        # Đánh giá tính khả thi của mục tiêu
        feasibility = self._assess_goal_feasibility(
            total_available_hours,
            required_hours,
            score_gap,
            learning_style
        )
        
        return {
            'recommended_level': recommended_level,
            'required_hours': required_hours,
            'available_hours': total_available_hours,
            'feasibility': feasibility,
            'score_gap': score_gap
        }
    
    def _assess_goal_feasibility(self, available_hours, required_hours, score_gap, learning_style):
        """Đánh giá tính khả thi của mục tiêu học tập"""
        # Tính toán hệ số điều chỉnh dựa trên phong cách học
        style_factor = {
            'practical': 0.9,  # Cần ít thời gian hơn cho lý thuyết
            'theory': 1.1,    # Cần nhiều thời gian hơn cho lý thuyết
            'combined': 1.0   # Cân bằng
        }.get(learning_style, 1.0)
        
        # Tính toán thời gian cần thiết có điều chỉnh
        adjusted_required_hours = required_hours * style_factor
        
        # Đánh giá tính khả thi
        if available_hours >= adjusted_required_hours * 1.2:
            return 'high'  # Rất khả thi
        elif available_hours >= adjusted_required_hours:
            return 'medium'  # Khả thi
        else:
            return 'low'  # Ít khả thi
    
    def generate_detailed_schedule(self, subject, current_score, target_score, 
                                 duration_weeks, daily_study_hours, learning_style, grade):
        """Tạo lịch học chi tiết dựa trên đánh giá hồ sơ"""
        # Đánh giá hồ sơ học sinh
        profile = self.evaluate_student_profile(
            current_score, target_score, learning_style, 
            daily_study_hours, duration_weeks
        )
        
        # Tạo lịch học chi tiết
        schedule = []
        current_date = datetime.now()
        
        # Phân bổ thời gian theo cấp độ
        level_hours = {
            'basic': 22.5,
            'intermediate': 33.5,
            'advanced': 44.5
        }
        
        # Tính số tuần cho mỗi cấp độ
        total_hours = level_hours[profile['recommended_level']]
        weeks_per_level = max(1, int(total_hours / (daily_study_hours * 5)))
        
        for week in range(duration_weeks):
            week_plan = {
                'week_number': week + 1,
                'start_date': current_date.strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=6)).strftime('%Y-%m-%d'),
                'level': profile['recommended_level'],
                'daily_schedule': []
            }
            
            # Tạo lịch học cho từng ngày
            for day in range(7):
                if day < 5:  # Chỉ học 5 ngày/tuần
                    daily_schedule = self._create_detailed_daily_schedule(
                        subject=subject,
                        learning_style=learning_style,
                        daily_hours=daily_study_hours,
                        week_number=week + 1,
                        level=profile['recommended_level'],
                        grade=grade
                    )
                    week_plan['daily_schedule'].append(daily_schedule)
                else:
                    # Cuối tuần: ôn tập và nghỉ ngơi
                    week_plan['daily_schedule'].append({
                        'day': 'weekend',
                        'activities': ['Ôn tập', 'Nghỉ ngơi'] if day == 6 else ['Nghỉ ngơi']
                    })
            
            schedule.append(week_plan)
            current_date += timedelta(days=7)
        
        return {
            'student_profile': profile,
            'schedule': schedule
        }
    
    def _create_detailed_daily_schedule(self, subject, learning_style, daily_hours, 
                                      week_number, level, grade):
        """Tạo lịch học chi tiết cho một ngày"""
        # Phân bổ thời gian học
        if learning_style == 'practical':
            theory_hours = daily_hours * 0.3
            practice_hours = daily_hours * 0.7
        elif learning_style == 'theory':
            theory_hours = daily_hours * 0.7
            practice_hours = daily_hours * 0.3
        else:  # combined
            theory_hours = daily_hours * 0.5
            practice_hours = daily_hours * 0.5
        
        # Lấy nội dung học
        theory_topics = self._get_theory_topics(subject, week_number, 12, level, grade)
        practice_exercises = self._get_practice_exercises(subject, week_number, 12, level, grade)
        
        # Tạo lịch học chi tiết
        schedule = {
            'morning': {
                'time': '08:00 - 10:00',
                'activity': 'Học lý thuyết',
                'topics': theory_topics,
                'duration': theory_hours
            },
            'afternoon': {
                'time': '14:00 - 16:00',
                'activity': 'Làm bài tập',
                'exercises': practice_exercises,
                'duration': practice_hours
            },
            'evening': {
                'time': '19:00 - 20:00',
                'activity': 'Ôn tập và chuẩn bị bài mới',
                'duration': 1
            }
        }
        
        return schedule
    
    def _get_theory_topics(self, subject, week_number, total_weeks, level, grade):
        """Lấy danh sách chủ đề lý thuyết từ Excel"""
        try:
            print("\n[DEBUG] ====== Bắt đầu lấy chủ đề lý thuyết ======")
            print(f"[DEBUG] Input parameters: subject={subject}, week={week_number}, level={level}, grade={grade}")
            
            if 'theory' not in self.excel_data:
                print("[ERROR] Không tìm thấy dữ liệu theory trong excel_data")
                return []
                
            theory_df = self.excel_data['theory']
            print(f"[DEBUG] Columns in theory.xlsx: {theory_df.columns.tolist()}")
            
            # Lấy ID_subject từ bảng subject
            if 'subject' in self.excel_data:
                subject_df = self.excel_data['subject']
                print(f"[DEBUG] Columns in subject.xlsx: {subject_df.columns.tolist()}")
                
                # Chuyển đổi tên môn học thành định dạng phù hợp
                subject_mapping = {
                    'math': 'Toán học',
                    'physics': 'Vật lý',
                    'chemistry': 'Hóa học'
                }
                
                subject_name = subject_mapping.get(subject.lower())
                if not subject_name:
                    print(f"[ERROR] Không tìm thấy tên môn học cho {subject}")
                    return []
                    
                # Tìm ID_subject tương ứng
                subject_row = subject_df[subject_df['name_subject'] == subject_name]
                if subject_row.empty:
                    print(f"[ERROR] Không tìm thấy môn học {subject} trong bảng subject")
                    return []
                    
                subject_id = subject_row['ID_subject'].iloc[0]
                print(f"[DEBUG] ID_subject cho {subject}: {subject_id}")
                
                # Lấy ID_grade từ bảng grade
                if 'grade' in self.excel_data:
                    grade_df = self.excel_data['grade']
                    grade_row = grade_df[grade_df['name_grade'] == f'Lớp {grade}']
                    if grade_row.empty:
                        print(f"[ERROR] Không tìm thấy lớp {grade} trong bảng grade")
                        return []
                        
                    grade_id = grade_row['ID_grade'].iloc[0]
                    print(f"[DEBUG] ID_grade cho lớp {grade}: {grade_id}")
                    
                    # Lọc theo ID_subject và ID_grade
                    filtered_theory = theory_df[
                        (theory_df['ID_subject'] == subject_id) &
                        (theory_df['ID_grade'] == grade_id)
                    ]
                    print(f"[DEBUG] Số lượng chủ đề tìm thấy: {len(filtered_theory)}")
                else:
                    print("[ERROR] Không tìm thấy bảng grade")
                    return []
            else:
                print("[ERROR] Không tìm thấy bảng subject")
                return []
            
            # Lọc theo cấp độ
            filtered_theory = filtered_theory[filtered_theory['level'] == level]
            print(f"[DEBUG] Số lượng chủ đề sau khi lọc theo level {level}: {len(filtered_theory)}")
            
            # Sắp xếp theo thứ tự ưu tiên nếu có cột priority
            if 'priority' in filtered_theory.columns:
                filtered_theory = filtered_theory.sort_values('priority')
            
            # Tính số chủ đề cần lấy dựa trên tuần học
            topics_per_week = max(1, len(filtered_theory) // total_weeks)
            start_idx = (week_number - 1) * topics_per_week
            end_idx = start_idx + topics_per_week
            
            selected_topics = filtered_theory.iloc[start_idx:end_idx]
            print(f"[DEBUG] Số lượng chủ đề được chọn: {len(selected_topics)}")
            
            # Chuyển đổi thành định dạng mong muốn
            topics = []
            for _, row in selected_topics.iterrows():
                topic = {
                    'name': row['theory_name'],
                    'description': row.get('content', ''),
                    'estimated_hours': float(row.get('estimated_time', 2.0))
                }
                topics.append(topic)
            
            print(f"[DEBUG] Số lượng chủ đề trả về: {len(topics)}")
            print("[DEBUG] ====== Kết thúc lấy chủ đề lý thuyết ======\n")
            return topics
            
        except Exception as e:
            print(f"[ERROR] Lỗi khi lấy chủ đề lý thuyết: {str(e)}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            print("[DEBUG] ====== Kết thúc lấy chủ đề lý thuyết với lỗi ======\n")
            return []
    
    def _get_practice_exercises(self, subject, week_number, total_weeks, level, grade):
        """Lấy danh sách bài tập từ Excel hoặc tạo mới nếu chưa có"""
        try:
            print("\n[DEBUG] ====== Bắt đầu lấy bài tập ======")
            print(f"[DEBUG] Input parameters: subject={subject}, week={week_number}, level={level}, grade={grade}")
            
            if 'practice' not in self.excel_data:
                print("[DEBUG] Không tìm thấy dữ liệu practice trong excel_data")
                return []
                
            practice_df = self.excel_data['practice']
            print(f"[DEBUG] Columns in practice.xlsx: {practice_df.columns.tolist()}")
            
            # Lấy ID_subject từ bảng subject
            if 'subject' in self.excel_data:
                subject_df = self.excel_data['subject']
                print(f"[DEBUG] Columns in subject.xlsx: {subject_df.columns.tolist()}")
                print(f"[DEBUG] Subject data:\n{subject_df}")
                
                # Chuyển đổi tên môn học thành định dạng phù hợp
                subject_mapping = {
                    'math': 'Toán học',
                    'physics': 'Vật lý',
                    'chemistry': 'Hóa học'
                }
                
                subject_name = subject_mapping.get(subject.lower())
                if not subject_name:
                    print(f"[ERROR] Không tìm thấy tên môn học cho {subject}")
                    return []
                    
                print(f"[DEBUG] Tìm kiếm môn học: {subject_name}")
                # Tìm ID_subject tương ứng
                subject_row = subject_df[subject_df['name_subject'] == subject_name]
                print(f"[DEBUG] Kết quả tìm kiếm:\n{subject_row}")
                
                if subject_row.empty:
                    print(f"[ERROR] Không tìm thấy môn học {subject} trong bảng subject")
                    return []
                    
                subject_id = subject_row['ID_subject'].iloc[0]
                print(f"[DEBUG] ID_subject cho {subject}: {subject_id}")
                
                # Lọc theo ID_subject
                filtered_practice = practice_df[practice_df['ID_subject'] == subject_id]
                print(f"[DEBUG] Số lượng bài tập tìm thấy: {len(filtered_practice)}")
                print(f"[DEBUG] Bài tập tìm thấy:\n{filtered_practice}")
            else:
                print("[ERROR] Không tìm thấy bảng subject")
                return []
            
            # Lọc theo cấp độ
            filtered_practice = filtered_practice[filtered_practice['level'] == level]
            print(f"[DEBUG] Số lượng bài tập sau khi lọc theo level {level}: {len(filtered_practice)}")
            
            # Sắp xếp theo thứ tự ưu tiên nếu có cột priority
            if 'priority' in filtered_practice.columns:
                filtered_practice = filtered_practice.sort_values('priority')
            
            # Tính số bài tập cần lấy dựa trên tuần học
            exercises_per_week = max(1, len(filtered_practice) // total_weeks)
            start_idx = (week_number - 1) * exercises_per_week
            end_idx = start_idx + exercises_per_week
            
            selected_exercises = filtered_practice.iloc[start_idx:end_idx]
            print(f"[DEBUG] Số lượng bài tập được chọn: {len(selected_exercises)}")
            
            # Chuyển đổi thành định dạng mong muốn
            exercises = []
            for _, row in selected_exercises.iterrows():
                exercise = {
                    'name': row['practice_name'],
                    'description': row.get('description', ''),
                    'difficulty': row.get('difficulty', 'medium')
                }
                exercises.append(exercise)
            
            print(f"[DEBUG] Số lượng bài tập trả về: {len(exercises)}")
            print("[DEBUG] ====== Kết thúc lấy bài tập ======\n")
            return exercises
            
        except Exception as e:
            print(f"[ERROR] Lỗi khi lấy bài tập: {str(e)}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            print("[DEBUG] ====== Kết thúc lấy bài tập với lỗi ======\n")
            return []

    def create_flexible_schedule(self, subject, current_score, target_score, 
                               available_hours, learning_style, grade, preferred_times=None):
        """Tạo lịch học linh hoạt dựa trên thời gian có sẵn của người học
        
        Args:
            subject: Môn học
            current_score: Điểm số hiện tại
            target_score: Điểm số mục tiêu
            available_hours: Dict chứa thời gian có sẵn cho mỗi ngày trong tuần
                           Ví dụ: {'monday': ['18:00-20:00'], 'wednesday': ['19:00-21:00']}
            learning_style: Phong cách học (practical/theory/combined)
            grade: Lớp học
            preferred_times: Dict chứa thời gian ưa thích cho mỗi loại hoạt động
                           Ví dụ: {'theory': 'morning', 'practice': 'afternoon'}
        """
        # Đánh giá hồ sơ học sinh
        profile = self.evaluate_student_profile(
            current_score, target_score, learning_style,
            sum(len(times) for times in available_hours.values()) / 7,  # Ước tính giờ học trung bình mỗi ngày
            12  # Giả định 12 tuần
        )
        
        # Chuyển đổi thời gian có sẵn thành định dạng dễ xử lý
        available_slots = self._convert_time_slots(available_hours)
        
        # Tạo lịch học linh hoạt
        schedule = []
        current_date = datetime.now()
        
        # Phân bổ nội dung học theo cấp độ
        level_content = {
            'theory': self._get_theory_topics(subject, 1, 12, profile['recommended_level'], grade),
            'practice': self._get_practice_exercises(subject, 1, 12, profile['recommended_level'], grade)
        }
        
        # Tạo lịch học cho mỗi ngày có thời gian
        for day, slots in available_slots.items():
            daily_schedule = {
                'date': current_date.strftime('%Y-%m-%d'),
                'day': day,
                'slots': []
            }
            
            # Phân bổ nội dung học cho mỗi khung giờ
            for slot in slots:
                start_time, end_time = slot
                duration = self._calculate_duration(start_time, end_time)
                
                # Xác định loại hoạt động dựa trên thời gian và sở thích
                activity_type = self._determine_activity_type(
                    start_time, 
                    preferred_times.get('theory', 'morning'),
                    preferred_times.get('practice', 'afternoon')
                )
                
                # Phân bổ nội dung học
                if activity_type == 'theory':
                    content = level_content['theory'][:1]  # Lấy một chủ đề
                    level_content['theory'] = level_content['theory'][1:]  # Cập nhật danh sách còn lại
                else:
                    content = level_content['practice'][:1]  # Lấy một bài tập
                    level_content['practice'] = level_content['practice'][1:]  # Cập nhật danh sách còn lại
                
                daily_schedule['slots'].append({
                    'time': f"{start_time}-{end_time}",
                    'duration': duration,
                    'activity': activity_type,
                    'content': content[0] if content else "Ôn tập",
                    'break_time': self._calculate_break_time(duration)
                })
            
            schedule.append(daily_schedule)
            current_date += timedelta(days=1)
        
        return {
            'student_profile': profile,
            'schedule': schedule,
            'remaining_content': {
                'theory': level_content['theory'],
                'practice': level_content['practice']
            }
        }
    
    def _convert_time_slots(self, available_hours):
        """Chuyển đổi thời gian có sẵn thành định dạng dễ xử lý"""
        converted_slots = {}
        for day, times in available_hours.items():
            converted_slots[day] = []
            for time_slot in times:
                start, end = time_slot.split('-')
                converted_slots[day].append((start.strip(), end.strip()))
        return converted_slots
    
    def _calculate_duration(self, start_time, end_time):
        """Tính toán thời lượng học"""
        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')
        duration = (end - start).total_seconds() / 3600  # Chuyển đổi thành giờ
        return round(duration, 1)
    
    def _determine_activity_type(self, time, preferred_theory_time, preferred_practice_time):
        """Xác định loại hoạt động dựa trên thời gian và sở thích"""
        hour = int(time.split(':')[0])
        
        if preferred_theory_time == 'morning' and hour < 12:
            return 'theory'
        elif preferred_theory_time == 'afternoon' and 12 <= hour < 17:
            return 'theory'
        elif preferred_theory_time == 'evening' and hour >= 17:
            return 'theory'
        else:
            return 'practice'
    
    def _calculate_break_time(self, duration):
        """Tính toán thời gian nghỉ giữa các buổi học"""
        if duration <= 1:
            return 0
        elif duration <= 2:
            return 15  # 15 phút nghỉ
        else:
            return 30  # 30 phút nghỉ

    def _encode_categorical_features(self, df):
        """Mã hóa các biến phân loại"""
        try:
            print("\n[DEBUG] ====== Bắt đầu mã hóa dữ liệu phân loại ======")
            print("[DEBUG] Input DataFrame:", df)
            
            # Kiểm tra DataFrame rỗng
            if df.empty:
                print("[ERROR] Input DataFrame is empty")
                return None
                
            print("[DEBUG] DataFrame info:")
            print(df.info())
            print("\n[DEBUG] DataFrame description:")
            print(df.describe())
            
            # Tạo bản sao của DataFrame để tránh thay đổi dữ liệu gốc
            encoded_df = df.copy()
            
            # Chuyển đổi grade thành integer
            if 'grade' in encoded_df.columns:
                print("[DEBUG] Converting grade to integer")
                try:
                    encoded_df['grade'] = encoded_df['grade'].astype(int)
                    print(f"[DEBUG] Converted grade values: {encoded_df['grade'].values}")
                except Exception as e:
                    print(f"[ERROR] Error converting grade to integer: {e}")
                    return None
            
            # Kiểm tra các biến phân loại
            categorical_columns = ['subject', 'grade', 'learning_style']
            for col in categorical_columns:
                if col not in encoded_df.columns:
                    print(f"[ERROR] Missing column: {col}")
                    return None
                print(f"[DEBUG] Found column: {col}")
                print(f"[DEBUG] Unique values in {col}: {encoded_df[col].unique()}")
            
            # Đọc dữ liệu training để fit encoder
            try:
                training_data = pd.read_csv('training_data.csv')
                if training_data.empty:
                    print("[ERROR] Training data is empty")
                    return None
                    
                # Chuyển đổi grade trong training data thành integer
                if 'grade' in training_data.columns:
                    training_data['grade'] = training_data['grade'].astype(int)
                print("[DEBUG] Successfully loaded training data")
                print(f"[DEBUG] Training data shape: {training_data.shape}")
            except Exception as e:
                print(f"[ERROR] Error loading training data: {e}")
                return None
            
            # Mã hóa các biến phân loại
            for col, encoder in self.label_encoders.items():
                if col in encoded_df.columns:
                    print(f"\n[DEBUG] Processing column: {col}")
                    
                    # Fit encoder với dữ liệu training
                    try:
                        print(f"[DEBUG] Fitting encoder for {col} with training data")
                        encoder.fit(training_data[col])
                        print(f"[DEBUG] Encoder fitted with classes: {encoder.classes_}")
                    except Exception as e:
                        print(f"[ERROR] Error fitting encoder for {col}: {e}")
                        return None
                    
                    # Kiểm tra xem giá trị có nằm trong classes không
                    unique_values = encoded_df[col].unique()
                    for value in unique_values:
                        if value not in encoder.classes_:
                            print(f"[ERROR] Value '{value}' not found in encoder classes for {col}")
                            print(f"[ERROR] Available classes: {encoder.classes_}")
                            return None
                    
                    # Chuyển đổi dữ liệu
                    try:
                        print(f"[DEBUG] Transforming data for column: {col}")
                        print(f"[DEBUG] Original values: {encoded_df[col].values}")
                        encoded_df[col] = encoder.transform(encoded_df[col])
                        print(f"[DEBUG] Encoded values: {encoded_df[col].values}")
                    except Exception as e:
                        print(f"[ERROR] Error transforming {col}: {e}")
                        return None
            
            print("\n[DEBUG] Final encoded DataFrame:")
            print(encoded_df)
            print("\n[DEBUG] Final DataFrame info:")
            print(encoded_df.info())
            print("\n[DEBUG] ====== Kết thúc mã hóa dữ liệu phân loại ======\n")
            
            # Kiểm tra DataFrame sau khi mã hóa
            if encoded_df.empty:
                print("[ERROR] Encoded DataFrame is empty")
                return None
                
            return encoded_df
            
        except Exception as e:
            print("\n[ERROR] Exception in _encode_categorical_features:")
            print(f"[ERROR] Error type: {type(e).__name__}")
            print(f"[ERROR] Error message: {str(e)}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            print("[DEBUG] ====== Kết thúc mã hóa dữ liệu phân loại với lỗi ======\n")
            return None

    def _get_learning_resources(self, subject, grade, level):
        """Lấy tài liệu học tập từ Excel"""
        try:
            print("\n[DEBUG] ====== Bắt đầu lấy tài liệu học tập ======")
            print(f"[DEBUG] Input parameters: subject={subject}, grade={grade}, level={level}")
            
            if 'topic' not in self.excel_data:
                print("[ERROR] Không tìm thấy dữ liệu topic trong excel_data")
                return []
                
            topic_df = self.excel_data['topic']
            print(f"[DEBUG] Columns in topic.xlsx: {topic_df.columns.tolist()}")
            
            # Lấy ID_subject từ bảng subject
            if 'subject' in self.excel_data:
                subject_df = self.excel_data['subject']
                print(f"[DEBUG] Columns in subject.xlsx: {subject_df.columns.tolist()}")
                
                # Chuyển đổi tên môn học thành định dạng phù hợp
                subject_mapping = {
                    'math': 'Toán học',
                    'physics': 'Vật lý',
                    'chemistry': 'Hóa học'
                }
                
                subject_name = subject_mapping.get(subject.lower())
                if not subject_name:
                    print(f"[ERROR] Không tìm thấy tên môn học cho {subject}")
                    return []
                    
                # Tìm ID_subject tương ứng
                subject_row = subject_df[subject_df['name_subject'] == subject_name]
                if subject_row.empty:
                    print(f"[ERROR] Không tìm thấy môn học {subject} trong bảng subject")
                    return []
                    
                subject_id = subject_row['ID_subject'].iloc[0]
                print(f"[DEBUG] ID_subject cho {subject}: {subject_id}")
                
                # Lọc theo ID_subject
                filtered_resources = topic_df[topic_df['ID_subject'] == subject_id]
                print(f"[DEBUG] Số lượng tài liệu tìm thấy: {len(filtered_resources)}")
            else:
                print("[ERROR] Không tìm thấy bảng subject")
                return []
            
            # Lọc theo cấp độ
            filtered_resources = filtered_resources[filtered_resources['level'] == level]
            
            # Sắp xếp theo thứ tự ưu tiên nếu có cột priority
            if 'priority' in topic_df.columns:
                filtered_resources = filtered_resources.sort_values('priority')
            
            # Chuyển đổi thành định dạng mong muốn
            resources = []
            for _, row in filtered_resources.iterrows():
                resource = {
                    'name': row['topic_name'],
                    'type': 'document',
                    'url': '',
                    'description': f'Tài liệu học tập {subject} cho học sinh lớp {grade}'
                }
                resources.append(resource)
            
            print(f"[DEBUG] Số lượng tài liệu trả về: {len(resources)}")
            print("[DEBUG] ====== Kết thúc lấy tài liệu học tập ======\n")
            return resources
            
        except Exception as e:
            print(f"[ERROR] Lỗi khi lấy tài liệu học tập: {str(e)}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            print("[DEBUG] ====== Kết thúc lấy tài liệu học tập với lỗi ======\n")
            # Trả về tài liệu mặc định trong trường hợp lỗi
            return [{
                'name': f'Tài liệu {subject} lớp {grade}',
                'type': 'document',
                'url': '',
                'description': f'Tài liệu học tập {subject} cho học sinh lớp {grade}'
            }]

    def estimate_total_time(self, subject, grade, level):
        """Ước tính tổng thời gian cần thiết cho toàn bộ lộ trình học tập"""
        # Lấy danh sách chủ đề lý thuyết
        all_topics = self._get_theory_topics(subject, 1, 12, level, grade)
        
        # Ước lượng thời gian cho từng chủ đề
        topic_time_estimates = {
            'math': {
                '10': {
                    'Hàm số và đồ thị': 2.0,
                    'Hàm số bậc ba': 3.0,
                    'Phương trình bậc ba': 2.5,
                    'Bất phương trình bậc hai': 2.0,
                    'Hệ phương trình bậc ba': 2.5,
                    'Phương trình chứa căn': 2.0,
                    'Phương trình chứa dấu giá trị tuyệt đối': 2.0
                },
                '11': {
                    'Hàm số lượng giác': 3.0,
                    'Phương trình lượng giác cơ bản': 2.5,
                    'Tổ hợp và xác suất': 3.0,
                    'Dãy số và cấp số': 2.5,
                    'Giới hạn của dãy số': 2.0,
                    'Giới hạn của hàm số': 2.0
                },
                '12': {
                    'Khảo sát và vẽ đồ thị hàm số': 3.0,
                    'Tích phân và ứng dụng': 3.5,
                    'Số phức': 2.5,
                    'Hình học không gian': 3.0,
                    'Phương pháp tọa độ trong không gian': 2.5,
                    'Mặt cầu và mặt tròn xoay': 2.0
                }
            },
            'physics': {
                '10': {
                    'Chuyển động cơ học': 2.5,
                    'Định luật Newton': 3.0,
                    'Các lực cơ học': 2.5,
                    'Công và công suất': 2.0,
                    'Năng lượng và định luật bảo toàn': 2.5,
                    'Chất khí': 2.0
                },
                '11': {
                    'Điện tích và điện trường': 3.0,
                    'Dòng điện không đổi': 2.5,
                    'Dòng điện trong các môi trường': 2.0,
                    'Từ trường': 2.5,
                    'Cảm ứng điện từ': 2.0,
                    'Khúc xạ ánh sáng': 2.0
                },
                '12': {
                    'Dao động điện từ': 2.5,
                    'Sóng điện từ': 2.0,
                    'Sóng ánh sáng': 2.5,
                    'Lượng tử ánh sáng': 3.0,
                    'Hạt nhân nguyên tử': 2.5,
                    'Từ vi mô đến vĩ mô': 2.0
                }
            },
            'chemistry': {
                '10': {
                    'Cấu tạo nguyên tử': 2.5,
                    'Bảng tuần hoàn': 2.0,
                    'Liên kết hóa học': 2.5,
                    'Phản ứng oxi hóa khử': 2.0,
                    'Dung dịch': 2.0,
                    'Tốc độ phản ứng': 2.0
                },
                '11': {
                    'Sự điện li': 2.5,
                    'Nitơ và hợp chất': 2.0,
                    'Cacbon và hợp chất': 2.0,
                    'Silic và hợp chất': 1.5,
                    'Đại cương về hóa học hữu cơ': 2.0,
                    'Hiđrocacbon no': 2.5
                },
                '12': {
                    'Ancol và phenol': 2.0,
                    'Anđehit và xeton': 2.0,
                    'Axit cacboxylic': 2.0,
                    'Este và lipit': 2.0,
                    'Cacbohiđrat': 2.0,
                    'Amin và amino axit': 2.0
                }
            }
        }
        
        # Tính tổng thời gian lý thuyết
        total_theory_time = sum(topic_time_estimates.get(subject, {}).get(grade, {}).get(topic['name'], 2.0) for topic in all_topics)
        
        # Ước tính thời gian thực hành (thường bằng 1.5 lần thời gian lý thuyết)
        total_practice_time = total_theory_time * 1.5
        
        # Tổng thời gian cần thiết
        total_time = total_theory_time + total_practice_time
        
        # Tính số ngày cần thiết dựa trên số giờ học mỗi ngày
        hours_per_day = 2  # Mặc định 2 giờ/ngày
        days_needed = total_time / hours_per_day
        
        return {
            'total_theory_time': round(total_theory_time, 1),
            'total_practice_time': round(total_practice_time, 1),
            'total_time': round(total_time, 1),
            'days_needed': round(days_needed, 1),
            'weeks_needed': round(days_needed / 7, 1)
        }

    def get_topic_breakdown(self, subject, grade, level):
        """Hiển thị chi tiết cách phân chia các bài học trong từng chủ đề"""
        topic_lessons = {
            'math': {
                '10': {
                    'Hàm số và đồ thị': [
                        'Khái niệm hàm số',
                        'Tập xác định và tập giá trị',
                        'Đồ thị hàm số',
                        'Tính đơn điệu của hàm số',
                        'Bài tập tổng hợp'
                    ],
                    'Hàm số bậc ba': [
                        'Định nghĩa và tính chất',
                        'Đồ thị hàm số bậc ba',
                        'Cực trị của hàm số bậc ba',
                        'Ứng dụng trong bài toán thực tế',
                        'Bài tập tổng hợp'
                    ],
                    'Phương trình bậc ba': [
                        'Dạng tổng quát',
                        'Cách giải phương trình bậc ba',
                        'Định lý Vi-ét cho phương trình bậc ba',
                        'Ứng dụng trong bài toán thực tế',
                        'Bài tập tổng hợp'
                    ],
                    'Bất phương trình bậc hai': [
                        'Dạng tổng quát',
                        'Cách giải bất phương trình bậc hai',
                        'Bảng xét dấu tam thức bậc hai',
                        'Ứng dụng trong bài toán thực tế',
                        'Bài tập tổng hợp'
                    ],
                    'Hệ phương trình bậc ba': [
                        'Dạng tổng quát',
                        'Phương pháp thế',
                        'Phương pháp cộng đại số',
                        'Ứng dụng trong bài toán thực tế',
                        'Bài tập tổng hợp'
                    ],
                    'Phương trình chứa căn': [
                        'Điều kiện xác định',
                        'Phương pháp giải',
                        'Các dạng bài tập cơ bản',
                        'Ứng dụng trong bài toán thực tế',
                        'Bài tập tổng hợp'
                    ],
                    'Phương trình chứa dấu giá trị tuyệt đối': [
                        'Định nghĩa giá trị tuyệt đối',
                        'Phương pháp giải',
                        'Các dạng bài tập cơ bản',
                        'Ứng dụng trong bài toán thực tế',
                        'Bài tập tổng hợp'
                    ]
                },
                '11': {
                    'Hàm số lượng giác': [
                        'Các hàm số lượng giác cơ bản',
                        'Tập xác định và tập giá trị',
                        'Tính tuần hoàn',
                        'Đồ thị các hàm số lượng giác',
                        'Bài tập tổng hợp'
                    ],
                    'Phương trình lượng giác cơ bản': [
                        'Phương trình sinx = a',
                        'Phương trình cosx = a',
                        'Phương trình tanx = a',
                        'Phương trình cotx = a',
                        'Bài tập tổng hợp'
                    ],
                    'Tổ hợp và xác suất': [
                        'Quy tắc đếm',
                        'Hoán vị, chỉnh hợp, tổ hợp',
                        'Nhị thức Newton',
                        'Xác suất của biến cố',
                        'Bài tập tổng hợp'
                    ],
                    'Dãy số và cấp số': [
                        'Dãy số',
                        'Cấp số cộng',
                        'Cấp số nhân',
                        'Ứng dụng trong bài toán thực tế',
                        'Bài tập tổng hợp'
                    ],
                    'Giới hạn của dãy số': [
                        'Định nghĩa giới hạn',
                        'Các định lý về giới hạn',
                        'Giới hạn vô cực',
                        'Ứng dụng trong bài toán thực tế',
                        'Bài tập tổng hợp'
                    ],
                    'Giới hạn của hàm số': [
                        'Định nghĩa giới hạn',
                        'Các định lý về giới hạn',
                        'Giới hạn vô cực',
                        'Ứng dụng trong bài toán thực tế',
                        'Bài tập tổng hợp'
                    ]
                },
                '12': {
                    'Khảo sát và vẽ đồ thị hàm số': [
                        'Sơ đồ khảo sát hàm số',
                        'Khảo sát hàm số bậc ba',
                        'Khảo sát hàm số trùng phương',
                        'Khảo sát hàm số phân thức',
                        'Bài tập tổng hợp'
                    ],
                    'Tích phân và ứng dụng': [
                        'Nguyên hàm',
                        'Tích phân xác định',
                        'Phương pháp tính tích phân',
                        'Ứng dụng tích phân',
                        'Bài tập tổng hợp'
                    ],
                    'Số phức': [
                        'Định nghĩa số phức',
                        'Các phép toán với số phức',
                        'Dạng lượng giác của số phức',
                        'Ứng dụng số phức',
                        'Bài tập tổng hợp'
                    ],
                    'Hình học không gian': [
                        'Quan hệ song song',
                        'Quan hệ vuông góc',
                        'Góc và khoảng cách',
                        'Thể tích khối đa diện',
                        'Bài tập tổng hợp'
                    ],
                    'Phương pháp tọa độ trong không gian': [
                        'Hệ tọa độ',
                        'Phương trình mặt phẳng',
                        'Phương trình đường thẳng',
                        'Vị trí tương đối',
                        'Bài tập tổng hợp'
                    ],
                    'Mặt cầu và mặt tròn xoay': [
                        'Mặt cầu',
                        'Mặt trụ',
                        'Mặt nón',
                        'Ứng dụng trong thực tế',
                        'Bài tập tổng hợp'
                    ]
                }
            },
            'physics': {
                '10': {
                    'Chuyển động cơ học': [
                        'Chuyển động thẳng đều',
                        'Chuyển động thẳng biến đổi đều',
                        'Rơi tự do',
                        'Chuyển động tròn đều',
                        'Bài tập tổng hợp'
                    ],
                    'Định luật Newton': [
                        'Định luật I Newton',
                        'Định luật II Newton',
                        'Định luật III Newton',
                        'Ứng dụng các định luật Newton',
                        'Bài tập tổng hợp'
                    ],
                    'Các lực cơ học': [
                        'Lực hấp dẫn',
                        'Lực đàn hồi',
                        'Lực ma sát',
                        'Lực hướng tâm',
                        'Bài tập tổng hợp'
                    ],
                    'Công và công suất': [
                        'Công cơ học',
                        'Công suất',
                        'Hiệu suất',
                        'Ứng dụng trong thực tế',
                        'Bài tập tổng hợp'
                    ],
                    'Năng lượng và định luật bảo toàn': [
                        'Động năng',
                        'Thế năng',
                        'Cơ năng',
                        'Định luật bảo toàn cơ năng',
                        'Bài tập tổng hợp'
                    ],
                    'Chất khí': [
                        'Cấu tạo chất khí',
                        'Định luật Bôi-lơ - Ma-ri-ốt',
                        'Định luật Sác-lơ',
                        'Phương trình trạng thái',
                        'Bài tập tổng hợp'
                    ]
                }
            },
            'chemistry': {
                '10': {
                    'Cấu tạo nguyên tử': [
                        'Thành phần nguyên tử',
                        'Đồng vị',
                        'Cấu hình electron',
                        'Bảng tuần hoàn',
                        'Bài tập tổng hợp'
                    ],
                    'Bảng tuần hoàn': [
                        'Cấu tạo bảng tuần hoàn',
                        'Định luật tuần hoàn',
                        'Tính chất các nguyên tố',
                        'Ứng dụng bảng tuần hoàn',
                        'Bài tập tổng hợp'
                    ],
                    'Liên kết hóa học': [
                        'Liên kết ion',
                        'Liên kết cộng hóa trị',
                        'Liên kết cho nhận',
                        'Liên kết hiđro',
                        'Bài tập tổng hợp'
                    ],
                    'Phản ứng oxi hóa khử': [
                        'Khái niệm oxi hóa khử',
                        'Cân bằng phương trình',
                        'Dãy điện hóa',
                        'Ứng dụng trong thực tế',
                        'Bài tập tổng hợp'
                    ],
                    'Dung dịch': [
                        'Nồng độ dung dịch',
                        'Độ tan',
                        'Áp suất thẩm thấu',
                        'Ứng dụng trong thực tế',
                        'Bài tập tổng hợp'
                    ],
                    'Tốc độ phản ứng': [
                        'Định nghĩa tốc độ phản ứng',
                        'Các yếu tố ảnh hưởng',
                        'Cân bằng hóa học',
                        'Ứng dụng trong thực tế',
                        'Bài tập tổng hợp'
                    ]
                }
            }
        }
        
        # Lấy danh sách chủ đề và bài học
        topics = topic_lessons.get(subject.lower(), {}).get(grade, {})
        if not topics:
            return None
            
        # Tạo kết quả chi tiết
        result = {
            'subject': subject,
            'grade': grade,
            'level': level,
            'topics': []
        }
        
        # Thêm thông tin chi tiết cho từng chủ đề
        for topic, lessons in topics.items():
            topic_info = {
                'name': topic,
                'lessons': lessons,
                'total_lessons': len(lessons),
                'estimated_hours': self.estimate_total_time(subject, grade, level)['total_theory_time'] / len(topics)
            }
            result['topics'].append(topic_info)
            
        return result

    def generate_exercises(self, topic_name, subject, grade, level):
        """Tạo bài tập tự động cho một chủ đề lý thuyết"""
        try:
            print(f"\n[DEBUG] Tạo bài tập cho chủ đề: {topic_name}")
            
            # Tạo các bài tập dựa trên chủ đề
            exercises = []
            
            # Tạo 3-5 bài tập cho mỗi chủ đề
            num_exercises = np.random.randint(3, 6)
            
            for i in range(num_exercises):
                exercise = {
                    'exercise_name': f'Bài tập {i+1} - {topic_name}',
                    'description': self._generate_exercise_description(topic_name, subject, grade, level),
                    'difficulty': level,
                    'subject': subject,
                    'grade': grade,
                    'topic': topic_name,
                    'priority': i + 1
                }
                exercises.append(exercise)
            
            return exercises
            
        except Exception as e:
            print(f"[ERROR] Lỗi khi tạo bài tập: {str(e)}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            return []

    def _generate_exercise_description(self, topic_name, subject, grade, level):
        """Tạo mô tả bài tập dựa trên chủ đề và cấp độ"""
        try:
            # Tạo các loại bài tập khác nhau dựa trên môn học
            if subject == 'math':
                exercise_types = [
                    f"Giải bài toán về {topic_name}",
                    f"Chứng minh tính chất của {topic_name}",
                    f"Ứng dụng {topic_name} vào bài toán thực tế",
                    f"Phân tích và giải thích {topic_name}",
                    f"Tìm giá trị của biểu thức liên quan đến {topic_name}"
                ]
            elif subject == 'physics':
                exercise_types = [
                    f"Giải bài toán về {topic_name}",
                    f"Phân tích hiện tượng {topic_name}",
                    f"Tính toán các đại lượng trong {topic_name}",
                    f"Vẽ đồ thị biểu diễn {topic_name}",
                    f"Giải thích nguyên lý {topic_name}"
                ]
            else:  # chemistry
                exercise_types = [
                    f"Viết phương trình phản ứng {topic_name}",
                    f"Tính toán nồng độ trong {topic_name}",
                    f"Phân tích cấu trúc {topic_name}",
                    f"Giải thích hiện tượng {topic_name}",
                    f"Ứng dụng {topic_name} trong thực tế"
                ]
            
            # Chọn ngẫu nhiên một loại bài tập
            exercise_type = np.random.choice(exercise_types)
            
            # Thêm độ khó vào mô tả
            difficulty_desc = {
                'basic': 'cơ bản',
                'intermediate': 'trung bình',
                'advanced': 'nâng cao',
                'expert': 'chuyên sâu'
            }
            
            return f"{exercise_type} ({difficulty_desc.get(level, 'cơ bản')})"
            
        except Exception as e:
            print(f"[ERROR] Lỗi khi tạo mô tả bài tập: {str(e)}")
            return "Bài tập về " + topic_name

    def _save_exercises_to_excel(self, exercises):
        """Lưu bài tập vào file Excel"""
        try:
            # Đọc file Excel hiện tại nếu có
            try:
                practice_df = pd.read_excel('practice.xlsx')
            except:
                practice_df = pd.DataFrame(columns=[
                    'exercise_name', 'description', 'difficulty',
                    'subject', 'grade', 'topic', 'priority'
                ])
            
            # Thêm bài tập mới
            new_exercises_df = pd.DataFrame(exercises)
            practice_df = pd.concat([practice_df, new_exercises_df], ignore_index=True)
            
            # Lưu lại vào file Excel
            practice_df.to_excel('practice.xlsx', index=False)
            print("[DEBUG] Đã lưu bài tập vào file Excel")
            
        except Exception as e:
            print(f"[ERROR] Lỗi khi lưu bài tập vào Excel: {str(e)}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()

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
        grade='10'
    )
    
    if learning_path:
        # In kết quả
        for week in learning_path['weekly_plans']:
            print(f"\nTuần {week['week_number']} ({week['start_date']} - {week['end_date']}):")
            print(f"Cấp độ: {week['level']}")
            print(f"Lớp: {week['grade']}")
            print(f"Tỷ lệ thành công dự đoán: {week['predicted_success_rate']}%")
            for day, plan in enumerate(week['daily_schedule'], 1):
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