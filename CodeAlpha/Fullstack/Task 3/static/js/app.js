// App State
let state = {
    currentUser: null,
    projects: [],
    currentProject: null,
    users: [], // For assignment candidates
    activeTask: null,
    socket: null
};

// DOM Elements
const elements = {
    authContainer: document.getElementById('auth-container'),
    appContainer: document.getElementById('app-container'),
    loginForm: document.getElementById('login-form'),
    registerForm: document.getElementById('register-form'),
    toRegister: document.getElementById('to-register'),
    toLogin: document.getElementById('to-login'),
    authSubtitle: document.getElementById('auth-subtitle'),
    
    projectList: document.getElementById('project-list'),
    btnCreateProjectTrigger: document.getElementById('btn-create-project-trigger'),
    btnWelcomeCreateProject: document.getElementById('btn-welcome-create-project'),
    
    userAvatar: document.getElementById('user-avatar'),
    userDisplayName: document.getElementById('user-display-name'),
    userDisplayEmail: document.getElementById('user-display-email'),
    btnLogout: document.getElementById('btn-logout'),
    
    dashboardWelcome: document.getElementById('dashboard-welcome'),
    projectWorkspace: document.getElementById('project-workspace'),
    currentProjectName: document.getElementById('current-project-name'),
    currentProjectDesc: document.getElementById('current-project-desc'),
    projectMembersAvatars: document.getElementById('project-members-avatars'),
    btnInviteMemberTrigger: document.getElementById('btn-invite-member-trigger'),
    
    // Kanban lists
    tasksTodo: document.getElementById('tasks-todo'),
    tasksProgress: document.getElementById('tasks-progress'),
    tasksReview: document.getElementById('tasks-review'),
    tasksDone: document.getElementById('tasks-done'),
    
    // Counts
    countTodo: document.getElementById('count-todo'),
    countProgress: document.getElementById('count-progress'),
    countReview: document.getElementById('count-review'),
    countDone: document.getElementById('count-done'),
    
    // Modals
    modalCreateProject: document.getElementById('modal-create-project'),
    formCreateProject: document.getElementById('form-create-project'),
    
    modalInviteMember: document.getElementById('modal-invite-member'),
    formInviteMember: document.getElementById('form-invite-member'),
    
    modalTaskDetails: document.getElementById('modal-task-details'),
    taskDetailTitle: document.getElementById('task-detail-title'),
    taskDetailProjectName: document.getElementById('task-detail-project-name'),
    taskDetailStatusBadge: document.getElementById('task-detail-status-badge'),
    taskDetailAssignee: document.getElementById('task-detail-assignee'),
    taskDetailPriority: document.getElementById('task-detail-priority'),
    taskDetailDue: document.getElementById('task-detail-due'),
    taskDetailDesc: document.getElementById('task-detail-desc'),
    btnSaveTaskDetails: document.getElementById('btn-save-task-details'),
    btnDeleteTask: document.getElementById('btn-delete-task'),
    
    // Comments
    commentsContainer: document.getElementById('comments-container'),
    formAddComment: document.getElementById('form-add-comment'),
    newCommentContent: document.getElementById('new-comment-content'),
    commentFormAvatar: document.getElementById('comment-form-avatar'),
    
    // Notifications
    btnNotificationsTrigger: document.getElementById('btn-notifications-trigger'),
    notiBadge: document.getElementById('noti-badge'),
    notificationsPanel: document.getElementById('notifications-panel'),
    notificationsList: document.getElementById('notifications-list'),
    btnMarkAllRead: document.getElementById('btn-mark-all-read'),
    btnCloseNotifications: document.getElementById('btn-close-notifications'),
    toastContainer: document.getElementById('toast-container')
};

// ================= TOAST ALERTS =================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconClass = 'fa-circle-info';
    if (type === 'success') iconClass = 'fa-circle-check';
    if (type === 'error') iconClass = 'fa-circle-exclamation';
    
    toast.innerHTML = `<i class="fa-solid ${iconClass}"></i> <span>${message}</span>`;
    elements.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ================= INITIALIZATION & AUTH =================
