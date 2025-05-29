from flask import Flask, render_template, request, redirect, jsonify, send_from_directory
from openpyxl import Workbook, load_workbook
import os
from datetime import datetime, timedelta
import base64
from werkzeug.utils import secure_filename
import time
from learning_path_ai import LearningPathAI
from generate_training_data import generate_training_data
import pandas as pd

app = Flask(__name__)
ai = LearningPathAI()

EXCEL_FILE = "users.xlsx"
UPLOAD_FOLDER = 'static/uploads'
DEFAULT_AVATAR = 'static/default-avatar.svg'

# Tạo thư mục uploads nếu chưa tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Tạo ảnh mặc định nếu chưa tồn tại
if not os.path.exists(DEFAULT_AVATAR):
    # Tạo một ảnh SVG đơn giản
    svg_content = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
        <rect width="200" height="200" fill="#e0e0e0"/>
        <circle cx="100" cy="100" r="50" fill="#9e9e9e"/>
    </svg>'''
    
    # Lưu file SVG
    with open(DEFAULT_AVATAR, 'w') as f:
        f.write(svg_content)

# Kiểm tra xem mô hình đã được huấn luyện chưa
print("\nKiểm tra và khởi tạo mô hình AI...")
if os.path.exists('learning_path_model.joblib'):
    try:
        print("Tìm thấy file mô hình, đang tải...")
        ai.load_model()
        if not ai.is_trained:
            print("Mô hình chưa được huấn luyện, đang huấn luyện lại...")
            # Tạo và lưu dữ liệu training mới
            training_file = generate_training_data()
            print(f"Đã tạo dữ liệu training mới: {training_file}")
            # Đổi tên file mới nhất thành training_data.csv
            if training_file != 'training_data.csv':
                if os.path.exists('training_data.csv'):
                    os.remove('training_data.csv')
                os.rename(training_file, 'training_data.csv')
            ai.train()
    except Exception as e:
        print(f"Lỗi khi tải mô hình: {e}")
        print("Đang tạo mô hình mới...")
        # Tạo và lưu dữ liệu training mới
        training_file = generate_training_data()
        print(f"Đã tạo dữ liệu training mới: {training_file}")
        # Đổi tên file mới nhất thành training_data.csv
        if training_file != 'training_data.csv':
            if os.path.exists('training_data.csv'):
                os.remove('training_data.csv')
            os.rename(training_file, 'training_data.csv')
        ai.train()
else:
    print("Không tìm thấy file mô hình, đang tạo mới...")
    # Tạo và lưu dữ liệu training mới
    training_file = generate_training_data()
    print(f"Đã tạo dữ liệu training mới: {training_file}")
    # Đổi tên file mới nhất thành training_data.csv
    if training_file != 'training_data.csv':
        if os.path.exists('training_data.csv'):
            os.remove('training_data.csv')
        os.rename(training_file, 'training_data.csv')
    ai.train()

print("Khởi tạo mô hình AI hoàn tất!")

# ✅ Khởi tạo file Excel nếu chưa tồn tại
def init_excel():
    try:
        if not os.path.exists(EXCEL_FILE):
            wb = Workbook()
            ws = wb.active
            ws.title = "Users"
            # Thêm header
            headers = ['student_id', 'full_name', 'email', 'password', 'dob', 'join_date', 'image_url']
            ws.append(headers)
            wb.save(EXCEL_FILE)
            print(f"Đã tạo file Excel mới: {EXCEL_FILE}")
        else:
            # Kiểm tra xem file có phải là file Excel hợp lệ không
            try:
                wb = load_workbook(EXCEL_FILE)
                print(f"File Excel đã tồn tại và hợp lệ: {EXCEL_FILE}")
            except Exception as e:
                print(f"File Excel không hợp lệ, đang tạo lại: {e}")
                os.remove(EXCEL_FILE)
                wb = Workbook()
                ws = wb.active
                ws.title = "Users"
                headers = ['student_id', 'full_name', 'email', 'password', 'dob', 'join_date', 'image_url']
                ws.append(headers)
                wb.save(EXCEL_FILE)
                print(f"Đã tạo lại file Excel: {EXCEL_FILE}")
    except Exception as e:
        print(f"Lỗi khi khởi tạo Excel: {e}")
        raise

# ✅ Đọc người dùng từ Excel
def read_excel():
    try:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
        users = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:  # Kiểm tra nếu có dữ liệu
                users.append({
                    'student_id': row[0],
                    'full_name': row[1],
                    'email': row[2],
                    'password': row[3],
                    'dob': row[4],
                    'join_date': row[5],
                    'image_url': row[6]
                })
        return users
    except Exception as e:
        print(f"Lỗi khi đọc file Excel: {e}")
        return []

# ✅ Thêm người dùng mới
def add_user(name, dob, email, password):
    try:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
        student_id = generate_student_id()
        join_date = datetime.now().strftime('%Y-%m-%d')
        ws.append([student_id, name, email, password, dob, join_date, None])
        wb.save(EXCEL_FILE)
        print(f"Đã thêm người dùng mới: {email}")
    except Exception as e:
        print(f"Lỗi khi thêm người dùng: {e}")
        raise

# ✅ Tạo mã học sinh mới
def generate_student_id():
    users = read_excel()
    if not users:
        return 'HS0001'
    last_id = max(user['student_id'] for user in users)
    num = int(last_id[2:]) + 1
    return f'HS{num:04d}'

# ✅ API đăng ký
@app.route("/api/register", methods=["POST"])
def register_user():
    try:
        data = request.get_json()
        users = read_excel()
        if any(user["email"] == data["email"] for user in users):
            return jsonify({"success": False, "message": "Email đã tồn tại."}), 400
        add_user(data["name"], data["dob"], data["email"], data["password"])
        return jsonify({"success": True})
    except Exception as e:
        print(f"Lỗi khi đăng ký: {e}")
        return jsonify({"success": False, "message": "Có lỗi xảy ra khi đăng ký."}), 500

# ✅ API đăng nhập
@app.route("/api/login", methods=["POST"])
def do_login():
    try:
        data = request.get_json()
        users = read_excel()
        for user in users:
            if user["email"] == data["email"] and user["password"] == data["password"]:
                return jsonify({"success": True})
        return jsonify({"success": False, "message": "Sai email hoặc mật khẩu."}), 401
    except Exception as e:
        print(f"Lỗi khi đăng nhập: {e}")
        return jsonify({"success": False, "message": "Có lỗi xảy ra khi đăng nhập."}), 500

# ✅ API lấy thông tin hồ sơ
@app.route("/api/profile", methods=["GET"])
def get_profile():
    try:
        # Lấy email từ query params hoặc session
        email = request.args.get("email")
        if not email:
            # Nếu không có email trong query params, trả về thông tin mặc định
            return jsonify({
                "success": True,
                "profile": {
                    "student_id": "",
                    "full_name": "",
                    "email": "",
                    "join_date": "",
                    "image_url": "/static/default-avatar.svg"
                },
                "notifications": {
                    "email": True,
                    "new_messages": True,
                    "assignment_updates": True,
                    "system_announcements": True
                }
            })

        users = read_excel()
        user = next((u for u in users if u["email"] == email), None)
        
        if not user:
            return jsonify({"success": False, "message": "Không tìm thấy thông tin người dùng"}), 404
        
        return jsonify({
            "success": True,
            "profile": {
                "student_id": user["student_id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "join_date": user["join_date"],
                "image_url": user["image_url"] or "/static/default-avatar.svg"
            },
            "notifications": {
                "email": True,
                "new_messages": True,
                "assignment_updates": True,
                "system_announcements": True
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ✅ API cập nhật thông tin người dùng
@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    try:
        # Lấy dữ liệu từ form
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        student_id = request.form.get('student_id')
        
        # Kiểm tra email có tồn tại không
        if not email:
            return jsonify({'success': False, 'message': 'Email không được để trống'})

        # Đọc dữ liệu từ Excel
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
        
        # Tìm người dùng theo email
        user_found = False
        for row in ws.iter_rows(min_row=2):
            if row[2].value == email:  # Email ở cột thứ 3
                user_found = True
                # Cập nhật thông tin
                row[1].value = full_name  # Tên ở cột thứ 2
                
                # Xử lý upload ảnh nếu có
                if 'image' in request.files:
                    image = request.files['image']
                    if image and image.filename:
                        # Tạo tên file an toàn
                        filename = secure_filename(image.filename)
                        # Thêm timestamp để tránh trùng tên
                        filename = f"{int(time.time())}_{filename}"
                        # Lưu file
                        image_path = os.path.join('static/uploads', filename)
                        image.save(image_path)
                        # Cập nhật đường dẫn ảnh trong Excel
                        row[6].value = f'/static/uploads/{filename}'  # Image URL ở cột thứ 7
                
                # Lưu lại vào Excel
                wb.save(EXCEL_FILE)
                
                return jsonify({
                    'success': True,
                    'message': 'Cập nhật hồ sơ thành công',
                    'profile': {
                        'full_name': full_name,
                        'email': email,
                        'student_id': student_id,
                        'image_url': row[6].value or '/static/default-avatar.svg'
                    }
                })
        
        if not user_found:
            return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'})
        
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi cập nhật hồ sơ'})

# ✅ API đổi mật khẩu
@app.route("/api/change-password", methods=["POST"])
def change_password():
    try:
        data = request.get_json()
        email = data.get("email")
        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not all([email, current_password, new_password]):
            return jsonify({"success": False, "message": "Vui lòng điền đầy đủ thông tin"}), 400

        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
        
        # Tìm dòng chứa email và kiểm tra mật khẩu hiện tại
        for row in ws.iter_rows(min_row=2):
            if row[2].value == email:  # Email ở cột thứ 3
                if row[3].value != current_password:  # Password ở cột thứ 4
                    return jsonify({"success": False, "message": "Mật khẩu hiện tại không đúng"}), 400
                
                # Cập nhật mật khẩu mới
                row[3].value = new_password
                wb.save(EXCEL_FILE)
                return jsonify({"success": True, "message": "Đổi mật khẩu thành công"}), 200
        
        return jsonify({"success": False, "message": "Không tìm thấy thông tin người dùng"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ✅ Trang chính
@app.route("/")
def home():
    return redirect("/login")

# ✅ Trang đăng nhập
@app.route("/login")
def login_page():
    return render_template("login.html")

# ✅ Trang đăng ký
@app.route("/register")
def register_page():
    return render_template("register.html")

# ✅ Trang dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route('/api/generate-study-plan', methods=['POST'])
def generate_study_plan():
    try:
        print("\n[DEBUG] ====== Bắt đầu xử lý request generate-study-plan ======")
        
        # Lấy dữ liệu từ request
        data = request.get_json()
        print("[DEBUG] Received data:", data)
        
        # Kiểm tra dữ liệu đầu vào
        required_fields = ['subject', 'grade', 'current_score', 'target_score', 
                         'duration_weeks', 'daily_study_hours', 'learning_style']
        
        # In ra kiểu dữ liệu của các trường
        print("[DEBUG] Data types:", {k: type(v).__name__ for k, v in data.items()})
        
        # Kiểm tra các trường bắt buộc
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Thiếu trường {field}'
                }), 400
        
        # Chuyển đổi các giá trị số
        try:
            current_score = float(data['current_score'])
            target_score = float(data['target_score'])
            duration_weeks = int(data['duration_weeks'])
            daily_study_hours = float(data['daily_study_hours'])
            
            print(f"[DEBUG] Converted values: current_score={current_score} ({type(current_score)}), "
                  f"target_score={target_score} ({type(target_score)}), "
                  f"duration_weeks={duration_weeks} ({type(duration_weeks)}), "
                  f"daily_study_hours={daily_study_hours} ({type(daily_study_hours)})")
            
        except ValueError as e:
            return jsonify({
                'error': f'Giá trị không hợp lệ: {str(e)}'
            }), 400
        
        # Kiểm tra giá trị hợp lệ
        if not (0 <= current_score <= 10 and 0 <= target_score <= 10):
            return jsonify({
                'error': 'Điểm số phải nằm trong khoảng 0-10'
            }), 400
            
        if duration_weeks <= 0 or daily_study_hours <= 0:
            return jsonify({
                'error': 'Thời gian học phải lớn hơn 0'
            }), 400
        
        # Gọi AI để tạo lộ trình học tập
        print("[DEBUG] Calling AI generate_learning_path with:", {
            'subject': data['subject'],
            'current_score': current_score,
            'target_score': target_score,
            'duration_weeks': duration_weeks,
            'daily_study_hours': daily_study_hours,
            'learning_style': data['learning_style'],
            'grade': data['grade']
        })
        
        learning_path = ai.generate_learning_path(
            subject=data['subject'],
            current_score=current_score,
            target_score=target_score,
            duration_weeks=duration_weeks,
            daily_study_hours=daily_study_hours,
            learning_style=data['learning_style'],
            grade=data['grade']
        )
        
        if learning_path is None:
            print("[ERROR] AI returned None (không thể tạo lộ trình học tập)")
            return jsonify({
                'error': 'Không thể tạo lộ trình học tập. Vui lòng thử lại.'
            }), 500
            
        print("[DEBUG] Learning path generated successfully")
        print("[DEBUG] Learning path structure:", {
            'type': type(learning_path).__name__,
            'length': len(learning_path),
            'first_week': type(learning_path[0]).__name__ if learning_path else None
        })
        
        return jsonify({
            'success': True,
            'learning_path': learning_path
        })
        
    except Exception as e:
        print("\n[ERROR] Exception in generate_study_plan:")
        print(f"[ERROR] Error type: {type(e).__name__}")
        print(f"[ERROR] Error message: {str(e)}")
        import traceback
        print("[ERROR] Stack trace:")
        traceback.print_exc()
        return jsonify({
            'error': 'Đã xảy ra lỗi khi tạo lộ trình học tập'
        }), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ✅ Khởi chạy app
if __name__ == "__main__":
    init_excel()
    # Tạo và lưu dữ liệu training mới khi khởi động app
    training_file = generate_training_data()
    print(f"Đã tạo dữ liệu training mới: {training_file}")
    # Đổi tên file mới nhất thành training_data.csv
    if training_file != 'training_data.csv':
        if os.path.exists('training_data.csv'):
            os.remove('training_data.csv')
        os.rename(training_file, 'training_data.csv')
    app.run(debug=True)
