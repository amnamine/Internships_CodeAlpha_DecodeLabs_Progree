// ==========================================================================
// AETHER FRONTEND ENGINE (app.js)
// ==========================================================================

const STATE = {
  currentUser: null,
  activeTab: 'home',      // home, explore, profile
  activeFeedFilter: 'feed', // feed (following), explore (global)
  currentProfileUserId: null,
  postCommentsOpen: {}    // Map to trace which posts have comment sections open
};

// DOM Elements
const authScreen = document.getElementById('auth-screen');
const appContainer = document.getElementById('app-container');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const authError = document.getElementById('auth-error');
const toRegisterBtn = document.getElementById('to-register');
const toLoginBtn = document.getElementById('to-login');

const navItems = document.querySelectorAll('.nav-item');
const logoutBtn = document.getElementById('logout-btn');
const sidebarAvatar = document.getElementById('sidebar-avatar');
const sidebarDisplayName = document.getElementById('sidebar-display-name');
const sidebarUsername = document.getElementById('sidebar-username');

const feedToggle = document.getElementById('feed-toggle');
const currentViewTitle = document.getElementById('current-view-title');
const composerArea = document.getElementById('composer-area');
const createPostForm = document.getElementById('create-post-form');
const postContent = document.getElementById('post-content');
const toggleImageBtn = document.getElementById('toggle-image-btn');
const imageInputContainer = document.getElementById('image-input-container');
const postImageUrl = document.getElementById('post-image-url');
const composerAvatar = document.getElementById('composer-avatar');
const postsList = document.getElementById('posts-list');

const profileContainer = document.getElementById('profile-container');
const profileAvatar = document.getElementById('profile-avatar');
const profileDisplayName = document.getElementById('profile-display-name');
const profileUsername = document.getElementById('profile-username');
const profileBio = document.getElementById('profile-bio');
const profileFollowersCount = document.getElementById('profile-followers-count');
const profileFollowingCount = document.getElementById('profile-following-count');
const followProfileBtn = document.getElementById('follow-profile-btn');
const editProfileBtn = document.getElementById('edit-profile-btn');
const profilePostsList = document.getElementById('profile-posts-list');

const editProfileModal = document.getElementById('edit-profile-modal');
const editProfileForm = document.getElementById('edit-profile-form');
const editDisplayName = document.getElementById('edit-display-name');
const editAvatarUrl = document.getElementById('edit-avatar-url');
const editBio = document.getElementById('edit-bio');
const closeModalBtn = document.getElementById('close-modal-btn');
const cancelEditBtn = document.getElementById('cancel-edit-btn');

const suggestionsContainer = document.getElementById('suggestions-container');

// --- HELPER FUNCTIONS ---

function formatTime(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHr / 24);

  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  return `${diffDays}d ago`;
}

function showAuthError(msg) {
  authError.textContent = msg;
  authError.classList.remove('hidden');
}

function hideAuthError() {
  authError.classList.add('hidden');
  authError.textContent = '';
}

// --- API ACTIONS ---

async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      }
    });
    
    if (response.status === 401) {
      // Session expired or unauthorized
      STATE.currentUser = null;
      showView('auth');
      return null;
    }
    
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Something went wrong');
    }
    return data;
  } catch (err) {
    console.error(`API Error on ${url}:`, err);
    throw err;
  }
}

// Check current user session
async function checkSession() {
  try {
    const data = await apiRequest('/api/auth/me');
    if (data && data.user) {
      STATE.currentUser = data.user;
      setupUserSidebar();
      showView('app');
      loadFeed();
      loadSuggestions();
    } else {
      showView('auth');
    }
  } catch (err) {
    showView('auth');
  }
}

// Setup User Sidebar
function setupUserSidebar() {
  sidebarAvatar.src = STATE.currentUser.avatar_url || 'https://api.dicebear.com/7.x/bottts/svg?seed=default';
  composerAvatar.src = STATE.currentUser.avatar_url || 'https://api.dicebear.com/7.x/bottts/svg?seed=default';
  sidebarDisplayName.textContent = STATE.currentUser.display_name;
  sidebarUsername.textContent = `@${STATE.currentUser.username}`;
}

// Handle switching between Auth forms and main App container
function showView(view) {
  if (view === 'auth') {
    authScreen.classList.remove('hidden');
    appContainer.classList.add('hidden');
  } else {
    authScreen.classList.add('hidden');
    appContainer.classList.remove('hidden');
  }
}

