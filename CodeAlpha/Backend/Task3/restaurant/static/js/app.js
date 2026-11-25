// Restaurant Management System - Frontend SPA Controller
document.addEventListener('DOMContentLoaded', () => {
    // Application State
    const state = {
        activeTab: 'dashboard',
        menu: [],
        tables: [],
        orders: [],
        reservations: [],
        inventory: [],
        cart: [], // {menuItem, quantity}
        stats: {
            total_sales: 0.00,
            active_orders: 0,
            low_stock_count: 0,
            tables: { occupied: 0, reserved: 0, available: 0, total: 0 }
        }
    };

    // DOM Elements
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const toastContainer = document.getElementById('toast-container');

    // Sidebar navigation switching
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });

    function switchTab(tabId) {
        state.activeTab = tabId;
        
        // Update nav items active state
        navItems.forEach(item => {
            if (item.getAttribute('data-tab') === tabId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Update tab contents visibility
        tabContents.forEach(content => {
            if (content.id === `${tabId}-tab`) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });

        // Load tab-specific data
        refreshData();
    }

    // Refresh Data depending on current active tab
    function refreshData() {
        fetchDashboardStats();
        fetchTables();
        
        if (state.activeTab === 'dashboard') {
            fetchOrders();
        } else if (state.activeTab === 'menu') {
            fetchMenu();
        } else if (state.activeTab === 'kitchen') {
            fetchOrders();
        } else if (state.activeTab === 'reservations') {
            fetchReservations();
        } else if (state.activeTab === 'inventory') {
            fetchInventory();
        }
    }

    // Toast alerts helper
    window.showToast = function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let iconClass = 'fa-info-circle';
        if (type === 'success') iconClass = 'fa-check-circle';
        if (type === 'error') iconClass = 'fa-exclamation-circle';
        if (type === 'warning') iconClass = 'fa-exclamation-triangle';

        toast.innerHTML = `
            <i class="fas ${iconClass}"></i>
            <span>${message}</span>
        `;
        
        toastContainer.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 50);

        // Auto remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    };

    // API fetches
    async function fetchDashboardStats() {
        try {
            const res = await fetch('/api/dashboard-stats/');
            const data = await res.json();
            if (data.status === 'success') {
                state.stats = data.stats;
                updateStatsUI();
            }
        } catch (err) {
            console.error('Error fetching stats:', err);
        }
    }

    function updateStatsUI() {
        const totalSalesEl = document.getElementById('stat-total-sales');
        const activeOrdersEl = document.getElementById('stat-active-orders');
        const lowStockEl = document.getElementById('stat-low-stock');
        const tableOccupancyEl = document.getElementById('stat-table-occupancy');

        if (totalSalesEl) totalSalesEl.innerText = `$${state.stats.total_sales.toFixed(2)}`;
        if (activeOrdersEl) activeOrdersEl.innerText = state.stats.active_orders;
        if (lowStockEl) lowStockEl.innerText = state.stats.low_stock_count;
        
        if (tableOccupancyEl) {
            const total = state.stats.tables.total || 1;
            const occupied = state.stats.tables.occupied + state.stats.tables.reserved;
            const percentage = Math.round((occupied / total) * 100);
            tableOccupancyEl.innerText = `${percentage}%`;
        }
    }

    async function fetchTables() {
        try {
            const res = await fetch('/api/tables/');
            const data = await res.json();
            if (data.status === 'success') {
                state.tables = data.tables;
                renderTablesLayout();
                updateTableOptionsInForms();
            }
        } catch (err) {
            console.error('Error fetching tables:', err);
        }
    }

    function renderTablesLayout() {
        const layoutGrid = document.getElementById('tables-layout');
        if (!layoutGrid) return;
        
        layoutGrid.innerHTML = '';
        state.tables.forEach(table => {
            const tableEl = document.createElement('div');
            tableEl.className = `restaurant-table ${table.status}`;
            tableEl.innerHTML = `
                <div class="table-badge"></div>
                <div class="table-num">T-${table.table_number}</div>
                <div class="table-capacity"><i class="fas fa-users"></i> Max ${table.capacity}</div>
                <div style="font-size: 0.75rem; text-transform:capitalize; margin-top:2px;">${table.status}</div>
            `;
            
            // Allow setting table occupied/available from layout directly
            tableEl.addEventListener('click', () => {
                showTableActionsModal(table);
            });
            
            layoutGrid.appendChild(tableEl);
        });
    }

    function updateTableOptionsInForms() {
        const selectEls = document.querySelectorAll('.table-select-dropdown');
        selectEls.forEach(select => {
            const currentVal = select.value;
            select.innerHTML = '<option value="">-- Choose Table --</option>';
            state.tables.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.id;
                opt.innerText = `Table ${t.table_number} (Capacity: ${t.capacity}) - ${t.status}`;
                if (t.status !== 'available' && currentVal != t.id) {
                    opt.disabled = true;
                }
                select.appendChild(opt);
            });
            if (currentVal) select.value = currentVal;
        });
    }

    async function fetchMenu() {
        try {
            const res = await fetch('/api/menu/');
            const data = await res.json();
            if (data.status === 'success') {
                state.menu = data.menu;
                renderMenuGrid();
            }
        } catch (err) {
            console.error('Error fetching menu:', err);
        }
    }

    let activeMenuFilter = 'all';
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeMenuFilter = btn.getAttribute('data-category');
            renderMenuGrid();
        });
    });

    function renderMenuGrid() {
        const grid = document.getElementById('menu-items-grid');
        if (!grid) return;
        
        grid.innerHTML = '';
        const filteredMenu = activeMenuFilter === 'all' 
            ? state.menu 
            : state.menu.filter(item => item.category === activeMenuFilter);

        filteredMenu.forEach(item => {
            const card = document.createElement('div');
            card.className = 'menu-card';
            
            const categoryIcons = {
                appetizer: '🥗',
                main: '🍔',
                dessert: '🍰',
                beverage: '☕'
            };
            const icon = categoryIcons[item.category] || '🍽️';

            card.innerHTML = `
                <div class="menu-image-container">
                    <span class="menu-category-tag">${item.category}</span>
                    <span>${icon}</span>
                </div>
                <div class="menu-card-body">
                    <div class="menu-item-title">
                        <span>${item.name}</span>
                        <span class="menu-item-price">$${item.price.toFixed(2)}</span>
                    </div>
                    <p class="menu-item-desc">${item.description}</p>
                    <div class="menu-card-footer">
                        ${item.is_available 
                            ? `<button class="btn-primary add-to-cart-btn" data-id="${item.id}" style="width: 100%; justify-content: center;"><i class="fas fa-plus"></i> Add to Cart</button>`
                            : `<button class="btn-secondary" style="width: 100%; cursor: not-allowed; opacity: 0.6;" disabled>Out of Stock</button>`
                        }
                    </div>
                </div>
            `;
            
            const addBtn = card.querySelector('.add-to-cart-btn');
            if (addBtn) {
                addBtn.addEventListener('click', () => addToCart(item));
            }

            grid.appendChild(card);
        });
    }

    // Cart operations
    function addToCart(menuItem) {
        const existing = state.cart.find(c => c.menuItem.id === menuItem.id);
        if (existing) {
            existing.quantity += 1;
        } else {
            state.cart.push({ menuItem, quantity: 1 });
        }
        updateCartUI();
        showToast(`${menuItem.name} added to cart`, 'success');
    }

    function updateCartUI() {
        const countBadge = document.getElementById('cart-badge');
        const cartList = document.getElementById('cart-items');
        const cartTotal = document.getElementById('cart-total-val');
        
        let totalCount = 0;
        let totalPrice = 0;
        
        if (cartList) cartList.innerHTML = '';
        
        state.cart.forEach((item, index) => {
            totalCount += item.quantity;
            totalPrice += item.menuItem.price * item.quantity;
            
            if (cartList) {
                const itemEl = document.createElement('div');
                itemEl.className = 'cart-item';
                itemEl.innerHTML = `
                    <div class="cart-item-info">
                        <h4>${item.menuItem.name}</h4>
                        <p>$${(item.menuItem.price * item.quantity).toFixed(2)}</p>
                    </div>
                    <div class="cart-item-qty">
                        <button class="qty-btn dec-qty" data-index="${index}">-</button>
                        <span>${item.quantity}</span>
                        <button class="qty-btn inc-qty" data-index="${index}">+</button>
                    </div>
                `;
                
                itemEl.querySelector('.dec-qty').addEventListener('click', () => adjustCartQty(index, -1));
                itemEl.querySelector('.inc-qty').addEventListener('click', () => adjustCartQty(index, 1));
                
                cartList.appendChild(itemEl);
            }
        });

        if (countBadge) countBadge.innerText = totalCount;
        if (cartTotal) cartTotal.innerText = `$${totalPrice.toFixed(2)}`;
    }

    function adjustCartQty(index, delta) {
        state.cart[index].quantity += delta;
        if (state.cart[index].quantity <= 0) {
            state.cart.splice(index, 1);
        }
        updateCartUI();
    }

    // Cart drawer toggles
    const cartToggle = document.getElementById('cart-toggle-btn');
    const closeCart = document.getElementById('close-cart-btn');
    const cartDrawer = document.getElementById('cart-drawer');

    if (cartToggle) {
        cartToggle.addEventListener('click', () => {
            cartDrawer.classList.toggle('open');
        });
    }
    if (closeCart) {
        closeCart.addEventListener('click', () => {
            cartDrawer.classList.remove('open');
        });
    }

    // Place Order submission
    const placeOrderForm = document.getElementById('place-order-form');
    if (placeOrderForm) {
        placeOrderForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const tableId = document.getElementById('order-table-select').value;
            if (!tableId) {
                showToast('Please select a table for the order.', 'warning');
                return;
            }
            if (state.cart.length === 0) {
                showToast('Your cart is empty.', 'warning');
                return;
            }

            const items = state.cart.map(c => ({
                menu_item_id: c.menuItem.id,
                quantity: c.quantity
            }));

            try {
                const response = await fetch('/api/orders/create/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ table_id: tableId, items })
                });
                const data = await response.json();
                
                if (data.status === 'success') {
                    showToast('Order placed successfully!', 'success');
                    state.cart = [];
                    updateCartUI();
                    cartDrawer.classList.remove('open');
                    refreshData();
                } else {
                    showToast(data.message || 'Failed to place order.', 'error');
                }
            } catch (err) {
                showToast('Connection error occurred.', 'error');
            }
        });
    }

    // Kitchen Order board (Kanban)
    async function fetchOrders() {
        try {
            const res = await fetch('/api/orders/');
            const data = await res.json();
            if (data.status === 'success') {
                state.orders = data.orders;
                renderKitchenBoard();
                renderRecentOrdersTable();
            }
        } catch (err) {
            console.error('Error fetching orders:', err);
        }
    }

    function renderKitchenBoard() {
        const columns = {
            pending: document.getElementById('col-pending'),
            preparing: document.getElementById('col-preparing'),
            completed: document.getElementById('col-completed'),
            cancelled: document.getElementById('col-cancelled')
        };
        
        // Reset lists
        Object.keys(columns).forEach(status => {
            if (columns[status]) {
                columns[status].innerHTML = '';
                const countEl = document.getElementById(`count-${status}`);
                if (countEl) countEl.innerText = 0;
            }
        });

        state.orders.forEach(order => {
            const col = columns[order.status];
            if (!col) return;
            
            // Increment header count
            const countEl = document.getElementById(`count-${order.status}`);
            if (countEl) countEl.innerText = parseInt(countEl.innerText) + 1;

            const card = document.createElement('div');
            card.className = 'order-card';
            
            const itemsSummary = order.items.map(i => `${i.quantity}x ${i.menu_item_name}`).join(', ');

            let actionButtons = '';
            if (order.status === 'pending') {
                actionButtons = `
                    <button class="action-icon-btn next" onclick="updateOrderStatus(${order.id}, 'preparing')"><i class="fas fa-play"></i></button>
                    <button class="action-icon-btn cancel" onclick="updateOrderStatus(${order.id}, 'cancelled')"><i class="fas fa-times"></i></button>
                `;
            } else if (order.status === 'preparing') {
                actionButtons = `
                    <button class="action-icon-btn next" onclick="updateOrderStatus(${order.id}, 'completed')"><i class="fas fa-check"></i></button>
                    <button class="action-icon-btn cancel" onclick="updateOrderStatus(${order.id}, 'cancelled')"><i class="fas fa-times"></i></button>
                `;
            }

            card.innerHTML = `
                <div class="order-card-header">
                    <span class="order-id">Order #${order.id}</span>
                    <span class="order-time">${order.created_at.split(' ')[1]}</span>
                </div>
                <div class="order-items-summary">${itemsSummary}</div>
                <div class="order-footer">
                    <span class="order-table-badge">Table ${order.table_number}</span>
                    <div class="order-actions">
                        ${actionButtons}
                    </div>
                </div>
            `;
            col.appendChild(card);
        });
    }

    function renderRecentOrdersTable() {
        const tbody = document.getElementById('recent-orders-list');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        // take first 5 recent orders
        state.orders.slice(0, 5).forEach(order => {
            const tr = document.createElement('tr');
            const itemsSummary = order.items.map(i => `${i.quantity}x ${i.menu_item_name}`).join(', ');
            tr.innerHTML = `
                <td>#${order.id}</td>
                <td>Table ${order.table_number}</td>
                <td><span class="status-badge ${order.status}">${order.status}</span></td>
                <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${itemsSummary}</td>
                <td>$${order.total_amount.toFixed(2)}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    window.updateOrderStatus = async function(orderId, status) {
        try {
            const response = await fetch(`/api/orders/${orderId}/status/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });
            const data = await response.json();
            if (data.status === 'success') {
                showToast(`Order #${orderId} marked as ${status}`, 'success');
                refreshData();
            } else {
                showToast(data.message, 'error');
            }
        } catch (err) {
            showToast('Failed to update order status.', 'error');
        }
    };

    // Reservations Operations
    async function fetchReservations() {
        try {
            const res = await fetch('/api/reservations/');
            const data = await res.json();
            if (data.status === 'success') {
                state.reservations = data.reservations;
                renderReservationsTable();
            }
        } catch (err) {
            console.error('Error fetching reservations:', err);
        }
    }

    function renderReservationsTable() {
        const tbody = document.getElementById('reservations-list');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        state.reservations.forEach(res => {
            const tr = document.createElement('tr');
            
            let actions = '';
            if (res.status === 'pending') {
                actions = `
                    <button class="btn-primary" onclick="updateReservationStatus(${res.id}, 'confirmed')" style="padding: 4px 8px; font-size:0.8rem; display:inline-flex;"><i class="fas fa-check"></i></button>
                    <button class="btn-secondary" onclick="updateReservationStatus(${res.id}, 'cancelled')" style="padding: 4px 8px; font-size:0.8rem; display:inline-flex;"><i class="fas fa-times"></i></button>
                `;
            }
            
            tr.innerHTML = `
                <td>${res.customer_name}</td>
                <td>${res.customer_phone}</td>
                <td>Table ${res.table_number}</td>
                <td>${res.reservation_time}</td>
                <td>${res.number_of_guests} guests</td>
                <td><span class="status-badge ${res.status}">${res.status}</span></td>
                <td>
                    <div style="display:flex; gap: 4px;">
                        ${actions}
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    window.updateReservationStatus = async function(resId, status) {
        try {
            const response = await fetch(`/api/reservations/${resId}/status/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });
            const data = await response.json();
            if (data.status === 'success') {
                showToast(`Reservation status updated!`, 'success');
                refreshData();
            } else {
                showToast(data.message, 'error');
            }
        } catch (err) {
            showToast('Failed to update reservation status.', 'error');
        }
    };

    // Reservation creation modal toggles
    const openResModal = document.getElementById('btn-open-reservation-modal');
    const closeResModal = document.getElementById('btn-close-reservation-modal');
    const resModal = document.getElementById('reservation-modal');

    if (openResModal) {
        openResModal.addEventListener('click', () => {
            resModal.classList.add('open');
        });
    }
    if (closeResModal) {
        closeResModal.addEventListener('click', () => {
            resModal.classList.remove('open');
        });
    }

    const reservationForm = document.getElementById('new-reservation-form');
    if (reservationForm) {
        reservationForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                customer_name: document.getElementById('res-name').value,
                customer_email: document.getElementById('res-email').value,
                customer_phone: document.getElementById('res-phone').value,
                number_of_guests: parseInt(document.getElementById('res-guests').value),
                reservation_time: document.getElementById('res-time').value
            };

            try {
                const response = await fetch('/api/reservations/create/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();
                
                if (data.status === 'success') {
                    showToast(data.message, 'success');
                    resModal.classList.remove('open');
                    reservationForm.reset();
                    refreshData();
                } else {
                    showToast(data.message || 'Could not place reservation.', 'error');
                }
            } catch (err) {
                showToast('Connection error occurred.', 'error');
            }
        });
    }

    // Inventory operations
    async function fetchInventory() {
        try {
            const res = await fetch('/api/inventory/');
            const data = await res.json();
            if (data.status === 'success') {
                state.inventory = data.inventory;
                renderInventoryTable();
            }
        } catch (err) {
            console.error('Error fetching inventory:', err);
        }
    }

    function renderInventoryTable() {
        const tbody = document.getElementById('inventory-list');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        state.inventory.forEach(item => {
            const tr = document.createElement('tr');
            
            const alertClass = item.needs_reorder ? 'status-badge cancelled' : 'status-badge completed';
            const alertText = item.needs_reorder ? 'Low Stock' : 'Good';

            tr.innerHTML = `
                <td><strong>${item.name}</strong></td>
                <td>${item.quantity.toFixed(2)} ${item.unit}</td>
                <td>${item.reorder_level} ${item.unit}</td>
                <td><span class="${alertClass}">${alertText}</span></td>
                <td>
                    <div class="stock-refill-widget">
                        <input type="number" step="any" min="0.1" id="refill-${item.id}" placeholder="Qty" class="form-control" style="width: 80px; padding: 4px 8px; margin-right: 4px;">
                        <button class="btn-primary" onclick="refillStock(${item.id})" style="padding: 4px 10px; font-size: 0.8rem;"><i class="fas fa-plus"></i> Add</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    window.refillStock = async function(itemId) {
        const input = document.getElementById(`refill-${itemId}`);
        const val = parseFloat(input.value);
        if (isNaN(val) || val <= 0) {
            showToast('Enter a valid amount to add.', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/inventory/${itemId}/update-stock/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ quantity: val })
            });
            const data = await response.json();
            if (data.status === 'success') {
                showToast(data.message, 'success');
                refreshData();
            } else {
                showToast(data.message, 'error');
            }
        } catch (err) {
            showToast('Failed to refill inventory.', 'error');
        }
    };

    // Table settings Modal actions
    const tableActionsModal = document.getElementById('table-actions-modal');
    const closeTableModal = document.getElementById('btn-close-table-modal');
    const tableNumTitle = document.getElementById('table-num-title');
    const tableStatusDropdown = document.getElementById('table-status-action');
    const tableActionForm = document.getElementById('table-action-form');
    let selectedTable = null;

    if (closeTableModal) {
        closeTableModal.addEventListener('click', () => {
            tableActionsModal.classList.remove('open');
        });
    }

    function showTableActionsModal(table) {
        selectedTable = table;
        if (tableNumTitle) tableNumTitle.innerText = `Manage Table ${table.table_number}`;
        if (tableStatusDropdown) tableStatusDropdown.value = table.status;
        if (tableActionsModal) tableActionsModal.classList.add('open');
    }

    // Since we don't have a direct API to update table status only, let's create a quick API or just mock it.
    // Actually, we can update the table status by creating an empty order or changing it. Let's make an API for updating table status in views.py if we need to.
    // Wait, let's look at views.py. We don't have an explicit table status update endpoint, but we can easily add one if needed! Or we can use update_order_status / place_order to set it.
    // Let's create an endpoint in views.py for updating table status directly:
    // Let's check if we can add a table status update API. Yes, it's very easy to add, but we can also just handle it smoothly. Let's write the table status update endpoint!
    // But wait! We can just call a POST to `/api/tables/<int:table_id>/status/` in restaurant/views.py. Let's do that to make it clean!
    // For now, let's draft the JS call to `/api/tables/${selectedTable.id}/status/` in the form submit.
    if (tableActionForm) {
        tableActionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!selectedTable) return;
            const newStatus = tableStatusDropdown.value;

            try {
                const response = await fetch(`/api/tables/${selectedTable.id}/status/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await response.json();
                if (data.status === 'success') {
                    showToast(`Table ${selectedTable.table_number} status updated to ${newStatus}`, 'success');
                    tableActionsModal.classList.remove('open');
                    refreshData();
                } else {
                    showToast(data.message || 'Failed to update table.', 'error');
                }
            } catch (err) {
                showToast('Connection error occurred.', 'error');
            }
        });
    }

    // Initial load
    refreshData();
});
