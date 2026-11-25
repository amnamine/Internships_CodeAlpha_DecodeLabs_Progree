const authContainer = document.getElementById('auth-container');
const dashboardContainer = document.getElementById('dashboard-container');
const authForm = document.getElementById('auth-form');
const toggleBtn = document.getElementById('toggle-btn');
const formTitle = document.getElementById('form-title');
const formSubtitle = document.getElementById('form-subtitle');
const togglePrompt = document.getElementById('toggle-prompt');
const submitBtn = document.getElementById('submit-btn');
const errorMessage = document.getElementById('error-message');

const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');

const dashUsername = document.getElementById('dash-username');
const fetchProtectedBtn = document.getElementById('fetch-protected-btn');
const logoutBtn = document.getElementById('logout-btn');
const secretDataDisplay = document.getElementById('secret-data-display');
const secretMessage = document.getElementById('secret-message');
const secretContent = document.getElementById('secret-content');

let isLoginMode = true;

// Check if user is already logged in
function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        const username = localStorage.getItem('username') || 'User';
        showDashboard(username);
    } else {
        showAuth();
    }
}

// Toggle between Login and Register
toggleBtn.addEventListener('click', () => {
    isLoginMode = !isLoginMode;
    errorMessage.textContent = '';
    
    if (isLoginMode) {
        formTitle.textContent = 'Login';
        formSubtitle.textContent = 'Welcome back to the secure portal';
        submitBtn.textContent = 'Login';
        togglePrompt.textContent = "Don't have an account?";
        toggleBtn.textContent = 'Register';
    } else {
        formTitle.textContent = 'Register';
        formSubtitle.textContent = 'Create a new secure account';
        submitBtn.textContent = 'Register';
        togglePrompt.textContent = "Already have an account?";
        toggleBtn.textContent = 'Login';
    }
});

// Handle Auth Form Submission
authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = usernameInput.value;
    const password = passwordInput.value;
    
    errorMessage.textContent = '';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';

    const endpoint = isLoginMode ? '/api/login' : '/api/register';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            if (isLoginMode) {
                // Successful Login
                localStorage.setItem('token', data.token);
                localStorage.setItem('username', username);
                showDashboard(username);
            } else {
                // Successful Registration
                alert('Registration successful! You can now log in.');
                toggleBtn.click(); // Switch to login mode
            }
        } else {
            errorMessage.textContent = data.error || 'An error occurred';
        }
    } catch (err) {
        errorMessage.textContent = 'Network error. Please try again.';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = isLoginMode ? 'Login' : 'Register';
        if (!isLoginMode || !response?.ok) passwordInput.value = '';
    }
});

// Handle Fetch Protected Data
fetchProtectedBtn.addEventListener('click', async () => {
    const token = localStorage.getItem('token');
    
    if (!token) {
        showAuth();
        return;
    }

    fetchProtectedBtn.disabled = true;
    fetchProtectedBtn.textContent = 'Fetching...';

    try {
        const response = await fetch('/api/protected', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            secretDataDisplay.classList.remove('hidden');
            secretMessage.textContent = data.message;
            secretContent.textContent = JSON.stringify(data.user, null, 2);
        } else {
            if (response.status === 401 || response.status === 403) {
                // Token invalid or expired
                alert('Session expired. Please log in again.');
                handleLogout();
            } else {
                alert('Error fetching data: ' + (data.error || 'Unknown error'));
            }
        }
    } catch (err) {
        alert('Network error while fetching protected data.');
    } finally {
        fetchProtectedBtn.disabled = false;
        fetchProtectedBtn.textContent = 'Fetch Secret Data';
    }
});

// Handle Logout
logoutBtn.addEventListener('click', handleLogout);

function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    secretDataDisplay.classList.add('hidden');
    showAuth();
}

// UI State Toggles
function showDashboard(username) {
    dashUsername.textContent = username;
    authContainer.classList.add('hidden');
    setTimeout(() => {
        dashboardContainer.classList.remove('hidden');
    }, 400); // Wait for transition
}

function showAuth() {
    dashboardContainer.classList.add('hidden');
    setTimeout(() => {
        authContainer.classList.remove('hidden');
    }, 400); // Wait for transition
}

// Initialize
checkAuth();