document.addEventListener('DOMContentLoaded', () => {
    checkCurrentUser();
    setupEventListeners();
});

function setupEventListeners() {
    // Auth Switching
    elements.toRegister.addEventListener('click', () => {
        elements.loginForm.classList.remove('active');
        elements.registerForm.classList.add('active');
        elements.authSubtitle.textContent = 'Join us and start organizing projects in seconds.';
    });
    
    elements.toLogin.addEventListener('click', () => {
        elements.registerForm.classList.remove('active');
        elements.loginForm.classList.add('active');
        elements.authSubtitle.textContent = 'Collaborate, organize, and hit deadlines in real-time.';
    });
    
    // Submit Auth Forms
    elements.loginForm.addEventListener('submit', handleLogin);
    elements.registerForm.addEventListener('submit', handleRegister);
    elements.btnLogout.addEventListener('click', handleLogout);
    
    // Modal Open/Close triggers
    elements.btnCreateProjectTrigger.addEventListener('click', () => openModal(elements.modalCreateProject));
    elements.btnWelcomeCreateProject.addEventListener('click', () => openModal(elements.modalCreateProject));
    elements.btnInviteMemberTrigger.addEventListener('click', () => openModal(elements.modalInviteMember));
    
    document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal-overlay');
            closeModal(modal);
        });
    });
    
    // Submit Create Project
    elements.formCreateProject.addEventListener('submit', handleCreateProject);
    elements.formInviteMember.addEventListener('submit', handleInviteMember);
    
    // Create Task triggers (Delegated for dynamically rendered column buttons)
    document.querySelectorAll('.btn-add-task-trigger').forEach(btn => {
        btn.addEventListener('click', () => {
            const status = btn.getAttribute('data-status');
            createNewTaskPrompt(status);
        });
    });
    
    // Task Detail Actions
    elements.btnSaveTaskDetails.addEventListener('click', saveTaskDetails);
    elements.btnDeleteTask.addEventListener('click', deleteTask);
    elements.formAddComment.addEventListener('submit', postComment);
    
    // Notifications trigger
    elements.btnNotificationsTrigger.addEventListener('click', toggleNotificationsPanel);
    elements.btnCloseNotifications.addEventListener('click', () => elements.notificationsPanel.classList.remove('active'));
    elements.btnMarkAllRead.addEventListener('click', markAllNotificationsRead);
}

function openModal(modal) {
    modal.classList.add('active');
}

function closeModal(modal) {
    modal.classList.remove('active');
}

// User Check
async function checkCurrentUser() {
    try {
        const response = await fetch('/api/auth/me');
        const data = await response.json();
        if (data.user) {
            loginAppSuccess(data.user);
        } else {
            elements.authContainer.classList.add('active');
            elements.appContainer.classList.remove('active');
        }
    } catch (err) {
        console.error('Error checking authentication status:', err);
    }
}

// Login Handler
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await res.json();
        if (res.ok) {
            showToast(`Welcome back, ${data.user.username}!`, 'success');
            loginAppSuccess(data.user);
        } else {
            showToast(data.error || 'Authentication failed', 'error');
        }
    } catch (err) {
        showToast('Server connection error', 'error');
    }
}

// Register Handler
async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    
    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await res.json();
        if (res.ok) {
            showToast(`Account created successfully!`, 'success');
            loginAppSuccess(data.user);
        } else {
            showToast(data.error || 'Registration failed', 'error');
        }
    } catch (err) {
        showToast('Server connection error', 'error');
    }
}

// Logout Handler
async function handleLogout() {
    try {
        const res = await fetch('/api/auth/logout', { method: 'POST' });
        if (res.ok) {
            if (state.socket) {
                state.socket.disconnect();
                state.socket = null;
            }
            state.currentUser = null;
            state.projects = [];
            state.currentProject = null;
            
            elements.appContainer.classList.remove('active');
            elements.authContainer.classList.add('active');
            elements.loginForm.reset();
            elements.registerForm.reset();
            showToast('Logged out successfully', 'info');
        }
    } catch (err) {
        console.error('Logout error:', err);
    }
}

