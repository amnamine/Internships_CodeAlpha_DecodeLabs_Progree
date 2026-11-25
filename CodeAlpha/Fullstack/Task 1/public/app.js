// Shared Application Logic
document.addEventListener('DOMContentLoaded', () => {
  initCart();
  
  // Route check
  const path = window.location.pathname;
  if (path.endsWith('/product.html') || window.location.search.includes('id=')) {
    initProductDetailsPage();
  } else if (path.endsWith('/cart.html')) {
    initCartPage();
  } else {
    initCatalogPage();
  }
});

// Toast notification helper
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container') || createToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  let icon = '✓';
  if (type === 'error') icon = '✕';
  else if (type === 'info') icon = 'ℹ';
  
  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);
  
  // Auto-remove after 4 seconds
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(20px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toast-container';
  container.className = 'toast-container';
  document.body.appendChild(container);
  return container;
}

// Category Emoji Map for premium graphics
const categoryIcons = {
  'Keyboards': '⌨️',
  'Mice': '🖱️',
  'Accessories': '🪵',
  'Lighting': '💡',
  'Audio': '🔊',
  'Default': '📦'
};

// Cart State Management
let cart = [];

function initCart() {
  const storedCart = localStorage.getItem('ecommerce_cart');
  if (storedCart) {
    try {
      cart = JSON.parse(storedCart);
    } catch (e) {
      cart = [];
    }
  }
  updateCartCount();
}

function saveCart() {
  localStorage.setItem('ecommerce_cart', JSON.stringify(cart));
  updateCartCount();
}

function updateCartCount() {
  const count = cart.reduce((sum, item) => sum + item.quantity, 0);
  const badges = document.querySelectorAll('.cart-count');
  badges.forEach(badge => {
    badge.textContent = count;
    badge.style.display = count > 0 ? 'inline-block' : 'none';
  });
}

function addToCart(productId, name, price, quantity = 1, stockLimit = 99) {
  const existingItem = cart.find(item => item.productId === productId);
  
  if (existingItem) {
    if (existingItem.quantity + quantity > stockLimit) {
      showToast(`Cannot add more. Limit of ${stockLimit} reached based on stock.`, 'error');
      return;
    }
    existingItem.quantity += quantity;
  } else {
    cart.push({ productId, name, price, quantity });
  }
  
  saveCart();
  showToast(`Added ${name} to cart!`);
}

// Catalog Page Functionality
let allProducts = [];

async function initCatalogPage() {
  const grid = document.getElementById('products-grid');
  if (!grid) return;

  grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-secondary);">Loading premium catalog...</div>';

  try {
    const response = await fetch('/api/products');
    if (!response.ok) throw new Error('Failed to load products');
    allProducts = await response.json();
    
    renderProducts(allProducts);
    setupFilters();
  } catch (error) {
    console.error(error);
    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--danger);">Failed to load products. Please try again.</div>';
  }
}