// --- RENDER POSTS & COMMENTS ---

async function renderPosts(posts, container) {
  container.innerHTML = '';
  
  if (posts.length === 0) {
    container.innerHTML = `
      <div class="post-card" style="justify-content: center; color: var(--text-muted);">
        No posts to display in the ether.
      </div>
    `;
    return;
  }

  posts.forEach(post => {
    const isOwner = STATE.currentUser && post.user_id === STATE.currentUser.id;
    const likedClass = post.user_liked ? 'liked' : '';
    const commentsOpen = STATE.postCommentsOpen[post.id];

    const postElement = document.createElement('div');
    postElement.className = 'post-card';
    postElement.dataset.id = post.id;
    
    postElement.innerHTML = `
      <img src="${post.avatar_url || 'https://api.dicebear.com/7.x/bottts/svg?seed=' + post.username}" alt="${post.display_name}" class="avatar avatar-md post-author-avatar" style="cursor: pointer;">
      <div class="post-main">
        <div class="post-header">
          <div class="post-author-info">
            <span class="post-author-name" data-userid="${post.user_id}">${post.display_name}</span>
            <span class="post-author-handle">@${post.username}</span>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="post-time">${formatTime(post.created_at)}</span>
            ${isOwner ? `<button class="btn-icon btn-delete-post" title="Delete Post" style="color: rgba(239, 68, 68, 0.7);"><svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg></button>` : ''}
          </div>
        </div>
        <p class="post-content-text">${escapeHTML(post.content)}</p>
        ${post.image_url ? `<img src="${post.image_url}" class="post-image" alt="Post Image Attachment" onerror="this.style.display='none'">` : ''}
        
        <div class="post-actions">
          <button class="post-action-btn btn-like-post ${likedClass}">
            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>
            <span class="likes-count">${post.likes_count}</span>
          </button>
          <button class="post-action-btn btn-comment-toggle">
            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
            <span class="comments-count">${post.comments_count}</span>
          </button>
        </div>

        <!-- Comments Drawer -->
        <div class="comments-section ${commentsOpen ? '' : 'hidden'}">
          <div class="comments-list"></div>
          <form class="comment-composer">
            <input type="text" placeholder="Write a comment..." required maxlength="180">
            <button type="submit" class="btn btn-primary btn-sm">Reply</button>
          </form>
        </div>

      </div>
    `;

    // Click on profile avatar or profile name
    postElement.querySelector('.post-author-avatar').addEventListener('click', () => viewUserProfile(post.user_id));
    postElement.querySelector('.post-author-name').addEventListener('click', () => viewUserProfile(post.user_id));

    // Like Action
    const likeBtn = postElement.querySelector('.btn-like-post');
    likeBtn.addEventListener('click', () => toggleLike(post.id, likeBtn));

    // Comments Toggle Drawer
    const commentBtn = postElement.querySelector('.btn-comment-toggle');
    const commentSection = postElement.querySelector('.comments-section');
    commentBtn.addEventListener('click', () => toggleComments(post.id, commentSection));

    // Delete post action
    if (isOwner) {
      postElement.querySelector('.btn-delete-post').addEventListener('click', () => deletePost(post.id));
    }

    // Comment submission
    const commentForm = postElement.querySelector('.comment-composer');
    commentForm.addEventListener('submit', (e) => submitComment(e, post.id, commentSection.querySelector('.comments-list'), commentBtn.querySelector('.comments-count')));

    // If comments already open, render them immediately
    if (commentsOpen) {
      loadComments(post.id, commentSection.querySelector('.comments-list'));
    }

    container.appendChild(postElement);
  });
}