// Authentication Success
function loginAppSuccess(user) {
    state.currentUser = user;
    
    // Update User UI elements
    elements.userDisplayName.textContent = user.username;
    elements.userDisplayEmail.textContent = user.email;
    elements.userAvatar.textContent = user.username.substring(0, 2).toUpperCase();
    elements.userAvatar.style.backgroundColor = user.avatar_color;
    elements.commentFormAvatar.textContent = user.username.substring(0, 2).toUpperCase();
    elements.commentFormAvatar.style.backgroundColor = user.avatar_color;
    
    // Switch views
    elements.authContainer.classList.remove('active');
    elements.appContainer.classList.add('active');
    
    // Initialize sockets & APIs
    initSocketConnection();
    loadProjects();
    loadUsersList();
    loadNotifications();
    
    // Poll notifications every 30 seconds
    setInterval(loadNotifications, 30000);
}

// ================= SOCKETS FOR REAL-TIME COLLABORATION =================
function initSocketConnection() {
    if (state.socket) return;
    
    state.socket = io();
    
    state.socket.on('connect', () => {
        console.log('Real-time connection active.');
        // Re-join project room if active
        if (state.currentProject) {
            state.socket.emit('join_project', { project_id: state.currentProject.id });
        }
    });
    
    // Bind syncing events from server
    state.socket.on('task_moved_sync', (data) => {
        // Find task and update status locally
        if (state.currentProject && data.project_id === state.currentProject.id) {
            const task = state.currentProject.tasks.find(t => t.id === data.task_id);
            if (task) {
                task.status = data.status;
                renderKanbanBoard();
                showToast(`Task "${task.title}" was moved to ${data.status} by teammate.`, 'info');
            }
        }
    });
    
    state.socket.on('task_created_sync', (data) => {
        if (state.currentProject && data.task.project_id === state.currentProject.id) {
            state.currentProject.tasks.push(data.task);
            renderKanbanBoard();
            showToast(`New task "${data.task.title}" added to board.`, 'success');
        }
    });
    
    state.socket.on('task_updated_sync', (data) => {
        if (state.currentProject && data.task.project_id === state.currentProject.id) {
            const idx = state.currentProject.tasks.findIndex(t => t.id === data.task.id);
            if (idx !== -1) {
                state.currentProject.tasks[idx] = data.task;
                renderKanbanBoard();
                
                // If this task is active in modal, update it
                if (state.activeTask && state.activeTask.id === data.task.id) {
                    state.activeTask = data.task;
                    populateTaskDetailsModal(data.task);
                }
                showToast(`Task "${data.task.title}" was updated.`, 'info');
            }
        }
    });
    
    state.socket.on('task_deleted_sync', (data) => {
        if (state.currentProject && data.project_id === state.currentProject.id) {
            const idx = state.currentProject.tasks.findIndex(t => t.id === data.task_id);
            if (idx !== -1) {
                const deletedTitle = state.currentProject.tasks[idx].title;
                state.currentProject.tasks.splice(idx, 1);
                renderKanbanBoard();
                
                // Close modal if looking at deleted task
                if (state.activeTask && state.activeTask.id === data.task_id) {
                    closeModal(elements.modalTaskDetails);
                    state.activeTask = null;
                }
                showToast(`Task "${deletedTitle}" was deleted by teammate.`, 'warning');
            }
        }
    });
    
    state.socket.on('comment_added_sync', (data) => {
        // If modal open matches task ID, append comment
        if (state.activeTask && state.activeTask.id === data.comment.task_id) {
            appendCommentToView(data.comment);
        }
    });
    
    state.socket.on('member_added_sync', (data) => {
        if (state.currentProject && data.project_id === state.currentProject.id) {
            // Reload project info to refresh members list
            reloadCurrentProjectDetails();
            showToast(`${data.username} joined the project workspace!`, 'success');
        }
    });
}

