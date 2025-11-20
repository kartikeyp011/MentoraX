// Load profile on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Verify session
    const isValid = await verifySession();
    if (!isValid) return;

    // Load user profile
    await loadUserProfile();
});

async function loadUserProfile() {
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
                const profile = data.profile;

                // Display profile info
                document.getElementById('profileDegree').textContent = profile.degree || 'Not specified';
                document.getElementById('profileGoal').textContent = profile.career_goal || 'Exploring options';
                document.getElementById('profileSkillsCount').textContent =
                    profile.skills.length > 0 ? `${profile.skills.length} skills` : 'No skills yet';

                // Display skills
                const skillsContainer = document.getElementById('profileSkills');
                skillsContainer.innerHTML = '';

                if (profile.skills.length > 0) {
                    profile.skills.forEach(skill => {
                        const badge = document.createElement('span');
                        badge.className = 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm';
                        badge.textContent = skill.skill_name;
                        skillsContainer.appendChild(badge);
                    });
                } else {
                    skillsContainer.innerHTML = '<p class="text-gray-500 text-sm">No skills added yet. Add skills in your profile.</p>';
                }
            }
        } else if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

async function getCareerRecommendations() {
    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('session_token');

    if (!token) {
        window.location.href = '/login';
        return;
    }

    const btn = document.getElementById('getRecommendationsBtn');
    const loadingState = document.getElementById('loadingState');
    const careerPaths = document.getElementById('careerPaths');

    // Show loading
    btn.disabled = true;
    btn.textContent = 'Analyzing...';
    loadingState.classList.remove('hidden');
    careerPaths.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/career/path`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ user_id: parseInt(userId) })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Hide loading, show results
            loadingState.classList.add('hidden');
            careerPaths.classList.remove('hidden');

            // Display career paths
            displayCareerPaths(data.career_paths);
        } else if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login';
        } else {
            alert('Error getting recommendations: ' + (data.detail || 'Unknown error'));
            loadingState.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error. Please try again.');
        loadingState.classList.add('hidden');
    } finally {
        btn.disabled = false;
        btn.textContent = '🎯 Get Career Recommendations';
    }
}


function displayCareerPaths(paths) {
    const container = document.getElementById('careerPathsContainer');
    container.innerHTML = '';

    paths.forEach((path, index) => {
        const card = document.createElement('div');
        card.className = 'bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-600';

        card.innerHTML = `
            <div class="flex items-start justify-between mb-4">
                <div>
                    <h4 class="text-2xl font-bold text-gray-900">${path.title}</h4>
                    <span class="inline-block mt-2 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                        Path ${index + 1}
                    </span>
                </div>
                <span class="text-4xl">🚀</span>
            </div>
            
            <div class="mb-4">
                <h5 class="font-semibold text-gray-900 mb-2">Why This Fits You:</h5>
                <p class="text-gray-700">${path.fit_reason}</p>
            </div>
            
            <div class="mb-4">
                <h5 class="font-semibold text-gray-900 mb-2">Skills to Develop:</h5>
                <div class="flex flex-wrap gap-2">
                    ${path.missing_skills.map(skill => 
                        `<span class="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">${skill}</span>`
                    ).join('')}
                </div>
            </div>
            
            <div>
                <h5 class="font-semibold text-gray-900 mb-3">Learning Roadmap:</h5>
                <ol class="space-y-2">
                    ${path.roadmap.map((step, idx) => 
                        `<li class="flex items-start">
                            <span class="flex-shrink-0 w-6 h-6 rounded-full bg-blue-600 text-white text-sm flex items-center justify-center mr-3">
                                ${idx + 1}
                            </span>
                            <span class="text-gray-700">${step}</span>
                        </li>`
                    ).join('')}
                </ol>
            </div>
        `;

        container.appendChild(card);
    });
}