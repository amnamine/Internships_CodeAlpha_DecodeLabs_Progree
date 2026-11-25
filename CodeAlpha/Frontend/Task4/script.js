// Track Database
const trackList = [
    {
        id: 1,
        title: "Neon Horizon",
        artist: "Cosimo Fogg",
        src: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        cover: "assets/synthwave.png",
        accent: "#ec4899", // Magenta/pink
        accentGlow: "rgba(236, 72, 153, 0.4)",
        bgStart: "#1e1b4b", // Deep indigo
        bgEnd: "#030712"
    },
    {
        id: 2,
        title: "Rainy Afternoon",
        artist: "Lofi Dreamer",
        src: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        cover: "assets/lofi.png",
        accent: "#f59e0b", // Warm Amber
        accentGlow: "rgba(245, 158, 11, 0.4)",
        bgStart: "#451a03", // Deep orange/brown
        bgEnd: "#0c0a09"
    },
    {
        id: 3,
        title: "Deep Space Ambient",
        artist: "Solaris Voyager",
        src: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
        cover: "assets/ambient.png",
        accent: "#10b981", // Emerald
        accentGlow: "rgba(16, 185, 129, 0.4)",
        bgStart: "#022c22", // Deep forest green
        bgEnd: "#020617"
    },
    {
        id: 4,
        title: "Nebula Dreams",
        artist: "Astropilot",
        src: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
        cover: "assets/ambient.png", // reusing ambient cover
        accent: "#8b5cf6", // Purple
        accentGlow: "rgba(139, 92, 246, 0.4)",
        bgStart: "#2e1065", // Deep purple
        bgEnd: "#030712"
    }
];

// App State
let currentTrackIndex = 0;
let isPlaying = false;
let isShuffle = false;
let isRepeat = false; // false = no repeat, true = repeat current track
let likedTracks = new Set();
let volume = 0.8;
let isMuted = false;

// Web Audio API Variables
let audioContext, analyser, dataArray, sourceNode;
let animationFrameId;

// DOM Elements
const audio = document.getElementById("audio-player");
const albumCover = document.getElementById("album-cover");
const vinylDisk = document.getElementById("vinyl-disk");
const songTitle = document.getElementById("song-title");
const songArtist = document.getElementById("song-artist");

const playPauseBtn = document.getElementById("btn-play-pause");
const playIcon = document.getElementById("play-icon");
const prevBtn = document.getElementById("btn-prev");
const nextBtn = document.getElementById("btn-next");
const shuffleBtn = document.getElementById("btn-shuffle");
const repeatBtn = document.getElementById("btn-repeat");
const favoriteBtn = document.getElementById("btn-favorite");
const volumeBtn = document.getElementById("btn-volume");
const volumeIcon = document.getElementById("volume-icon");

const currentTimeEl = document.getElementById("current-time");
const totalDurationEl = document.getElementById("total-duration");
const progressBarOuter = document.getElementById("progress-bar-outer");
const progressBarInner = document.getElementById("progress-bar-inner");
const progressHandle = document.getElementById("progress-handle");

const volumeSliderOuter = document.getElementById("volume-slider-outer");
const volumeSliderInner = document.getElementById("volume-slider-inner");

const playlistSearch = document.getElementById("playlist-search");
const tracksListContainer = document.getElementById("tracks-list");
const trackCountEl = document.getElementById("track-count");

const tabButtons = document.querySelectorAll(".tab-btn");
const playerView = document.getElementById("player-view");
const visualizerView = document.getElementById("visualizer-view");
const canvas = document.getElementById("visualizer-canvas");
const canvasCtx = canvas?.getContext("2d");
const visualizerStatus = document.querySelector(".visualizer-status");

// Initialize Application
function init() {
    loadTrack(currentTrackIndex);
    renderPlaylist(trackList);
    setupEventListeners();
    setupCanvasResize();
    lucide.createIcons();
}

// Load Track Details
function loadTrack(index) {
    currentTrackIndex = index;
    const track = trackList[index];

    audio.src = track.src;
    songTitle.textContent = track.title;
    songArtist.textContent = track.artist;
    albumCover.src = track.cover;

    // Apply Dynamic Colors
    document.documentElement.style.setProperty('--accent-color', track.accent);
    document.documentElement.style.setProperty('--accent-glow', track.accentGlow);
    document.documentElement.style.setProperty('--bg-gradient-start', track.bgStart);
    document.documentElement.style.setProperty('--bg-gradient-end', track.bgEnd);

    // Apply animated background color shift
    const blob1 = document.querySelector(".blob-1");
    if (blob1) blob1.style.background = `radial-gradient(circle, ${track.accent} 0%, transparent 70%)`;

    // Highlight playing track in playlist
    updateActivePlaylistItem();

    // Check if Liked
    const heart = favoriteBtn.querySelector(".heart-icon");
    if (likedTracks.has(track.id)) {
        heart.classList.add("liked");
        heart.setAttribute("data-lucide", "heart");
    } else {
        heart.classList.remove("liked");
        heart.setAttribute("data-lucide", "heart");
    }
    lucide.createIcons();

    // Reset progress UI
    progressBarInner.style.width = "0%";
    progressHandle.style.left = "0%";
    currentTimeEl.textContent = "0:00";
    totalDurationEl.textContent = "0:00";
}

