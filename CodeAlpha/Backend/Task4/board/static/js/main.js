document.addEventListener('DOMContentLoaded', () => {
    // 1. Light/Dark Theme Toggle
    const themeToggleBtn = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'dark';

    // Apply saved theme on load
    if (currentTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        updateThemeIcon('light');
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateThemeIcon('dark');
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            let theme = document.documentElement.getAttribute('data-theme');
            if (theme === 'light') {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                updateThemeIcon('dark');
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
                updateThemeIcon('light');
            }
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        if (theme === 'light') {
            themeToggleBtn.innerHTML = '<i data-lucide="moon"></i>';
        } else {
            themeToggleBtn.innerHTML = '<i data-lucide="sun"></i>';
        }
        // Re-initialize Lucide icons if available
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    // 2. AJAX Application Status Updates for Employers
    const statusSelects = document.querySelectorAll('.status-select');
    statusSelects.forEach(select => {
        select.addEventListener('change', async (e) => {
            const selectEl = e.target;
            const applicationId = selectEl.getAttribute('data-app-id');
            const newStatus = selectEl.value;
            const url = `/application/status/${applicationId}/`;
            
            // Get CSRF Token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            if (!csrfToken) {
                console.error("CSRF token not found!");
                return;
            }

            try {
                selectEl.disabled = true;
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken
                    },
                    body: `status=${encodeURIComponent(newStatus)}`
                });

                const result = await response.json();
                if (result.success) {
                    // Find the status badge and update its text and classes
                    const badge = document.getElementById(`badge-${applicationId}`);
                    if (badge) {
                        badge.textContent = result.new_status;
                        // Clear old status classes
                        badge.className = 'status-badge';
                        badge.classList.add(`status-${result.status_code}`);
                    }
                    
                    // Flash success effect
                    selectEl.style.borderColor = 'var(--color-success)';
                    setTimeout(() => {
                        selectEl.style.borderColor = 'var(--border-color)';
                    }, 1500);
                } else {
                    alert('Error updating status: ' + (result.error || 'Unknown error'));
                }
            } catch (err) {
                console.error('Fetch error:', err);
                alert('An error occurred. Please try again.');
            } finally {
                selectEl.disabled = false;
            }
        });
    });

    // 3. Dynamic Registration Field Visibility
    const roleSelect = document.getElementById('role-select');
    const employerFields = document.getElementById('employer-fields');
    const candidateFields = document.getElementById('candidate-fields');

    if (roleSelect) {
        const toggleFields = () => {
            if (roleSelect.value === 'employer') {
                if (employerFields) employerFields.style.display = 'block';
                if (candidateFields) candidateFields.style.display = 'none';
            } else {
                if (employerFields) employerFields.style.display = 'none';
                if (candidateFields) candidateFields.style.display = 'block';
            }
        };
        roleSelect.addEventListener('change', toggleFields);
        toggleFields(); // Initial run
    }
});