// ================= PROJECTS MODULE =================
async function loadProjects() {
    try {
        const res = await fetch('/api/projects');
        const data = await res.json();
        state.projects = data;
        renderProjectsList();
    } catch (err) {
        console.error('Error fetching projects:', err);
    }
}

function renderProjectsList() {
    elements.projectList.innerHTML = '';
    
    if (state.projects.length === 0) {
        elements.projectList.innerHTML = '<p class="text-center font-sm p-3 text-muted">No projects yet</p>';
        return;
    }
    
    state.projects.forEach(proj => {
        const li = document.createElement('li');
        li.setAttribute('data-id', proj.id);
        if (state.currentProject && state.currentProject.id === proj.id) {
            li.className = 'active';
        }
        li.innerHTML = `<i class="fa-regular fa-folder-open"></i> <span>${proj.name}</span>`;
        li.addEventListener('click', () => selectProject(proj.id));
        elements.projectList.appendChild(li);
    });
}

async function selectProject(projectId) {
    // Leave previous room if any
    if (state.currentProject && state.socket) {
        state.socket.emit('leave_project', { project_id: state.currentProject.id });
    }
    
    // Toggle active sidebar link
    document.querySelectorAll('#project-list li').forEach(li => {
        li.classList.remove('active');
        if (li.getAttribute('data-id') == projectId) li.classList.add('active');
    });
    
    // Fetch details
    try {
        const res = await fetch(`/api/projects/${projectId}`);
        if (!res.ok) {
            showToast('Forbidden access or project not found', 'error');
            return;
        }
        const data = await res.json();
        state.currentProject = data;
        
        // Hide welcome screen
        elements.dashboardWelcome.classList.remove('active');
        elements.projectWorkspace.classList.add('active');
        
        // Update header info
        elements.currentProjectName.textContent = data.name;
        elements.currentProjectDesc.textContent = data.description || 'No description provided.';
        
        // Render project members
        renderProjectMembersAvatars();
        
        // Populate Assignees dropdown in Task detail modal
        populateAssigneesSelectDropdown();
        
        // Render cards
        renderKanbanBoard();
        
        // Join SocketIO Project room
        if (state.socket) {
            state.socket.emit('join_project', { project_id: projectId });
        }
    } catch (err) {
        console.error('Error fetching project data:', err);
    }
}

async function reloadCurrentProjectDetails() {
    if (!state.currentProject) return;
    try {
        const res = await fetch(`/api/projects/${state.currentProject.id}`);
        if (res.ok) {
            const data = await res.json();
            state.currentProject = data;
            renderProjectMembersAvatars();
            populateAssigneesSelectDropdown();
        }
    } catch (err) {
        console.error('Error reloading project:', err);
    }
}

function renderProjectMembersAvatars() {
    elements.projectMembersAvatars.innerHTML = '';
    if (!state.currentProject || !state.currentProject.members) return;
    
    // Limit to 5 visible avatars and show count for remainder
    const visibleMembers = state.currentProject.members.slice(0, 5);
    const hiddenCount = state.currentProject.members.length - visibleMembers.length;
    
    visibleMembers.forEach(mem => {
        const div = document.createElement('div');
        div.className = 'member-avatar';
        div.style.backgroundColor = mem.avatar_color;
        div.textContent = mem.username.substring(0, 2).toUpperCase();
        div.title = `${mem.username} (${mem.role})`;
        elements.projectMembersAvatars.appendChild(div);
    });
    
    if (hiddenCount > 0) {
        const div = document.createElement('div');
        div.className = 'member-avatar';
        div.style.backgroundColor = '#4b5563';
        div.textContent = `+${hiddenCount}`;
        div.title = `${hiddenCount} other members`;
        elements.projectMembersAvatars.appendChild(div);
    }
}

