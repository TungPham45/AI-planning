//đăng ký đăng nhập
// Đặt ở ngoài

// Xử lý Modal
function showModal(modalId, message = '') {
    const modal = document.getElementById(modalId);
    if (message) {
        const messageElement = modal.querySelector('p');
        if (messageElement) {
            messageElement.textContent = message;
        }
    }
    modal.style.display = 'flex';
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'none';
}

// Đóng modal khi click vào nút close
document.querySelectorAll('.close').forEach(closeBtn => {
    closeBtn.onclick = function() {
        this.closest('.modal').style.display = 'none';
    }
});

// Đóng modal khi click bên ngoài
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Xử lý đăng nhập
async function login(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.success) {
            // Lưu email vào localStorage để sử dụng sau này
            localStorage.setItem('userEmail', email);
            window.location.href = '/dashboard';
        } else {
            showModal('errorModal', data.message || 'Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.');
        }
    } catch (error) {
        showModal('errorModal', 'Có lỗi xảy ra. Vui lòng thử lại sau.');
    }
}

// Xử lý đăng ký
async function register(event) {
    event.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const dob = document.getElementById('registerDOB').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const join_date = new Date().toISOString().split('T')[0];

    try {
        // Gửi dữ liệu đến server để lưu vào Excel
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                name, 
                dob, 
                email, 
                password,
                join_date
            })
        });

        const data = await response.json();

        if (data.success) {
            // Lưu thông tin người dùng vào localStorage
            localStorage.setItem('userInfo', JSON.stringify({
                full_name: name,
                email: email,
                join_date: join_date,
                student_id: data.student_id
            }));
            
            showModal('successModal');
            document.getElementById('modalOkBtn').onclick = function() {
                window.location.href = '/login';
            };
        } else {
            showModal('errorModal', data.message || 'Đăng ký thất bại. Vui lòng thử lại.');
        }
    } catch (error) {
        showModal('errorModal', 'Có lỗi xảy ra. Vui lòng thử lại sau.');
    }
}

// Xử lý nút OK trong modal thành công
document.getElementById('modalOkBtn')?.addEventListener('click', function() {
    hideModal('successModal');
});