// Play Audio
function playTrack() {
    isPlaying = true;
    audio.play()
        .then(() => {
            vinylDisk.classList.add("playing");
            vinylDisk.classList.remove("paused");
            playPauseBtn.innerHTML = `<i data-lucide="pause"></i>`;
            playPauseBtn.classList.add("playing-pulse");
            updateActivePlaylistItemState(true);
            lucide.createIcons();
            initVisualizer();
        })
        .catch(err => {
            console.log("Autoplay / Audio loading failed", err);
            isPlaying = false;
        });
}

// Pause Audio
function pauseTrack() {
    isPlaying = false;
    audio.pause();
    vinylDisk.classList.add("paused");
    playPauseBtn.innerHTML = `<i data-lucide="play"></i>`;
    playPauseBtn.classList.remove("playing-pulse");
    updateActivePlaylistItemState(false);
    lucide.createIcons();
}

// Toggle Play/Pause
function togglePlay() {
    if (isPlaying) {
        pauseTrack();
    } else {
        playTrack();
    }
}

// Previous Track
function prevTrack() {
    let index = currentTrackIndex - 1;
    if (index < 0) {
        index = trackList.length - 1;
    }
    loadTrack(index);
    if (isPlaying) playTrack();
}

// Next Track
function nextTrack() {
    if (isShuffle) {
        let index;
        do {
            index = Math.floor(Math.random() * trackList.length);
        } while (index === currentTrackIndex && trackList.length > 1);
        loadTrack(index);
    } else {
        let index = currentTrackIndex + 1;
        if (index >= trackList.length) {
            index = 0;
        }
        loadTrack(index);
    }
    if (isPlaying) playTrack();
}

