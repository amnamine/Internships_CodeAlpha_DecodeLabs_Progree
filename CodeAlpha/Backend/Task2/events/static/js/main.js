document.addEventListener('DOMContentLoaded', () => {
    // 1. Toast Notifications Dismissal
    initToasts();

    // 2. Countdown Timer
    initCountdown();

    // 3. Mobile Navigation Menu Toggle
    initMobileNav();

    // 4. Confirmation Prompts
    initConfirmations();

    // 5. AJAX Ticket booking & cancellation
    initAjaxForms();
});

/**
 * Handle Toast alerts behavior
 */
function initToasts() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        // Auto dismiss after 4 seconds
        const timeout = setTimeout(() => {
            dismissToast(toast);
        }, 4000);

        // Manual dismiss
        const closeBtn = toast.querySelector('.toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                clearTimeout(timeout);
                dismissToast(toast);
            });
        }
    });
}

function dismissToast(toast) {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-20px) scale(0.95)';
    setTimeout(() => {
        toast.remove();
    }, 300);
}

/**
 * Helper to show dynamic toast alerts
 */
function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconClass = 'bi-info-circle-fill';
    if (type === 'success') iconClass = 'bi-check-circle-fill';
    if (type === 'warning') iconClass = 'bi-exclamation-triangle-fill';
    if (type === 'error') iconClass = 'bi-x-circle-fill';

    toast.innerHTML = `
        <div class="toast-content">
            <i class="bi ${iconClass}"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close">&times;</button>
    `;

    container.appendChild(toast);
    
    // Wire up event listener for the new toast
    const timeout = setTimeout(() => {
        dismissToast(toast);
    }, 4000);

    toast.querySelector('.toast-close').addEventListener('click', () => {
        clearTimeout(timeout);
        dismissToast(toast);
    });
}

/**
 * Count down timer to event date/time
 */
function initCountdown() {
    const widget = document.getElementById('countdown-widget');
    if (!widget) return;

    const targetDateStr = widget.getAttribute('data-date'); // YYYY-MM-DD
    const targetTimeStr = widget.getAttribute('data-time'); // HH:MM:SS
    
    const targetDateTime = new Date(`${targetDateStr}T${targetTimeStr}`);

    const daysEl = document.getElementById('days');
    const hoursEl = document.getElementById('hours');
    const minsEl = document.getElementById('minutes');
    const secsEl = document.getElementById('seconds');

    function updateTimer() {
        const now = new Date();
        const diff = targetDateTime - now;

        if (diff <= 0) {
            // Event has started
            const timerContainer = widget.querySelector('.countdown-timer');
            if (timerContainer) {
                timerContainer.innerHTML = '<div style="color: var(--color-primary); font-weight: 700; font-size: 1.1rem; padding: 0.5rem 0;">Event has started!</div>';
            }
            clearInterval(intervalId);
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);

        if (daysEl) daysEl.textContent = String(days).padStart(2, '0');
        if (hoursEl) hoursEl.textContent = String(hours).padStart(2, '0');
        if (minsEl) minsEl.textContent = String(minutes).padStart(2, '0');
        if (secsEl) secsEl.textContent = String(seconds).padStart(2, '0');
    }

    updateTimer();
    const intervalId = setInterval(updateTimer, 1000);
}

/**
 * Mobile responsive navigation menu toggles
 */
function initMobileNav() {
    const toggleBtn = document.querySelector('.mobile-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (toggleBtn && navLinks) {
        toggleBtn.addEventListener('click', () => {
            // Simple toggle. In full apps, it slides out.
            if (navLinks.style.display === 'flex') {
                navLinks.style.display = '';
            } else {
                navLinks.style.display = 'flex';
                navLinks.style.flexDirection = 'column';
                navLinks.style.position = 'absolute';
                navLinks.style.top = 'var(--header-height)';
                navLinks.style.left = '0';
                navLinks.style.width = '100%';
                navLinks.style.background = 'rgba(9, 13, 22, 0.95)';
                navLinks.style.padding = '2rem';
                navLinks.style.borderBottom = '1px solid var(--border-light)';
                navLinks.style.gap = '1.5rem';
                navLinks.style.alignItems = 'flex-start';
                
                const userMenu = navLinks.querySelector('.user-menu');
                if (userMenu) {
                    userMenu.style.borderLeft = 'none';
                    userMenu.style.paddingLeft = '0';
                    userMenu.style.borderTop = '1px solid var(--border-light)';
                    userMenu.style.paddingTop = '1rem';
                    userMenu.style.width = '100%';
                    userMenu.style.flexDirection = 'column';
                    userMenu.style.alignItems = 'flex-start';
                }
            }
        });
    }
}

/**
 * Handle confirmation boxes
 */
function initConfirmations() {
    const deleteForms = document.querySelectorAll('.confirm-delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const title = form.getAttribute('data-title') || 'this event';
            if (!confirm(`Are you sure you want to permanently delete "${title}"? This cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Dynamic AJAX Booking and Cancellation
 */
function initAjaxForms() {
    const forms = document.querySelectorAll('.ajax-form, .ajax-cancel-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const url = form.getAttribute('action');
            const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Show loading state
            const submitBtn = form.querySelector('button[type=submit]');
            const originalContent = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner" style="display:inline-block; animation: spin 1s linear infinite; margin-right: 0.5rem;"><i class="bi bi-arrow-repeat"></i></span> Processing...';

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    showToast(data.message, 'success');
                    // Reload after 1 second so toast is readable and UI updates fully
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showToast(data.message || 'An error occurred', 'error');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalContent;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Fallback to standard form submission if AJAX fails
                form.submit();
            });
        });
    });
}

// Spin animation rule injection dynamically
const styleSheet = document.createElement("style");
styleSheet.innerText = `
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
`;
document.head.appendChild(styleSheet);