function populateAssigneesSelectDropdown() {
    elements.taskDetailAssignee.innerHTML = '<option value="">Unassigned</option>';
    if (!state.currentProject || !state.currentProject.members) return;
    
    state.currentProject.members.forEach(mem => {
        const opt = document.createElement('option');
        opt.value = mem.id;
        opt.textContent = mem.username;
        elements.taskDetailAssignee.appendChild(opt);
    });
}

// Create Project Submission
async function handleCreateProject(e) {
    e.preventDefault();
    const name = document.getElementById('new-project-name').value;
    const description = document.getElementById('new-project-desc').value;
    
    try {
        const res = await fetch('/api/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        
        const newProj = await res.json();
        if (res.ok) {
            showToast(`Project "${newProj.name}" created!`, 'success');
            elements.formCreateProject.reset();
            closeModal(elements.modalCreateProject);
            
            // Reload sidebar list and select newly created project
            await loadProjects();
            selectProject(newProj.id);
        } else {
            showToast(newProj.error || 'Failed to create project', 'error');
        }
    } catch (err) {
        showToast('Network error', 'error');
    }
}

// Invite Member Submission
async function handleInviteMember(e) {
    e.preventDefault();
    if (!state.currentProject) return;
    const username = document.getElementById('invite-username').value;
    
    try {
        const res = await fetch(`/api/projects/${state.currentProject.id}/invite`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        
        const data = await res.json();
        if (res.ok) {
            showToast(`User "${username}" invited to team!`, 'success');
            elements.formInviteMember.reset();
            closeModal(elements.modalInviteMember);
            
            // Sync via sockets & reload
            if (state.socket) {
                state.socket.emit('member_added', { project_id: state.currentProject.id, username });
            }
            reloadCurrentProjectDetails();
        } else {
            showToast(data.error || 'Failed to invite user', 'error');
        }
    } catch (err) {
        showToast('Network error', 'error');
    }
}

// ================= USERS MODULE =================
async function loadUsersList() {
    try {
        const res = await fetch('/api/users');
        const data = await res.json();
        state.users = data;
    } catch (err) {
        console.error('Error fetching global users:', err);
    }
}

// ================= KANBAN BOARD & DRAG-AND-DROP =================
function renderKanbanBoard() {
    // Clear list boxes
    elements.tasksTodo.innerHTML = '';
    elements.tasksProgress.innerHTML = '';
    elements.tasksReview.innerHTML = '';
    elements.tasksDone.innerHTML = '';
    
    if (!state.currentProject || !state.currentProject.tasks) return;
    
    let todoCount = 0;
    let progressCount = 0;
    let reviewCount = 0;
    let doneCount = 0;
    
    // Sort tasks and append cards
    state.currentProject.tasks.forEach(task => {
        const card = createTaskCardDOM(task);
        
        if (task.status === 'Todo') {
            elements.tasksTodo.appendChild(card);
            todoCount++;
        } else if (task.status === 'In Progress') {
            elements.tasksProgress.appendChild(card);
            progressCount++;
        } else if (task.status === 'Review') {
            elements.tasksReview.appendChild(card);
            reviewCount++;
        } else if (task.status === 'Done') {
            elements.tasksDone.appendChild(card);
            doneCount++;
        }
    });
    
    // Update count labels
    elements.countTodo.textContent = todoCount;
    elements.countProgress.textContent = progressCount;
    elements.countReview.textContent = reviewCount;
    elements.countDone.textContent = doneCount;
}

function createTaskCardDOM(task) {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.setAttribute('draggable', 'true');
    card.setAttribute('data-id', task.id);
    
    // Find assignee details
    let assigneeHtml = '<div class="card-assignee card-unassigned"><i class="fa-regular fa-user"></i></div>';
    if (task.assignee_id && state.currentProject.members) {
        const assignee = state.currentProject.members.find(m => m.id === task.assignee_id);
        if (assignee) {
            assigneeHtml = `<div class="card-assignee" style="background-color: ${assignee.avatar_color}" title="Assigned to ${assignee.username}">${assignee.username.substring(0, 2).toUpperCase()}</div>`;
        }
    }
    
    // Priority Badge
    let priorityClass = 'badge-priority-low';
    if (task.priority === 'High') priorityClass = 'badge-priority-high';
    if (task.priority === 'Medium') priorityClass = 'badge-priority-medium';
    
    // Due Date Badge
    let dueHtml = '';
    if (task.due_date) {
        const todayStr = new Date().toISOString().split('T')[0];
        const isOverdue = task.due_date < todayStr && task.status !== 'Done';
        const dateObj = new Date(task.due_date);
        const formatStr = dateObj.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
        dueHtml = `<span class="badge badge-due ${isOverdue ? 'overdue' : ''}"><i class="fa-regular fa-clock"></i> ${formatStr}</span>`;
    }
    
    card.innerHTML = `
        <h4>${escapeHTML(task.title)}</h4>
        <p>${escapeHTML(task.description || 'No description')}</p>
        <div class="card-footer">
            <div class="card-meta-badges">
                <span class="badge ${priorityClass}">${task.priority}</span>
                ${dueHtml}
            </div>
            ${assigneeHtml}
        </div>
    `;
    
    // Drag and drop event listeners
    card.addEventListener('dragstart', (e) => {
        card.classList.add('dragging');
        e.dataTransfer.setData('text/plain', task.id);
    });
    
    card.addEventListener('dragend', () => {
        card.classList.remove('dragging');
    });
    
    // Click opens detail modal
    card.addEventListener('click', (e) => {
        // Prevent click trigger if interacting with child buttons/links
        if (e.target.closest('.card-assignee')) return;
        openTaskDetailsModal(task);
    });
    
    return card;
}

// Drag & Drop Handlers
function allowDrop(e) {
    e.preventDefault();
    const column = e.target.closest('.task-cards-container');
    if (column) {
        column.closest('.kanban-column').classList.add('drag-over');
    }
}

document.querySelectorAll('.task-cards-container').forEach(container => {
    container.addEventListener('dragover', allowDrop);
    container.addEventListener('dragleave', (e) => {
        const column = e.target.closest('.kanban-column');
        if (column) column.classList.remove('drag-over');
    });
});

async function drop(e, newStatus) {
    e.preventDefault();
    const column = e.target.closest('.kanban-column');
    if (column) column.classList.remove('drag-over');
    
    const taskIdStr = e.dataTransfer.getData('text/plain');
    if (!taskIdStr) return;
    
    const taskId = parseInt(taskIdStr);
    const task = state.currentProject.tasks.find(t => t.id === taskId);
    if (!task || task.status === newStatus) return;
    
    const oldStatus = task.status;
    
    // Optimistic UI updates
    task.status = newStatus;
    renderKanbanBoard();
    
    try {
        const res = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (res.ok) {
            // Broadcast the move using SocketIO room
            if (state.socket) {
                state.socket.emit('task_moved', { 
                    project_id: state.currentProject.id, 
                    task_id: taskId, 
                    status: newStatus 
                });
            }
            showToast(`Task moved to ${newStatus}`, 'success');
        } else {
            // Revert changes
            task.status = oldStatus;
            renderKanbanBoard();
            showToast('Failed to update task status on server', 'error');
        }
    } catch (err) {
        // Revert changes
        task.status = oldStatus;
        renderKanbanBoard();
        showToast('Network error while moving task', 'error');
    }
}

// Create Task Prompt
async function createNewTaskPrompt(status) {
    const title = prompt('Enter task name:');
    if (!title || !title.trim()) return;
    
    try {
        const res = await fetch(`/api/projects/${state.currentProject.id}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, status })
        });
        
        const newTask = await res.json();
        if (res.ok) {
            state.currentProject.tasks.push(newTask);
            renderKanbanBoard();
            
            // Broadcast using socket
            if (state.socket) {
                state.socket.emit('task_created', {
                    project_id: state.currentProject.id,
                    task: newTask
                });
            }
            showToast('Task created successfully', 'success');
        } else {
            showToast(newTask.error || 'Failed to create task', 'error');
        }
    } catch (err) {
        showToast('Network error', 'error');
    }
}

// ================= TASK DETAILS MODAL & COMMENTS =================
function openTaskDetailsModal(task) {
    state.activeTask = task;
    populateTaskDetailsModal(task);
    loadComments(task.id);
    openModal(elements.modalTaskDetails);
}

function populateTaskDetailsModal(task) {
    elements.taskDetailTitle.value = task.title;
    elements.taskDetailProjectName.textContent = state.currentProject.name;
    elements.taskDetailStatusBadge.textContent = task.status;
    
    // Status color class
    elements.taskDetailStatusBadge.className = 'badge';
    if (task.status === 'Todo') elements.taskDetailStatusBadge.classList.add('badge-due');
    if (task.status === 'In Progress') elements.taskDetailStatusBadge.classList.add('badge-priority-medium');
    if (task.status === 'Review') elements.taskDetailStatusBadge.classList.add('badge-priority-high');
    if (task.status === 'Done') elements.taskDetailStatusBadge.classList.add('badge-priority-low');
    
    // Options
    elements.taskDetailAssignee.value = task.assignee_id || '';
    elements.taskDetailPriority.value = task.priority || 'Medium';
    elements.taskDetailDue.value = task.due_date || '';
    elements.taskDetailDesc.value = task.description || '';
}

async function saveTaskDetails() {
    if (!state.activeTask) return;
    
    const title = elements.taskDetailTitle.value.trim();
    const assignee_id = elements.taskDetailAssignee.value ? parseInt(elements.taskDetailAssignee.value) : null;
    const priority = elements.taskDetailPriority.value;
    const due_date = elements.taskDetailDue.value || null;
    const description = elements.taskDetailDesc.value;
    
    if (!title) {
        showToast('Task title is required', 'error');
        return;
    }
    
    try {
        const res = await fetch(`/api/tasks/${state.activeTask.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, assignee_id, priority, due_date, description })
        });
        
        const updatedTask = await res.json();
        if (res.ok) {
            // Update local state
            const idx = state.currentProject.tasks.findIndex(t => t.id === state.activeTask.id);
            if (idx !== -1) {
                state.currentProject.tasks[idx] = updatedTask;
                renderKanbanBoard();
            }
            
            // Broadcast update
            if (state.socket) {
                state.socket.emit('task_updated', {
                    project_id: state.currentProject.id,
                    task: updatedTask
                });
            }
            
            closeModal(elements.modalTaskDetails);
            showToast('Task details saved', 'success');
        } else {
            showToast(updatedTask.error || 'Failed to update task details', 'error');
        }
    } catch (err) {
        showToast('Network error', 'error');
    }
}

