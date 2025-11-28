let allOpportunities = [];
let currentTab = 'all';
let savedOpportunityIds = new Set();

// Load opportunities on page load
document.addEventListener('DOMContentLoaded', async () => {
    const isValid = await verifySession();
    if (!isValid) return;

    await loadSavedCount();
    await loadOpportunities();
});

async function loadSavedCount() {
    try {
        const token = localStorage.getItem('session_token');
        const response = await fetch(`${API_BASE_URL}/user/stats`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                document.getElementById('savedCount').textContent = data.stats.saved_opportunities;
            }
        }
    } catch (error) {
        console.error('Error loading saved count:', error);
    }
}

async function loadOpportunities() {
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/opportunities/all`);
        const data = await response.json();

        if (data.success) {
            allOpportunities = data.opportunities;
            await checkSavedStatus();
            displayOpportunities(allOpportunities);
        } else {
            showEmpty();
        }
    } catch (error) {
        console.error('Error loading opportunities:', error);
        showEmpty();
    }
}

async function checkSavedStatus() {
    const token = localStorage.getItem('session_token');
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE_URL}/opportunities/saved`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                savedOpportunityIds = new Set(data.opportunities.map(o => o.opportunity_id));
            }
        }
    } catch (error) {
        console.error('Error checking saved status:', error);
    }
}

function displayOpportunities(opportunities) {
    const grid = document.getElementById('opportunitiesGrid');
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');

    if (opportunities.length === 0) {
        showEmpty();
        return;
    }

    loadingState.classList.add('hidden');
    emptyState.classList.add('hidden');
    grid.classList.remove('hidden');

    document.getElementById('oppCount').textContent = opportunities.length;

    grid.innerHTML = '';

    opportunities.forEach(opp => {
        const card = createOpportunityCard(opp);
        grid.appendChild(card);
    });
}

function createOpportunityCard(opp) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition';

    const deadline = new Date(opp.deadline).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });

    const isSaved = savedOpportunityIds.has(opp.opportunity_id);

    card.innerHTML = `
        <div class="flex justify-between items-start mb-3">
            <div class="flex-1">
                <h3 class="text-xl font-bold text-gray-900 mb-2">${opp.title}</h3>
                <div class="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                    <span class="flex items-center">
                        <span class="mr-1">🏢</span> ${opp.source}
                    </span>
                    <span class="flex items-center">
                        <span class="mr-1">📍</span> ${opp.location}
                    </span>
                    <span class="flex items-center">
                        <span class="mr-1">📅</span> ${deadline}
                    </span>
                </div>
            </div>
            <button onclick="toggleSave(${opp.opportunity_id})" 
                    id="saveBtn_${opp.opportunity_id}"
                    class="ml-4 text-2xl hover:scale-110 transition">
                ${isSaved ? '❤️' : '🤍'}
            </button>
        </div>
        
        <p class="text-gray-700 mb-4 line-clamp-3">${opp.description}</p>
        
        ${opp.required_skills && opp.required_skills.length > 0 ? `
            <div class="mb-4">
                <p class="text-sm font-medium text-gray-700 mb-2">Required Skills:</p>
                <div class="flex flex-wrap gap-2">
                    ${opp.required_skills.slice(0, 5).map(skill => 
                        `<span class="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">${skill}</span>`
                    ).join('')}
                    ${opp.required_skills.length > 5 ? 
                        `<span class="px-3 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">+${opp.required_skills.length - 5} more</span>` 
                        : ''}
                </div>
            </div>
        ` : ''}
        
        <div class="flex space-x-3">
            <a href="${opp.link}" target="_blank" 
               class="flex-1 bg-blue-600 text-white text-center px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                View Details →
            </a>
        </div>
    `;

    return card;
}

async function toggleSave(opportunityId) {
    const token = localStorage.getItem('session_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    const isSaved = savedOpportunityIds.has(opportunityId);
    const btn = document.getElementById(`saveBtn_${opportunityId}`);

    try {
        if (isSaved) {
            // Unsave
            const response = await fetch(`${API_BASE_URL}/opportunities/unsave/${opportunityId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                savedOpportunityIds.delete(opportunityId);
                btn.textContent = '🤍';
                await loadSavedCount();
            }
        } else {
            // Save
            const response = await fetch(`${API_BASE_URL}/opportunities/save/${opportunityId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                savedOpportunityIds.add(opportunityId);
                btn.textContent = '❤️';
                await loadSavedCount();
            }
        }
    } catch (error) {
        console.error('Error toggling save:', error);
        alert('Error saving opportunity. Please try again.');
    }
}

async function changeTab(tab) {
    currentTab = tab;

    // Update tab styling
    document.getElementById('tabAll').className = tab === 'all'
        ? 'px-4 py-2 font-medium text-blue-600 border-b-2 border-blue-600'
        : 'px-4 py-2 font-medium text-gray-600 hover:text-blue-600';

    document.getElementById('tabSaved').className = tab === 'saved'
        ? 'px-4 py-2 font-medium text-blue-600 border-b-2 border-blue-600'
        : 'px-4 py-2 font-medium text-gray-600 hover:text-blue-600';

    // Hide/show filters
    document.getElementById('filtersSection').style.display = tab === 'all' ? 'block' : 'none';

    showLoading();

    if (tab === 'saved') {
        await loadSavedOpportunities();
    } else {
        await loadOpportunities();
    }
}

async function loadSavedOpportunities() {
    const token = localStorage.getItem('session_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/opportunities/saved`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            displayOpportunities(data.opportunities);
        } else {
            showEmpty();
        }
    } catch (error) {
        console.error('Error loading saved opportunities:', error);
        showEmpty();
    }
}

function applyFilters() {
    const location = document.getElementById('locationFilter').value;
    const source = document.getElementById('sourceFilter').value;
    const search = document.getElementById('searchInput').value.toLowerCase();

    let filtered = allOpportunities;

    if (location) {
        filtered = filtered.filter(o => o.location && o.location.includes(location));
    }

    if (source) {
        filtered = filtered.filter(o => o.source === source);
    }

    if (search) {
        filtered = filtered.filter(o =>
            o.title.toLowerCase().includes(search) ||
            o.description.toLowerCase().includes(search)
        );
    }

    displayOpportunities(filtered);
}

function clearFilters() {
    document.getElementById('locationFilter').value = '';
    document.getElementById('sourceFilter').value = '';
    document.getElementById('searchInput').value = '';
    displayOpportunities(allOpportunities);
}

function showLoading() {
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('opportunitiesGrid').classList.add('hidden');
}

function showEmpty() {
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('emptyState').classList.remove('hidden');
    document.getElementById('opportunitiesGrid').classList.add('hidden');
    document.getElementById('oppCount').textContent = '0';
}