function escapeHTML(str) {
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

// --- EVENT ACTIONS (LIKE, COMMENT, DELETE) ---

async function toggleLike(postId, button) {
  try {
    const data = await apiRequest(`/api/posts/${postId}/like`, { method: 'POST' });
    if (data) {
      const countSpan = button.querySelector('.likes-count');
      countSpan.textContent = data.likesCount;
      if (data.liked) {
        button.classList.add('liked');
      } else {
        button.classList.remove('liked');
      }
    }
  } catch (err) {
    alert(err.message);
  }
}

async function toggleComments(postId, commentSection) {
  if (commentSection.classList.contains('hidden')) {
    commentSection.classList.remove('hidden');
    STATE.postCommentsOpen[postId] = true;
    loadComments(postId, commentSection.querySelector('.comments-list'));
  } else {
    commentSection.classList.add('hidden');
    STATE.postCommentsOpen[postId] = false;
  }
}

async function loadComments(postId, container) {
  container.innerHTML = '<div style="font-size:0.8rem; color:var(--text-muted);">Loading comments...</div>';
  try {
    const comments = await apiRequest(`/api/posts/${postId}/comments`);
    container.innerHTML = '';
    if (comments.length === 0) {
      container.innerHTML = '<div style="font-size:0.8rem; color:var(--text-muted); padding: 5px 0;">No comments yet. Be the first to reply!</div>';
      return;
    }
    comments.forEach(comment => {
      const commentCard = document.createElement('div');
      commentCard.className = 'comment-card';
      commentCard.innerHTML = `
        <img src="${comment.avatar_url || 'https://api.dicebear.com/7.x/bottts/svg?seed=' + comment.username}" alt="${comment.display_name}" class="avatar avatar-sm" style="width:32px; height:32px;">
        <div class="comment-main">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="comment-author-name" style="cursor:pointer;">${comment.display_name} <span style="font-weight:400; color:var(--text-muted); font-size:0.8rem;">@${comment.username}</span></span>
            <span class="comment-time">${formatTime(comment.created_at)}</span>
          </div>
          <p class="comment-content">${escapeHTML(comment.content)}</p>
        </div>
      `;
      // Click user inside comments
      commentCard.querySelector('.comment-author-name').addEventListener('click', () => viewUserProfile(comment.user_id));
      container.appendChild(commentCard);
    });
  } catch (err) {
    container.innerHTML = '<div style="color:#ef4444; font-size:0.8rem;">Error loading comments</div>';
  }
}

async function submitComment(e, postId, container, countSpan) {
  e.preventDefault();
  const input = e.target.querySelector('input');
  const content = input.value.trim();
  if (!content) return;

  try {
    const newComment = await apiRequest(`/api/posts/${postId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content })
    });
    if (newComment) {
      input.value = '';
      loadComments(postId, container);
      countSpan.textContent = parseInt(countSpan.textContent) + 1;
    }
  } catch (err) {
    alert(err.message);
  }
}

async function deletePost(postId) {
  if (!confirm('Are you sure you want to delete this post?')) return;
  try {
    const data = await apiRequest(`/api/posts/${postId}`, { method: 'DELETE' });
    if (data) {
      // Reload current tab
      if (STATE.activeTab === 'home') {
        loadFeed();
      } else if (STATE.activeTab === 'profile') {
        viewUserProfile(STATE.currentProfileUserId);
      }
    }
  } catch (err) {
    alert(err.message);
  }
}

// --- FEED ROUTING / VIEW NAVIGATION ---

async function loadFeed() {
  postsList.innerHTML = '<div style="text-align:center; padding:40px; color:var(--text-muted);">Tuning into the ether...</div>';
  try {
    const filter = STATE.activeTab === 'explore' ? 'explore' : STATE.activeFeedFilter;
    const posts = await apiRequest(`/api/posts?filter=${filter}`);
    if (posts) {
      renderPosts(posts, postsList);
    }
  } catch (err) {
    postsList.innerHTML = '<div style="text-align:center; padding:40px; color:#ef4444;">Failed to load posts</div>';
  }
}

async function loadSuggestions() {
  suggestionsContainer.innerHTML = '<div style="font-size:0.85rem; color:var(--text-muted);">Searching...</div>';
  try {
    const suggestions = await apiRequest('/api/users');
    suggestionsContainer.innerHTML = '';
    if (!suggestions || suggestions.length === 0) {
      suggestionsContainer.innerHTML = '<div style="font-size:0.85rem; color:var(--text-muted);">No suggestions available.</div>';
      return;
    }
    suggestions.forEach(user => {
      const item = document.createElement('div');
      item.className = 'suggestion-item';
      item.innerHTML = `
        <div class="suggestion-info">
          <img src="${user.avatar_url || 'https://api.dicebear.com/7.x/bottts/svg?seed=' + user.username}" alt="${user.display_name}" class="avatar avatar-sm" style="width:36px; height:36px;">
          <div style="min-width:0;">
            <span class="suggestion-name">${user.display_name}</span>
            <span class="suggestion-handle">@${user.username}</span>
          </div>
        </div>
        <button class="btn btn-outline btn-sm follow-suggest-btn">Follow</button>
      `;
      // Click Suggestion Avatar/Name
      item.querySelector('.suggestion-info').addEventListener('click', () => viewUserProfile(user.id));
      
      // Follow Suggestion Action
      const btn = item.querySelector('.follow-suggest-btn');
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        try {
          const data = await apiRequest(`/api/users/${user.id}/follow`, { method: 'POST' });
          if (data) {
            loadSuggestions();
            // Refresh feed if active
            if (STATE.activeTab === 'home') loadFeed();
          }
        } catch (err) {
          alert(err.message);
        }
      });
      suggestionsContainer.appendChild(item);
    });
  } catch (err) {
    suggestionsContainer.innerHTML = '<div style="font-size:0.85rem; color:#ef4444;">Error loading suggestions</div>';
  }
}

async function viewUserProfile(userId) {
  STATE.activeTab = 'profile';
  STATE.currentProfileUserId = userId;
  
  // Update nav highlight
  navItems.forEach(item => {
    if (item.dataset.tab === 'profile' && userId === STATE.currentUser.id) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Hide general feed UI, show Profile UI
  composerArea.classList.add('hidden');
  feedToggle.classList.add('hidden');
  postsList.classList.add('hidden');
  profileContainer.classList.remove('hidden');

  currentViewTitle.textContent = 'User Profile';
  profilePostsList.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-muted);">Fetching posts...</div>';

  try {
    const profileData = await apiRequest(`/api/users/${userId}`);
    if (profileData) {
      const { user, followerCount, followingCount, isFollowing } = profileData;
      
      profileAvatar.src = user.avatar_url || 'https://api.dicebear.com/7.x/bottts/svg?seed=' + user.username;
      profileDisplayName.textContent = user.display_name;
      profileUsername.textContent = `@${user.username}`;
      profileBio.textContent = user.bio || 'This user has no bio yet.';
      profileFollowersCount.innerHTML = `<strong>${followerCount}</strong> Followers`;
      profileFollowingCount.innerHTML = `<strong>${followingCount}</strong> Following`;

      // Show Edit button for owner, follow button for others
      if (STATE.currentUser && STATE.currentUser.id === user.id) {
        followProfileBtn.classList.add('hidden');
        editProfileBtn.classList.remove('hidden');
      } else {
        editProfileBtn.classList.add('hidden');
        followProfileBtn.classList.remove('hidden');
        followProfileBtn.textContent = isFollowing ? 'Unfollow' : 'Follow';
        followProfileBtn.className = isFollowing ? 'btn btn-secondary' : 'btn btn-outline';
      }

      // Load Profile Posts
      const posts = await apiRequest(`/api/posts?filter=user&userId=${userId}`);
      if (posts) {
        renderPosts(posts, profilePostsList);
      }
    }
  } catch (err) {
    profilePostsList.innerHTML = '<div style="text-align:center; padding:20px; color:#ef4444;">Failed to load profile</div>';
  }
}

// --- EVENT LISTENERS & FORM SUBMISSIONS ---

// Form toggles
toRegisterBtn.addEventListener('click', (e) => {
  e.preventDefault();
  loginForm.classList.add('hidden');
  registerForm.classList.remove('hidden');
  hideAuthError();
});

toLoginBtn.addEventListener('click', (e) => {
  e.preventDefault();
  registerForm.classList.add('hidden');
  loginForm.classList.remove('hidden');
  hideAuthError();
});

// Login Form Submit
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideAuthError();
  const username = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;

  try {
    const data = await apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    
    if (data && data.user) {
      STATE.currentUser = data.user;
      setupUserSidebar();
      showView('app');
      // Reset forms
      loginForm.reset();
      // Set to home feed
      switchTab('home');
      loadSuggestions();
    }
  } catch (err) {
    showAuthError(err.message);
  }
});

// Register Form Submit
registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideAuthError();
  const display_name = document.getElementById('register-display-name').value;
  const username = document.getElementById('register-username').value;
  const password = document.getElementById('register-password').value;

  try {
    const data = await apiRequest('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ display_name, username, password })
    });
    
    if (data) {
      registerForm.reset();
      // Directly check session to auto-login
      checkSession();
    }
  } catch (err) {
    showAuthError(err.message);
  }
});

// Logout Submit
logoutBtn.addEventListener('click', async () => {
  try {
    const data = await apiRequest('/api/auth/logout', { method: 'POST' });
    if (data) {
      STATE.currentUser = null;
      showView('auth');
    }
  } catch (err) {
    console.error('Logout error:', err);
  }
});

// Nav items tab clicking
navItems.forEach(item => {
  item.addEventListener('click', () => {
    if (item.classList.contains('btn-compose-trigger')) return; // handled separately or focus content
    const tab = item.dataset.tab;
    switchTab(tab);
  });
});

function switchTab(tab) {
  STATE.activeTab = tab;
  
  navItems.forEach(nav => {
    if (nav.dataset.tab === tab) {
      nav.classList.add('active');
    } else {
      nav.classList.remove('active');
    }
  });

  profileContainer.classList.add('hidden');
  postsList.classList.remove('hidden');

  if (tab === 'home') {
    composerArea.classList.remove('hidden');
    feedToggle.classList.remove('hidden');
    currentViewTitle.textContent = 'Home Feed';
    loadFeed();
  } else if (tab === 'explore') {
    composerArea.classList.add('hidden');
    feedToggle.classList.add('hidden');
    currentViewTitle.textContent = 'Explore';
    loadFeed();
  } else if (tab === 'profile') {
    if (STATE.currentUser) {
      viewUserProfile(STATE.currentUser.id);
    }
  }
}

// Feed selector (Following vs Global)
const toggleButtons = document.querySelectorAll('.btn-toggle');
toggleButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    toggleButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    STATE.activeFeedFilter = btn.dataset.feed;
    loadFeed();
  });
});

// Composer Image URL toggle input field
toggleImageBtn.addEventListener('click', () => {
  imageInputContainer.classList.toggle('hidden');
  postImageUrl.value = '';
});

// Submit New Post
createPostForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const content = postContent.value.trim();
  const image_url = postImageUrl.value.trim();

  if (!content) return;

  try {
    const data = await apiRequest('/api/posts', {
      method: 'POST',
      body: JSON.stringify({ content, image_url })
    });
    if (data) {
      postContent.value = '';
      postImageUrl.value = '';
      imageInputContainer.classList.add('hidden');
      loadFeed();
    }
  } catch (err) {
    alert(err.message);
  }
});

// Quick compose floating button action
document.getElementById('compose-post-btn').addEventListener('click', () => {
  switchTab('home');
  postContent.focus();
});

// Follow/Unfollow user profile page
followProfileBtn.addEventListener('click', async () => {
  const targetId = STATE.currentProfileUserId;
  if (!targetId) return;

  try {
    const data = await apiRequest(`/api/users/${targetId}/follow`, { method: 'POST' });
    if (data) {
      viewUserProfile(targetId);
      loadSuggestions();
    }
  } catch (err) {
    alert(err.message);
  }
});

// Edit profile profile modal popup
editProfileBtn.addEventListener('click', () => {
  if (!STATE.currentUser) return;
  editDisplayName.value = STATE.currentUser.display_name;
  editAvatarUrl.value = STATE.currentUser.avatar_url || '';
  editBio.value = STATE.currentUser.bio || '';
  editProfileModal.classList.remove('hidden');
});

// Close Profile Modal actions
const closeModal = () => editProfileModal.classList.add('hidden');
closeModalBtn.addEventListener('click', closeModal);
cancelEditBtn.addEventListener('click', closeModal);
editProfileModal.addEventListener('click', (e) => {
  if (e.target === editProfileModal) closeModal();
});

// Submit edit profile edits
editProfileForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const display_name = editDisplayName.value.trim();
  const avatar_url = editAvatarUrl.value.trim();
  const bio = editBio.value.trim();

  if (!display_name) return;

  try {
    const data = await apiRequest('/api/users/profile', {
      method: 'PUT',
      body: JSON.stringify({ display_name, avatar_url, bio })
    });
    if (data) {
      closeModal();
      // Update local state
      STATE.currentUser.display_name = display_name;
      STATE.currentUser.avatar_url = avatar_url;
      STATE.currentUser.bio = bio;
      setupUserSidebar();
      viewUserProfile(STATE.currentUser.id);
    }
  } catch (err) {
    alert(err.message);
  }
});

// --- MAIN RUNTIME INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
  checkSession();
});
