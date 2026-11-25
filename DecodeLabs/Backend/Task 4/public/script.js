document.addEventListener('DOMContentLoaded', () => {
    const landingState = document.getElementById('landing-state');
    const dashboardWrapper = document.getElementById('dashboard-wrapper');
    const dashboard = document.getElementById('dashboard');
    const loader = document.getElementById('loader');
    const errorMsg = document.getElementById('error-message');
    
    // Forms
    const formLanding = document.getElementById('weather-form');
    const inputLanding = document.getElementById('city-input');
    const historyDropdown = document.getElementById('history-dropdown');
    
    const formActive = document.getElementById('weather-form-active');
    const inputActive = document.getElementById('city-input-active');

    // Dynamic Greeting
    const hour = new Date().getHours();
    const greetingEl = document.getElementById('greeting');
    if(hour < 12) greetingEl.textContent = "Good Morning!";
    else if(hour < 18) greetingEl.textContent = "Good Afternoon!";
    else greetingEl.textContent = "Good Evening!";

    // Fetch history on load for landing page
    fetchHistory();

    // Event Listeners for searching
    formLanding.addEventListener('submit', (e) => {
        e.preventDefault();
        const city = inputLanding.value.trim();
        if (city) executeSearch(city);
    });

    formActive.addEventListener('submit', (e) => {
        e.preventDefault();
        const city = inputActive.value.trim();
        if (city) executeSearch(city);
    });

    // History Dropdown logic
    inputLanding.addEventListener('focus', () => {
        if (historyDropdown.children.length > 0) historyDropdown.classList.remove('hidden');
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.input-wrapper')) {
            historyDropdown.classList.add('hidden');
        }
    });

    // Suggestion Cards logic
    const suggestionCards = document.querySelectorAll('.suggestion-card');
    suggestionCards.forEach(card => {
        card.addEventListener('click', () => {
            const city = card.getAttribute('data-city');
            executeSearch(city);
        });
    });

    async function fetchHistory() {
        try {
            const res = await fetch('/api/history');
            const data = await res.json();
            if (data.success && data.data.length > 0) {
                historyDropdown.innerHTML = '';
                data.data.forEach(city => {
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.textContent = city;
                    div.addEventListener('click', () => {
                        inputLanding.value = city;
                        historyDropdown.classList.add('hidden');
                        executeSearch(city);
                    });
                    historyDropdown.appendChild(div);
                });
            }
        } catch (e) {
            console.error(e);
        }
    }

    async function executeSearch(city) {
        // Switch to dashboard view mode
        landingState.classList.add('hidden');
        dashboardWrapper.classList.remove('hidden');
        dashboard.classList.add('hidden');
        errorMsg.classList.add('hidden');
        loader.classList.remove('hidden');
        
        // Sync inputs
        inputActive.value = city;

        try {
            const res = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
            const data = await res.json();

            loader.classList.add('hidden');

            if (data.success) {
                renderDashboard(data.data);
                fetchHistory(); // Refresh history dropdown for next time
            } else {
                showError(data.error);
            }
        } catch (e) {
            loader.classList.add('hidden');
            showError("Network Error. Please make sure the server is running.");
        }
    }

    function renderDashboard(data) {
        // Theme Update
        document.body.className = data.current.isDay ? 'theme-day' : 'theme-night';

        // Hero Update
        document.getElementById('city-name').textContent = data.city;
        document.getElementById('date-current').textContent = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
        document.getElementById('main-temp').textContent = data.current.temperature;
        document.getElementById('main-desc').textContent = data.current.description;
        document.getElementById('feels-like').textContent = data.current.feels_like;
        document.getElementById('main-icon').src = `https://openweathermap.org/img/wn/${data.current.icon}@4x.png`;

        // Hourly Update
        const hourlyContainer = document.getElementById('hourly-container');
        hourlyContainer.innerHTML = '';
        data.hourly.forEach(hour => {
            const date = new Date(hour.time);
            const timeStr = date.toLocaleTimeString('en-US', { hour: 'numeric', hour12: true });
            hourlyContainer.innerHTML += `
                <div class="hourly-item">
                    <span class="time">${timeStr}</span>
                    <img src="https://openweathermap.org/img/wn/${hour.code}@2x.png" alt="icon">
                    <span class="temp">${hour.temp}°</span>
                </div>
            `;
        });

        // Weekly Update
        const weeklyContainer = document.getElementById('weekly-container');
        weeklyContainer.innerHTML = '';
        data.daily.forEach((day, index) => {
            const date = new Date(day.date);
            const dayName = index === 0 ? 'Today' : date.toLocaleDateString('en-US', { weekday: 'short' });
            weeklyContainer.innerHTML += `
                <div class="weekly-item">
                    <span class="day">${dayName}</span>
                    <div class="icon-wrapper">
                        <img src="https://openweathermap.org/img/wn/${day.code}@2x.png">
                        ${day.uv > 7 ? `<span class="uv-badge">UV High</span>` : ''}
                    </div>
                    <div class="temps">
                        <span class="max">${day.max}°</span>
                        <span class="min">${day.min}°</span>
                    </div>
                </div>
            `;
        });

        // Metrics Update
        document.getElementById('aqi-val').textContent = data.current.aqi;
        document.getElementById('uv-val').textContent = data.current.uv;
        document.getElementById('wind-val').textContent = data.current.windSpeed;
        document.getElementById('humidity-val').textContent = data.current.humidity;
        document.getElementById('pressure-val').textContent = data.current.pressure;
        
        // Sun times
        const formatTime = (timeStr) => new Date(timeStr).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        document.getElementById('sunrise').textContent = formatTime(data.sunrise);
        document.getElementById('sunset').textContent = formatTime(data.sunset);

        // Display Dashboard
        dashboard.classList.remove('hidden');
    }

    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.classList.remove('hidden');
    }
});