async function deleteTask() {
    if (!state.activeTask) return;
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
        const res = await fetch(`/api/tasks/${state.activeTask.id}`, {
            method: 'DELETE'
        });
        
        if (res.ok) {
            const deletedId = state.activeTask.id;
            
            // Update local state
            state.currentProject.tasks = state.currentProject.tasks.filter(t => t.id !== deletedId);
            renderKanbanBoard();
            
            // Broadcast deletion
            if (state.socket) {
                state.socket.emit('task_deleted', {
                    project_id: state.currentProject.id,
                    task_id: deletedId
                });
            }
            
            closeModal(elements.modalTaskDetails);
            showToast('Task deleted successfully', 'warning');
            state.activeTask = null;
        } else {
            showToast('Failed to delete task', 'error');
        }
    } catch (err) {
        showToast('Network error', 'error');
    }
}

// Comments Logic
async function loadComments(taskId) {
    elements.commentsContainer.innerHTML = '<div class="loader-spinner"></div>';
    
    try {
        const res = await fetch(`/api/tasks/${taskId}/comments`);
        const comments = await res.json();
        
        elements.commentsContainer.innerHTML = '';
        if (comments.length === 0) {
            elements.commentsContainer.innerHTML = '<p class="text-center font-sm p-4 text-muted">No comments yet. Start the conversation!</p>';
            return;
        }
        
        comments.forEach(c => appendCommentToView(c));
    } catch (err) {
        console.error('Error loading comments:', err);
    }
}

