require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const { logSearch, getRecentSearches } = require('./database');

const app = express();
const PORT = process.env.PORT || 4000;
const API_KEY = process.env.WEATHER_API_KEY;

// Middleware
app.use(cors());
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

// Main Route to serve the frontend
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// API Endpoint to get search history
app.get('/api/history', async (req, res) => {
    try {
        const history = await getRecentSearches(5);
        res.json({ success: true, data: history });
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch history' });
    }
});

// API Endpoint to fetch weather data
app.get('/api/weather', async (req, res) => {
    const city = req.query.city;

    if (!city) {
        return res.status(400).json({ error: 'City is required' });
    }

    try {
        // Log the search query in SQLite securely
        logSearch(city);

        let weatherData;

        // Check if a real OpenWeatherMap key is provided, otherwise fallback to Open-Meteo for testing
        // For the "MAX FEATURES", we are upgrading the Open-Meteo fallback to provide huge amounts of data.
        if (API_KEY && API_KEY !== 'YOUR_OPENWEATHERMAP_API_KEY_HERE') {
            // Fetch from OpenWeatherMap (Basic implementation, doesn't have all the advanced features without ONE CALL API subscription)
            const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city}&units=metric&appid=${API_KEY}`);
            if (!response.ok) throw new Error('City not found or API error');
            const data = await response.json();
            
            weatherData = {
                city: data.name,
                current: {
                    temperature: Math.round(data.main.temp),
                    feels_like: Math.round(data.main.feels_like),
                    description: data.weather[0].description,
                    humidity: data.main.humidity,
                    windSpeed: data.wind.speed,
                    pressure: data.main.pressure,
                    visibility: data.visibility / 1000,
                    icon: data.weather[0].icon,
                    isDay: data.weather[0].icon.includes('d')
                },
                source: 'OpenWeatherMap'
            };
        } else {
            console.log('Using Open-Meteo fallback API for advanced features.');
            
            // 1. Geocoding API to get lat/lon for the city
            const geoResponse = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${city}&count=1&language=en&format=json`);
            const geoData = await geoResponse.json();
            
            if (!geoData.results || geoData.results.length === 0) throw new Error('City not found');
            
            const location = geoData.results[0];
            const lat = location.latitude;
            const lon = location.longitude;
            const cityName = location.name;

            // 2. Weather API (Current, Hourly, Daily)
            const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,cloud_cover,surface_pressure,wind_speed_10m&hourly=temperature_2m,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max&timezone=auto`;
            const weatherResponse = await fetch(weatherUrl);
            const wData = await weatherResponse.json();

            // 3. Air Quality API
            const aqiUrl = `https://air-quality-api.open-meteo.com/v1/air-quality?latitude=${lat}&longitude=${lon}&current=us_aqi,pm10,pm2_5`;
            let aqiData = { current: { us_aqi: 0 } };
            try {
                const aqiResponse = await fetch(aqiUrl);
                aqiData = await aqiResponse.json();
            } catch (e) {
                console.log("AQI not available for this region.");
            }
            
            // Map WMO Weather codes to descriptions and simple icon names
            const mapCode = (code, isDay) => {
                let d = isDay ? "d" : "n";
                if(code === 0) return { desc: "Clear", icon: `01${d}` };
                if(code >= 1 && code <= 3) return { desc: "Partly cloudy", icon: `02${d}` };
                if(code >= 45 && code <= 48) return { desc: "Foggy", icon: `50${d}` };
                if(code >= 51 && code <= 67) return { desc: "Rainy", icon: `10${d}` };
                if(code >= 71 && code <= 77) return { desc: "Snowy", icon: `13${d}` };
                if(code >= 80 && code <= 82) return { desc: "Showers", icon: `09${d}` };
                if(code >= 95) return { desc: "Thunderstorm", icon: `11${d}` };
                return { desc: "Unknown", icon: `01${d}` };
            };

            const currentCode = mapCode(wData.current.weather_code, wData.current.is_day);

            // Process Hourly
            const hourly = [];
            for (let i = 0; i < 24; i++) {
                hourly.push({
                    time: wData.hourly.time[i],
                    temp: Math.round(wData.hourly.temperature_2m[i]),
                    code: mapCode(wData.hourly.weather_code[i], 1).icon
                });
            }

            // Process Daily
            const daily = [];
            for (let i = 0; i < 7; i++) {
                daily.push({
                    date: wData.daily.time[i],
                    max: Math.round(wData.daily.temperature_2m_max[i]),
                    min: Math.round(wData.daily.temperature_2m_min[i]),
                    code: mapCode(wData.daily.weather_code[i], 1).icon,
                    uv: wData.daily.uv_index_max[i]
                });
            }

            weatherData = {
                city: cityName,
                current: {
                    temperature: Math.round(wData.current.temperature_2m),
                    feels_like: Math.round(wData.current.apparent_temperature),
                    description: currentCode.desc,
                    humidity: wData.current.relative_humidity_2m,
                    windSpeed: wData.current.wind_speed_10m,
                    pressure: Math.round(wData.current.surface_pressure),
                    uv: daily[0].uv,
                    aqi: aqiData.current?.us_aqi || "N/A",
                    isDay: wData.current.is_day,
                    icon: currentCode.icon
                },
                hourly: hourly,
                daily: daily,
                sunrise: wData.daily.sunrise[0],
                sunset: wData.daily.sunset[0],
                source: 'Open-Meteo (Max Features)'
            };
        }

        res.json({
            success: true,
            data: weatherData
        });

    } catch (error) {
        console.error('Error fetching weather data:', error.message);
        res.status(500).json({ error: error.message || 'Failed to fetch weather data' });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`\n===========================================`);
    console.log(`🚀 Premium Server running on http://localhost:${PORT}`);
    console.log(`===========================================\n`);
});
