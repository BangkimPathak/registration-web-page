// Mode switching function (Login <=> Register)
function switchMode(mode) {
    // Select elements
    const loginTab = document.getElementById('tab-login');
    const signupTab = document.getElementById('tab-signup');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const toast = document.getElementById('toast-message');

    // Hide toast when switching modes
    hideToast();

    if (mode === 'login') {
        loginTab.classList.add('active');
        signupTab.classList.remove('active');
        loginForm.classList.add('active');
        signupForm.classList.remove('active');
    } else {
        signupTab.classList.add('active');
        loginTab.classList.remove('active');
        signupForm.classList.add('active');
        loginForm.classList.remove('active');
    }
}

// Helper to show custom toast message
function showToast(message, type) {
    const toast = document.getElementById('toast-message');
    toast.textContent = message;
    toast.className = `toast ${type}`; // type is 'success' or 'error'
}

// Helper to hide toast message
function hideToast() {
    const toast = document.getElementById('toast-message');
    toast.className = 'toast hidden';
    toast.textContent = '';
}

// Handle Form Submissions asynchronously
async function handleFormSubmit(event, mode) {
    event.preventDefault();
    hideToast();

    // Disable button to prevent double-submits
    const form = event.target;
    const submitBtn = form.querySelector('.submit-btn');
    const originalBtnText = submitBtn.textContent;
    submitBtn.textContent = 'Processing...';
    submitBtn.disabled = true;

    try {
        let endpoint = '';
        let payload = {};

        if (mode === 'login') {
            endpoint = '/api/login';
            payload = {
                email: document.getElementById('login-email').value,
                password: document.getElementById('login-password').value
            };
        } else {
            endpoint = '/api/signup';
            payload = {
                name: document.getElementById('signup-name').value,
                email: document.getElementById('signup-email').value,
                role: 'Patient',
                gender: document.getElementById('signup-gender').value,
                age: parseInt(document.getElementById('signup-age').value, 10),
                phone: document.getElementById('signup-phone').value,
                address: document.getElementById('signup-address').value
            };
        }

        // Post data to Python backend for validation & database writing
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok) {
            // Success response from backend
            showToast(result.message, 'success');
            
            if (mode === 'signup') {
                // Clear signup form and redirect to OTP validation
                form.reset();
                setTimeout(() => {
                    window.location.href = result.redirect;
                }, 1200);
            } else {
                // Save user info to local storage and redirect to dashboard home
                localStorage.setItem('currentUser', JSON.stringify(result.user));
                setTimeout(() => {
                    window.location.href = '/home';
                }, 800);
            }
        } else {
            // Fail response with custom error message from backend validation
            showToast(result.message || 'An error occurred during submission.', 'error');
        }

    } catch (error) {
        console.error('API Error:', error);
        showToast('Network error: Could not reach the hospital authentication server.', 'error');
    } finally {
        // Re-enable submit button
        submitBtn.textContent = originalBtnText;
        submitBtn.disabled = false;
    }
}

// On page load, check for verification success toast flag
document.addEventListener('DOMContentLoaded', () => {
    const successMsg = localStorage.getItem('signupSuccessMsg');
    if (successMsg) {
        showToast(successMsg, 'success');
        localStorage.removeItem('signupSuccessMsg');
        switchMode('login');
    }
});
