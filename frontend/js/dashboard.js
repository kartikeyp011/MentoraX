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
            // Show only first 2
            const recentOpps = data.opportunities.slice(0, 2);


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
    card.className = 'opportunity-item card-hover';

    // Format deadline with urgency indicator
    const deadline = new Date(opp.deadline);
    const today = new Date();
    const daysUntilDeadline = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24));

    let deadlineText = deadline.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });

    // Add urgency indicator
    if (daysUntilDeadline <= 3) {
        deadlineText = `⏰ ${deadlineText}`;
    }

    // Truncate description if too long
    const maxDescriptionLength = 150;
    let description = opp.description || 'No description available.';
    if (description.length > maxDescriptionLength) {
        description = description.substring(0, maxDescriptionLength) + '...';
    }

    card.innerHTML = `
        <div class="opportunity-header">
            <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                    <div class="opportunity-title">${opp.title}</div>
                    <span class="opportunity-type">${opp.type || 'Full-time'}</span>
                </div>
                <div class="opportunity-company">${opp.source}</div>
                <div class="opportunity-location">
                    <span>📍</span>
                    ${opp.location}
                </div>
            </div>
        </div>
        
        <div class="opportunity-description">
            ${description}
        </div>
        
        ${opp.required_skills && opp.required_skills.length > 0 ? `
            <div class="opportunity-skills">
                ${opp.required_skills.slice(0, 4).map(skill => 
                    `<span class="skill-tag">${skill}</span>`
                ).join('')}
                ${opp.required_skills.length > 4 ? 
                    `<span class="skill-tag">+${opp.required_skills.length - 4} more</span>` 
                    : ''}
            </div>
        ` : ''}
        
        <div class="opportunity-footer">
            <div class="flex items-center gap-4">
                <div class="opportunity-deadline">
                    <span>📅</span>
                    <span class="opportunity-deadline-date">${deadlineText}</span>
                </div>
                ${daysUntilDeadline ? `
                    <div class="text-xs px-2 py-1 bg-red-500/20 text-red-400 rounded-full border border-red-500/30">
                        ${daysUntilDeadline} day${daysUntilDeadline !== 0 ? 's' : ''} left
                    </div>
                ` : ''}
            </div>
            <a href="${opp.link}" target="_blank" class="opportunity-action">
                <span>Apply Now</span>
                <span>→</span>
            </a>
        </div>
    `;

    return card;
}

// Add this function to handle empty states
function handleOpportunitiesEmptyState(hasOpportunities) {
    const container = document.getElementById('recentOpportunities');
    const emptyState = document.getElementById('noOpportunities');

    if (!hasOpportunities) {
        container.classList.add('hidden');
        emptyState.classList.remove('hidden');
    } else {
        container.classList.remove('hidden');
        emptyState.classList.add('hidden');
    }
}

// Update your loadRecentOpportunities function
async function loadRecentOpportunities() {
    try {
        const response = await fetch(`${API_BASE_URL}/opportunities/all`);
        const data = await response.json();

        const container = document.getElementById('recentOpportunities');

        if (data.success && data.opportunities.length > 0) {
            // Show only first 3 for better spacing
            const recentOpps = data.opportunities.slice(0, 2);
            container.innerHTML = '';

            recentOpps.forEach(opp => {
                const oppCard = createOpportunityCard(opp);
                container.appendChild(oppCard);
            });

            handleOpportunitiesEmptyState(true);
        } else {
            handleOpportunitiesEmptyState(false);
        }

    } catch (error) {
        console.error('Error loading opportunities:', error);
        handleOpportunitiesEmptyState(false);
    }
}

// Simple toggle function
function toggleDescription(descriptionElement) {
    const content = descriptionElement.querySelector('.opportunity-description-content');
    const fullText = descriptionElement.getAttribute('data-full-text');

    if (descriptionElement.classList.contains('expanded')) {
        content.textContent = fullText.substring(0, 120) + '...';
        descriptionElement.classList.remove('expanded');
    } else {
        content.textContent = fullText;
        descriptionElement.classList.add('expanded');
    }
}