// Hàm tạo bài đánh giá
function createEvaluation(dayNumber, subjectParam = null, subjectNameParam = null) {
    const modal = document.getElementById('evaluationModal');
    const evaluationDay = document.getElementById('evaluationDay');
    const evaluationSubject = document.getElementById('evaluationSubject');
    const quizContainer = document.getElementById('quizContainer');
    
    // Lấy thông tin môn học từ tham số hoặc từ form
    let subject = subjectParam;
    let subjectName = subjectNameParam;
    if (!subject) {
        const subjectSelect = document.getElementById('subject');
        subject = subjectSelect?.value || '';
        subjectName = subjectSelect?.options[subjectSelect.selectedIndex]?.text || '';
    }
    
    // Hiển thị thông tin
    evaluationDay.textContent = `Ngày ${dayNumber}`;
    evaluationSubject.textContent = subjectName || subject;
    
    // Tạo câu hỏi dựa trên môn học và ngày học
    const questions = generateQuestions(subject, dayNumber);
    
    // Hiển thị câu hỏi
    quizContainer.innerHTML = questions.map((q, index) => `
        <div class="quiz-question">
            <h4>Câu ${index + 1}: ${q.question}</h4>
            <div class="quiz-options">
                ${q.options.map((option, optIndex) => `
                    <label class="quiz-option">
                        <input type="radio" name="q${index}" value="${optIndex}">
                        ${option}
                    </label>
                `).join('')}
            </div>
        </div>
    `).join('');
    
    // Hiển thị modal
    modal.style.display = 'flex';
    
    // Xử lý sự kiện chọn đáp án
    document.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', function() {
            const questionDiv = this.closest('.quiz-question');
            questionDiv.querySelectorAll('.quiz-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            this.classList.add('selected');
        });
    });
}

// Hàm tạo câu hỏi dựa trên môn học và ngày học
function generateQuestions(subject, dayNumber) {
    // Đây là dữ liệu mẫu, trong thực tế sẽ được lấy từ server
    const questions = {
        math: [
            {
                question: "Giải phương trình bậc hai: x² + 5x + 6 = 0",
                options: [
                    "x = -2 hoặc x = -3",
                    "x = 2 hoặc x = 3",
                    "x = -1 hoặc x = -4",
                    "x = 1 hoặc x = 4"
                ],
                correctAnswer: 0
            },
            {
                question: "Tính đạo hàm của hàm số f(x) = x² + 3x + 2",
                options: [
                    "f'(x) = 2x + 3",
                    "f'(x) = 2x + 2",
                    "f'(x) = x + 3",
                    "f'(x) = x + 2"
                ],
                correctAnswer: 0
            }
        ],
        physics: [
            {
                question: "Công thức tính vận tốc trung bình là:",
                options: [
                    "v = s/t",
                    "v = t/s",
                    "v = s×t",
                    "v = s²/t"
                ],
                correctAnswer: 0
            },
            {
                question: "Đơn vị của lực là:",
                options: [
                    "Newton (N)",
                    "Joule (J)",
                    "Watt (W)",
                    "Pascal (Pa)"
                ],
                correctAnswer: 0
            }
        ]
    };
    
    return questions[subject] || [];
}

// Xử lý sự kiện nộp bài
document.getElementById('submitEvaluation').addEventListener('click', function() {
    const answers = [];
    let allAnswered = true;
    
    // Lấy tất cả câu hỏi
    const questions = document.querySelectorAll('.quiz-question');
    
    questions.forEach((question, index) => {
        const selectedOption = question.querySelector('input[type="radio"]:checked');
        if (selectedOption) {
            answers.push(parseInt(selectedOption.value));
        } else {
            allAnswered = false;
        }
    });
    
    if (!allAnswered) {
        alert('Vui lòng trả lời tất cả các câu hỏi!');
        return;
    }
    
    // Tính điểm
    const score = calculateScore(answers);
    
    // Hiển thị kết quả
    showEvaluationResult(score, questions.length);
});

// Hàm tính điểm
function calculateScore(answers) {
    // Trong thực tế, sẽ so sánh với đáp án đúng từ server
    return answers.filter((answer, index) => answer === 0).length;
}

// Hàm hiển thị kết quả
function showEvaluationResult(score, totalQuestions) {
    const modal = document.getElementById('evaluationModal');
    const quizContainer = document.getElementById('quizContainer');
    const percentage = (score / totalQuestions) * 100;
    
    quizContainer.innerHTML = `
        <div class="evaluation-result">
            <h3>Kết Quả Đánh Giá</h3>
            <div class="score-display">
                <p>Điểm số: ${score}/${totalQuestions}</p>
                <p>Tỷ lệ đúng: ${percentage.toFixed(1)}%</p>
            </div>
            <div class="result-message">
                ${percentage >= 80 ? 
                    '<p class="success">Xuất sắc! Bạn đã nắm vững kiến thức.</p>' :
                    percentage >= 60 ?
                    '<p class="warning">Khá tốt! Hãy ôn tập thêm một chút.</p>' :
                    '<p class="error">Cần cố gắng thêm! Hãy xem lại bài học.</p>'
                }
            </div>
        </div>
    `;
    
    // Thay đổi nút nộp bài thành nút đóng
    const submitButton = document.getElementById('submitEvaluation');
    submitButton.textContent = 'Đóng';
    submitButton.onclick = function() {
        modal.style.display = 'none';
        // Reset modal về trạng thái ban đầu
        setTimeout(() => {
            submitButton.textContent = 'Nộp Bài';
            submitButton.onclick = null;
        }, 300);
    };
}

// Xử lý đóng modal
document.querySelectorAll('.modal .close').forEach(closeBtn => {
    closeBtn.onclick = function() {
        this.closest('.modal').style.display = 'none';
    };
});

// Đóng modal khi click bên ngoài
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}; 