/**
 * TASK 3 - INTERACTIVE WEB ELEMENTS
 * Core JavaScript Application Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  
  // ==========================================
  // 1. STATE & GLOBAL COUNTERS
  // ==========================================
  const state = {
    interactionCount: 0,
    soundEnabled: true,
    activeTheme: localStorage.getItem('task3_theme') || 'dark',
    filterCategory: 'all',
    searchQuery: '',
    sortMode: 'name-asc',
    viewMode: 'grid',
    likedCards: new Set(),
    tasks: [
      { id: 1, text: 'Explore DOM manipulation tools', priority: 'high', completed: true },
      { id: 2, text: 'Customize CSS properties in live sandbox', priority: 'medium', completed: false },
      { id: 3, text: 'Complete JavaScript quiz evaluation', priority: 'high', completed: false },
      { id: 4, text: 'Trigger custom toast notifications', priority: 'low', completed: false }
    ],
    taskFilter: 'all',
    quizIndex: 0,
    quizScore: 0,
    quizAnswered: false,
    cards: [
      { id: 101, title: 'DOM Event Listeners', category: 'frontend', icon: 'fa-solid fa-bolt', desc: 'Listen to mouse clicks, keystrokes, and dynamic resize events.', likes: 42, tags: ['JavaScript', 'DOM', 'Events'] },
      { id: 102, title: 'CSS Glassmorphism', category: 'uiux', icon: 'fa-solid fa-wand-magic-sparkles', desc: 'Backdrop blur filters with translucent borders and soft ambient glow.', likes: 38, tags: ['CSS3', 'Design', 'Glass'] },
      { id: 103, title: 'Web Audio Synthesizer', category: 'frontend', icon: 'fa-solid fa-wave-square', desc: 'Real-time sound generation without external media assets using AudioContext.', likes: 29, tags: ['Web Audio API', 'JS'] },
      { id: 104, title: 'REST & GraphQL APIs', category: 'backend', icon: 'fa-solid fa-server', desc: 'Asynchronous fetch pipelines and dynamic state synchronizations.', likes: 55, tags: ['Backend', 'Fetch', 'Async'] },
      { id: 105, title: 'Vite & Webpack Bundlers', category: 'tools', icon: 'fa-solid fa-gears', desc: 'Modern module bundling with hot module replacement (HMR).', likes: 21, tags: ['Build Tools', 'Tooling'] },
      { id: 106, title: 'CSS Grid & Flexbox', category: 'uiux', icon: 'fa-solid fa-table-cells', desc: 'Fluid responsive layout systems without hardcoded dimensions.', likes: 49, tags: ['CSS Grid', 'Flexbox'] },
      { id: 107, title: 'Interactive Canvas Particles', category: 'frontend', icon: 'fa-solid fa-circle-nodes', desc: 'GPU-accelerated HTML5 2D graphics rendering with velocity physics.', likes: 64, tags: ['Canvas 2D', 'Animations'] },
      { id: 108, title: 'Node.js Microservices', category: 'backend', icon: 'fa-brands fa-node-js', desc: 'Scalable event-driven non-blocking server architecture.', likes: 33, tags: ['Node.js', 'Backend', 'Express'] }
    ],
    quizQuestions: [
      {
        question: "What does DOM stand for in JavaScript web development?",
        options: ["Document Object Model", "Dynamic Operations Module", "Direct Output Mechanism", "Data Object Manager"],
        correct: 0,
        explanation: "DOM stands for Document Object Model, which represents HTML pages as a tree structure of nodes."
      },
      {
        question: "Which method is used to attach an event handler to a DOM element?",
        options: ["element.attachEvent()", "element.addEventListener()", "element.bindEvent()", "element.on()"],
        correct: 1,
        explanation: "addEventListener() registers a single event listener on a target element."
      },
      {
        question: "How do you select an element with ID 'target' in modern JavaScript?",
        options: ["document.select('#target')", "document.getElementById('target')", "document.query('target')", "Both B & document.querySelector('#target')"],
        correct: 3,
        explanation: "Both getElementById('target') and querySelector('#target') return the target DOM element."
      },
      {
        question: "Which CSS property creates the semi-transparent frosted glass backdrop effect?",
        options: ["background-filter", "backdrop-filter: blur()", "filter: frosted()", "opacity-blur"],
        correct: 1,
        explanation: "backdrop-filter: blur(16px) applies graphical blur effects to the area behind an element."
      },
      {
        question: "What happens when document.createElement('div') is invoked?",
        options: ["A div is immediately drawn on screen", "A div is created in memory but not attached to DOM tree", "It deletes all existing divs", "It triggers a page reload"],
        correct: 1,
        explanation: "It creates the HTML element in memory. You must call appendChild() or append() to attach it to the DOM."
      }
    ],
    gallery: [
      { id: 1, title: 'Cyber Pulse Interface', category: 'UI/UX Design', icon: 'fa-solid fa-microchip', desc: 'Futuristic glassmorphic dashboard interface built with micro-interactions.', likes: 120, tags: ['UI/UX', 'Glassmorphism', 'Neon'] },
      { id: 2, title: 'Web Sound Engine', category: 'Audio Web', icon: 'fa-solid fa-music', desc: 'Synthesized sound effects generated purely via Web Audio API oscillators.', likes: 88, tags: ['Audio', 'JavaScript', 'Web Audio'] },
      { id: 3, title: 'Dynamic Data Grid', category: 'DOM Engine', icon: 'fa-solid fa-network-wired', desc: 'Real-time filtering, sorting, and responsive layout toggling engine.', likes: 145, tags: ['DOM', 'Filtering', 'Grid'] },
      { id: 4, title: 'Particle Physics Stage', category: 'HTML5 Canvas', icon: 'fa-solid fa-sparkles', desc: 'Interactive particle canvas canvas physics with mouse cursor attraction.', likes: 210, tags: ['Canvas', 'Particles', 'Interactive'] }
    ]
  };

  // Track user click interactions globally
  document.addEventListener('click', (e) => {
    // Only increment when clicking interactive elements
    if (e.target.closest('button, a, input, select, .tech-card, .gallery-card, .task-item')) {
      state.interactionCount++;
      updateCounterDisplay();
      playAudioBeep(600, 0.03); // Subtle click feedback sound
    }
  });

  function updateCounterDisplay() {
    const el = document.getElementById('counterInteractions');
    if (el) el.textContent = state.interactionCount;
  }

  // ==========================================
  // 2. WEB AUDIO FEEDBACK SYNTHESIZER
  // ==========================================
  let audioCtx = null;
  function getAudioContext() {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    return audioCtx;
  }

  function playAudioBeep(freq = 440, duration = 0.05, type = 'sine') {
    if (!state.soundEnabled) return;
    try {
      const ctx = getAudioContext();
      if (ctx.state === 'suspended') {
        ctx.resume();
      }
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      
      osc.type = type;
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch (err) {
      // Ignore audio context errors gracefully
    }
  }

  // Sound Toggle Button
  const soundBtn = document.getElementById('soundToggleBtn');
  soundBtn?.addEventListener('click', () => {
    state.soundEnabled = !state.soundEnabled;
    const soundOnIcon = soundBtn.querySelector('.sound-on');
    const soundOffIcon = soundBtn.querySelector('.sound-off');
    
    if (state.soundEnabled) {
      soundOnIcon.classList.remove('hidden');
      soundOffIcon.classList.add('hidden');
      showToast('Sound Enabled', 'Audio feedback synthesizer activated', 'info');
      playAudioBeep(880, 0.1);
    } else {
      soundOnIcon.classList.add('hidden');
      soundOffIcon.classList.remove('hidden');
      showToast('Sound Muted', 'Audio feedback silent mode', 'info');
    }
  });

  // ==========================================
  // 3. THEME TOGGLE & LIVE CLOCK
  // ==========================================
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('task3_theme', theme);
    state.activeTheme = theme;
  }
  
  applyTheme(state.activeTheme);

  themeToggleBtn?.addEventListener('click', () => {
    const nextTheme = state.activeTheme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
    playAudioBeep(700, 0.08, 'triangle');
    showToast('Theme Changed', `Switched to ${nextTheme.toUpperCase()} theme mode`, 'info');
  });

  // Live Clock
  const clockText = document.getElementById('clockText');
  function updateClock() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const mins = String(now.getMinutes()).padStart(2, '0');
    const secs = String(now.getSeconds()).padStart(2, '0');
    if (clockText) clockText.textContent = `${hours}:${mins}:${secs}`;
  }
  setInterval(updateClock, 1000);
  updateClock();

  // Mobile Menu Toggle
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const navMenu = document.getElementById('navMenu');
  mobileMenuBtn?.addEventListener('click', () => {
    navMenu.classList.toggle('mobile-open');
  });

  // Smooth scroll active nav highlights
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      navLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');
      navMenu.classList.remove('mobile-open');
    });
  });

  // ==========================================
  // 4. INTERACTIVE CANVAS BACKGROUND
  // ==========================================
  const canvas = document.getElementById('particleCanvas');
  const ctx = canvas?.getContext('2d');
  let particles = [];
  let mouse = { x: null, y: null, radius: 140 };

  function initCanvas() {
    if (!canvas || !ctx) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    particles = [];
    const count = Math.floor((canvas.width * canvas.height) / 18000);
    
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 2 + 1,
        vx: (Math.random() - 0.5) * 0.8,
        vy: (Math.random() - 0.5) * 0.8,
        color: state.activeTheme === 'dark' ? 'rgba(99, 102, 241, 0.4)' : 'rgba(79, 70, 229, 0.25)'
      });
    }
  }

  window.addEventListener('resize', initCanvas);
  window.addEventListener('mousemove', (e) => {
    mouse.x = e.x;
    mouse.y = e.y;
  });

  function animateParticles() {
    if (!canvas || !ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < particles.length; i++) {
      let p = particles[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

      // Mouse attraction / interaction
      if (mouse.x && mouse.y) {
        let dx = mouse.x - p.x;
        let dy = mouse.y - p.y;
        let dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < mouse.radius) {
          p.x -= (dx / dist) * 1.5;
          p.y -= (dy / dist) * 1.5;
        }
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = state.activeTheme === 'dark' ? 'rgba(99, 102, 241, 0.5)' : 'rgba(79, 70, 229, 0.3)';
      ctx.fill();

      // Connect nearby particles
      for (let j = i + 1; j < particles.length; j++) {
        let p2 = particles[j];
        let dx = p.x - p2.x;
        let dy = p.y - p2.y;
        let dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 100) {
          ctx.beginPath();
          ctx.strokeStyle = state.activeTheme === 'dark' 
            ? `rgba(99, 102, 241, ${0.2 * (1 - dist / 100)})`
            : `rgba(79, 70, 229, ${0.15 * (1 - dist / 100)})`;
          ctx.lineWidth = 0.6;
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(animateParticles);
  }

  initCanvas();
  animateParticles();

  // ==========================================
  // 5. CARDS & DYNAMIC DATA EXPLORER
  // ==========================================
  const cardsGrid = document.getElementById('cardsGrid');
  const cardsEmptyState = document.getElementById('cardsEmptyState');
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const filterPills = document.getElementById('filterPills');
  const sortSelect = document.getElementById('sortSelect');
  const viewGridBtn = document.getElementById('viewGridBtn');
  const viewListBtn = document.getElementById('viewListBtn');
  const counterItems = document.getElementById('counterItems');

  function renderCards() {
    if (!cardsGrid) return;

    // Filter Logic
    let filtered = state.cards.filter(c => {
      const matchFilter = state.filterCategory === 'all' || c.category === state.filterCategory;
      const matchSearch = c.title.toLowerCase().includes(state.searchQuery.toLowerCase()) ||
                          c.desc.toLowerCase().includes(state.searchQuery.toLowerCase()) ||
                          c.tags.some(t => t.toLowerCase().includes(state.searchQuery.toLowerCase()));
      return matchFilter && matchSearch;
    });

    // Sort Logic
    filtered.sort((a, b) => {
      if (state.sortMode === 'name-asc') return a.title.localeCompare(b.title);
      if (state.sortMode === 'name-desc') return b.title.localeCompare(a.title);
      if (state.sortMode === 'likes-desc') return b.likes - a.likes;
      if (state.sortMode === 'likes-asc') return a.likes - b.likes;
      return 0;
    });

    // Update Counter
    if (counterItems) counterItems.textContent = filtered.length;

    // Handle Empty State
    if (filtered.length === 0) {
      cardsGrid.classList.add('hidden');
      cardsEmptyState?.classList.remove('hidden');
      return;
    } else {
      cardsGrid.classList.remove('hidden');
      cardsEmptyState?.classList.add('hidden');
    }

    cardsGrid.innerHTML = '';

    filtered.forEach(card => {
      const cardEl = document.createElement('div');
      cardEl.className = 'tech-card';
      cardEl.dataset.id = card.id;

      const isLiked = state.likedCards.has(card.id);

      cardEl.innerHTML = `
        <div class="card-top">
          <div class="card-icon-wrapper"><i class="${card.icon}"></i></div>
          <span class="card-category-badge">${card.category}</span>
        </div>
        <h3 class="card-title">${escapeHTML(card.title)}</h3>
        <p class="card-description">${escapeHTML(card.desc)}</p>
        <div class="card-bottom">
          <button class="like-btn ${isLiked ? 'liked' : ''}" data-id="${card.id}">
            <i class="${isLiked ? 'fa-solid' : 'fa-regular'} fa-heart"></i>
            <span class="like-count">${card.likes}</span> Likes
          </button>
          <button class="delete-card-btn" data-id="${card.id}" title="Remove card from DOM">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
      `;

      cardsGrid.appendChild(cardEl);
    });

    attachCardEventListeners();
  }

  function attachCardEventListeners() {
    // Like button handler
    document.querySelectorAll('.like-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(btn.dataset.id);
        const card = state.cards.find(c => c.id === id);
        if (!card) return;

        if (state.likedCards.has(id)) {
          state.likedCards.delete(id);
          card.likes--;
        } else {
          state.likedCards.add(id);
          card.likes++;
          playAudioBeep(900, 0.12, 'sine');
        }

        renderCards();
      });
    });

    // Delete card handler
    document.querySelectorAll('.delete-card-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(btn.dataset.id);
        const cardEl = btn.closest('.tech-card');

        cardEl.style.transform = 'scale(0.8) translateY(20px)';
        cardEl.style.opacity = '0';

        setTimeout(() => {
          state.cards = state.cards.filter(c => c.id !== id);
          renderCards();
          playAudioBeep(300, 0.15, 'sawtooth');
          showToast('Card Removed', 'Element dynamically removed from DOM tree', 'warning');
        }, 300);
      });
    });
  }

  // Filter Pills Event Listeners
  filterPills?.addEventListener('click', (e) => {
    const pill = e.target.closest('.pill-btn');
    if (!pill) return;

    filterPills.querySelectorAll('.pill-btn').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
    state.filterCategory = pill.dataset.filter;
    renderCards();
  });

  // Search Input Listener
  searchInput?.addEventListener('input', (e) => {
    state.searchQuery = e.target.value;
    if (state.searchQuery.length > 0) {
      clearSearchBtn?.classList.remove('hidden');
    } else {
      clearSearchBtn?.classList.add('hidden');
    }
    renderCards();
  });

  clearSearchBtn?.addEventListener('click', () => {
    searchInput.value = '';
    state.searchQuery = '';
    clearSearchBtn.classList.add('hidden');
    renderCards();
  });

  // Sort Select Listener
  sortSelect?.addEventListener('change', (e) => {
    state.sortMode = e.target.value;
    renderCards();
  });

  // View Switcher Listener
  viewGridBtn?.addEventListener('click', () => {
    viewGridBtn.classList.add('active');
    viewListBtn.classList.remove('active');
    cardsGrid.className = 'cards-grid grid-layout';
  });

  viewListBtn?.addEventListener('click', () => {
    viewListBtn.classList.add('active');
    viewGridBtn.classList.remove('active');
    cardsGrid.className = 'cards-grid list-layout';
  });

  // Add Card Modal
  const addCardModal = document.getElementById('addCardModal');
  const openAddModalBtn = document.getElementById('openAddModalBtn');
  const closeAddModalBtn = document.getElementById('closeAddModalBtn');
  const cancelAddModalBtn = document.getElementById('cancelAddModalBtn');
  const addCardForm = document.getElementById('addCardForm');

  function openModal(modal) { modal?.classList.remove('hidden'); }
  function closeModal(modal) { modal?.classList.add('hidden'); }

  openAddModalBtn?.addEventListener('click', () => openModal(addCardModal));
  closeAddModalBtn?.addEventListener('click', () => closeModal(addCardModal));
  cancelAddModalBtn?.addEventListener('click', () => closeModal(addCardModal));

  addCardForm?.addEventListener('submit', (e) => {
    e.preventDefault();
    const title = document.getElementById('newCardTitle').value.trim();
    const category = document.getElementById('newCardCategory').value;
    const icon = document.getElementById('newCardIcon').value.trim() || 'fa-solid fa-code';
    const desc = document.getElementById('newCardDesc').value.trim();

    if (!title || !desc) return;

    const newCard = {
      id: Date.now(),
      title,
      category,
      icon,
      desc,
      likes: 0,
      tags: ['Custom', category]
    };

    state.cards.unshift(newCard);
    renderCards();
    addCardForm.reset();
    closeModal(addCardModal);
    playAudioBeep(1000, 0.15, 'sine');
    showToast('New Card Injected!', `Successfully created "${title}" element`, 'success');
  });

  document.getElementById('resetFiltersBtn')?.addEventListener('click', () => {
    state.filterCategory = 'all';
    state.searchQuery = '';
    if (searchInput) searchInput.value = '';
    filterPills?.querySelectorAll('.pill-btn').forEach(p => p.classList.remove('active'));
    filterPills?.querySelector('[data-filter="all"]')?.classList.add('active');
    renderCards();
  });

  renderCards();

  // ==========================================
  // 6. LIVE DYNAMIC CSS SANDBOX ENGINE
  // ==========================================
  const sandboxTarget = document.getElementById('sandboxTargetCard');
  const inputRadius = document.getElementById('inputRadius');
  const inputGlow = document.getElementById('inputGlow');
  const inputBlur = document.getElementById('inputBlur');
  const inputRotate = document.getElementById('inputRotate');
  const inputScale = document.getElementById('inputScale');
  const toggleBorder = document.getElementById('toggleBorder');
  const togglePulse = document.getElementById('togglePulse');
  const colorPresets = document.querySelectorAll('.color-preset');
  const generatedCssCode = document.getElementById('generatedCssCode');
  const copyCssBtn = document.getElementById('copyCssBtn');
  const sandboxClickBtn = document.getElementById('sandboxClickBtn');

  let activeGradient = "linear-gradient(135deg, rgba(99, 102, 241, 0.4), rgba(168, 85, 247, 0.4))";

  function updateSandbox() {
    if (!sandboxTarget) return;

    const radius = inputRadius.value + 'px';
    const glow = inputGlow.value + 'px';
    const blur = inputBlur.value + 'px';
    const rotate = inputRotate.value + 'deg';
    const scale = inputScale.value;
    const hasBorderGlow = toggleBorder.checked;
    const isPulse = togglePulse.checked;

    // Update Value Badges
    document.getElementById('valRadius').textContent = radius;
    document.getElementById('valGlow').textContent = glow;
    document.getElementById('valBlur').textContent = blur;
    document.getElementById('valRotate').textContent = rotate;
    document.getElementById('valScale').textContent = `${scale}x`;

    // Apply Inline Dynamic CSS to Target Node
    sandboxTarget.style.background = activeGradient;
    sandboxTarget.style.borderRadius = radius;
    sandboxTarget.style.backdropFilter = `blur(${blur})`;
    sandboxTarget.style.webkitBackdropFilter = `blur(${blur})`;
    sandboxTarget.style.transform = `rotate(${rotate}) scale(${scale})`;
    sandboxTarget.style.boxShadow = hasBorderGlow 
      ? `0 0 ${glow} var(--border-glow), 0 10px 30px rgba(0,0,0,0.5)`
      : `0 10px 30px rgba(0,0,0,0.3)`;
    
    if (isPulse) {
      sandboxTarget.classList.add('pulse-anim');
    } else {
      sandboxTarget.classList.remove('pulse-anim');
    }

    // Generate Clean CSS snippet
    const cssSnippet = `.custom-glass-card {\n` +
      `  background: ${activeGradient};\n` +
      `  border-radius: ${radius};\n` +
      `  backdrop-filter: blur(${blur});\n` +
      `  transform: rotate(${rotate}) scale(${scale});\n` +
      `  box-shadow: ${sandboxTarget.style.boxShadow};\n` +
      `}`;

    if (generatedCssCode) generatedCssCode.textContent = cssSnippet;
  }

  // Attach Sandbox Event Listeners
  [inputRadius, inputGlow, inputBlur, inputRotate, inputScale].forEach(slider => {
    slider?.addEventListener('input', updateSandbox);
  });

  [toggleBorder, togglePulse].forEach(toggle => {
    toggle?.addEventListener('change', updateSandbox);
  });

  colorPresets.forEach(preset => {
    preset.addEventListener('click', () => {
      colorPresets.forEach(p => p.classList.remove('active'));
      preset.classList.add('active');
      activeGradient = preset.dataset.gradient;
      document.getElementById('valColorMode').textContent = preset.style.background;
      updateSandbox();
    });
  });

  copyCssBtn?.addEventListener('click', () => {
    const code = generatedCssCode.textContent;
    navigator.clipboard.writeText(code).then(() => {
      showToast('CSS Copied!', 'Custom CSS rules copied to clipboard', 'success');
      playAudioBeep(1200, 0.1);
    });
  });

  sandboxClickBtn?.addEventListener('click', () => {
    sandboxTarget.style.transform = 'scale(0.9) rotate(5deg)';
    playAudioBeep(950, 0.1, 'square');
    setTimeout(() => updateSandbox(), 180);
  });

  updateSandbox();

  // ==========================================
  // 7. INTERACTIVE TASK & CHECKLIST MANAGER
  // ==========================================
  const taskForm = document.getElementById('taskForm');
  const taskInput = document.getElementById('taskInput');
  const taskPriority = document.getElementById('taskPriority');
  const taskList = document.getElementById('taskList');
  const taskProgressFill = document.getElementById('taskProgressFill');
  const taskProgressPercent = document.getElementById('taskProgressPercent');
  const counterCompleted = document.getElementById('counterCompleted');
  const clearCompletedTasksBtn = document.getElementById('clearCompletedTasksBtn');

  function renderTasks() {
    if (!taskList) return;

    // Filter Tasks
    let filteredTasks = state.tasks.filter(t => {
      if (state.taskFilter === 'active') return !t.completed;
      if (state.taskFilter === 'completed') return t.completed;
      return true;
    });

    taskList.innerHTML = '';

    filteredTasks.forEach(task => {
      const li = document.createElement('li');
      li.className = `task-item ${task.completed ? 'completed' : ''}`;
      li.dataset.id = task.id;

      li.innerHTML = `
        <label class="task-checkbox-label">
          <input type="checkbox" ${task.completed ? 'checked' : ''} data-id="${task.id}">
          <span class="custom-check"><i class="fa-solid fa-check"></i></span>
          <span class="task-text">${escapeHTML(task.text)}</span>
        </label>
        <span class="priority-tag priority-${task.priority}">${task.priority}</span>
        <button class="delete-task-btn" data-id="${task.id}" title="Delete task"><i class="fa-solid fa-xmark"></i></button>
      `;

      taskList.appendChild(li);
    });

    // Update Counts & Progress
    const total = state.tasks.length;
    const completedCount = state.tasks.filter(t => t.completed).length;
    const activeCount = total - completedCount;

    document.getElementById('countAll').textContent = total;
    document.getElementById('countActive').textContent = activeCount;
    document.getElementById('countCompleted').textContent = completedCount;
    if (counterCompleted) counterCompleted.textContent = completedCount;

    const percent = total === 0 ? 0 : Math.round((completedCount / total) * 100);
    if (taskProgressFill) taskProgressFill.style.width = `${percent}%`;
    if (taskProgressPercent) taskProgressPercent.textContent = `${percent}%`;

    attachTaskEvents();
  }

  function attachTaskEvents() {
    document.querySelectorAll('.task-checkbox-label input').forEach(input => {
      input.addEventListener('change', (e) => {
        const id = parseInt(e.target.dataset.id);
        const task = state.tasks.find(t => t.id === id);
        if (task) {
          task.completed = e.target.checked;
          if (task.completed) playAudioBeep(800, 0.1, 'triangle');
          renderTasks();
        }
      });
    });

    document.querySelectorAll('.delete-task-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(btn.dataset.id);
        state.tasks = state.tasks.filter(t => t.id !== id);
        playAudioBeep(400, 0.1);
        renderTasks();
      });
    });
  }

  taskForm?.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = taskInput.value.trim();
    const priority = taskPriority.value;

    if (!text) return;

    state.tasks.unshift({
      id: Date.now(),
      text,
      priority,
      completed: false
    });

    taskInput.value = '';
    renderTasks();
    playAudioBeep(1100, 0.1);
    showToast('Task Created', 'Added new interactive item to checklist', 'info');
  });

  document.querySelectorAll('.task-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.task-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      state.taskFilter = tab.dataset.status;
      renderTasks();
    });
  });

  clearCompletedTasksBtn?.addEventListener('click', () => {
    state.tasks = state.tasks.filter(t => !t.completed);
    renderTasks();
    showToast('Cleared Completed', 'Removed finished checklist items', 'info');
  });

  renderTasks();

  // ==========================================
  // 8. INTERACTIVE QUIZ ENGINE
  // ==========================================
  const quizCurrentStep = document.getElementById('quizCurrentStep');
  const quizTotalSteps = document.getElementById('quizTotalSteps');
  const quizCurrentScore = document.getElementById('quizCurrentScore');
  const quizProgressInner = document.getElementById('quizProgressInner');
  const quizQuestionText = document.getElementById('quizQuestionText');
  const quizOptionsGrid = document.getElementById('quizOptionsGrid');
  const quizFeedbackBox = document.getElementById('quizFeedbackBox');
  const feedbackIcon = document.getElementById('feedbackIcon');
  const feedbackText = document.getElementById('feedbackText');
  const quizPrevBtn = document.getElementById('quizPrevBtn');
  const quizNextBtn = document.getElementById('quizNextBtn');
  const quizMainContent = document.getElementById('quizMainContent');
  const quizResultScreen = document.getElementById('quizResultScreen');
  const restartQuizBtn = document.getElementById('restartQuizBtn');
  const counterScore = document.getElementById('counterScore');

  function renderQuizQuestion() {
    if (!quizQuestionText) return;

    const total = state.quizQuestions.length;
    const currentQ = state.quizQuestions[state.quizIndex];

    quizCurrentStep.textContent = state.quizIndex + 1;
    quizTotalSteps.textContent = total;
    quizCurrentScore.textContent = state.quizScore;
    if (counterScore) counterScore.textContent = state.quizScore;

    quizProgressInner.style.width = `${((state.quizIndex + 1) / total) * 100}%`;
    quizQuestionText.textContent = currentQ.question;
    quizOptionsGrid.innerHTML = '';
    quizFeedbackBox.classList.add('hidden');
    state.quizAnswered = false;

    currentQ.options.forEach((optText, idx) => {
      const btn = document.createElement('button');
      btn.className = 'quiz-option-btn';
      btn.innerHTML = `<span>${optText}</span> <i class="fa-regular fa-circle"></i>`;
      btn.dataset.idx = idx;

      btn.addEventListener('click', () => handleQuizOptionClick(idx, btn));
      quizOptionsGrid.appendChild(btn);
    });

    quizPrevBtn.disabled = state.quizIndex === 0;
    quizNextBtn.disabled = true;
  }

  function handleQuizOptionClick(selectedIndex, optionBtn) {
    if (state.quizAnswered) return;
    state.quizAnswered = true;

    const currentQ = state.quizQuestions[state.quizIndex];
    const isCorrect = selectedIndex === currentQ.correct;

    const allButtons = quizOptionsGrid.querySelectorAll('.quiz-option-btn');
    allButtons.forEach((btn, idx) => {
      btn.disabled = true;
      if (idx === currentQ.correct) {
        btn.classList.add('correct');
        btn.querySelector('i').className = 'fa-solid fa-circle-check';
      } else if (idx === selectedIndex) {
        btn.classList.add('incorrect');
        btn.querySelector('i').className = 'fa-solid fa-circle-xmark';
      }
    });

    if (isCorrect) {
      state.quizScore += 20;
      quizCurrentScore.textContent = state.quizScore;
      if (counterScore) counterScore.textContent = state.quizScore;
      quizFeedbackBox.className = 'quiz-feedback-box correct';
      feedbackIcon.innerHTML = '<i class="fa-solid fa-circle-check"></i>';
      feedbackText.textContent = `Correct! ${currentQ.explanation}`;
      playAudioBeep(1200, 0.15, 'sine');
    } else {
      quizFeedbackBox.className = 'quiz-feedback-box incorrect';
      feedbackIcon.innerHTML = '<i class="fa-solid fa-circle-xmark"></i>';
      feedbackText.textContent = `Incorrect! ${currentQ.explanation}`;
      playAudioBeep(300, 0.2, 'sawtooth');
    }

    quizFeedbackBox.classList.remove('hidden');
    quizNextBtn.disabled = false;
  }

  quizNextBtn?.addEventListener('click', () => {
    if (state.quizIndex < state.quizQuestions.length - 1) {
      state.quizIndex++;
      renderQuizQuestion();
    } else {
      // Quiz Finished
      quizMainContent.classList.add('hidden');
      quizResultScreen.classList.remove('hidden');
      document.getElementById('finalScoreVal').textContent = state.quizScore;
      triggerConfetti();
    }
  });

  quizPrevBtn?.addEventListener('click', () => {
    if (state.quizIndex > 0) {
      state.quizIndex--;
      renderQuizQuestion();
    }
  });

  restartQuizBtn?.addEventListener('click', () => {
    state.quizIndex = 0;
    state.quizScore = 0;
    quizResultScreen.classList.add('hidden');
    quizMainContent.classList.remove('hidden');
    renderQuizQuestion();
  });

  renderQuizQuestion();

  // Confetti Particle Generator
  function triggerConfetti() {
    const confettiCount = 80;
    for (let i = 0; i < confettiCount; i++) {
      const confetti = document.createElement('div');
      confetti.style.position = 'fixed';
      confetti.style.left = `${Math.random() * 100}vw`;
      confetti.style.top = `-10px`;
      confetti.style.width = `${Math.random() * 10 + 5}px`;
      confetti.style.height = `${Math.random() * 10 + 5}px`;
      confetti.style.backgroundColor = ['#6366f1', '#a855f7', '#06b6d4', '#10b981', '#f43f5e', '#f59e0b'][Math.floor(Math.random() * 6)];
      confetti.style.zIndex = '9999';
      confetti.style.pointerEvents = 'none';
      confetti.style.borderRadius = '50%';
      confetti.style.transition = `all ${Math.random() * 2 + 2}s cubic-bezier(0.25, 0.46, 0.45, 0.94)`;

      document.body.appendChild(confetti);

      setTimeout(() => {
        confetti.style.transform = `translateY(${window.innerHeight + 50}px) rotate(${Math.random() * 720}deg)`;
        confetti.style.opacity = '0';
      }, 50);

      setTimeout(() => confetti.remove(), 4000);
    }
  }

  // ==========================================
  // 9. DYNAMIC TOAST NOTIFICATION SYSTEM
  // ==========================================
  const toastContainer = document.getElementById('toastContainer');

  function showToast(title, message, type = 'info', durationSec = 4) {
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast-item ${type}`;

    const iconMap = {
      success: 'fa-solid fa-circle-check',
      info: 'fa-solid fa-circle-info',
      warning: 'fa-solid fa-triangle-exclamation',
      error: 'fa-solid fa-circle-xmark'
    };

    toast.innerHTML = `
      <div class="toast-icon-wrapper"><i class="${iconMap[type] || iconMap.info}"></i></div>
      <div class="toast-body">
        <div class="toast-title">${escapeHTML(title)}</div>
        <div class="toast-message">${escapeHTML(message)}</div>
      </div>
      <button class="toast-close-btn"><i class="fa-solid fa-xmark"></i></button>
      <div class="toast-progress" style="animation-duration: ${durationSec}s;"></div>
    `;

    toastContainer.appendChild(toast);

    const closeBtn = toast.querySelector('.toast-close-btn');
    const dismiss = () => {
      toast.classList.add('toast-hiding');
      setTimeout(() => toast.remove(), 300);
    };

    closeBtn.addEventListener('click', dismiss);
    setTimeout(dismiss, durationSec * 1000);
  }

  document.getElementById('triggerCustomToastBtn')?.addEventListener('click', () => {
    const title = document.getElementById('toastTitleInput').value || 'Alert';
    const msg = document.getElementById('toastMsgInput').value || 'Body text';
    const type = document.getElementById('toastTypeSelect').value;
    const dur = parseInt(document.getElementById('toastDurationInput').value) || 4;
    showToast(title, msg, type, dur);
  });

  document.getElementById('triggerSuccessToastBtn')?.addEventListener('click', () => {
    showToast('Success!', 'Operation completed flawlessly.', 'success');
  });

  document.getElementById('triggerWarningToastBtn')?.addEventListener('click', () => {
    showToast('Warning', 'Check your input settings before saving.', 'warning');
  });

  document.getElementById('triggerErrorToastBtn')?.addEventListener('click', () => {
    showToast('System Error', 'Unable to reach backend endpoint.', 'error');
  });

  document.getElementById('triggerRandomToastBtn')?.addEventListener('click', () => {
    showToast('Sparkles Triggered!', 'Dynamic micro-interaction executed!', 'info');
  });

  // ==========================================
  // 10. GALLERY & LIGHTBOX MODAL
  // ==========================================
  const galleryGrid = document.getElementById('galleryGrid');
  const lightboxModal = document.getElementById('lightboxModal');
  const closeLightboxBtn = document.getElementById('closeLightboxBtn');
  const lightboxTitle = document.getElementById('lightboxTitle');
  const lightboxDescription = document.getElementById('lightboxDescription');
  const lightboxCategory = document.getElementById('lightboxCategory');
  const lightboxTags = document.getElementById('lightboxTags');
  const lightboxIcon = document.getElementById('lightboxIcon');
  const lightboxLikeBtn = document.getElementById('lightboxLikeBtn');
  const lightboxLikeCount = document.getElementById('lightboxLikeCount');

  let activeGalleryItem = null;

  function renderGallery() {
    if (!galleryGrid) return;
    galleryGrid.innerHTML = '';

    state.gallery.forEach(item => {
      const card = document.createElement('div');
      card.className = 'gallery-card';
      card.innerHTML = `
        <div class="gallery-card-bg"><i class="${item.icon}"></i></div>
        <div class="gallery-card-sub">${item.category}</div>
        <div class="gallery-card-title">${escapeHTML(item.title)}</div>
      `;

      card.addEventListener('click', () => openLightbox(item));
      galleryGrid.appendChild(card);
    });
  }

  function openLightbox(item) {
    activeGalleryItem = item;
    lightboxTitle.textContent = item.title;
    lightboxDescription.textContent = item.desc;
    lightboxCategory.textContent = item.category;
    lightboxLikeCount.textContent = item.likes;
    lightboxIcon.innerHTML = `<i class="${item.icon}"></i>`;

    lightboxTags.innerHTML = item.tags.map(t => `<span class="lightbox-tag">#${t}</span>`).join('');

    openModal(lightboxModal);
    playAudioBeep(750, 0.1);
  }

  lightboxLikeBtn?.addEventListener('click', () => {
    if (activeGalleryItem) {
      activeGalleryItem.likes++;
      lightboxLikeCount.textContent = activeGalleryItem.likes;
      playAudioBeep(1100, 0.12);
    }
  });

  closeLightboxBtn?.addEventListener('click', () => closeModal(lightboxModal));
  renderGallery();

  // ==========================================
  // 11. NEWSLETTER FORM VALIDATION
  // ==========================================
  const newsletterForm = document.getElementById('newsletterForm');
  const newsletterFeedback = document.getElementById('newsletterFeedback');

  newsletterForm?.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('newsletterEmail').value.trim();
    if (!email) return;

    newsletterFeedback.className = 'newsletter-feedback success';
    newsletterFeedback.textContent = `Thank you! ${email} has been subscribed to updates.`;
    newsletterFeedback.classList.remove('hidden');

    newsletterForm.reset();
    showToast('Subscribed!', 'Welcome to our interactive community.', 'success');
  });

  // Utility HTML Escape
  function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
      tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
  }

});
