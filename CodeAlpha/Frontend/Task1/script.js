/**
 * Lumière Image Gallery
 * Carousel, lightbox, category filters, keyboard navigation
 */

const GALLERY_IMAGES = [
  {
    id: 1,
    title: 'Morning Mist',
    caption: 'Soft fog rolling over alpine meadows at dawn.',
    category: 'nature',
    url: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&q=80',
    thumb: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=70',
  },
  {
    id: 2,
    title: 'Urban Geometry',
    caption: 'Lines and shadows in a modern cityscape.',
    category: 'architecture',
    url: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bcff?w=1200&q=80',
    thumb: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bcff?w=600&q=70',
  },
  {
    id: 3,
    title: 'Silent Portrait',
    caption: 'A moment of quiet reflection captured in natural light.',
    category: 'people',
    url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=1200&q=80',
    thumb: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&q=70',
  },
  {
    id: 4,
    title: 'Color Waves',
    caption: 'Fluid abstract forms in vibrant motion.',
    category: 'abstract',
    url: 'https://images.unsplash.com/photo-1557672172-298ba812a0f9?w=1200&q=80',
    thumb: 'https://images.unsplash.com/photo-1557672172-298ba812a0f9?w=600&q=70',
  },
  {
    id: 5,
    title: 'Forest Path',
    caption: 'Sunlight filtering through ancient woodland trees.',
    category: 'nature',
    url: 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=1200&q=80',
    thumb: 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=600&q=70',
  },
  {
    id: 6,
    title: 'Glass Tower',
    caption: 'Reflective surfaces mirroring the sky above.',
    category: 'architecture',
    url: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&q=80',
    thumb: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&q=70',
  },
  {
    id: 7,
    title: 'Street Story',
    caption: 'Candid energy of city life in motion.',
    category: 'people',
    url: 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1200&q=80',
    thumb: 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600&q=70',
  },
  {
    id: 8,
    title: 'Neon Dreams',
    caption: 'Electric hues blending into the darkness.',
    category: 'abstract',
    url: 'https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=1200&q=80',
    thumb: 'https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=600&q=70',
  },
  {
    id: 9,
    title: 'Ocean Horizon',
    caption: 'Where the sea meets an endless sky.',
    category: 'nature',
    url: 'https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=1200&q=80',
    thumb: 'https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=600&q=70',
  },
  {
    id: 10,
    title: 'Ancient Columns',
    caption: 'Timeless stone architecture standing proud.',
    category: 'architecture',
    url: 'https://images.unsplash.com/photo-1514565131-fce0801e5785?w=1200&q=80',
    thumb: 'https://images.unsplash.com/photo-1514565131-fce0801e5785?w=600&q=70',
  },
  {
    id: 11,
    title: 'Golden Hour',
    caption: 'Warm light wrapping around a thoughtful gaze.',
    category: 'people',
    url: 'https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=1200&q=80',
    thumb: 'https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=600&q=70',
  },
  {
    id: 12,
    title: 'Liquid Light',
    caption: 'Swirling pigments creating organic patterns.',
    category: 'abstract',
    url: 'https://images.unsplash.com/photo-1541701490177-6f3f1c025fff?w=1200&q=80',
    thumb: 'https://images.unsplash.com/photo-1541701490177-6f3f1c025fff?w=600&q=70',
  },
];

const CATEGORY_LABELS = {
  nature: 'Nature',
  architecture: 'Architecture',
  people: 'People',
  abstract: 'Abstract',
};

// State
let carouselIndex = 0;
let lightboxIndex = 0;
let activeFilter = 'all';
let filteredImages = [...GALLERY_IMAGES];
let carouselTimer = null;

