/**
 * OmniForm Studio - Advanced Form Engine & Validation Logic
 * Task 4 - DecodeLabs Internship
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- State Management ---
    const state = {
        currentStep: 1,
        maxSteps: 4,
        mode: 'wizard', // wizard, contact, survey
        theme: localStorage.getItem('omniform_theme') || 'emerald',
        inspectorOpen: true,
        formData: {},
        validity: {},
        submissions: JSON.parse(localStorage.getItem('omniform_submissions') || '[]'),
        selectedFile: null
    };

    // --- DOM Elements ---
    const form = document.getElementById('main-interactive-form');
    const formTitle = document.getElementById('form-title');
    const formSubtitle = document.getElementById('form-subtitle');
    const wizardWrapper = document.getElementById('wizard-progress-wrapper');
    const wizardBarFill = document.getElementById('wizard-bar-fill');
    const stepItems = document.querySelectorAll('.step-item');
    const stepPanes = document.querySelectorAll('.form-step-pane');

    // Action Buttons
    const btnPrev = document.getElementById('btn-prev-step');
    const btnNext = document.getElementById('btn-next-step');
    const btnSubmit = document.getElementById('btn-submit-form');
    const btnFillValid = document.getElementById('btn-fill-valid');
    const btnFillInvalid = document.getElementById('btn-fill-invalid');
    const btnClear = document.getElementById('btn-clear-form');
    
    // Theme & Inspector Controls
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeDropdown = document.getElementById('theme-dropdown');
    const themeOptions = document.querySelectorAll('.theme-option');
    const btnToggleInspector = document.getElementById('btn-toggle-inspector');
    const btnCloseInspector = document.getElementById('btn-close-inspector');
    const appLayout = document.getElementById('app-layout');
    const inspectorAside = document.getElementById('inspector-aside');

    // Password Elements
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const togglePassBtn = document.getElementById('toggle-password');
    const toggleConfirmPassBtn = document.getElementById('toggle-confirm-password');
    const strengthMeterFill = document.getElementById('strength-meter-fill');
    const strengthText = document.getElementById('strength-text');
    const strengthChecklist = document.querySelectorAll('#strength-checklist li');

    // File Upload Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file_input');
    const btnBrowseFile = document.getElementById('btn-browse-file');
    const dropZoneContent = document.getElementById('drop-zone-content');
    const filePreviewCard = document.getElementById('file-preview-card');
    const previewFilename = document.getElementById('preview-filename');
    const previewFilesize = document.getElementById('preview-filesize');
    const btnRemoveFile = document.getElementById('btn-remove-file');
    const previewThumbnail = document.getElementById('preview-thumbnail');

    // Bio Char Counter
    const bioTextarea = document.getElementById('bio');
    const bioCharCount = document.getElementById('bio-char-count');

    // Inspector Outlets
    const jsonOutput = document.getElementById('json-output');
    const logFeed = document.getElementById('log-feed');
    const healthPercentage = document.getElementById('health-percentage');
    const healthBarFill = document.getElementById('health-bar-fill');
    const badgeValidCount = document.getElementById('badge-valid-count');
    const badgeInvalidCount = document.getElementById('badge-invalid-count');
    const historyList = document.getElementById('history-list');
    const historyCount = document.getElementById('history-count');
    const btnCopyJson = document.getElementById('btn-copy-json');

    // Modal
    const successModal = document.getElementById('success-modal');
    const modalDetailsBox = document.getElementById('modal-details-box');
    const btnCloseModal = document.getElementById('btn-close-modal');

    // --- Validation Regex Rules ---
    const validators = {
        fullname: (val) => val.trim().length >= 3 && /^[a-zA-Z\s'-]+$/.test(val.trim()),
        email: (val) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim()),
        phone: (val) => /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/.test(val.trim().replace(/\s+/g, '')),
        dob: (val) => {
            if (!val) return false;
            const birthDate = new Date(val);
            const today = new Date();
            let age = today.getFullYear() - birthDate.getFullYear();
            const m = today.getMonth() - birthDate.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
            return age >= 18 && age <= 120;
        },
        country: (val) => val !== '',
        role: (val) => val !== '',
        password: (val) => calculatePasswordStrength(val).score >= 3,
        confirm_password: (val) => val !== '' && val === passwordInput.value,
        sec_question: (val) => val !== '',
        sec_answer: (val) => val.trim().length >= 2,
        terms: (val, el) => el ? el.checked : false
    };

    // Initialize System
    function init() {
        setTheme(state.theme);
        setupEventListeners();
        updateWizardUI();
        renderSubmissionsHistory();
        validateAllFieldsSilent();
    }

    // --- Theme Selector Engine ---
    function setTheme(newTheme) {
        state.theme = newTheme;
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('omniform_theme', newTheme);
        themeOptions.forEach(opt => {
            opt.classList.toggle('active', opt.dataset.themeVal === newTheme);
        });
    }

    // --- Password Strength Meter ---
    function calculatePasswordStrength(pwd) {
        let score = 0;
        const checks = {
            length: pwd.length >= 8,
            uppercase: /[A-Z]/.test(pwd),
            number: /[0-9]/.test(pwd),
            special: /[^A-Za-z0-9]/.test(pwd)
        };

        if (checks.length) score++;
        if (checks.uppercase) score++;
        if (checks.number) score++;
        if (checks.special) score++;

        return { score, checks };
    }

    function updatePasswordStrengthUI(pwd) {
        const { score, checks } = calculatePasswordStrength(pwd);

        // Update Checklist
        strengthChecklist.forEach(li => {
            const rule = li.dataset.rule;
            if (checks[rule]) {
                li.classList.add('pass');
                li.querySelector('i').className = 'fa-solid fa-circle-check';
            } else {
                li.classList.remove('pass');
                li.querySelector('i').className = 'fa-solid fa-circle';
            }
        });

        // Meter Bar Colors
        let width = '0%';
        let text = 'None';
        let color = '#64748b';

        if (pwd.length > 0) {
            switch (score) {
                case 1:
                    width = '25%';
                    text = 'Weak';
                    color = '#ef4444';
                    break;
                case 2:
                    width = '50%';
                    text = 'Fair';
                    color = '#f59e0b';
                    break;
                case 3:
                    width = '75%';
                    text = 'Strong';
                    color = '#3b82f6';
                    break;
                case 4:
                    width = '100%';
                    text = 'Unstoppable';
                    color = '#10b981';
                    break;
            }
        }

        strengthMeterFill.style.width = width;
        strengthMeterFill.style.backgroundColor = color;
        strengthText.textContent = text;
        strengthText.style.color = color;
    }

    // --- Single Field Real-Time Validator ---
    function validateField(fieldId, showFeedback = true) {
        const inputEl = document.getElementById(fieldId);
        if (!inputEl) return true;

        const groupEl = inputEl.closest('.form-group') || inputEl.closest('.checkbox-group');
        const val = inputEl.type === 'checkbox' ? inputEl.checked : inputEl.value;

        let isValid = true;
        if (validators[fieldId]) {
            isValid = validators[fieldId](val, inputEl);
        } else if (inputEl.required) {
            isValid = val !== '';
        }

        state.validity[fieldId] = isValid;

        if (showFeedback && groupEl) {
            if (isValid) {
                groupEl.classList.remove('is-invalid');
                groupEl.classList.add('is-valid');
            } else {
                groupEl.classList.remove('is-valid');
                groupEl.classList.add('is-invalid');
            }
        }

        updateFormDataState();
        return isValid;
    }

    function validateAllFieldsSilent() {
        const fieldIds = ['fullname', 'email', 'phone', 'dob', 'country', 'role', 'password', 'confirm_password', 'sec_question', 'sec_answer', 'terms'];
        fieldIds.forEach(id => {
            const inputEl = document.getElementById(id);
            if (inputEl) {
                const val = inputEl.type === 'checkbox' ? inputEl.checked : inputEl.value;
                if (validators[id]) {
                    state.validity[id] = validators[id](val, inputEl);
                }
            }
        });
        updateFormDataState();
    }

    // --- Live Data & JSON Inspector Updating ---
    function updateFormDataState() {
        const formDataObj = {};
        const elements = form.querySelectorAll('input, select, textarea');

        elements.forEach(el => {
            if (el.name) {
                if (el.type === 'checkbox') {
                    formDataObj[el.name] = el.checked;
                } else if (el.type === 'radio') {
                    if (el.checked) formDataObj[el.name] = el.value;
                } else if (el.type !== 'password' && el.type !== 'file') {
                    formDataObj[el.name] = el.value;
                } else if (el.type === 'file') {
                    formDataObj[el.name] = state.selectedFile ? state.selectedFile.name : null;
                }
            }
        });

        state.formData = formDataObj;
        jsonOutput.innerHTML = `<code>${JSON.stringify(formDataObj, null, 2)}</code>`;

        // Calculate Form Health
        const totalTracked = Object.keys(state.validity).length || 1;
        let validCount = 0;
        let invalidCount = 0;

        Object.values(state.validity).forEach(v => {
            if (v) validCount++;
            else invalidCount++;
        });

        const percent = Math.round((validCount / totalTracked) * 100);
        healthPercentage.textContent = `${percent}%`;
        healthBarFill.style.width = `${percent}%`;
        badgeValidCount.innerHTML = `<i class="fa-solid fa-check"></i> ${validCount} Valid`;
        badgeInvalidCount.innerHTML = `<i class="fa-solid fa-xmark"></i> ${invalidCount} Invalid`;
    }

    function addLogEntry(message, type = 'info') {
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const logItem = document.createElement('div');
        logItem.className = `log-entry ${type}`;
        logItem.innerHTML = `<span class="time">[${timeStr}]</span> ${message}`;
        logFeed.prepend(logItem);
    }

    // --- Multi-Step Wizard Navigation ---
    function validateStep(stepNum) {
        let isStepValid = true;
        let fieldsToValidate = [];

        if (stepNum === 1) {
            fieldsToValidate = ['fullname', 'email', 'phone', 'dob', 'country', 'role'];
        } else if (stepNum === 2) {
            fieldsToValidate = ['password', 'confirm_password', 'sec_question', 'sec_answer'];
        } else if (stepNum === 3) {
            fieldsToValidate = []; // optional fields
        } else if (stepNum === 4) {
            fieldsToValidate = ['terms'];
        }

        fieldsToValidate.forEach(fieldId => {
            const valid = validateField(fieldId, true);
            if (!valid) {
                isStepValid = false;
                addLogEntry(`Validation error on field '${fieldId}'`, 'invalid');
            }
        });

        return isStepValid;
    }

    function updateWizardUI() {
        // Hide/Show Step Panes
        stepPanes.forEach(pane => {
            pane.classList.toggle('active', parseInt(pane.dataset.pane) === state.currentStep);
        });

        // Step Circles
        stepItems.forEach(item => {
            const s = parseInt(item.dataset.step);
            item.classList.toggle('active', s === state.currentStep);
            item.classList.toggle('completed', s < state.currentStep);
        });

        // Progress Fill Bar
        const fillPercent = (state.currentStep / state.maxSteps) * 100;
        wizardBarFill.style.width = `${fillPercent}%`;

        // Footer Action Buttons
        btnPrev.classList.toggle('hidden', state.currentStep === 1);
        btnNext.classList.toggle('hidden', state.currentStep === state.maxSteps);
        btnSubmit.classList.toggle('hidden', state.currentStep !== state.maxSteps);

        if (state.currentStep === 4) {
            renderSummaryReview();
        }
    }

    function renderSummaryReview() {
        const list = document.getElementById('summary-preview-list');
        list.innerHTML = `
            <div class="summary-item">
                <label>Full Name</label>
                <span>${state.formData.fullname || 'N/A'}</span>
            </div>
            <div class="summary-item">
                <label>Email Address</label>
                <span>${state.formData.email || 'N/A'}</span>
            </div>
            <div class="summary-item">
                <label>Phone Number</label>
                <span>${state.formData.phone || 'N/A'}</span>
            </div>
            <div class="summary-item">
                <label>Role / Target</label>
                <span>${state.formData.role || 'N/A'} (${state.formData.country || 'N/A'})</span>
            </div>
            <div class="summary-item">
                <label>Selected File</label>
                <span>${state.selectedFile ? state.selectedFile.name : 'No file attached'}</span>
            </div>
            <div class="summary-item">
                <label>Experience</label>
                <span style="text-transform: capitalize;">${state.formData.experience || 'Junior'}</span>
            </div>
        `;
    }

    // --- Mode Switcher ---
    function switchMode(newMode) {
        state.mode = newMode;
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === newMode);
        });

        if (newMode === 'wizard') {
            formTitle.textContent = 'Account Registration Wizard';
            formSubtitle.textContent = 'Complete all steps to experience real-time validation & rich animated micro-interactions.';
            wizardWrapper.style.display = 'block';
            state.currentStep = 1;
        } else if (newMode === 'contact') {
            formTitle.textContent = 'Support & Feedback Portal';
            formSubtitle.textContent = 'Quick single-page form for prompt customer support and issue logging.';
            wizardWrapper.style.display = 'none';
            state.currentStep = 1;
        } else if (newMode === 'survey') {
            formTitle.textContent = 'Interactive Developer Survey';
            formSubtitle.textContent = 'Help us understand your workflow and preferences.';
            wizardWrapper.style.display = 'none';
            state.currentStep = 1;
        }
        updateWizardUI();
        addLogEntry(`Form mode switched to [${newMode.toUpperCase()}]`);
    }

    // --- Drag & Drop File Handler ---
    function setupFileHandlers() {
        btnBrowseFile.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleSelectedFile(e.target.files[0]);
            }
        });

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                handleSelectedFile(e.dataTransfer.files[0]);
            }
        });

        btnRemoveFile.addEventListener('click', () => {
            state.selectedFile = null;
            fileInput.value = '';
            filePreviewCard.classList.add('hidden');
            dropZoneContent.style.display = 'block';
            updateFormDataState();
            addLogEntry('File attachment removed');
        });
    }

    function handleSelectedFile(file) {
        if (file.size > 5 * 1024 * 1024) {
            alert('File size exceeds 5MB limit.');
            addLogEntry(`File error: ${file.name} is too large (${(file.size / 1024 / 1024).toFixed(2)} MB)`, 'invalid');
            return;
        }

        state.selectedFile = file;
        previewFilename.textContent = file.name;
        previewFilesize.textContent = `${(file.size / 1024).toFixed(1)} KB`;

        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewThumbnail.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            };
            reader.readAsDataURL(file);
        } else {
            previewThumbnail.innerHTML = `<i class="fa-solid fa-file-lines"></i>`;
        }

        dropZoneContent.style.display = 'none';
        filePreviewCard.classList.remove('hidden');
        updateFormDataState();
        addLogEntry(`Attached file: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`, 'valid');
    }

    // --- Submissions History Management ---
    function renderSubmissionsHistory() {
        historyCount.textContent = state.submissions.length;
        if (state.submissions.length === 0) {
            historyList.innerHTML = `<p class="empty-state">No saved submissions yet.</p>`;
            return;
        }

        historyList.innerHTML = state.submissions.map((sub, index) => `
            <div class="history-card">
                <div style="display: flex; justify-content: space-between; font-weight:700; color:var(--accent-color);">
                    <span>#${state.submissions.length - index} ${sub.fullname || 'User'}</span>
                    <span style="font-size:0.7rem; color:var(--text-muted);">${sub.timestamp}</span>
                </div>
                <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:2px;">
                    ${sub.email} • ${sub.role || 'Developer'}
                </div>
            </div>
        `).join('');
    }

    // --- Event Listeners Setup ---
    function setupEventListeners() {
        // Inputs Real-Time Events
        const liveInputs = form.querySelectorAll('input, select, textarea');
        liveInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                validateField(e.target.id, true);
            });

            input.addEventListener('blur', (e) => {
                validateField(e.target.id, true);
            });
        });

        // Bio Character Counter
        bioTextarea.addEventListener('input', (e) => {
            const len = e.target.value.length;
            bioCharCount.textContent = `${len} / 250`;
        });

        // Password Strength Live Update
        passwordInput.addEventListener('input', (e) => {
            updatePasswordStrengthUI(e.target.value);
            if (confirmPasswordInput.value) {
                validateField('confirm_password', true);
            }
        });

        // Password Visibility Toggles
        togglePassBtn.addEventListener('click', () => {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            togglePassBtn.querySelector('i').className = type === 'password' ? 'fa-solid fa-eye' : 'fa-solid fa-eye-slash';
        });

        toggleConfirmPassBtn.addEventListener('click', () => {
            const type = confirmPasswordInput.type === 'password' ? 'text' : 'password';
            confirmPasswordInput.type = type;
            toggleConfirmPassBtn.querySelector('i').className = type === 'password' ? 'fa-solid fa-eye' : 'fa-solid fa-eye-slash';
        });

        // Mode Nav
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', () => switchMode(btn.dataset.mode));
        });

        // Wizard Buttons
        btnNext.addEventListener('click', () => {
            if (validateStep(state.currentStep)) {
                addLogEntry(`Step ${state.currentStep} validated successfully. Moving to Step ${state.currentStep + 1}.`, 'valid');
                state.currentStep++;
                updateWizardUI();
            } else {
                addLogEntry(`Cannot proceed. Please fix errors in Step ${state.currentStep}.`, 'invalid');
            }
        });

        btnPrev.addEventListener('click', () => {
            if (state.currentStep > 1) {
                state.currentStep--;
                updateWizardUI();
            }
        });

        // Quick Action Toolbar Buttons
        btnFillValid.addEventListener('click', () => {
            document.getElementById('fullname').value = 'Alex Rivera';
            document.getElementById('email').value = 'alex.rivera@decodelabs.com';
            document.getElementById('phone').value = '+1 (555) 234-5678';
            document.getElementById('dob').value = '1998-05-14';
            document.getElementById('country').value = 'US';
            document.getElementById('role').value = 'fullstack';
            document.getElementById('password').value = 'SecureP@ss2026!';
            document.getElementById('confirm_password').value = 'SecureP@ss2026!';
            document.getElementById('sec_question').value = 'pet';
            document.getElementById('sec_answer').value = 'Shadow';
            document.getElementById('bio').value = 'Experienced developer passionate about responsive UI design and clean JavaScript code.';
            document.getElementById('terms').checked = true;

            bioCharCount.textContent = `${document.getElementById('bio').value.length} / 250`;
            updatePasswordStrengthUI('SecureP@ss2026!');
            
            ['fullname', 'email', 'phone', 'dob', 'country', 'role', 'password', 'confirm_password', 'sec_question', 'sec_answer', 'terms'].forEach(id => {
                validateField(id, true);
            });
            addLogEntry('Auto-filled form with 100% valid test dataset.', 'valid');
        });

        btnFillInvalid.addEventListener('click', () => {
            document.getElementById('fullname').value = 'Al'; // too short
            document.getElementById('email').value = 'invalid-email-address';
            document.getElementById('phone').value = '123';
            document.getElementById('dob').value = '2025-01-01'; // under 18
            document.getElementById('country').value = '';
            document.getElementById('role').value = '';
            document.getElementById('password').value = '123';
            document.getElementById('confirm_password').value = '456';
            document.getElementById('terms').checked = false;

            updatePasswordStrengthUI('123');

            ['fullname', 'email', 'phone', 'dob', 'country', 'role', 'password', 'confirm_password', 'terms'].forEach(id => {
                validateField(id, true);
            });
            addLogEntry('Auto-filled form with invalid test data to demonstrate errors.', 'invalid');
        });

        btnClear.addEventListener('click', () => {
            form.reset();
            state.selectedFile = null;
            filePreviewCard.classList.add('hidden');
            dropZoneContent.style.display = 'block';
            bioCharCount.textContent = '0 / 250';
            updatePasswordStrengthUI('');

            document.querySelectorAll('.form-group, .checkbox-group').forEach(group => {
                group.classList.remove('is-valid', 'is-invalid');
            });

            validateAllFieldsSilent();
            addLogEntry('Cleared all form inputs.');
        });

        // Theme Toggle Dropdown
        themeToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            themeDropdown.classList.toggle('show');
        });

        document.addEventListener('click', (e) => {
            if (!themePickerContains(e.target)) {
                themeDropdown.classList.remove('show');
            }
        });

        themeOptions.forEach(opt => {
            opt.addEventListener('click', () => {
                setTheme(opt.dataset.themeVal);
                themeDropdown.classList.remove('show');
                addLogEntry(`Switched theme palette to ${opt.dataset.themeVal.toUpperCase()}`);
            });
        });

        function themePickerContains(target) {
            return themeToggleBtn.contains(target) || themeDropdown.contains(target);
        }

        // Drawer Inspector Toggle
        btnToggleInspector.addEventListener('click', () => {
            inspectorAside.classList.toggle('collapsed');
            appLayout.classList.toggle('inspector-collapsed');
        });

        btnCloseInspector.addEventListener('click', () => {
            inspectorAside.classList.add('collapsed');
            appLayout.classList.add('inspector-collapsed');
        });

        // Copy JSON Button
        btnCopyJson.addEventListener('click', () => {
            const codeText = jsonOutput.innerText;
            navigator.clipboard.writeText(codeText).then(() => {
                btnCopyJson.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
                setTimeout(() => {
                    btnCopyJson.innerHTML = `<i class="fa-solid fa-copy"></i> Copy`;
                }, 2000);
            });
        });

        // Tabs in Inspector
        document.querySelectorAll('.inspector-tabs .tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.inspector-tabs .tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.inspector-aside .tab-pane').forEach(p => p.classList.remove('active'));

                btn.classList.add('active');
                document.getElementById(`pane-${btn.dataset.tab}`).classList.add('active');
            });
        });

        // Setup Drag and Drop File Handlers
        setupFileHandlers();

        // Form Submit Listener
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            let allValid = true;
            const requiredFields = ['fullname', 'email', 'phone', 'dob', 'country', 'role', 'password', 'confirm_password', 'sec_question', 'sec_answer', 'terms'];

            requiredFields.forEach(id => {
                if (!validateField(id, true)) {
                    allValid = false;
                }
            });

            if (!allValid) {
                addLogEntry('Submission blocked: 1 or more validation checks failed.', 'invalid');
                alert('Please resolve all validation errors highlighted in red before submitting.');
                return;
            }

            // Record Submission
            const submissionRecord = {
                ...state.formData,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };

            state.submissions.unshift(submissionRecord);
            localStorage.setItem('omniform_submissions', JSON.stringify(state.submissions));
            renderSubmissionsHistory();

            // Populate Success Modal Details
            modalDetailsBox.innerHTML = `
                <p><strong>Name:</strong> ${submissionRecord.fullname}</p>
                <p><strong>Email:</strong> ${submissionRecord.email}</p>
                <p><strong>Phone:</strong> ${submissionRecord.phone}</p>
                <p><strong>Role:</strong> ${submissionRecord.role} (${submissionRecord.country})</p>
                <p><strong>File Attached:</strong> ${submissionRecord.file_input || 'None'}</p>
                <p><strong>Timestamp:</strong> ${submissionRecord.timestamp}</p>
            `;

            successModal.classList.remove('hidden');
            addLogEntry('Form successfully validated & submitted!', 'valid');
        });

        // Close Modal
        btnCloseModal.addEventListener('click', () => {
            successModal.classList.add('hidden');
            btnClear.click();
            state.currentStep = 1;
            updateWizardUI();
        });
    }

    // Run Initializer
    init();
});
