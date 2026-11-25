document.addEventListener('DOMContentLoaded', () => {
    const shortenForm = document.getElementById('shortenForm');
    const longUrlInput = document.getElementById('longUrl');
    const resultCard = document.getElementById('resultCard');
    const shortenedUrlInput = document.getElementById('shortenedUrl');
    const copyBtn = document.getElementById('copyBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    const analyticsBody = document.getElementById('analyticsBody');
    const submitBtn = shortenForm.querySelector('.btn-submit');

    // Load initial analytics
    loadAnalytics();

    // Form Submission
    shortenForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = longUrlInput.value.strip ? longUrlInput.value.strip() : longUrlInput.value.trim();
        
        if (!url) return;

        // Set Loading state
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        resultCard.classList.add('hidden');

        try {
            const response = await fetch('/api/shorten', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Something went wrong');
            }

            // Display success
            shortenedUrlInput.value = data.short_url;
            resultCard.classList.remove('hidden');
            
            // Clear input and reload analytics
            longUrlInput.value = '';
            loadAnalytics();

        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    });

    // Copy to Clipboard Action
    copyBtn.addEventListener('click', async () => {
        const url = shortenedUrlInput.value;
        const success = await copyToClipboard(url);
        if (success) {
            copyBtn.innerHTML = '✨ Copied!';
            copyBtn.classList.add('copied');
            setTimeout(() => {
                copyBtn.innerHTML = '📋 Copy';
                copyBtn.classList.remove('copied');
            }, 2000);
        }
    });

    // Refresh Action
    refreshBtn.addEventListener('click', loadAnalytics);

    // Fetch and render analytics
    async function loadAnalytics() {
        try {
            const response = await fetch('/api/analytics');
            const urls = await response.json();

            if (urls.length === 0) {
                analyticsBody.innerHTML = `
                    <tr>
                        <td colspan="5" class="empty-state">No links shortened yet. Create one above!</td>
                    </tr>
                `;
                return;
            }

            analyticsBody.innerHTML = urls.map(url => {
                const date = new Date(url.created_at).toLocaleString();
                return `
                    <tr>
                        <td>
                            <a href="${url.original_url}" target="_blank" class="link-original" title="${url.original_url}">
                                ${url.original_url}
                            </a>
                        </td>
                        <td>
                            <a href="${url.short_url}" target="_blank" class="link-short">
                                ${url.short_url}
                            </a>
                        </td>
                        <td>${date}</td>
                        <td><span class="clicks-badge">${url.clicks}</span></td>
                        <td>
                            <button class="btn-table-copy" onclick="copyTableLink(this, '${url.short_url}')">
                                Copy
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');

        } catch (error) {
            console.error('Error fetching analytics:', error);
        }
    }

    // Helper functions
    async function copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            // Fallback for non-secure contexts
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                document.body.removeChild(textarea);
                return true;
            } catch (fallbackErr) {
                console.error('Fallback copy failed', fallbackErr);
                document.body.removeChild(textarea);
                return false;
            }
        }
    }

    // Global helper exposed to inline click handler
    window.copyTableLink = async (button, url) => {
        const success = await copyToClipboard(url);
        if (success) {
            const originalText = button.innerHTML;
            button.innerHTML = 'Copied!';
            button.style.borderColor = '#10b981';
            button.style.color = '#10b981';
            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.borderColor = '';
                button.style.color = '';
            }, 1500);
        }
    };
});
