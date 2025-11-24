// Load dashboard data on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Verify session
    const isValid = await verifySession();
    if (!isValid) return;

    // Load user name
    loadUserName();

    // Load dashboard stats
    await loadDashboardStats();

    // Load recent opportunities
    await loadRecentOpportunities();
});

function loadUserName() {
    const userName = localStorage.getItem('user_name');
    if (userName) {
        document.getElementById('userName').textContent = userName;
        document.getElementById('userNameMain').textContent = userName;
    }
}

async function loadDashboardStats() {
    try {
        const token = localStorage.getItem('session_token');

        // Get opportunities count
        const oppResponse = await fetch(`${API_BASE_URL}/opportunities/stats`);
        const oppData = await oppResponse.json();

        if (oppData.success) {
            document.getElementById('oppCount').textContent = oppData.stats.total;
        }

        // Get user profile (for skills count)
        if (token) {
            const profileResponse = await fetch(`${API_BASE_URL}/user/profile`, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            if (profileResponse.ok) {
                const profileData = await profileResponse.json();
                if (profileData.success && profileData.profile.skills) {
                    document.getElementById('skillCount').textContent = profileData.profile.skills.length;
                } else {
                    document.getElementById('skillCount').textContent = '0';
                }
            } else if (profileResponse.status === 401) {
                localStorage.clear();
                window.location.href = '/login';
            } else {
                document.getElementById('skillCount').textContent = '0';
            }
        } else {
            window.location.href = '/login';
        }

    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        document.getElementById('oppCount').textContent = '0';
        document.getElementById('skillCount').textContent = '0';
    }
}


async function loadRecentOpportunities() {
    try {
        const response = await fetch(`${API_BASE_URL}/opportunities/all`);
        const data = await response.json();

        if (data.success && data.opportunities.length > 0) {
            // Show only first 5
            const recentOpps = data.opportunities.slice(0, 5);

            const container = document.getElementById('recentOpportunities');
            container.innerHTML = '';

            recentOpps.forEach(opp => {
                const oppCard = createOpportunityCard(opp);
                container.appendChild(oppCard);
            });
        } else {
            document.getElementById('recentOpportunities').innerHTML =
                '<p class="text-gray-500 text-center py-8">No opportunities available yet.</p>';
        }

    } catch (error) {
        console.error('Error loading opportunities:', error);
        document.getElementById('recentOpportunities').innerHTML =
            '<p class="text-red-500 text-center py-8">Error loading opportunities.</p>';
    }
}

function createOpportunityCard(opp) {
    const card = document.createElement('div');
    card.className = 'opportunity-item';

    // Format deadline
    const deadline = new Date(opp.deadline).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });

    card.innerHTML = `
        <div class="opportunity-header">
            <div class="flex-1">
                <div class="opportunity-title">${opp.title}</div>
                <div class="opportunity-company">${opp.source}</div>
                <div class="opportunity-location">
                    <span class="mr-1">📍</span>
                    ${opp.location}
                </div>
            </div>
        </div>
        <div class="opportunity-description">
            ${opp.description}
        </div>
        ${opp.required_skills && opp.required_skills.length > 0 ? `
            <div class="opportunity-skills">
                ${opp.required_skills.slice(0, 3).map(skill => 
                    `<span class="opportunity-skill">${skill}</span>`
                ).join('')}
                ${opp.required_skills.length > 3 ? 
                    `<span class="opportunity-skill">+${opp.required_skills.length - 3} more</span>` 
                    : ''}
            </div>
        ` : ''}
        <div class="opportunity-footer">
            <div class="opportunity-deadline">
                Deadline: 
                <span class="opportunity-deadline-date">${deadline}</span>
            </div>
            <a href="${opp.link}" target="_blank" class="opportunity-action">
                View Details →
            </a>
        </div>
    `;

    return card;
}