// Trạng thái active của Navigation
document.addEventListener('DOMContentLoaded', function() {
    // Chức năng chuyển tab
    const navLinks = document.querySelectorAll('.nav-link');
    const tabContents = document.querySelectorAll('.tab-content');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Xóa class active của tất cả các link và nội dung tab
            navLinks.forEach(l => l.classList.remove('active'));
            tabContents.forEach(tab => tab.classList.remove('active'));
            
            // Thêm class active cho link được click
            this.classList.add('active');
            
            // Hiển thị nội dung tab tương ứng
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Hiệu ứng animation thanh tiến trình (progress bar)
    const progressBars = document.querySelectorAll('.progress');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0';
        setTimeout(() => {
            bar.style.width = width;
        }, 200);
    });

    // Xử lý gửi form Kế hoạch học tập
    const studyPlanForm = document.getElementById('study-plan-form');
    if (studyPlanForm) {
        studyPlanForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Thu thập dữ liệu từ form (theo id mới)
            const formData = {
                subject: document.getElementById('subject')?.value || '',
                grade: document.getElementById('grade')?.value || '',
                current_score: parseFloat(document.getElementById('current-score')?.value) || 0,
                target_score: parseFloat(document.getElementById('target-score')?.value) || 0,
                duration_weeks: parseInt(document.getElementById('duration-weeks')?.value) || 0,
                daily_study_hours: parseInt(document.getElementById('daily-study-hours')?.value) || 0,
                learning_style: document.querySelector('input[name="learning-style"]:checked')?.value || ''
            };

            // Kiểm tra dữ liệu bắt buộc
            if (!formData.subject || !formData.grade || !formData.current_score || !formData.target_score || !formData.duration_weeks || !formData.daily_study_hours || !formData.learning_style) {
                alert('Vui lòng nhập đầy đủ các trường bắt buộc!');
                return;
            }

            // Kiểm tra giá trị hợp lệ
            if (formData.current_score < 0 || formData.current_score > 10 || formData.target_score < 0 || formData.target_score > 10) {
                alert('Điểm số phải nằm trong khoảng 0-10!');
                return;
            }
            if (formData.duration_weeks < 1 || formData.duration_weeks > 52) {
                alert('Thời gian học phải từ 1-52 tuần!');
                return;
            }
            if (formData.daily_study_hours < 1 || formData.daily_study_hours > 8) {
                alert('Số giờ học mỗi ngày phải từ 1-8 giờ!');
                return;
            }

            // Gửi dữ liệu tới API hoặc xử lý tiếp
            // ...
        });
    }

    // Hàm tạo kế hoạch học tập
    function generateStudyPlan(data) {
        const startDate = new Date(data.startDate);
        const endDate = new Date(data.endDate);
        const totalDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
        const totalHours = totalDays * data.studyHours;

        // Tính lịch học theo tuần
        const weeklySchedule = data.studyTimes.map(time => {
            return {
                time: time,
                hours: Math.floor(data.studyHours / data.studyTimes.length)
            };
        });

        // Tạo các mốc quan trọng
        const milestones = [
            {
                week: 1,
                task: "Hoàn thành các khái niệm cơ bản và nền tảng",
                resources: data.resources.filter(r => r === 'videos' || r === 'books')
            },
            {
                week: Math.ceil(totalDays / 14),
                task: "Luyện tập và áp dụng kiến thức",
                resources: data.resources.filter(r => r === 'practice' || r === 'quizzes')
            },
            {
                week: Math.ceil(totalDays / 7),
                task: "Ôn tập và đánh giá",
                resources: data.resources
            }
        ];

        return {
            subjectName: data.subjectName,
            level: data.subjectLevel,
            mainGoal: data.mainGoal,
            specificObjectives: data.specificObjectives.split('\n'),
            duration: {
                startDate: data.startDate,
                endDate: data.endDate,
                totalDays: totalDays,
                totalHours: totalHours
            },
            weeklySchedule: weeklySchedule,
            milestones: milestones,
            learningStyle: data.learningStyle,
            resources: data.resources,
            prerequisites: data.prerequisites,
            notes: data.notes
        };
    }

    // Hiển thị kế hoạch học tập
    function displayStudyPlan(plan) {
        // Tạo một modal để hiển thị kế hoạch
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h2>Kế hoạch học tập của bạn cho môn ${plan.subjectName}</h2>
                <div class="plan-details">
                    <h3>Tổng quan</h3>
                    <p><strong>Cấp độ:</strong> ${plan.level}</p>
                    <p><strong>Mục tiêu chính:</strong> ${plan.mainGoal}</p>
                    <p><strong>Thời gian:</strong> ${plan.duration.totalDays} ngày (${plan.duration.totalHours} giờ)</p>
                    
                    <h3>Lịch học hàng tuần</h3>
                    <ul>
                        ${plan.weeklySchedule.map(schedule => `
                            <li>${schedule.time}: ${schedule.hours} giờ</li>
                        `).join('')}
                    </ul>
                    
                    <h3>Các mốc quan trọng</h3>
                    <ul>
                        ${plan.milestones.map(milestone => `
                            <li>
                                <strong>Tuần ${milestone.week}:</strong> ${milestone.task}
                                <br>
                                <small>Tài nguyên: ${milestone.resources.join(', ')}</small>
                            </li>
                        `).join('')}
                    </ul>
                    
                    <h3>Phương pháp học</h3>
                    <p>${plan.learningStyle}</p>
                    
                    <h3>Mục tiêu cụ thể</h3>
                    <ul>
                        ${plan.specificObjectives.map(obj => `<li>${obj}</li>`).join('')}
                    </ul>
                </div>
                <button class="btn" onclick="this.closest('.modal').remove()">Đóng</button>
            </div>
        `;

        document.body.appendChild(modal);
    }

    // Chức năng nút Bắt đầu học
    const startLearningBtn = document.querySelector('.btn');
    if (startLearningBtn) {
        startLearningBtn.addEventListener('click', function() {
            alert('Bắt đầu buổi học của bạn!');
            // Thêm logic cho buổi học tại đây
        });
    }

    // Xử lý gửi form Cài đặt
    const settingsForm = document.querySelector('.settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Đã lưu cài đặt thành công!');
            // Thêm logic lưu cài đặt tại đây
        });
    }

    // Đăng ký khóa học
    const enrollButtons = document.querySelectorAll('.course-card .btn');
    enrollButtons.forEach(button => {
        button.addEventListener('click', function() {
            const courseName = this.closest('.course-card').querySelector('h3').textContent;
            alert(`Bạn đã đăng ký khóa học ${courseName}!`);
            // Thêm logic đăng ký tại đây
        });
    });

    // Tạo menu di động
    const createMobileMenu = () => {
        const header = document.querySelector('.header');
        const nav = document.querySelector('.main-nav');
        
        // Tạo nút menu di động
        const mobileMenuBtn = document.createElement('button');
        mobileMenuBtn.classList.add('mobile-menu-btn');
        mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
        
        // Thêm nút vào header
        header.insertBefore(mobileMenuBtn, nav);
        
        // Chuyển đổi menu khi click
        mobileMenuBtn.addEventListener('click', () => {
            if (nav) nav.classList.toggle('show');
        });

        // Đóng menu khi click ngoài
        document.addEventListener('click', (e) => {
            if (!nav.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                if (nav) nav.classList.remove('show');
            }
        });
    };

    // Kiểm tra nếu cần menu di động
    if (window.innerWidth <= 768) {
        createMobileMenu();
    }

    // Xử lý khi thay đổi kích thước cửa sổ
    window.addEventListener('resize', () => {
        if (window.innerWidth <= 768) {
            if (!document.querySelector('.mobile-menu-btn')) {
                createMobileMenu();
            }
        }
    });

    // Hiển thị/ẩn mật khẩu khi đăng ký
    if (document.getElementById('togglePassword')) {
        document.getElementById('togglePassword').addEventListener('change', function() {
            const pw = document.getElementById('registerPassword');
            const cpw = document.getElementById('registerConfirmPassword');
            if (this.checked) {
                pw.type = 'text';
                cpw.type = 'text';
            } else {
                pw.type = 'password';
                cpw.type = 'password';
            }
        });
    }

    // Kiểm tra xác nhận mật khẩu khi đăng ký
    if (document.getElementById('registerForm')) {
        document.getElementById('registerForm').addEventListener('submit', function(e) {
            const pw = document.getElementById('registerPassword').value;
            const cpw = document.getElementById('registerConfirmPassword').value;
            if (pw !== cpw) {
                e.preventDefault();
                showModal('errorModal', 'Mật khẩu xác nhận không khớp!');
            }
        });
    }

    // Hiển thị/ẩn mật khẩu bằng icon con mắt ở trang đăng nhập
    const toggleLoginPassword = document.getElementById('toggleLoginPassword');
    if (toggleLoginPassword) {
        toggleLoginPassword.addEventListener('click', function() {
            const pw = document.getElementById('loginPassword');
            const eyeIcon = document.getElementById('loginEyeIcon');
            const isHidden = pw.type === 'password';
            pw.type = isHidden ? 'text' : 'password';
            eyeIcon.className = isHidden ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye';
        });
    }

    // Hiển thị/ẩn mật khẩu bằng icon con mắt ở trang đăng ký
    const toggleRegisterPassword = document.getElementById('toggleRegisterPassword');
    if (toggleRegisterPassword) {
        toggleRegisterPassword.addEventListener('click', function() {
            const pw = document.getElementById('registerPassword');
            const cpw = document.getElementById('registerConfirmPassword');
            const eyeIcon = document.getElementById('registerEyeIcon');
            const isHidden = pw.type === 'password';
            pw.type = isHidden ? 'text' : 'password';
            cpw.type = isHidden ? 'text' : 'password';
            eyeIcon.className = isHidden ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye';
        });
    }

    // Mobile Menu Toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navMenu = document.querySelector('.nav-menu');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            if (navMenu) navMenu.classList.toggle('active');
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.nav-menu') && !event.target.closest('.mobile-menu-btn')) {
            if (navMenu) navMenu.classList.remove('active');
        }
    });

    // Load initial profile data
    loadProfileData();

    // Profile image upload
    const profileImageInput = document.getElementById('profileImage');
    if (profileImageInput) {
        profileImageInput.addEventListener('change', handleProfileImageUpload);
    }

    // Password visibility toggle
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', togglePasswordVisibility);
    });

    // Form submissions
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileUpdate);
    }

    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', handlePasswordChange);
    }

    const notificationForm = document.getElementById('notificationForm');
    if (notificationForm) {
        notificationForm.addEventListener('submit', handleNotificationUpdate);
    }

    // Xử lý đăng xuất
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            // Hiển thị modal xác nhận
            showModal('confirmModal', 'Bạn có chắc chắn muốn đăng xuất?');
            
            // Xử lý khi người dùng xác nhận
            document.getElementById('confirmYesBtn').onclick = function() {
                // Xóa thông tin người dùng khỏi localStorage
                localStorage.removeItem('userEmail');
                localStorage.removeItem('userInfo');
                
                // Chuyển hướng về trang đăng nhập
                window.location.href = '/login';
            };
        });
    }
});

// Update user avatar from settings
function updateUserAvatar(imageUrl) {
    const userAvatar = document.querySelector('.user-avatar');
    if (userAvatar) {
        userAvatar.src = imageUrl;
    }
}

// Handle active navigation item
function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// Call setActiveNavItem when page loads
document.addEventListener('DOMContentLoaded', setActiveNavItem);

// Load profile data from Excel
async function loadProfileData() {
    try {
        // Lấy email từ localStorage
        const email = localStorage.getItem('userEmail');
        if (!email) {
            console.log('No email found in localStorage');
            return;
        }

        // Gọi API để lấy thông tin từ Excel
        const response = await fetch(`/api/profile?email=${encodeURIComponent(email)}`);
        const data = await response.json();
        
        if (data.success) {
            // Cập nhật ảnh đại diện
            const profileImage = document.querySelector('.profile-image-container img');
            const profileAvatar = document.getElementById('profileAvatar');
            if (profileImage) {
                profileImage.src = data.profile.image_url || '/static/default-avatar.svg';
            }
            if (profileAvatar) {
                profileAvatar.src = data.profile.image_url || '/static/default-avatar.svg';
            }

            // Cập nhật form fields với dữ liệu từ Excel
            const fullNameInput = document.getElementById('fullName');
            const emailInput = document.getElementById('email');
            const studentIdInput = document.getElementById('studentId');
            const joinDateInput = document.getElementById('joinDate');

            if (fullNameInput) fullNameInput.value = data.profile.full_name || '';
            if (emailInput) emailInput.value = data.profile.email || '';
            if (studentIdInput) studentIdInput.value = data.profile.student_id || '';
            if (joinDateInput) joinDateInput.value = data.profile.join_date || '';

            // Cập nhật thông tin trong tab Hồ sơ
            const profileFullName = document.getElementById('profileFullName');
            const profileEmail = document.getElementById('profileEmail');
            const profileStudentId = document.getElementById('profileStudentId');
            const profileJoinDate = document.getElementById('profileJoinDate');

            if (profileFullName) profileFullName.textContent = data.profile.full_name || '';
            if (profileEmail) profileEmail.textContent = data.profile.email || '';
            if (profileStudentId) profileStudentId.textContent = data.profile.student_id || '';
            if (profileJoinDate) profileJoinDate.textContent = data.profile.join_date || '';

            // Cập nhật cài đặt thông báo
            const emailNotifications = document.getElementById('emailNotifications');
            const newMessages = document.getElementById('newMessages');
            const assignmentUpdates = document.getElementById('assignmentUpdates');
            const systemAnnouncements = document.getElementById('systemAnnouncements');

            if (emailNotifications) emailNotifications.checked = data.notifications.email || false;
            if (newMessages) newMessages.checked = data.notifications.new_messages || false;
            if (assignmentUpdates) assignmentUpdates.checked = data.notifications.assignment_updates || false;
            if (systemAnnouncements) systemAnnouncements.checked = data.notifications.system_announcements || false;

            // Cập nhật localStorage
            localStorage.setItem('userInfo', JSON.stringify({
                full_name: data.profile.full_name,
                email: data.profile.email,
                student_id: data.profile.student_id,
                join_date: data.profile.join_date
            }));

            // Cập nhật tên người dùng trong menu
            const userNameElement = document.querySelector('.user-name');
            if (userNameElement) {
                userNameElement.textContent = data.profile.full_name;
            }
        }
    } catch (error) {
        console.error('Error loading profile data:', error);
        showModal('errorModal', 'Không thể tải thông tin hồ sơ. Vui lòng thử lại sau.');
    }
}

// Handle profile image upload
function handleProfileImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const profileImage = document.querySelector('.profile-image-container img');
            if (profileImage) {
                profileImage.src = e.target.result;
            }
        };
        reader.readAsDataURL(file);
    }
}

// Toggle password visibility
function togglePasswordVisibility(event) {
    const button = event.currentTarget;
    const input = button.previousElementSibling;
    const icon = button.querySelector('i');

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Handle profile update
async function handleProfileUpdate(event) {
    event.preventDefault();
    
    const formData = new FormData();
    formData.append('full_name', document.getElementById('fullName').value);
    formData.append('email', document.getElementById('email').value);
    formData.append('student_id', document.getElementById('studentId').value);
    
    // Thêm ảnh nếu có
    const imageInput = document.getElementById('imageUpload');
    if (imageInput.files.length > 0) {
        formData.append('image', imageInput.files[0]);
    }

    try {
        const response = await fetch('/api/update-profile', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        if (data.success) {
            showModal('successModal', 'Cập nhật hồ sơ thành công!');
            // Cập nhật ảnh đại diện nếu có
            if (data.profile.image_url) {
                const profileImage = document.querySelector('.profile-image-container img');
                const profileAvatar = document.getElementById('profileAvatar');
                if (profileImage) profileImage.src = data.profile.image_url;
                if (profileAvatar) profileAvatar.src = data.profile.image_url;
            }
            // Thêm sự kiện cho nút OK trong modal thành công
            document.getElementById('modalOkBtn').onclick = function() {
                hideModal('successModal');
            };
        } else {
            showModal('errorModal', data.message || 'Có lỗi xảy ra khi cập nhật hồ sơ.');
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        showModal('errorModal', 'Không thể cập nhật hồ sơ. Vui lòng thử lại sau.');
    }
}

// Handle password change
async function handlePasswordChange(event) {
    event.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const email = localStorage.getItem('userEmail');

    if (!email) {
        showModal('errorModal', 'Vui lòng đăng nhập lại');
        return;
    }

    if (newPassword !== confirmPassword) {
        showModal('errorModal', 'Mật khẩu mới không khớp!');
        return;
    }

    if (newPassword.length < 6) {
        showModal('errorModal', 'Mật khẩu mới phải có ít nhất 6 ký tự!');
        return;
    }

    try {
        const response = await fetch('/api/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                current_password: currentPassword,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        if (data.success) {
            showModal('successModal', 'Đổi mật khẩu thành công!');
            // Xóa form
            event.target.reset();
            // Thêm sự kiện cho nút OK trong modal thành công
            document.getElementById('modalOkBtn').onclick = function() {
                hideModal('successModal');
            };
        } else {
            showModal('errorModal', data.message || 'Có lỗi xảy ra khi đổi mật khẩu.');
        }
    } catch (error) {
        console.error('Error changing password:', error);
        showModal('errorModal', 'Không thể đổi mật khẩu. Vui lòng thử lại sau.');
    }
}

// Handle notification settings update
async function handleNotificationUpdate(event) {
    event.preventDefault();
    
    const notificationSettings = {
        email: document.getElementById('emailNotifications').checked,
        new_messages: document.getElementById('newMessages').checked,
        assignment_updates: document.getElementById('assignmentUpdates').checked,
        system_announcements: document.getElementById('systemAnnouncements').checked
    };

    try {
        const response = await fetch('/api/update-notifications', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(notificationSettings)
        });
        
        const data = await response.json();
        if (data.success) {
            showModal('success', 'Cập nhật cài đặt thông báo thành công!');
        } else {
            showModal('error', data.message || 'Có lỗi xảy ra khi cập nhật cài đặt thông báo.');
        }
    } catch (error) {
        console.error('Error updating notification settings:', error);
        showModal('error', 'Không thể cập nhật cài đặt thông báo. Vui lòng thử lại sau.');
    }
}