function renderProducts(products) {
  const grid = document.getElementById('products-grid');
  if (!grid) return;

  if (products.length === 0) {
    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-muted);">No products found matching your criteria.</div>';
    return;
  }

  grid.innerHTML = products.map(product => {
    const emoji = categoryIcons[product.category] || categoryIcons.Default;
    const isOutOfStock = product.stock <= 0;
    
    return `
      <div class="product-card">
        <div class="product-img-container">
          <div class="product-img-fallback">
            <span class="product-img-icon">${emoji}</span>
            <span>${product.category}</span>
          </div>
          <span class="product-badge">${isOutOfStock ? 'Sold Out' : `In Stock: ${product.stock}`}</span>
        </div>
        <div class="product-content">
          <span class="product-category">${product.category}</span>
          <a href="/product.html?id=${product.id}" class="product-name">${product.name}</a>
          <p class="product-desc">${product.description}</p>
          <div class="product-meta">
            <div class="product-rating">
              <span class="star-icon">★</span>
              <span>${product.rating.toFixed(1)}</span>
              <span class="product-reviews">(${product.reviews_count})</span>
            </div>
            <span class="product-price">$${product.price.toFixed(2)}</span>
          </div>
          <div class="card-actions">
            <a href="/product.html?id=${product.id}" class="btn-secondary">View details</a>
            <button 
              class="btn-primary" 
              onclick="addToCart(${product.id}, '${product.name.replace(/'/g, "\\'")}', ${product.price}, 1, ${product.stock})"
              ${isOutOfStock ? 'disabled' : ''}
            >
              ${isOutOfStock ? 'Out of stock' : 'Add to cart'}
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function setupFilters() {
  const searchInput = document.getElementById('search-input');
  const tabs = document.querySelectorAll('.tab-btn');

  let activeCategory = 'All';
  let searchQuery = '';

  const filterHandler = () => {
    const filtered = allProducts.filter(p => {
      const matchCategory = activeCategory === 'All' || p.category === activeCategory;
      const matchSearch = p.name.toLowerCase().includes(searchQuery) || 
                          p.description.toLowerCase().includes(searchQuery) ||
                          p.category.toLowerCase().includes(searchQuery);
      return matchCategory && matchSearch;
    });
    renderProducts(filtered);
  };

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.toLowerCase();
      filterHandler();
    });
  }

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      activeCategory = tab.dataset.category;
      filterHandler();
    });
  });
}

// Product Details Page
async function initProductDetailsPage() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');
  
  if (!id) {
    window.location.href = '/';
    return;
  }

  const detailWrapper = document.getElementById('product-detail-wrapper');
  if (!detailWrapper) return;

  try {
    const response = await fetch(`/api/products/${id}`);
    if (!response.ok) throw new Error('Product not found');
    const product = await response.json();

    const emoji = categoryIcons[product.category] || categoryIcons.Default;
    const isOutOfStock = product.stock <= 0;

    detailWrapper.innerHTML = `
      <a href="/" class="back-btn">← Back to catalog</a>
      <div class="detail-grid">
        <div class="detail-img-box">
          <div class="detail-img-large">
            <span>${emoji}</span>
            <span>${product.category} Setup Component</span>
          </div>
        </div>
        <div class="detail-info">
          <span class="detail-category">${product.category}</span>
          <h1 class="detail-name">${product.name}</h1>
          
          <div class="detail-rating-row">
            <div class="product-rating">
              <span class="star-icon" style="font-size: 1.1rem;">★</span>
              <span style="font-size: 1.1rem;">${product.rating.toFixed(1)}</span>
              <span class="product-reviews" style="font-size: 0.95rem;">(${product.reviews_count} community reviews)</span>
            </div>
            <span class="detail-stock ${isOutOfStock ? 'out' : ''}">
              ${isOutOfStock ? 'Sold Out' : `In Stock: ${product.stock} units`}
            </span>
          </div>
          
          <div class="detail-price">$${product.price.toFixed(2)}</div>
          
          <h3 class="detail-desc-title">About this piece</h3>
          <p class="detail-desc">${product.description}</p>
          
          <div class="purchase-actions">
            ${isOutOfStock ? `
              <button class="btn-primary" style="padding: 1rem 3rem;" disabled>Out of stock</button>
            ` : `
              <div class="quantity-selector">
                <button class="qty-btn" id="qty-minus">-</button>
                <div class="qty-val" id="qty-value">1</div>
                <button class="qty-btn" id="qty-plus">+</button>
              </div>
              <button class="btn-primary" id="add-to-cart-btn" style="padding: 1rem 3rem;">
                Add to cart
              </button>
            `}
          </div>
        </div>
      </div>
    `;

    // Handle Quantity increments/decrements
    if (!isOutOfStock) {
      const minus = document.getElementById('qty-minus');
      const plus = document.getElementById('qty-plus');
      const value = document.getElementById('qty-value');
      const addBtn = document.getElementById('add-to-cart-btn');

      let qty = 1;

      minus.addEventListener('click', () => {
        if (qty > 1) {
          qty--;
          value.textContent = qty;
        }
      });

      plus.addEventListener('click', () => {
        if (qty < product.stock) {
          qty++;
          value.textContent = qty;
        } else {
          showToast(`Only ${product.stock} units available in stock.`, 'info');
        }
      });

      addBtn.addEventListener('click', () => {
        addToCart(product.id, product.name, product.price, qty, product.stock);
      });
    }

  } catch (error) {
    console.error(error);
    detailWrapper.innerHTML = `
      <a href="/" class="back-btn">← Back to catalog</a>
      <div style="text-align: center; padding: 5rem 0; color: var(--danger);">
        <h2>Error Loading Product</h2>
        <p>The product you are trying to view does not exist or has been removed.</p>
      </div>
    `;
  }
}

// Cart & Checkout Page
function initCartPage() {
  const container = document.getElementById('cart-page-container');
  if (!container) return;

  renderCart();
  setupCheckoutForm();
}

function renderCart() {
  const list = document.getElementById('cart-items-list');
  const summarySubtotal = document.getElementById('subtotal-amount');
  const summaryTotal = document.getElementById('total-amount');
  const checkoutBtn = document.getElementById('checkout-submit-btn');
  const checkoutFormFields = document.getElementById('checkout-form-fields');

  if (!list) return;

  if (cart.length === 0) {
    list.innerHTML = `
      <div class="empty-cart-view">
        <span class="empty-cart-icon">🛒</span>
        <h2>Your space is empty</h2>
        <p>You haven't added any luxury items to your workstation selection yet.</p>
        <a href="/" class="hero-btn" style="text-shadow: none;">Browse Catalog</a>
      </div>
    `;
    if (summarySubtotal) summarySubtotal.textContent = '$0.00';
    if (summaryTotal) summaryTotal.textContent = '$0.00';
    if (checkoutBtn) checkoutBtn.disabled = true;
    if (checkoutFormFields) checkoutFormFields.style.opacity = '0.4';
    return;
  }

  if (checkoutBtn) checkoutBtn.disabled = false;
  if (checkoutFormFields) checkoutFormFields.style.opacity = '1';

  let subtotal = 0;

  list.innerHTML = cart.map(item => {
    // Look up emoji in local mapping or set default
    const matchingProd = allProducts.find(p => p.id === item.productId);
    const category = matchingProd ? matchingProd.category : 'Default';
    const emoji = categoryIcons[category] || categoryIcons.Default;
    const itemTotal = item.price * item.quantity;
    subtotal += itemTotal;

    return `
      <div class="cart-item">
        <div class="cart-item-img-box">${emoji}</div>
        <div class="cart-item-info">
          <h3>${item.name}</h3>
          <p>$${item.price.toFixed(2)} each</p>
        </div>
        <div class="quantity-selector">
          <button class="qty-btn" onclick="updateCartItemQty(${item.productId}, -1)">-</button>
          <div class="qty-val">${item.quantity}</div>
          <button class="qty-btn" onclick="updateCartItemQty(${item.productId}, 1)">+</button>
        </div>
        <div class="cart-item-price">$${itemTotal.toFixed(2)}</div>
        <button class="cart-item-remove" onclick="removeCartItem(${item.productId})">✕</button>
      </div>
    `;
  }).join('');

  if (summarySubtotal) summarySubtotal.textContent = `$${subtotal.toFixed(2)}`;
  if (summaryTotal) summaryTotal.textContent = `$${subtotal.toFixed(2)}`;
}

window.updateCartItemQty = function(productId, delta) {
  const item = cart.find(i => i.productId === productId);
  if (!item) return;

  if (item.quantity + delta <= 0) {
    removeCartItem(productId);
    return;
  }

  // To check stock we must run async or rely on cached info. For UI safety, let's update and server will validate
  item.quantity += delta;
  saveCart();
  renderCart();
};

window.removeCartItem = function(productId) {
  cart = cart.filter(i => i.productId !== productId);
  saveCart();
  renderCart();
  showToast('Item removed from cart', 'info');
};

function setupCheckoutForm() {
  const form = document.getElementById('checkout-form');
  const container = document.getElementById('cart-page-container');
  if (!form || !container) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (cart.length === 0) {
      showToast('Your cart is empty!', 'error');
      return;
    }

    const customerName = document.getElementById('cust-name').value.trim();
    const customerEmail = document.getElementById('cust-email').value.trim();
    const shippingAddress = document.getElementById('cust-address').value.trim();

    if (!customerName || !customerEmail || !shippingAddress) {
      showToast('Please fill out all billing and shipping fields.', 'error');
      return;
    }

    const orderData = {
      customerName,
      customerEmail,
      shippingAddress,
      items: cart.map(item => ({
        productId: item.productId,
        quantity: item.quantity
      }))
    };

    // Disable button to prevent double submit
    const submitBtn = document.getElementById('checkout-submit-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing transaction...';

    try {
      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderData)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Checkout process failed.');
      }

      // Success! Clear cart
      cart = [];
      saveCart();

      // Render success screen
      container.innerHTML = `
        <div class="order-success-card">
          <div class="success-badge-icon">✓</div>
          <h2>Transaction Confirmed</h2>
          <p>Thank you for shopping with us. Your luxury workspace upgrade order has been processed successfully.</p>
          <div class="order-id-label">ORDER ID: #${String(result.orderId).padStart(6, '0')}</div>
          <p style="font-size: 0.9rem; color: var(--text-muted);">A confirmation summary has been logged. Total charged: $${result.totalAmount.toFixed(2)}</p>
          <a href="/" class="hero-btn" style="text-shadow: none; margin-top: 1.5rem;">Continue Shopping</a>
        </div>
      `;
      showToast('Order created successfully!', 'success');

    } catch (err) {
      showToast(err.message, 'error');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Complete Order';
    }
  });
}