// Time formatting (MM:SS)
function formatTime(seconds) {
    if (isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

// Update Audio Progress
function updateProgress(e) {
    if (!audio.duration) return;
    const { currentTime, duration } = e.srcElement;
    
    // Update timestamps
    currentTimeEl.textContent = formatTime(currentTime);
    totalDurationEl.textContent = formatTime(duration);

    // Update Progress Slider
    const progressPercent = (currentTime / duration) * 100;
    progressBarInner.style.width = `${progressPercent}%`;
    progressHandle.style.left = `${progressPercent}%`;
}

// Seek Audio
function seekAudio(e) {
    const width = progressBarOuter.clientWidth;
    const clickX = e.offsetX;
    const duration = audio.duration;
    
    if (duration) {
        audio.currentTime = (clickX / width) * duration;
    }
}

// Seek Volume
function seekVolume(e) {
    const width = volumeSliderOuter.clientWidth;
    const clickX = e.offsetX;
    const percentage = clickX / width;
    
    volume = Math.max(0, Math.min(1, percentage));
    audio.volume = volume;
    isMuted = (volume === 0);
    updateVolumeUI();
}

// Update Volume Icon & bar
function updateVolumeUI() {
    volumeSliderInner.style.width = `${volume * 100}%`;
    
    if (isMuted || volume === 0) {
        volumeIcon.setAttribute("data-lucide", "volume-x");
    } else if (volume < 0.4) {
        volumeIcon.setAttribute("data-lucide", "volume");
    } else if (volume < 0.7) {
        volumeIcon.setAttribute("data-lucide", "volume-1");
    } else {
        volumeIcon.setAttribute("data-lucide", "volume-2");
    }
    lucide.createIcons();
}

// Toggle Mute
function toggleMute() {
    isMuted = !isMuted;
    if (isMuted) {
        audio.volume = 0;
    } else {
        audio.volume = volume;
    }
    updateVolumeUI();
}

// Toggle Shuffle
function toggleShuffle() {
    isShuffle = !isShuffle;
    shuffleBtn.classList.toggle("active", isShuffle);
}

// Toggle Repeat
function toggleRepeat() {
    isRepeat = !isRepeat;
    repeatBtn.classList.toggle("active", isRepeat);
}

// Toggle Like
function toggleFavorite() {
    const track = trackList[currentTrackIndex];
    const heart = favoriteBtn.querySelector(".heart-icon");
    if (likedTracks.has(track.id)) {
        likedTracks.delete(track.id);
        heart.classList.remove("liked");
    } else {
        likedTracks.add(track.id);
        heart.classList.add("liked");
    }
}

// Render Playlist HTML
function renderPlaylist(tracks) {
    tracksListContainer.innerHTML = "";
    trackCountEl.textContent = `${tracks.length} track${tracks.length !== 1 ? 's' : ''}`;

    tracks.forEach((track, i) => {
        // Find index in original array
        const originalIndex = trackList.findIndex(t => t.id === track.id);
        
        const item = document.createElement("div");
        item.classList.add("track-item");
        item.setAttribute("data-index", originalIndex);
        if (originalIndex === currentTrackIndex) {
            item.classList.add("active");
            if (isPlaying) item.classList.add("playing");
        }

        item.innerHTML = `
            <div class="track-number">${(i + 1).toString().padStart(2, '0')}</div>
            <div class="eq-bars">
                <span class="eq-bar"></span>
                <span class="eq-bar"></span>
                <span class="eq-bar"></span>
            </div>
            <div class="track-details">
                <div class="track-title">${track.title}</div>
                <div class="track-artist">${track.artist}</div>
            </div>
            <div class="track-duration">3:00</div>
        `;

        item.addEventListener("click", () => {
            loadTrack(originalIndex);
            playTrack();
        });

        tracksListContainer.appendChild(item);
    });
}

// Filter Playlist
function filterPlaylist(e) {
    const query = e.target.value.toLowerCase();
    const filtered = trackList.filter(track => 
        track.title.toLowerCase().includes(query) || 
        track.artist.toLowerCase().includes(query)
    );
    renderPlaylist(filtered);
}

// Update Active Playlist Row highlighting
function updateActivePlaylistItem() {
    const items = document.querySelectorAll(".track-item");
    items.forEach(item => {
        const index = parseInt(item.getAttribute("data-index"));
        if (index === currentTrackIndex) {
            item.classList.add("active");
            if (isPlaying) {
                item.classList.add("playing");
            } else {
                item.classList.remove("playing");
            }
        } else {
            item.classList.remove("active", "playing");
        }
    });
}

function updateActivePlaylistItemState(playing) {
    const items = document.querySelectorAll(".track-item");
    items.forEach(item => {
        const index = parseInt(item.getAttribute("data-index"));
        if (index === currentTrackIndex) {
            if (playing) {
                item.classList.add("playing");
            } else {
                item.classList.remove("playing");
            }
        } else {
            item.classList.remove("playing");
        }
    });
}

// Tabs Navigation
function handleTabChange(e) {
    const tabName = e.target.getAttribute("data-tab");
    tabButtons.forEach(btn => btn.classList.remove("active"));
    e.target.classList.add("active");

    if (tabName === "player") {
        playerView.classList.add("active");
        visualizerView.classList.remove("active");
    } else {
        playerView.classList.remove("active");
        visualizerView.classList.add("active");
        initVisualizer();
    }
}

// Initialize Web Audio API and Visualizer
function initVisualizer() {
    if (!canvasCtx || !visualizerView.classList.contains("active")) return;

    if (!audioContext) {
        try {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            
            // Connect nodes
            sourceNode = audioContext.createMediaElementSource(audio);
            sourceNode.connect(analyser);
            analyser.connect(audioContext.destination);
            
            const bufferLength = analyser.frequencyBinCount;
            dataArray = new Uint8Array(bufferLength);
            
            if (visualizerStatus) visualizerStatus.classList.add("hidden");
        } catch (e) {
            console.log("Web Audio API not fully supported or restricted", e);
        }
    }

    if (audioContext && audioContext.state === 'suspended') {
        audioContext.resume();
    }

    cancelAnimationFrame(animationFrameId);
    drawVisualizer();
}

// Draw Loop for Visualizer (Handles real audio input + beautiful simulated fallback if no context)
function drawVisualizer() {
    if (!canvasCtx) return;
    
    animationFrameId = requestAnimationFrame(drawVisualizer);
    
    const width = canvas.width;
    const height = canvas.height;
    canvasCtx.clearRect(0, 0, width, height);

    const trackColor = trackList[currentTrackIndex].accent;

    if (analyser && isPlaying) {
        // Real visualizer data
        analyser.getByteFrequencyData(dataArray);
        const bufferLength = analyser.frequencyBinCount;
        
        // Let's draw a beautiful radial visualizer or wavy bars
        const barWidth = (width / bufferLength) * 1.5;
        let barHeight;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            barHeight = dataArray[i] * 0.75;

            // Gradient for bar
            const grad = canvasCtx.createLinearGradient(x, height, x, height - barHeight);
            grad.addColorStop(0, `${trackColor}11`);
            grad.addColorStop(0.5, `${trackColor}aa`);
            grad.addColorStop(1, '#ffffff');

            canvasCtx.fillStyle = grad;
            // Draw rounded bars
            canvasCtx.beginPath();
            canvasCtx.roundRect(x, height - barHeight, barWidth - 2, barHeight, 4);
            canvasCtx.fill();

            x += barWidth;
        }
    } else {
        // Simulated beautiful visual waves (fallback when paused or context not active)
        const time = Date.now() * 0.003;
        const waveCount = 3;
        
        for (let w = 0; w < waveCount; w++) {
            canvasCtx.beginPath();
            canvasCtx.lineWidth = w === 0 ? 3 : 1.5;
            canvasCtx.strokeStyle = w === 0 ? trackColor : `${trackColor}55`;
            
            const amplitude = isPlaying ? (50 - w * 10) : (10 - w * 2);
            const frequency = 0.01 + w * 0.005;
            
            for (let x = 0; x < width; x++) {
                const y = height / 2 + Math.sin(x * frequency + time + w) * amplitude;
                if (x === 0) {
                    canvasCtx.moveTo(x, y);
                } else {
                    canvasCtx.lineTo(x, y);
                }
            }
            canvasCtx.stroke();
        }
        
        if (!isPlaying && visualizerStatus) {
            visualizerStatus.classList.remove("hidden");
        } else if (visualizerStatus) {
            visualizerStatus.classList.add("hidden");
        }
    }
}

// Adjust canvas display dimensions
function setupCanvasResize() {
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    canvasCtx.scale(window.devicePixelRatio, window.devicePixelRatio);
}

// Keyboard shortcuts & DOM event hooks
function setupEventListeners() {
    // Media controls
    playPauseBtn.addEventListener("click", togglePlay);
    prevBtn.addEventListener("click", prevTrack);
    nextBtn.addEventListener("click", nextTrack);
    shuffleBtn.addEventListener("click", toggleShuffle);
    repeatBtn.addEventListener("click", toggleRepeat);
    favoriteBtn.addEventListener("click", toggleFavorite);
    volumeBtn.addEventListener("click", toggleMute);

    // Audio Element events
    audio.addEventListener("timeupdate", updateProgress);
    audio.addEventListener("ended", () => {
        if (isRepeat) {
            audio.currentTime = 0;
            playTrack();
        } else {
            nextTrack();
        }
    });

    // Loaded metadata to display total duration initially
    audio.addEventListener("loadedmetadata", () => {
        totalDurationEl.textContent = formatTime(audio.duration);
    });

    // Seek actions
    progressBarOuter.addEventListener("click", seekAudio);
    
    // Drag seeking capability
    let isDraggingProgress = false;
    progressBarOuter.addEventListener("mousedown", () => isDraggingProgress = true);
    document.addEventListener("mousemove", (e) => {
        if (isDraggingProgress) {
            const rect = progressBarOuter.getBoundingClientRect();
            const pos = (e.clientX - rect.left) / rect.width;
            const percentage = Math.max(0, Math.min(1, pos));
            progressBarInner.style.width = `${percentage * 100}%`;
            progressHandle.style.left = `${percentage * 100}%`;
            
            if (audio.duration) {
                currentTimeEl.textContent = formatTime(percentage * audio.duration);
            }
        }
    });
    document.addEventListener("mouseup", (e) => {
        if (isDraggingProgress) {
            isDraggingProgress = false;
            const rect = progressBarOuter.getBoundingClientRect();
            const pos = (e.clientX - rect.left) / rect.width;
            const percentage = Math.max(0, Math.min(1, pos));
            if (audio.duration) {
                audio.currentTime = percentage * audio.duration;
            }
        }
    });

    // Drag volume capability
    let isDraggingVolume = false;
    volumeSliderOuter.addEventListener("mousedown", (e) => {
        isDraggingVolume = true;
        seekVolume(e);
    });
    document.addEventListener("mousemove", (e) => {
        if (isDraggingVolume) {
            const rect = volumeSliderOuter.getBoundingClientRect();
            const pos = (e.clientX - rect.left) / rect.width;
            volume = Math.max(0, Math.min(1, pos));
            audio.volume = isMuted ? 0 : volume;
            updateVolumeUI();
        }
    });
    document.addEventListener("mouseup", () => isDraggingVolume = false);

    // Search and tab navigation
    playlistSearch.addEventListener("keyup", filterPlaylist);
    tabButtons.forEach(btn => btn.addEventListener("click", handleTabChange));

    // Resize canvas
    window.addEventListener("resize", setupCanvasResize);

    // Keyboard controls
    document.addEventListener("keydown", (e) => {
        if (document.activeElement === playlistSearch) return;

        if (e.code === "Space") {
            e.preventDefault();
            togglePlay();
        } else if (e.code === "ArrowRight") {
            audio.currentTime = Math.min(audio.duration || 0, audio.currentTime + 5);
        } else if (e.code === "ArrowLeft") {
            audio.currentTime = Math.max(0, audio.currentTime - 5);
        }
    });
}

// Start application
window.addEventListener("DOMContentLoaded", init);
