/* ==========================================================================
   DECODELABS TASK 2 - INSANE JS ENGINE & INTERACTION LOGIC
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  /* --------------------------------------------------------------------------
     1. WEB AUDIO API SYNTHESIZER SOUND ENGINE
     -------------------------------------------------------------------------- */
  class SoundEngine {
    constructor() {
      this.ctx = null;
      this.enabled = true;
    }

    init() {
      if (!this.ctx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
          this.ctx = new AudioContext();
        }
      }
    }

    playTone(freq = 440, type = 'sine', duration = 0.1, gainValue = 0.05) {
      if (!this.enabled) return;
      this.init();
      if (!this.ctx) return;

      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
        gain.gain.setValueAtTime(gainValue, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start();
        osc.stop(this.ctx.currentTime + duration);
      } catch (e) {
        // Audio context muted or user blocked autoplay
      }
    }

    hover() {
      this.playTone(320, 'sine', 0.05, 0.02);
    }

    click() {
      this.playTone(600, 'triangle', 0.1, 0.04);
    }

    success() {
      if (!this.enabled) return;
      this.playTone(523.25, 'sine', 0.1, 0.05); // C5
      setTimeout(() => this.playTone(659.25, 'sine', 0.15, 0.05), 80); // E5
      setTimeout(() => this.playTone(783.99, 'sine', 0.25, 0.05), 160); // G5
    }

    toggle() {
      this.enabled = !this.enabled;
      return this.enabled;
    }
  }

  const sound = new SoundEngine();

  // Attach audio sounds to interactive elements
  const interactiveSelector = 'a, button, .feature-card, .theme-option, .device-tab, .cmd-item';
  document.querySelectorAll(interactiveSelector).forEach(el => {
    el.addEventListener('mouseenter', () => sound.hover());
    el.addEventListener('click', () => sound.click());
  });

  const soundToggleBtn = document.getElementById('soundToggleBtn');
  soundToggleBtn?.addEventListener('click', () => {
    const isMuted = !sound.toggle();
    soundToggleBtn.innerHTML = isMuted ? '🔇' : '🔊';
    showToast(isMuted ? 'Audio Feedback Muted' : 'Audio Feedback Enabled', 'info');
  });

  /* --------------------------------------------------------------------------
     2. CUSTOM MAGNETIC CURSOR TRACKER
     -------------------------------------------------------------------------- */
  const cursorDot = document.getElementById('cursorDot');
  const cursorRing = document.getElementById('cursorRing');

  if (cursorDot && cursorRing && window.innerWidth > 768) {
    let mouseX = 0, mouseY = 0;
    let ringX = 0, ringY = 0;

    window.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      cursorDot.style.left = `${mouseX}px`;
      cursorDot.style.top = `${mouseY}px`;
    });

    const animateRing = () => {
      ringX += (mouseX - ringX) * 0.15;
      ringY += (mouseY - ringY) * 0.15;
      cursorRing.style.left = `${ringX}px`;
      cursorRing.style.top = `${ringY}px`;
      requestAnimationFrame(animateRing);
    };
    animateRing();

    // Hover effect on magnetic targets
    document.querySelectorAll('a, button, input, textarea, [data-tilt]').forEach(el => {
      el.addEventListener('mouseenter', () => document.body.classList.add('cursor-hover'));
      el.addEventListener('mouseleave', () => document.body.classList.remove('cursor-hover'));
    });
  }

  /* --------------------------------------------------------------------------
     3. INTERACTIVE PARTICLE CANVAS BACKGROUND
     -------------------------------------------------------------------------- */
  const canvas = document.getElementById('particleCanvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let particles = [];
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    let mouse = { x: null, y: null, radius: 150 };

    window.addEventListener('mousemove', (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    });

    window.addEventListener('resize', () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      initParticles();
    });

    class Particle {
      constructor() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.size = Math.random() * 2.5 + 1;
        this.baseX = this.x;
        this.baseY = this.y;
        this.vx = (Math.random() - 0.5) * 0.8;
        this.vy = (Math.random() - 0.5) * 0.8;
        this.color = getComputedStyle(document.documentElement).getPropertyValue('--accent-primary').trim() || '#00f0ff';
      }

      draw() {
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.closePath();
        ctx.fill();
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;

        // Mouse Proximity Interaction
        if (mouse.x != null && mouse.y != null) {
          let dx = mouse.x - this.x;
          let dy = mouse.y - this.y;
          let distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < mouse.radius) {
            let angle = Math.atan2(dy, dx);
            let force = (mouse.radius - distance) / mouse.radius;
            this.x -= Math.cos(angle) * force * 3;
            this.y -= Math.sin(angle) * force * 3;
          }
        }
      }
    }

    const initParticles = () => {
      particles = [];
      const numParticles = Math.min(Math.floor((width * height) / 12000), 80);
      for (let i = 0; i < numParticles; i++) {
        particles.push(new Particle());
      }
    };
    initParticles();

    const connectParticles = () => {
      for (let a = 0; a < particles.length; a++) {
        for (let b = a; b < particles.length; b++) {
          let dx = particles[a].x - particles[b].x;
          let dy = particles[a].y - particles[b].y;
          let dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 120) {
            ctx.strokeStyle = particles[a].color;
            ctx.globalAlpha = 1 - dist / 120;
            ctx.lineWidth = 0.6;
            ctx.beginPath();
            ctx.moveTo(particles[a].x, particles[a].y);
            ctx.lineTo(particles[b].x, particles[b].y);
            ctx.stroke();
            ctx.globalAlpha = 1;
          }
        }
      }
    };

    const animateParticles = () => {
      ctx.clearRect(0, 0, width, height);
      particles.forEach(p => {
        p.update();
        p.draw();
      });
      connectParticles();
      requestAnimationFrame(animateParticles);
    };
    animateParticles();
  }

  /* --------------------------------------------------------------------------
     4. 3D CARD TILT EFFECT
     -------------------------------------------------------------------------- */
  const tiltCards = document.querySelectorAll('[data-tilt], #heroTiltCard');
  tiltCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -12;
      const rotateY = ((x - centerX) / centerX) * 12;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    });
  });

  /* --------------------------------------------------------------------------
     5. DYNAMIC THEME ENGINE & SWITCHER
     -------------------------------------------------------------------------- */
  const themeOptions = document.querySelectorAll('.theme-option');
  const currentThemeName = document.getElementById('currentThemeName');
  const themeQuickBtn = document.getElementById('themeQuickBtn');

  const themeNames = {
    cyberpunk: 'Cyberpunk',
    aurora: 'Aurora',
    deepspace: 'Deep Space',
    matrix: 'Matrix',
    pearl: 'Pearl Light'
  };

  const setTheme = (theme) => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('decodelabs_theme', theme);

    if (currentThemeName) {
      currentThemeName.textContent = themeNames[theme] || 'Cyberpunk';
    }

    themeOptions.forEach(opt => {
      opt.classList.toggle('active', opt.dataset.theme === theme);
    });

    showToast(`Switched theme to ${themeNames[theme]}`, 'success');
  };

  const savedTheme = localStorage.getItem('decodelabs_theme') || 'cyberpunk';
  setTheme(savedTheme);

  themeOptions.forEach(opt => {
    opt.addEventListener('click', () => setTheme(opt.dataset.theme));
  });

  themeQuickBtn?.addEventListener('click', () => {
    const themes = Object.keys(themeNames);
    const current = document.documentElement.getAttribute('data-theme') || 'cyberpunk';
    const nextIdx = (themes.indexOf(current) + 1) % themes.length;
    setTheme(themes[nextIdx]);
  });

  /* --------------------------------------------------------------------------
     6. LIVE SANDBOX CODE EDITOR
     -------------------------------------------------------------------------- */
  const sandboxInput = document.getElementById('sandboxInput');
  const sandboxOutput = document.getElementById('sandboxOutput');
  const sandboxPresets = document.querySelectorAll('.sandbox-preset-btn');
  const resetSandboxBtn = document.getElementById('resetSandboxBtn');

  const presets = {
    button: `<div style="
  padding: 2rem;
  background: linear-gradient(135deg, #00f0ff, #7000ff);
  border-radius: 16px;
  color: #fff;
  font-family: sans-serif;
  box-shadow: 0 10px 30px rgba(0,240,255,0.4);
  text-align: center;
">
  <h3 style="margin-bottom: 0.5rem;">⚡ DecodeLabs Live Card</h3>
  <p style="font-size: 0.9rem; opacity: 0.9;">Edit code on the left to customize me!</p>
</div>`,
    badge: `<div style="
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid #10b981;
  color: #10b981;
  border-radius: 99px;
  font-family: monospace;
  font-weight: bold;
">
  <span style="width:10px;height:10px;background:#10b981;border-radius:50%;"></span>
  STATUS: TASK_2_COMPLETE
</div>`,
    glow: `<div style="
  width: 140px;
  height: 140px;
  background: #0f121d;
  border: 2px solid #ff007b;
  border-radius: 20px;
  box-shadow: 0 0 25px #ff007b;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ff007b;
  font-size: 2rem;
">
  ✨
</div>`
  };

  const updateSandbox = () => {
    if (sandboxInput && sandboxOutput) {
      sandboxOutput.innerHTML = sandboxInput.value;
    }
  };

  if (sandboxInput) {
    sandboxInput.value = presets.button;
    updateSandbox();

    sandboxInput.addEventListener('input', updateSandbox);

    sandboxPresets.forEach(btn => {
      btn.addEventListener('click', () => {
        sandboxPresets.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const key = btn.dataset.preset;
        if (presets[key]) {
          sandboxInput.value = presets[key];
          updateSandbox();
          sound.click();
        }
      });
    });

    resetSandboxBtn?.addEventListener('click', () => {
      sandboxInput.value = presets.button;
      updateSandbox();
      showToast('Sandbox reset to default preset', 'info');
    });
  }

  /* --------------------------------------------------------------------------
     7. MULTI-DEVICE SIMULATOR
     -------------------------------------------------------------------------- */
  const deviceTabs = document.querySelectorAll('.device-tab');
  const deviceFrame = document.getElementById('deviceFrame');
  const dimensionBadge = document.getElementById('dimensionBadge');
  const previewIframe = document.getElementById('previewIframe');

  const dimensions = {
    desktop: '1440px × 900px',
    laptop: '1024px × 768px',
    tablet: '768px × 1024px',
    mobile: '375px × 667px',
    foldable: '280px × 650px'
  };

  if (previewIframe) {
    // Populate iframe with basic live clone preview
    const cloneContent = () => {
      const doc = previewIframe.contentDocument || previewIframe.contentWindow.document;
      doc.open();
      doc.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { font-family: sans-serif; background: #090a0f; color: #fff; padding: 20px; text-align: center; }
            .card { background: rgba(255,255,255,0.08); padding: 20px; border-radius: 12px; border: 1px solid #00f0ff; }
            h2 { color: #00f0ff; }
          </style>
        </head>
        <body>
          <div class="card">
            <h2>DecodeLabs Task 2 Viewport</h2>
            <p>Responsive Preview Active</p>
          </div>
        </body>
        </html>
      `);
      doc.close();
    };
    setTimeout(cloneContent, 500);
  }

  deviceTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      deviceTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const mode = tab.dataset.device;
      if (deviceFrame) {
        deviceFrame.className = `device-frame ${mode}-mode`;
      }
      if (dimensionBadge) {
        dimensionBadge.textContent = dimensions[mode] || '';
      }
      sound.click();
    });
  });

  /* --------------------------------------------------------------------------
     8. COMMAND PALETTE (CTRL + K)
     -------------------------------------------------------------------------- */
  const cmdPaletteModal = document.getElementById('cmdPaletteModal');
  const cmdPaletteBtn = document.getElementById('cmdPaletteBtn');
  const cmdSearchInput = document.getElementById('cmdSearchInput');
  const cmdItems = document.querySelectorAll('.cmd-item');

  const openCmd = () => {
    cmdPaletteModal?.classList.add('active');
    cmdSearchInput?.focus();
  };

  const closeCmd = () => {
    cmdPaletteModal?.classList.remove('active');
    if (cmdSearchInput) cmdSearchInput.value = '';
    cmdItems.forEach(i => i.style.display = 'flex');
  };

  cmdPaletteBtn?.addEventListener('click', openCmd);

  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      cmdPaletteModal?.classList.contains('active') ? closeCmd() : openCmd();
    }
    if (e.key === 'Escape' && cmdPaletteModal?.classList.contains('active')) {
      closeCmd();
    }
  });

  cmdPaletteModal?.addEventListener('click', (e) => {
    if (e.target === cmdPaletteModal) closeCmd();
  });

  cmdSearchInput?.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    cmdItems.forEach(item => {
      const text = item.textContent.toLowerCase();
      item.style.display = text.includes(query) ? 'flex' : 'none';
    });
  });

  cmdItems.forEach(item => {
    item.addEventListener('click', () => {
      const action = item.dataset.action;
      closeCmd();

      if (action === 'goto-hero') document.getElementById('hero')?.scrollIntoView();
      if (action === 'goto-features') document.getElementById('features')?.scrollIntoView();
      if (action === 'goto-skills') document.getElementById('skills')?.scrollIntoView();
      if (action === 'goto-playground') document.getElementById('playground')?.scrollIntoView();
      if (action === 'goto-devices') document.getElementById('devices')?.scrollIntoView();
      if (action === 'toggle-sound') soundToggleBtn?.click();
      if (action === 'cycle-theme') themeQuickBtn?.click();
    });
  });

  /* --------------------------------------------------------------------------
     9. CONFETTI CELEBRATION LAUNCHER
     -------------------------------------------------------------------------- */
  const triggerConfettiBtn = document.getElementById('triggerConfettiBtn');
  triggerConfettiBtn?.addEventListener('click', () => {
    sound.success();
    launchConfetti();
    showToast('🎉 Project Task 2 Requirements Verified!', 'success');
  });

  function launchConfetti() {
    const confettiCanvas = document.createElement('canvas');
    confettiCanvas.style.position = 'fixed';
    confettiCanvas.style.inset = '0';
    confettiCanvas.style.width = '100vw';
    confettiCanvas.style.height = '100vh';
    confettiCanvas.style.pointerEvents = 'none';
    confettiCanvas.style.zIndex = '99999';
    document.body.appendChild(confettiCanvas);

    const ctx = confettiCanvas.getContext('2d');
    confettiCanvas.width = window.innerWidth;
    confettiCanvas.height = window.innerHeight;

    const pieces = [];
    const colors = ['#00f0ff', '#7000ff', '#ff007b', '#00ffaa', '#f59e0b'];

    for (let i = 0; i < 120; i++) {
      pieces.push({
        x: Math.random() * confettiCanvas.width,
        y: -20,
        r: Math.random() * 8 + 4,
        d: Math.random() * 10 + 2,
        color: colors[Math.floor(Math.random() * colors.length)],
        tilt: Math.random() * 10 - 10,
        tiltAngleIncremental: Math.random() * 0.07 + 0.05
      });
    }

    let animationFrame;
    let opacity = 1;

    function draw() {
      ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
      ctx.globalAlpha = opacity;

      pieces.forEach(p => {
        ctx.beginPath();
        ctx.lineWidth = p.r / 2;
        ctx.strokeStyle = p.color;
        ctx.moveTo(p.x + p.tilt + p.r / 4, p.y);
        ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r / 4);
        ctx.stroke();

        p.y += p.d;
        p.tilt += p.tiltAngleIncremental;
      });

      if (pieces[0].y > confettiCanvas.height) {
        opacity -= 0.02;
      }

      if (opacity > 0) {
        animationFrame = requestAnimationFrame(draw);
      } else {
        cancelAnimationFrame(animationFrame);
        confettiCanvas.remove();
      }
    }

    draw();
  }

  /* --------------------------------------------------------------------------
     10. CONTACT FORM VALIDATION & TOAST ALERT SYSTEM
     -------------------------------------------------------------------------- */
  const contactForm = document.getElementById('contactForm');
  contactForm?.addEventListener('submit', (e) => {
    e.preventDefault();

    const name = document.getElementById('userName');
    const email = document.getElementById('userEmail');
    const message = document.getElementById('userMessage');

    let valid = true;

    if (!name.value.trim()) {
      name.parentElement.classList.add('error');
      valid = false;
    } else {
      name.parentElement.classList.remove('error');
    }

    if (!email.value.trim() || !/\S+@\S+\.\S+/.test(email.value)) {
      email.parentElement.classList.add('error');
      valid = false;
    } else {
      email.parentElement.classList.remove('error');
    }

    if (!message.value.trim()) {
      message.parentElement.classList.add('error');
      valid = false;
    } else {
      message.parentElement.classList.remove('error');
    }

    if (valid) {
      sound.success();
      showToast('🚀 Message sent successfully! Thank you for the feedback.', 'success');
      contactForm.reset();
    } else {
      showToast('⚠️ Please correct highlighted form errors.', 'error');
    }
  });

  function showToast(msg, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    toast.innerHTML = `<span>${icon}</span> <span>${msg}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(-30px)';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  /* --------------------------------------------------------------------------
     11. ANIMATED NUMBERS COUNTER
     -------------------------------------------------------------------------- */
  const counters = document.querySelectorAll('.stat-number');
  let animatedCounters = false;

  const animateCounters = () => {
    counters.forEach(counter => {
      const target = +counter.dataset.target;
      let count = 0;
      const speed = target / 50 || 1;

      const update = () => {
        count += speed;
        if (count < target) {
          counter.textContent = Math.ceil(count);
          setTimeout(update, 25);
        } else {
          counter.textContent = target;
        }
      };
      update();
    });
  };

  window.addEventListener('scroll', () => {
    const heroSection = document.getElementById('hero');
    if (heroSection && !animatedCounters) {
      const rect = heroSection.getBoundingClientRect();
      if (rect.top < window.innerHeight) {
        animateCounters();
        animatedCounters = true;
      }
    }
  });

  // Initial trigger for counters if hero is visible on load
  setTimeout(animateCounters, 300);

  // Mobile menu toggle
  const mobileToggle = document.getElementById('mobileMenuToggle');
  const navLinks = document.getElementById('navLinks');
  mobileToggle?.addEventListener('click', () => {
    navLinks?.classList.toggle('active');
  });

});
