let currentProfile = null;
let allSkills = [];
let selectedSkills = [];

// Load profile on page load
document.addEventListener('DOMContentLoaded', async () => {
    const isValid = await verifySession();
    if (!isValid) return;

    await loadProfile();
    await loadAllSkills();
});

function showAlert(message, type = 'success') {
    const alertDiv = document.getElementById('alertMessage');
    const alertText = document.getElementById('alertText');

    alertDiv.className = `rounded-md p-4 mb-6 ${type === 'success' ? 'bg-green-100' : 'bg-red-100'}`;
    alertText.className = `text-sm ${type === 'success' ? 'text-green-800' : 'text-red-800'}`;
    alertText.textContent = message;
    alertDiv.classList.remove('hidden');

    setTimeout(() => alertDiv.classList.add('hidden'), 5000);
}

async function loadProfile() {
    try {
        const token = localStorage.getItem('session_token');
        if (!token) {
            window.location.href = '/login';
            return;
        }

        const response = await fetch(`${API_BASE_URL}/user/profile`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();

            if (data.success) {
                currentProfile = data.profile;
                displayProfile(currentProfile);
            }
        } else if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        showAlert('Error loading profile', 'error');
    }
}

function displayProfile(profile) {
    document.getElementById('profileName').textContent = profile.name || '--';
    document.getElementById('profileEmail').textContent = profile.email || '--';
    document.getElementById('profileDegree').textContent = profile.degree || 'Not specified';
    document.getElementById('profileGoal').textContent = profile.career_goal || 'Not specified';

    // Display skills
    const skillsList = document.getElementById('skillsList');
    skillsList.innerHTML = '';

    if (profile.skills && profile.skills.length > 0) {
        profile.skills.forEach(skill => {
            const skillDiv = document.createElement('div');
            skillDiv.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg';

            skillDiv.innerHTML = `
                <div>
                    <p class="font-medium text-gray-900">${skill.skill_name}</p>
                    <div class="flex items-center mt-1">
                        ${Array(5).fill(0).map((_, i) => 
                            `<span class="${i < skill.proficiency ? 'text-blue-600' : 'text-gray-300'}">★</span>`
                        ).join('')}
                        <span class="text-sm text-gray-500 ml-2">${skill.proficiency}/5</span>
                    </div>
                </div>
            `;

            skillsList.appendChild(skillDiv);
        });
    } else {
        skillsList.innerHTML = '<p class="text-gray-500">No skills added yet</p>';
    }

    // Display resume
    if (profile.resume_url) {
        document.getElementById('resumeSection').classList.add('hidden');
        document.getElementById('resumeUploaded').classList.remove('hidden');
        document.getElementById('resumeLink').href = profile.resume_url;
    } else {
        document.getElementById('resumeSection').classList.remove('hidden');
        document.getElementById('resumeUploaded').classList.add('hidden');
    }
}

async function loadAllSkills() {
    try {
        const response = await fetch(`${API_BASE_URL}/user/skills/all`);
        const data = await response.json();

        if (data.success) {
            allSkills = data.skills;
        }
    } catch (error) {
        console.error('Error loading skills:', error);
    }
}

function openEditModal() {
    document.getElementById('editDegree').value = currentProfile.degree || '';
    document.getElementById('editGoal').value = currentProfile.career_goal || '';
    document.getElementById('editModal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
}

function openSkillsModal() {
    const container = document.getElementById('availableSkills');
    container.innerHTML = '';

    const userSkillIds = currentProfile.skills.map(s => s.skill_id);
    selectedSkills = [...userSkillIds];

    allSkills.forEach(skill => {
        const div = document.createElement('div');
        div.className = 'flex items-center p-2 hover:bg-gray-50 rounded';

        const isChecked = userSkillIds.includes(skill.skill_id);

        div.innerHTML = `
            <input type="checkbox" 
                   id="skill_${skill.skill_id}" 
                   value="${skill.skill_id}"
                   ${isChecked ? 'checked' : ''}
                   onchange="toggleSkill(${skill.skill_id}, this.checked)"
                   class="mr-3">
            <label for="skill_${skill.skill_id}" class="text-gray-900 cursor-pointer">
                ${skill.skill_name}
            </label>
        `;

        container.appendChild(div);
    });

    document.getElementById('skillsModal').classList.remove('hidden');
}

function closeSkillsModal() {
    document.getElementById('skillsModal').classList.add('hidden');
}

function toggleSkill(skillId, checked) {
    if (checked) {
        if (!selectedSkills.includes(skillId)) {
            selectedSkills.push(skillId);
        }
    } else {
        selectedSkills = selectedSkills.filter(id => id !== skillId);
    }
}

async function saveSkills() {
    try {
        const token = localStorage.getItem('session_token');
        if (!token) {
            window.location.href = '/login';
            return;
        }

        const skillsData = selectedSkills.map(id => ({
            skill_id: id,
            proficiency: 3  // Default proficiency
        }));

        const response = await fetch(`${API_BASE_URL}/user/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ skills: skillsData })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            currentProfile = data.profile;
            displayProfile(currentProfile);
            closeSkillsModal();
            showAlert('Skills updated successfully!');
        } else if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login';
        } else {
            showAlert('Error updating skills', 'error');
        }
    } catch (error) {
        console.error('Error saving skills:', error);
        showAlert('Error saving skills', 'error');
    }
}

document.getElementById('editProfileForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const token = localStorage.getItem('session_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    const degree = document.getElementById('editDegree').value;
    const career_goal = document.getElementById('editGoal').value;

    try {
        const response = await fetch(`${API_BASE_URL}/user/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ degree, career_goal })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            currentProfile = data.profile;
            displayProfile(currentProfile);
            closeEditModal();
            showAlert('Profile updated successfully!');
        } else if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login';
        } else {
            showAlert('Error updating profile', 'error');
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        showAlert('Error updating profile', 'error');
    }
});

async function handleResumeUpload() {
    const fileInput = document.getElementById('resumeFile');
    const file = fileInput.files[0];

    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
        showAlert('Only PDF files are allowed', 'error');
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        showAlert('File size must be less than 5MB', 'error');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('file', file);

        const token = localStorage.getItem('session_token');

        const response = await fetch(`${API_BASE_URL}/user/upload_resume`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showAlert('Resume uploaded successfully!');
            await loadProfile();
        } else {
            showAlert(data.detail || 'Error uploading resume', 'error');
        }
    } catch (error) {
        console.error('Error uploading resume:', error);
        showAlert('Error uploading resume', 'error');
    }
}