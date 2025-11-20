// Show alert message
function showAlert(message, type = 'error') {
    const alertDiv = document.getElementById('alertMessage');
    const alertText = document.getElementById('alertText');

    if (!alertDiv || !alertText) return;

    alertDiv.className = `rounded-md p-4 ${type === 'error' ? 'bg-red-100' : 'bg-green-100'}`;
    alertText.className = `text-sm ${type === 'error' ? 'text-red-800' : 'text-green-800'}`;
    alertText.textContent = message;
    alertDiv.classList.remove('hidden');

    // Hide after 5 seconds
    setTimeout(() => {
        alertDiv.classList.add('hidden');
    }, 5000);
}

// Login user
async function loginUser(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            // Store session token and user info
            localStorage.setItem('session_token', data.session_token);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_name', data.name);

            showAlert('Login successful! Redirecting...', 'success');

            // Redirect to dashboard after 1 second
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            showAlert(data.detail || 'Login failed. Please try again.');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('Network error. Please check your connection.');
    }
}

// Signup user
async function signupUser(name, email, password, degree, career_goal) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password, degree, career_goal })
        });

        const data = await response.json();

        if (response.ok) {
            // Store session token and user info
            localStorage.setItem('session_token', data.session_token);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_name', name);

            showAlert('Account created successfully! Redirecting...', 'success');

            // Redirect to dashboard after 1 second
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            showAlert(data.detail || 'Signup failed. Please try again.');
        }
    } catch (error) {
        console.error('Signup error:', error);
        showAlert('Network error. Please check your connection.');
    }
}

// Logout user
async function logoutUser() {
    try {
        const token = localStorage.getItem('session_token');

        if (token) {
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        }

        // Clear local storage
        localStorage.removeItem('session_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_name');

        // Redirect to log in
        window.location.href = '/login';
    } catch (error) {
        console.error('Logout error:', error);
        // Clear storage anyway
        localStorage.clear();
        window.location.href = '/login';
    }
}

// Check if user is logged in
function isLoggedIn() {
    return localStorage.getItem('session_token') !== null;
}

// Get auth headers
function getAuthHeaders() {
    const token = localStorage.getItem('session_token');
    if (!token) {
        return {
            'Content-Type': 'application/json'
        };
    }
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// Verify session (call this on protected pages)
async function verifySession() {
    if (!isLoggedIn()) {
        window.location.href = '/login';
        return false;
    }

    try {
        const token = localStorage.getItem('session_token');
        const response = await fetch(`${API_BASE_URL}/auth/verify`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            localStorage.clear();
            window.location.href = '/login';
            return false;
        }

        return true;
    } catch (error) {
        console.error('Session verification error:', error);
        return false;
    }
}

// Debug function - for testing
function debugAuth() {
    console.log('=== AUTH DEBUG ===');
    console.log('Session Token:', localStorage.getItem('session_token'));
    console.log('User ID:', localStorage.getItem('user_id'));
    console.log('User Name:', localStorage.getItem('user_name'));
    console.log('Headers:', getAuthHeaders());
    console.log('=================');
}

// Make it available globally
window.debugAuth = debugAuth;