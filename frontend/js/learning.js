let allResources = [];
let userProfile = null;

// Load on page load
document.addEventListener('DOMContentLoaded', async () => {
    const isValid = await verifySession();
    if (!isValid) return;

    await loadUserProfile();
    await loadDefaultResources();
    await loadRecommendedResources();
});

async function loadUserProfile() {
    try {
        const token = localStorage.getItem('session_token');
        const response = await fetch(`${API_BASE_URL}/user/profile`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                userProfile = data.profile;
            }
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

async function loadDefaultResources() {
    try {
        const response = await fetch(`${API_BASE_URL}/resources/all`);
        const data = await response.json();

        if (data.success) {
            allResources = data.resources;
            displayDefaultResources(allResources.slice(0, 6)); // Show first 6
        }
    } catch (error) {
        console.error('Error loading resources:', error);
    }
}

function displayDefaultResources(resources) {
    const container = document.getElementById('defaultResources');
    container.innerHTML = '';

    resources.forEach(resource => {
        const card = createResourceCard(resource, false);
        container.appendChild(card);
    });
}

async function loadRecommendedResources() {
    if (!userProfile) return;

    try {
        // Build query from user's career goal and skills
        let query = userProfile.career_goal || '';
        if (userProfile.skills && userProfile.skills.length > 0) {
            const skillNames = userProfile.skills.map(s => s.skill_name).join(' ');
            query = query ? `${query} ${skillNames}` : skillNames;
        }

        if (!query) {
            query = 'programming software development';
        }

        const response = await fetch(`${API_BASE_URL}/resources/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();

        if (data.success && data.resources.length > 0) {
            displayRecommendedResources(data.resources.slice(0, 4));
        } else {
            document.getElementById('recommendedSection').style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading recommended resources:', error);
    }
}

function displayRecommendedResources(resources) {
    const container = document.getElementById('recommendedResources');
    container.innerHTML = '';

    resources.forEach(resource => {
        const card = createResourceCard(resource, true);
        container.appendChild(card);
    });
}

function createResourceCard(resource, showRelevance = false) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition';

    // Calculate relevance badge
    let relevanceBadge = '';
    if (showRelevance && resource.relevance_score) {
        const score = Math.round(resource.relevance_score * 100);
        const color = score > 80 ? 'green' : score > 60 ? 'blue' : 'gray';
        relevanceBadge = `
            <span class="px-2 py-1 bg-${color}-100 text-${color}-800 text-xs rounded-full">
                ${score}% Match
            </span>
        `;
    }

    card.innerHTML = `
        <div class="flex justify-between items-start mb-3">
            <h4 class="text-lg font-bold text-gray-900 flex-1">${resource.title}</h4>
            ${relevanceBadge}
        </div>
        
        <p class="text-gray-700 mb-4 line-clamp-3">${resource.description}</p>
        
        <div class="flex items-center justify-between">
            <span class="text-sm text-gray-500">📚 Course</span>
            <a href="${resource.url}" target="_blank" 
               class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium transition">
                Learn More →
            </a>
        </div>
    `;

    return card;
}

async function searchResources() {
    const query = document.getElementById('searchQuery').value.trim();

    if (!query) {
        alert('Please enter a search query');
        return;
    }

    // Show loading
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('searchResults').classList.add('hidden');
    document.getElementById('defaultSection').style.display = 'none';
    document.getElementById('recommendedSection').style.display = 'none';
    document.getElementById('statsBar').classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/resources/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();

        document.getElementById('loadingState').classList.add('hidden');

        if (data.success && data.resources.length > 0) {
            displaySearchResults(data.resources);
            document.getElementById('resultCount').textContent = data.resources.length;
            document.getElementById('statsBar').classList.remove('hidden');
        } else {
            displayNoResults();
        }
    } catch (error) {
        console.error('Error searching resources:', error);
        document.getElementById('loadingState').classList.add('hidden');
        alert('Error searching resources. Please try again.');
    }
}

function displaySearchResults(resources) {
    const resultsSection = document.getElementById('searchResults');
    const container = document.getElementById('resultsContainer');

    resultsSection.classList.remove('hidden');
    container.innerHTML = '';

    resources.forEach((resource, index) => {
        const card = document.createElement('div');
        card.className = 'bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition';

        const relevanceScore = Math.round(resource.relevance_score * 100);
        const relevanceColor = relevanceScore > 80 ? 'green' : relevanceScore > 60 ? 'blue' : 'yellow';

        card.innerHTML = `
            <div class="flex items-start justify-between mb-3">
                <div class="flex items-start flex-1">
                    <div class="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold mr-4">
                        ${index + 1}
                    </div>
                    <div class="flex-1">
                        <h4 class="text-xl font-bold text-gray-900 mb-2">${resource.title}</h4>
                        <p class="text-gray-700 mb-3">${resource.description}</p>
                    </div>
                </div>
                <span class="ml-4 px-3 py-1 bg-${relevanceColor}-100 text-${relevanceColor}-800 text-sm rounded-full font-medium">
                    ${relevanceScore}% Match
                </span>
            </div>
            
            <div class="flex items-center justify-between border-t border-gray-200 pt-4">
                <div class="flex items-center space-x-4 text-sm text-gray-600">
                    <span>📚 Course</span>
                    <span>⭐ Recommended</span>
                </div>
                <a href="${resource.url}" target="_blank" 
                   class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 font-medium transition">
                    Start Learning →
                </a>
            </div>
        `;

        container.appendChild(card);
    });

    // Add back button
    const backButton = document.createElement('div');
    backButton.className = 'mt-6 text-center';
    backButton.innerHTML = `
        <button onclick="resetView()" class="text-blue-600 hover:text-blue-700 font-medium">
            ← Back to all resources
        </button>
    `;
    container.appendChild(backButton);
}

function displayNoResults() {
    const resultsSection = document.getElementById('searchResults');
    const container = document.getElementById('resultsContainer');

    resultsSection.classList.remove('hidden');
    container.innerHTML = `
        <div class="text-center py-12">
            <span class="text-6xl">🔍</span>
            <p class="text-gray-600 mt-4 text-lg">No resources found</p>
            <p class="text-gray-500 text-sm mt-2">Try different keywords or check our popular resources below</p>
            <button onclick="resetView()" class="mt-6 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
                View All Resources
            </button>
        </div>
    `;
}

function quickSearch(query) {
    document.getElementById('searchQuery').value = query;
    searchResources();
}

function resetView() {
    document.getElementById('searchQuery').value = '';
    document.getElementById('searchResults').classList.add('hidden');
    document.getElementById('statsBar').classList.add('hidden');
    document.getElementById('defaultSection').style.display = 'block';
    document.getElementById('recommendedSection').style.display = 'block';
}