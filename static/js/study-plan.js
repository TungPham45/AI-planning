document.addEventListener('DOMContentLoaded', function() {
    const studyPlanForm = document.getElementById('study-plan-form');
    const studyPlanResult = document.getElementById('study-plan-result');
    const planContent = document.getElementById('plan-content');

    // Hàm hiển thị modal thông báo
    function showModal(modalId, message) {
        const modal = document.getElementById(modalId);
        const messageElement = modal.querySelector('p');
        messageElement.textContent = message;
        modal.style.display = 'block';

        // Xử lý nút đóng
        const closeBtn = modal.querySelector('.close');
        const okBtn = modal.querySelector('.btn');
        
        closeBtn.onclick = function() {
            modal.style.display = 'none';
        }
        
        okBtn.onclick = function() {
            modal.style.display = 'none';
        }

        // Đóng modal khi click bên ngoài
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    }

    studyPlanForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Hiển thị trạng thái loading
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Đang tạo kế hoạch...';

        try {
            // Lấy dữ liệu từ form đúng trường, đúng kiểu
            const formData = {
                subject: document.getElementById('subject')?.value || '',
                grade: document.getElementById('grade')?.value || '',
                current_score: parseFloat(document.getElementById('current-score')?.value) || 0,
                target_score: parseFloat(document.getElementById('target-score')?.value) || 0,
                duration_weeks: parseInt(document.getElementById('duration-weeks')?.value) || 0,
                daily_study_hours: parseInt(document.getElementById('daily-study-hours')?.value) || 0,
                learning_style: document.querySelector('input[name="learning-style"]:checked')?.value || ''
            };
            window.lastOverview = formData;

            // Kiểm tra dữ liệu bắt buộc
            if (!formData.subject || !formData.grade || !formData.current_score || !formData.target_score || !formData.duration_weeks || !formData.daily_study_hours || !formData.learning_style) {
                showModal('errorModal', 'Vui lòng nhập đầy đủ các trường bắt buộc!');
                return;
            }
            // Kiểm tra giá trị hợp lệ
            if (formData.current_score < 0 || formData.current_score > 10 || formData.target_score < 0 || formData.target_score > 10) {
                showModal('errorModal', 'Điểm số phải nằm trong khoảng 0-10!');
                return;
            }
            if (formData.duration_weeks < 1 || formData.duration_weeks > 52) {
                showModal('errorModal', 'Thời gian học phải từ 1-52 tuần!');
                return;
            }
            if (formData.daily_study_hours < 1 || formData.daily_study_hours > 8) {
                showModal('errorModal', 'Số giờ học mỗi ngày phải từ 1-8 giờ!');
                return;
            }

            // Gửi request đến server
            const response = await fetch('/api/generate-study-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Lỗi khi tạo kế hoạch học tập');
            }

            // Log dữ liệu trả về để debug
            console.log('API response:', data);

            // Hiển thị kết quả
            displayStudyPlan(data);
            studyPlanResult.style.display = 'block';
            studyPlanResult.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error('Error:', error);
            showModal('errorModal', error.message || 'Có lỗi xảy ra khi tạo kế hoạch học tập. Vui lòng thử lại.');
        } finally {
            // Khôi phục trạng thái nút
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });

    // Helper: Lấy danh sách kế hoạch từ localStorage
    function getStudyPlans() {
        return JSON.parse(localStorage.getItem('studyPlans') || '[]');
    }
    // Helper: Lưu danh sách kế hoạch vào localStorage
    function setStudyPlans(plans) {
        localStorage.setItem('studyPlans', JSON.stringify(plans));
    }
    // Helper: Lấy trạng thái hoàn thành ngày học
    function getCompletedDays(planId) {
        return JSON.parse(localStorage.getItem(`completedDays_${planId}`) || '{}');
    }
    // Helper: Lưu trạng thái hoàn thành ngày học
    function setCompletedDays(planId, completedDays) {
        localStorage.setItem(`completedDays_${planId}`, JSON.stringify(completedDays));
    }
    // Helper: Tạo id duy nhất
    function generateId() {
        return Date.now().toString() + Math.random().toString(36).substr(2, 9);
    }

    // Thay đổi nút Lưu Kế Hoạch để lưu nhiều kế hoạch
    function saveCurrentPlan(plan, overview) {
        // Hiện modal nhập tên
        const modal = document.getElementById('planNameModal');
        const input = document.getElementById('planNameInput');
        const okBtn = document.getElementById('okPlanNameBtn');
        const cancelBtn = document.getElementById('cancelPlanNameBtn');
        const closeBtn = document.getElementById('closePlanNameModal');
        input.value = '';
        input.style.borderColor = '#e9ecef';
        modal.style.display = 'flex';

        function closeModal() {
            modal.style.display = 'none';
            okBtn.onclick = null;
            cancelBtn.onclick = null;
            closeBtn.onclick = null;
        }

        okBtn.onclick = function() {
            const name = input.value.trim();
            if (!name) {
                input.focus();
                input.style.borderColor = 'red';
                return;
            }
            let plans = getStudyPlans();
            const id = generateId();
            // Giữ lại đánh giá nếu có
            const dailyEvaluations = plan.dailyEvaluations || {};
            const weeklyEvaluations = plan.weeklyEvaluations || {};
            plans.push({
                id,
                name,
                overview: overview || {},
                plan: plan.plan || plan,
                dailyEvaluations: dailyEvaluations,
                weeklyEvaluations: weeklyEvaluations
            });
            setStudyPlans(plans);
            closeModal();
            renderSavedPlan();
            updateTotalStudyHoursStat();
            updateAverageScoreStat();
        };
        cancelBtn.onclick = closeBtn.onclick = closeModal;
    }

    // Thay đổi displayStudyPlan để dùng saveCurrentPlan
    function displayStudyPlan(plan) {
        const planContent = document.getElementById('plan-content');
        const resultSection = document.getElementById('study-plan-result');
        let html = '';
        if (!plan || !Array.isArray(plan)) {
            planContent.innerHTML = '<div class="error">Dữ liệu kế hoạch học tập không hợp lệ.</div>';
            resultSection.style.display = 'block';
            return;
        }
        plan.forEach((week, weekIndex) => {
            html += `
                <div class="week-plan">
                    <div class="week-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4>Tuần ${weekIndex + 1}</h4>
                        <button class="btn-evaluate" onclick="createWeekEvaluation(${weekIndex + 1})">
                            <i class="fas fa-clipboard-check"></i> Đánh Giá Tuần
                        </button>
                    </div>
                    <div class="daily-plans">
            `;
            if (!week.daily_plans || !Array.isArray(week.daily_plans)) {
                html += '<div class="error">Không có dữ liệu cho các ngày trong tuần này.</div>';
            } else {
                week.daily_plans.forEach((day, dayIndex) => {
                    html += `
                        <div class="day-plan">
                            <div class="day-header">
                                <h5>Ngày ${dayIndex + 1}</h5>
                                <button class="btn-evaluate" onclick="createEvaluation(${dayIndex + 1})">
                                    <i class="fas fa-clipboard-check"></i> Đánh Giá
                                </button>
                            </div>
                            <div class="theory-section">
                                <h6>Lý Thuyết</h6>
                                <ul>
                                    ${(Array.isArray(day.theory_topics) ? day.theory_topics : []).map(item => `<li>${item}</li>`).join('')}
                                </ul>
                            </div>
                            <div class="practice-section">
                                <h6>Thực Hành</h6>
                                <ul>
                                    ${(Array.isArray(day.practice_exercises) ? day.practice_exercises : []).map(item => `<li>${item}</li>`).join('')}
                                </ul>
                            </div>
                            <div class="resources-section">
                                <h6>Tài Liệu</h6>
                                <ul>
                                    ${(Array.isArray(day.learning_resources) ? day.learning_resources : []).map(item => `<li>${item}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    `;
                });
            }
            html += `
                    </div>
                </div>
            `;
        });
        planContent.innerHTML = html;
        resultSection.style.display = 'block';
        planContent.innerHTML += '<button id="savePlanBtn" class="btn btn-primary" style="margin-top:2rem;">Lưu Kế Hoạch</button>';
        document.getElementById('savePlanBtn').onclick = function() {
            saveCurrentPlan(plan, window.lastOverview);
        };
    }

    // Hiển thị danh sách kế hoạch đã lưu ở tab Nhiệm Vụ
    function renderSavedPlan() {
        const tasksTab = document.getElementById('tasks');
        if (!tasksTab) return;
        let afterSection = tasksTab.querySelector('.content-section');
        let planDiv = document.getElementById('saved-plan-content');
        if (!planDiv) {
            planDiv = document.createElement('div');
            planDiv.id = 'saved-plan-content';
            planDiv.style.marginTop = '2rem';
            if (afterSection && afterSection.nextSibling) {
                tasksTab.insertBefore(planDiv, afterSection.nextSibling);
            } else {
                tasksTab.appendChild(planDiv);
            }
        }
        const plans = JSON.parse(localStorage.getItem('studyPlans') || '[]');
        if (!plans.length) {
            planDiv.innerHTML = '<div style="color:#888; margin-top:1rem;">Chưa có kế hoạch học tập nào được lưu.</div>';
            return;
        }
        let html = '<h3 style="color:#667eea; margin-bottom:1rem;">Danh Sách Kế Hoạch Học Tập Đã Lưu</h3>';
        html += '<div style="display: flex; flex-wrap: wrap; gap: 2rem;">';
        plans.forEach((item, idx) => {
            // Lấy trạng thái hoàn thành kế hoạch
            const completedPlans = JSON.parse(localStorage.getItem('completedPlans') || '{}');
            const isPlanCompleted = !!completedPlans[item.id];
            html += `<div class="card" style="min-width:320px;max-width:400px;flex:1;position:relative;${isPlanCompleted ? 'opacity:0.5;filter:grayscale(0.7);' : ''}">
                <h4 style="color:#764ba2;display:flex;align-items:center;justify-content:space-between;gap:1rem;">
                    <span>${item.name || 'Kế hoạch ' + (idx+1)}</span>
                    <label style="font-size:0.95em;display:flex;align-items:center;gap:0.5rem;cursor:pointer;">
                        <input type="checkbox" class="plan-complete" data-planid="${item.id}" ${isPlanCompleted ? 'checked' : ''} style="width:20px;height:20px;"> Đã hoàn thành
                    </label>
                </h4>
                <div style="margin-bottom:1rem;">
                    <strong>Môn học:</strong> ${item.overview?.subject || ''}<br>
                    <strong>Cấp học:</strong> ${item.overview?.grade || ''}<br>
                    <strong>Điểm hiện tại:</strong> ${item.overview?.current_score || ''}<br>
                    <strong>Điểm mục tiêu:</strong> ${item.overview?.target_score || ''}<br>
                </div>
                <button class="btn btn-primary" onclick="window.showPlanDetail('${item.id}')">Xem chi tiết</button>
                <button class="btn btn-danger" style="margin-left:1rem;" onclick="window.deletePlan('${item.id}')">Xóa</button>
            </div>`;
        });
        html += '</div>';
        planDiv.innerHTML = html;
        // Gán sự kiện cho checkbox hoàn thành kế hoạch
        planDiv.querySelectorAll('.plan-complete').forEach(checkbox => {
            checkbox.onchange = function() {
                const planId = this.dataset.planid;
                const completedPlans = JSON.parse(localStorage.getItem('completedPlans') || '{}');
                completedPlans[planId] = this.checked;
                localStorage.setItem('completedPlans', JSON.stringify(completedPlans));
                renderSavedPlan();
                updateCompletedCoursesStat();
                updateTotalStudyHoursStat();
                updateAverageScoreStat();
                // Ghi log hoàn thành kế hoạch
                if (this.checked) {
                    const plan = plans.find(p => p.id === planId);
                    let subjectName = '';
                    const subject = plan?.overview?.subject;
                    if (subject === 'math') subjectName = 'Toán Học';
                    else if (subject === 'physics') subjectName = 'Vật Lý';
                    else if (subject === 'chemistry') subjectName = 'Hóa Học';
                    addActivityLog(`Đã hoàn thành kế hoạch "${plan?.name || ''}" (${subjectName})`);
                    updateRecentActivities();
                }
            };
        });
    }

    // Hàm hiển thị chi tiết kế hoạch trong modal popup
    window.showPlanDetailModal = function(planObj) {
        // Xóa modal cũ nếu có
        document.getElementById('planDetailModal')?.remove();
        // Tạo modal
        const modal = document.createElement('div');
        modal.id = 'planDetailModal';
        modal.className = 'modal';
        modal.style.display = 'flex';
        // Hàm đóng modal chi tiết để dùng ngoài onclick
        window._closePlanDetailModal = function() { modal.remove(); };
        // Lấy đánh giá ngày/tuần nếu có
        const dailyEvaluations = planObj.dailyEvaluations || {};
        const weeklyEvaluations = planObj.weeklyEvaluations || {};
        const plan = Array.isArray(planObj.plan) ? planObj.plan : planObj;
        // Lấy trạng thái hoàn thành ngày học
        const completedDays = getCompletedDays(planObj.id);
        
        modal.innerHTML = `
            <div class="modal-content" style="max-width:900px;max-height:90vh;overflow-y:auto;position:relative;">
                <span class="close" id="closePlanDetailModal" style="position:absolute;right:20px;top:10px;font-size:2rem;cursor:pointer;">&times;</span>
                <h2 style="color:#764ba2;margin-bottom:1rem;">Chi Tiết Kế Hoạch Học Tập</h2>
                ${Array.isArray(plan) ? plan.map((week, weekIndex) => `
                    <div class="week-plan">
                        <div class="week-header" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                            <h4>Tuần ${weekIndex + 1} <span style='font-size:0.9em;color:#888;'>(${week.start_date || ''} - ${week.end_date || ''})</span></h4>
                            <div style="display:flex;align-items:center;gap:1rem;">
                                <span style=\"color:#888;font-size:0.95em;\">Cấp độ: ${week.level || ''} | Lớp: ${week.grade || ''}</span>
                                <button class='btn-evaluate btn-evaluate-week' style='margin-left:1rem;' data-week='${weekIndex+1}'><i class="fas fa-clipboard-check"></i> Đánh Giá Tuần</button>
                            </div>
                        </div>
                        <div style='margin-bottom:1rem;'>
                            <strong>Đánh giá tuần:</strong> <span style='color:#4CAF50;'>${weeklyEvaluations[weekIndex+1] ? weeklyEvaluations[weekIndex+1] : 'Chưa có'}</span>
                        </div>
                        <div class="daily-plans">
                            ${(week.daily_plans||[]).map((day, dayIndex) => {
                                const dayKey = `w${weekIndex+1}d${dayIndex+1}`;
                                const isCompleted = completedDays[dayKey] || false;
                                return `
                                <div class="day-plan">
                                    <div class="day-header" style="display:flex;justify-content:space-between;align-items:center;">
                                        <div style="display:flex;align-items:center;gap:1rem;">
                                            <input type="checkbox" class="day-complete" data-day="${dayKey}" ${isCompleted ? 'checked' : ''} style="width:20px;height:20px;cursor:pointer;">
                                            <h5>Ngày ${dayIndex + 1}</h5>
                                        </div>
                                        <button class='btn-evaluate btn-evaluate-day' data-day='${dayIndex+1}'><i class="fas fa-clipboard-check"></i> Đánh Giá</button>
                                    </div>
                                    <div style='margin-bottom:0.5rem;'><strong>Đánh giá ngày:</strong> <span style='color:#4CAF50;'>${dailyEvaluations[dayKey] ? dailyEvaluations[dayKey] : 'Chưa có'}</span></div>
                                    <div class="theory-section"><h6>Lý Thuyết</h6><ul>${(day.theory_topics||[]).map(item=>`<li>${item}</li>`).join('')}</ul></div>
                                    <div class="practice-section"><h6>Thực Hành</h6><ul>${(day.practice_exercises||[]).map(item=>`<li>${item}</li>`).join('')}</ul></div>
                                    <div class="resources-section"><h6>Tài Liệu</h6><ul>${(day.learning_resources||[]).map(item=>`<li>${item}</li>`).join('')}</ul></div>
                                </div>
                            `}).join('')}
                        </div>
                        <div style="margin-top:1rem;color:#888;font-size:0.95em;">Tỷ lệ thành công dự đoán: ${week.predicted_success_rate || ''}%</div>
                    </div>
                `).join('') : '<div class="error">Dữ liệu kế hoạch không hợp lệ.</div>'}
            </div>
        `;
        document.body.appendChild(modal);
        document.getElementById('closePlanDetailModal').onclick = function() {
            modal.remove();
        };
        // Đóng modal khi click nền ngoài
        modal.onclick = function(e) {
            if (e.target === modal) modal.remove();
        };
        // Gán lại sự kiện cho các nút Đánh Giá trong modal chi tiết
        setTimeout(() => {
            // Đánh giá tuần
            modal.querySelectorAll('.btn-evaluate-week').forEach((btn, idx) => {
                btn.onclick = function() {
                    window.createWeekEvaluation(Number(btn.dataset.week));
                };
            });
            // Đánh giá ngày
            modal.querySelectorAll('.btn-evaluate-day').forEach((btn, idx) => {
                btn.onclick = function() {
                    // Lấy subject và subjectName từ overview nếu có
                    const subject = planObj.overview?.subject || planObj.subject || '';
                    let subjectName = planObj.overview?.subjectName || '';
                    // Nếu không có subjectName thì lấy text từ select
                    if (!subjectName && document.getElementById('subject')) {
                        const select = document.getElementById('subject');
                        subjectName = select.options[select.selectedIndex]?.text || '';
                    }
                    window.createEvaluation(Number(btn.dataset.day), subject, subjectName);
                };
            });
            // Xử lý checkbox hoàn thành ngày học
            modal.querySelectorAll('.day-complete').forEach(checkbox => {
                checkbox.onchange = function() {
                    const dayKey = this.dataset.day;
                    const completedDays = getCompletedDays(planObj.id);
                    completedDays[dayKey] = this.checked;
                    setCompletedDays(planObj.id, completedDays);
                    updateProgressSidebar();
                    updateSuggestedTasksSidebar();
                    // Ghi log hoạt động đã học ngày
                    if (this.checked) {
                        // Tìm thông tin tuần/ngày/môn
                        let week = 1, day = 1, subjectName = '';
                        const match = dayKey.match(/^w(\d+)d(\d+)$/);
                        if (match) { week = +match[1]; day = +match[2]; }
                        const subject = planObj.overview?.subject;
                        if (subject === 'math') subjectName = 'Toán Học';
                        else if (subject === 'physics') subjectName = 'Vật Lý';
                        else if (subject === 'chemistry') subjectName = 'Hóa Học';
                        addActivityLog(`Đã học Ngày ${day} Tuần ${week} (${subjectName}) trong kế hoạch "${planObj.name || ''}"`);
                        updateRecentActivities();
                    }
                };
            });
        }, 0);
    }

    // Sửa lại hàm showPlanDetail để gọi modal
    window.showPlanDetail = function(id) {
        const plans = JSON.parse(localStorage.getItem('studyPlans') || '[]');
        const item = plans.find(p => p.id === id);
        if (!item) return;
        window.showPlanDetailModal(item);
    }

    // Hàm xóa kế hoạch
    window.deletePlan = function(id) {
        const modal = document.getElementById('confirmDeletePlanModal');
        modal.style.display = 'flex';
        document.getElementById('confirmDeletePlanBtn').onclick = function() {
            let plans = JSON.parse(localStorage.getItem('studyPlans') || '[]');
            plans = plans.filter(p => p.id !== id);
            localStorage.setItem('studyPlans', JSON.stringify(plans));
            modal.style.display = 'none';
            renderSavedPlan();
            updateTotalStudyHoursStat();
            updateAverageScoreStat();
        };
        document.getElementById('cancelDeletePlanBtn').onclick =
        document.getElementById('closeDeletePlanModal').onclick = function() {
            modal.style.display = 'none';
        };
    }

    // Đặt hàm createWeekEvaluation ở phạm vi global
    function createWeekEvaluation(weekNumber) {
        const modal = document.getElementById('evaluationModal');
        const evaluationDay = document.getElementById('evaluationDay');
        const evaluationSubject = document.getElementById('evaluationSubject');
        const quizContainer = document.getElementById('quizContainer');

        evaluationDay.textContent = `Tuần ${weekNumber}`;
        evaluationSubject.textContent = '';

        quizContainer.innerHTML = `
            <div class="quiz-question">
                <h4>Bạn cảm thấy tuần này học tập như thế nào?</h4>
                <div class="quiz-options">
                    <label class="quiz-option"><input type="radio" name="q0" value="1"> Rất tốt</label>
                    <label class="quiz-option"><input type="radio" name="q0" value="2"> Bình thường</label>
                    <label class="quiz-option"><input type="radio" name="q0" value="3"> Cần cố gắng hơn</label>
                </div>
            </div>
            <div class="quiz-question">
                <h4>Bạn đã hoàn thành bao nhiêu % mục tiêu tuần?</h4>
                <div class="quiz-options">
                    <label class="quiz-option"><input type="radio" name="q1" value="1"> 100%</label>
                    <label class="quiz-option"><input type="radio" name="q1" value="2"> 70-99%</label>
                    <label class="quiz-option"><input type="radio" name="q1" value="3"> Dưới 70%</label>
                </div>
            </div>
        `;

        modal.style.display = 'flex';
        setTimeout(updateAverageScoreStat, 500);
    }
    window.createWeekEvaluation = createWeekEvaluation;

    // Đảm bảo hàm createEvaluation có trong phạm vi global
    if (typeof createEvaluation === 'function') {
        window.createEvaluation = createEvaluation;
    }

    // Hàm cập nhật tiến trình học tập ở sidebar
    function updateProgressSidebar() {
        // Lấy tất cả kế hoạch đã lưu
        const plans = getStudyPlans();
        // Gom nhóm theo môn học
        const subjectStats = {};
        plans.forEach(plan => {
            const subject = plan.overview?.subject;
            if (!subject) return;
            const planArr = Array.isArray(plan.plan) ? plan.plan : [];
            let totalDays = 0;
            let completedDays = 0;
            const completedMap = JSON.parse(localStorage.getItem(`completedDays_${plan.id}`) || '{}');
            planArr.forEach((week, weekIdx) => {
                (week.daily_plans||[]).forEach((day, dayIdx) => {
                    totalDays++;
                    const dayKey = `w${weekIdx+1}d${dayIdx+1}`;
                    if (completedMap[dayKey]) completedDays++;
                });
            });
            if (!subjectStats[subject]) subjectStats[subject] = { total: 0, done: 0 };
            subjectStats[subject].total += totalDays;
            subjectStats[subject].done += completedDays;
        });
        // Cập nhật giao diện
        const progressItems = document.querySelectorAll('.progress-item');
        progressItems.forEach(item => {
            const h3 = item.querySelector('h3');
            if (!h3) return;
            const subjectText = h3.textContent.trim().toLowerCase().replace(/\s/g, '');
            // Mapping tên hiển thị sang key subject
            let subjectKey = '';
            if (subjectText === 'toánhọc') subjectKey = 'math';
            else if (subjectText === 'vậtlý') subjectKey = 'physics';
            else if (subjectText === 'hóahọc') subjectKey = 'chemistry';
            else subjectKey = subjectText;
            let percent = 0;
            if (subjectStats[subjectKey] && subjectStats[subjectKey].total > 0) {
                percent = Math.round(subjectStats[subjectKey].done / subjectStats[subjectKey].total * 100);
            }
            const bar = item.querySelector('.progress');
            const span = item.querySelector('span');
            if (bar) bar.style.width = percent + '%';
            if (span) span.textContent = percent + '%';
        });
    }

    // Hàm cập nhật nhiệm vụ gợi ý ở sidebar
    function updateSuggestedTasksSidebar() {
        const plans = getStudyPlans();
        const ul = document.querySelector('.suggested-tasks ul');
        if (!ul) return;
        let tasks = [];
        plans.forEach(plan => {
            const subject = plan.overview?.subject;
            let subjectName = '';
            if (subject === 'math') subjectName = 'Toán Học';
            else if (subject === 'physics') subjectName = 'Vật Lý';
            else if (subject === 'chemistry') subjectName = 'Hóa Học';
            const planArr = Array.isArray(plan.plan) ? plan.plan : [];
            const completedMap = JSON.parse(localStorage.getItem(`completedDays_${plan.id}`) || '{}');
            planArr.forEach((week, weekIdx) => {
                (week.daily_plans||[]).forEach((day, dayIdx) => {
                    const dayKey = `w${weekIdx+1}d${dayIdx+1}`;
                    if (!completedMap[dayKey]) {
                        tasks.push({
                            subjectName,
                            week: weekIdx+1,
                            day: dayIdx+1
                        });
                    }
                });
            });
        });
        if (tasks.length === 0) {
            ul.innerHTML = '<li><i class="fas fa-check-circle"></i> Bạn đã hoàn thành tất cả các ngày học!</li>';
        } else {
            ul.innerHTML = tasks.slice(0, 10).map(task =>
                `<li><i class="fas fa-circle"></i> Hoàn thành Ngày ${task.day} Tuần ${task.week} ${task.subjectName}</li>`
            ).join('');
        }
    }

    // Hàm ghi lại hoạt động
    function addActivityLog(message) {
        const logs = JSON.parse(localStorage.getItem('activityLogs') || '[]');
        const now = new Date();
        logs.unshift({
            message,
            time: now.toLocaleString('vi-VN', { hour12: false })
        });
        // Giới hạn tối đa 20 hoạt động gần nhất
        if (logs.length > 20) logs.length = 20;
        localStorage.setItem('activityLogs', JSON.stringify(logs));
    }

    // Hàm cập nhật Hoạt Động Gần Đây trên trang chủ
    function updateRecentActivities() {
        const ul = document.querySelector('#home .activity-list');
        if (!ul) return;
        const logs = JSON.parse(localStorage.getItem('activityLogs') || '[]');
        if (!logs.length) {
            ul.innerHTML = '<li><i class="fas fa-info-circle"></i> Chưa có hoạt động nào.</li>';
        } else {
            ul.innerHTML = logs.slice(0, 10).map(log =>
                `<li><i class="fas fa-check"></i> ${log.message} <br><span style='color:#888;font-size:0.95em;'>${log.time}</span></li>`
            ).join('');
        }
    }

    // Hàm cập nhật số khóa học hoàn thành ở tab Hồ Sơ
    function updateCompletedCoursesStat() {
        const completedPlans = JSON.parse(localStorage.getItem('completedPlans') || '{}');
        const count = Object.values(completedPlans).filter(Boolean).length;
        // Tìm phần tử stat-number đầu tiên trong .stats-grid (Số Khóa Học Hoàn Thành)
        const statGrid = document.querySelector('#profile .stats-grid');
        if (statGrid) {
            const statNumber = statGrid.querySelector('.stat-item .stat-number');
            if (statNumber) statNumber.textContent = count;
        }
    }

    // Hàm cập nhật số giờ học ở tab Hồ Sơ
    function updateTotalStudyHoursStat() {
        const plans = getStudyPlans();
        let totalHours = 0;
        plans.forEach(plan => {
            const overview = plan.overview || {};
            const dailyHours = Number(overview.daily_study_hours) || 0;
            // Đếm tổng số ngày học trong kế hoạch
            let numDays = 0;
            const planArr = Array.isArray(plan.plan) ? plan.plan : [];
            planArr.forEach(week => {
                numDays += (week.daily_plans || []).length;
            });
            totalHours += dailyHours * numDays;
        });
        // Tìm phần tử stat-number thứ 3 trong .stats-grid (Số Giờ Học)
        const statGrid = document.querySelector('#profile .stats-grid');
        if (statGrid) {
            const statNumbers = statGrid.querySelectorAll('.stat-item .stat-number');
            if (statNumbers[2]) statNumbers[2].textContent = totalHours;
        }
    }

    // Hàm cập nhật điểm trung bình ở tab Hồ Sơ
    function updateAverageScoreStat() {
        const plans = getStudyPlans();
        let scores = [];
        plans.forEach(plan => {
            const weekly = plan.weeklyEvaluations || {};
            Object.values(weekly).forEach(val => {
                const num = Number(val);
                if (!isNaN(num)) scores.push(num);
            });
        });
        let avg = 0;
        if (scores.length) {
            avg = scores.reduce((a, b) => a + b, 0) / scores.length;
        }
        // Tìm phần tử stat-number thứ 2 trong .stats-grid (Điểm Trung Bình)
        const statGrid = document.querySelector('#profile .stats-grid');
        if (statGrid) {
            const statNumbers = statGrid.querySelectorAll('.stat-item .stat-number');
            if (statNumbers[1]) statNumbers[1].textContent = scores.length ? avg.toFixed(2) : '0';
        }
    }

    // Đảm bảo luôn cập nhật tiến trình khi trang load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            renderSavedPlan();
            updateProgressSidebar();
            updateSuggestedTasksSidebar();
            updateRecentActivities();
            updateCompletedCoursesStat();
            updateTotalStudyHoursStat();
            updateAverageScoreStat();
        });
    } else {
        renderSavedPlan();
        updateProgressSidebar();
        updateSuggestedTasksSidebar();
        updateRecentActivities();
        updateCompletedCoursesStat();
        updateTotalStudyHoursStat();
        updateAverageScoreStat();
    }
});

(function enableModalDrag() {
    const modal = document.getElementById('evaluationModal');
    const header = modal.querySelector('.modal-content h2');
    let isDragging = false, offsetX = 0, offsetY = 0;

    if (!header) return;

    header.style.cursor = 'move';

    header.onmousedown = function(e) {
        isDragging = true;
        offsetX = e.clientX - modal.offsetLeft;
        offsetY = e.clientY - modal.offsetTop;
        document.body.style.userSelect = 'none';
    };

    document.onmousemove = function(e) {
        if (isDragging) {
            modal.style.position = 'fixed';
            modal.style.left = (e.clientX - offsetX) + 'px';
            modal.style.top = (e.clientY - offsetY) + 'px';
        }
    };

    document.onmouseup = function() {
        isDragging = false;
        document.body.style.userSelect = '';
    };
})(); 