// DOM refs
const carouselImage = document.getElementById('carousel-image');
const carouselCategory = document.getElementById('carousel-category');
const carouselTitle = document.getElementById('carousel-title');
const carouselCaption = document.getElementById('carousel-caption');
const carouselCurrent = document.getElementById('carousel-current');
const carouselTotal = document.getElementById('carousel-total');
const carouselDots = document.getElementById('carousel-dots');
const galleryGrid = document.getElementById('gallery-grid');
const galleryEmpty = document.getElementById('gallery-empty');
const statCount = document.getElementById('stat-count');
const lightbox = document.getElementById('lightbox');
const lightboxImage = document.getElementById('lightbox-image');
const lightboxCategory = document.getElementById('lightbox-category');
const lightboxTitle = document.getElementById('lightbox-title');
const lightboxCaption = document.getElementById('lightbox-caption');
const lightboxCurrent = document.getElementById('lightbox-current');
const lightboxTotal = document.getElementById('lightbox-total');

function getCategoryLabel(category) {
  return CATEGORY_LABELS[category] || category;
}

function getVisibleImages() {
  if (activeFilter === 'all') return GALLERY_IMAGES;
  return GALLERY_IMAGES.filter((img) => img.category === activeFilter);
}

function updateCarousel(index, animate = true) {
  const images = getVisibleImages();
  if (images.length === 0) return;

  carouselIndex = ((index % images.length) + images.length) % images.length;
  const img = images[carouselIndex];

  const applyUpdate = () => {
    carouselImage.src = img.url;
    carouselImage.alt = img.title;
    carouselCategory.textContent = getCategoryLabel(img.category);
    carouselTitle.textContent = img.title;
    carouselCaption.textContent = img.caption;
    carouselCurrent.textContent = carouselIndex + 1;
    carouselTotal.textContent = images.length;

    document.querySelectorAll('.carousel__dot').forEach((dot, i) => {
      dot.classList.toggle('carousel__dot--active', i === carouselIndex);
      dot.setAttribute('aria-selected', i === carouselIndex ? 'true' : 'false');
    });
  };

  if (animate) {
    carouselImage.classList.add('fade-out');
    setTimeout(() => {
      applyUpdate();
      carouselImage.classList.remove('fade-out');
    }, 200);
  } else {
    applyUpdate();
  }
}

function buildCarouselDots() {
  const images = getVisibleImages();
  carouselDots.innerHTML = '';

  images.forEach((_, i) => {
    const dot = document.createElement('button');
    dot.className = 'carousel__dot' + (i === carouselIndex ? ' carousel__dot--active' : '');
    dot.setAttribute('role', 'tab');
    dot.setAttribute('aria-label', `Go to slide ${i + 1}`);
    dot.setAttribute('aria-selected', i === carouselIndex ? 'true' : 'false');
    dot.addEventListener('click', () => {
      updateCarousel(i);
      resetCarouselAutoplay();
    });
    carouselDots.appendChild(dot);
  });
}

function renderGallery() {
  filteredImages = getVisibleImages();
  galleryGrid.innerHTML = '';

  if (filteredImages.length === 0) {
    galleryEmpty.classList.remove('hidden');
    return;
  }

  galleryEmpty.classList.add('hidden');

  filteredImages.forEach((img, i) => {
    const item = document.createElement('article');
    item.className = 'gallery__item';
    item.setAttribute('role', 'listitem');
    item.style.animationDelay = `${i * 0.06}s`;
    item.dataset.index = i;

    item.innerHTML = `
      <img src="${img.thumb}" alt="${img.title}" loading="lazy">
      <div class="gallery__item-overlay">
        <span class="gallery__item-category">${getCategoryLabel(img.category)}</span>
        <h3 class="gallery__item-title">${img.title}</h3>
      </div>
      <div class="gallery__item-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
        </svg>
      </div>
    `;

    item.addEventListener('click', () => openLightbox(i));
    galleryGrid.appendChild(item);
  });

  statCount.textContent = GALLERY_IMAGES.length;
}

function applyFilter(filter) {
  activeFilter = filter;
  carouselIndex = 0;

  document.querySelectorAll('.filter-btn').forEach((btn) => {
    btn.classList.toggle('filter-btn--active', btn.dataset.filter === filter);
  });

  renderGallery();
  buildCarouselDots();
  updateCarousel(0, false);
  resetCarouselAutoplay();
}

function openLightbox(index) {
  lightboxIndex = index;
  updateLightbox(false);
  lightbox.classList.remove('hidden');
  document.body.classList.add('lightbox-open');
  stopCarouselAutoplay();
}

