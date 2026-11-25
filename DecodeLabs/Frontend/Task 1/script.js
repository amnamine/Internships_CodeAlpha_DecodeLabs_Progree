/* DecodeLabs Project 1 - Interactive Micro-Interactions */

document.addEventListener('DOMContentLoaded', () => {
  // Theme Toggle Functionality
  const themeToggleBtn = document.getElementById('themeToggle');
  const themeIcon = themeToggleBtn.querySelector('i');
  
  themeToggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    if (currentTheme === 'dark') {
      document.documentElement.removeAttribute('data-theme');
      themeIcon.className = 'fa-solid fa-moon';
    } else {
      document.documentElement.setAttribute('data-theme', 'dark');
      themeIcon.className = 'fa-solid fa-sun';
    }
  });

  // Intersection Observer for Smooth Scroll Fade-in Animations
  const observerOptions = {
    threshold: 0.15,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        
        // Trigger Skill Progress Fill if inside skills section
        const progressFills = entry.target.querySelectorAll('.progress-fill');
        progressFills.forEach(fill => {
          const targetWidth = fill.getAttribute('data-progress');
          fill.style.width = targetWidth;
        });
      }
    });
  }, observerOptions);

  document.querySelectorAll('.fade-in-up').forEach(el => observer.observe(el));

  // 3D Tilt Effect on Badge Seal Container
  const sealContainer = document.getElementById('tiltSeal');
  if (sealContainer) {
    document.addEventListener('mousemove', (e) => {
      const xAxis = (window.innerWidth / 2 - e.pageX) / 35;
      const yAxis = (window.innerHeight / 2 - e.pageY) / 35;
      sealContainer.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
    });
  }
});

// Playground Tab Switcher
function switchTab(tabName) {
  const htmlCode = document.getElementById('htmlCode');
  const cssCode = document.getElementById('cssCode');
  const tabFilename = document.getElementById('tabFilename');
  const buttons = document.querySelectorAll('.tab-btn');

  buttons.forEach(btn => btn.classList.remove('active'));

  if (tabName === 'htmlTab') {
    htmlCode.style.display = 'block';
    cssCode.style.display = 'none';
    tabFilename.textContent = 'index.html';
    buttons[0].classList.add('active');
  } else {
    htmlCode.style.display = 'none';
    cssCode.style.display = 'block';
    tabFilename.textContent = 'styles.css';
    buttons[1].classList.add('active');
  }
}