function appendCommentToView(comment) {
    // Remove empty comments text placeholder if present
    const emptyPlaceholder = elements.commentsContainer.querySelector('.text-muted');
    if (emptyPlaceholder) emptyPlaceholder.remove();
    
    const div = document.createElement('div');
    div.className = 'comment-item';
    
    // Format timestamp nicely
    const dateObj = new Date(comment.created_at);
    const timeStr = dateObj.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) + ' ' + dateObj.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    
    div.innerHTML = `
        <div class="user-avatar" style="background-color: ${comment.avatar_color}" title="${comment.username}">
            ${comment.username.substring(0, 2).toUpperCase()}
        </div>
        <div class="comment-bubble">
            <div class="comment-author-name">${comment.username} <span class="comment-time">${timeStr}</span></div>
            <div class="comment-text">${escapeHTML(comment.content)}</div>
        </div>
    `;
    
    elements.commentsContainer.appendChild(div);
    elements.commentsContainer.scrollTop = elements.commentsContainer.scrollHeight;
}

async function postComment(e) {
    e.preventDefault();
    if (!state.activeTask) return;
    
    const content = elements.newCommentContent.value.trim();
    if (!content) return;
    
    try {
        const res = await fetch(`/api/tasks/${state.activeTask.id}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        
        const newComment = await res.json();
        if (res.ok) {
            elements.newCommentContent.value = '';
            appendCommentToView(newComment);
            
            // Broadcast using socket
            if (state.socket) {
                state.socket.emit('comment_added', {
                    project_id: state.currentProject.id,
                    comment: newComment
                });
            }
        } else {
            showToast(newComment.error || 'Failed to post comment', 'error');
        }
    } catch (err) {
        showToast('Network error', 'error');
    }
}

// ================= NOTIFICATIONS MODULE =================
async function loadNotifications() {
    if (!state.currentUser) return;
    
    try {
        const res = await fetch('/api/notifications');
        const notifications = await res.json();
        
        // Count unread
        const unreadCount = notifications.filter(n => !n.is_read).length;
        if (unreadCount > 0) {
            elements.notiBadge.textContent = unreadCount;
            elements.notiBadge.classList.remove('hide');
        } else {
            elements.notiBadge.classList.add('hide');
        }
        
        renderNotificationsPanelList(notifications);
    } catch (err) {
        console.error('Error fetching notifications:', err);
    }
}

function renderNotificationsPanelList(notifications) {
    elements.notificationsList.innerHTML = '';
    
    if (notifications.length === 0) {
        elements.notificationsList.innerHTML = '<div class="no-notifications">No notifications yet.</div>';
        return;
    }
    
    notifications.forEach(n => {
        const div = document.createElement('div');
        div.className = `noti-item ${n.is_read ? '' : 'unread'}`;
        
        const dateObj = new Date(n.created_at);
        const timeStr = dateObj.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) + ' ' + dateObj.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
        
        div.innerHTML = `
            <div>${n.message}</div>
            <span class="noti-time">${timeStr}</span>
        `;
        
        elements.notificationsList.appendChild(div);
    });
}

function toggleNotificationsPanel() {
    elements.notificationsPanel.classList.toggle('active');
}

async function markAllNotificationsRead() {
    try {
        const res = await fetch('/api/notifications/read', { method: 'POST' });
        if (res.ok) {
            loadNotifications();
            showToast('All notifications marked as read', 'info');
        }
    } catch (err) {
        console.error(err);
    }
}

// Helper to escape HTML tags to avoid XSS
function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}