function closeLightbox() {
  lightbox.classList.add('hidden');
  document.body.classList.remove('lightbox-open');
  startCarouselAutoplay();
}

function updateLightbox(animate = true) {
  const img = filteredImages[lightboxIndex];
  if (!img) return;

  const applyUpdate = () => {
    lightboxImage.src = img.url;
    lightboxImage.alt = img.title;
    lightboxCategory.textContent = getCategoryLabel(img.category);
    lightboxTitle.textContent = img.title;
    lightboxCaption.textContent = img.caption;
    lightboxCurrent.textContent = lightboxIndex + 1;
    lightboxTotal.textContent = filteredImages.length;
  };

  if (animate) {
    lightboxImage.classList.add('fade-out');
    setTimeout(() => {
      applyUpdate();
      lightboxImage.classList.remove('fade-out');
    }, 150);
  } else {
    applyUpdate();
  }
}

function navigateLightbox(direction) {
  lightboxIndex = (lightboxIndex + direction + filteredImages.length) % filteredImages.length;
  updateLightbox(true);
}

function navigateCarousel(direction) {
  updateCarousel(carouselIndex + direction);
  resetCarouselAutoplay();
}

function startCarouselAutoplay() {
  stopCarouselAutoplay();
  carouselTimer = setInterval(() => {
    updateCarousel(carouselIndex + 1);
  }, 6000);
}

function stopCarouselAutoplay() {
  if (carouselTimer) {
    clearInterval(carouselTimer);
    carouselTimer = null;
  }
}

function resetCarouselAutoplay() {
  stopCarouselAutoplay();
  startCarouselAutoplay();
}

function handleKeydown(e) {
  const lightboxOpen = !lightbox.classList.contains('hidden');

  if (lightboxOpen) {
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') navigateLightbox(-1);
    if (e.key === 'ArrowRight') navigateLightbox(1);
    return;
  }

  if (e.key === 'ArrowLeft') navigateCarousel(-1);
  if (e.key === 'ArrowRight') navigateCarousel(1);
}

function initEventListeners() {
  document.getElementById('carousel-prev').addEventListener('click', () => navigateCarousel(-1));
  document.getElementById('carousel-next').addEventListener('click', () => navigateCarousel(1));

  document.querySelectorAll('.filter-btn').forEach((btn) => {
    btn.addEventListener('click', () => applyFilter(btn.dataset.filter));
  });

  document.getElementById('lightbox-close').addEventListener('click', closeLightbox);
  document.getElementById('lightbox-backdrop').addEventListener('click', closeLightbox);
  document.getElementById('lightbox-prev').addEventListener('click', () => navigateLightbox(-1));
  document.getElementById('lightbox-next').addEventListener('click', () => navigateLightbox(1));

  document.addEventListener('keydown', handleKeydown);

  // Touch swipe for carousel
  let touchStartX = 0;
  const carouselFrame = document.querySelector('.carousel__frame');

  carouselFrame.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  carouselFrame.addEventListener('touchend', (e) => {
    const diff = touchStartX - e.changedTouches[0].screenX;
    if (Math.abs(diff) > 50) {
      navigateCarousel(diff > 0 ? 1 : -1);
    }
  }, { passive: true });

  // Touch swipe for lightbox
  let lightboxTouchStartX = 0;

  lightbox.addEventListener('touchstart', (e) => {
    lightboxTouchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  lightbox.addEventListener('touchend', (e) => {
    if (lightbox.classList.contains('hidden')) return;
    const diff = lightboxTouchStartX - e.changedTouches[0].screenX;
    if (Math.abs(diff) > 50) {
      navigateLightbox(diff > 0 ? 1 : -1);
    }
  }, { passive: true });

  carouselFrame.addEventListener('mouseenter', stopCarouselAutoplay);
  carouselFrame.addEventListener('mouseleave', startCarouselAutoplay);
}

function init() {
  renderGallery();
  buildCarouselDots();
  updateCarousel(0, false);
  initEventListeners();
  startCarouselAutoplay();
}

document.addEventListener('DOMContentLoaded', init);
