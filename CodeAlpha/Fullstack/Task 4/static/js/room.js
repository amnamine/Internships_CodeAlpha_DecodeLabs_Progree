// CoSync - WebRTC Signaling & Collaboration Controller

document.addEventListener('DOMContentLoaded', () => {
    // UI elements selection
    const tabs = document.querySelectorAll('.tab-btn');
    const panes = document.querySelectorAll('.tab-pane');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    const fileDropZone = document.getElementById('fileDropZone');
    const fileInput = document.getElementById('fileInput');
    const sharedFilesList = document.getElementById('sharedFilesList');
    const emptyFilesMessage = document.getElementById('emptyFilesMessage');
    
    // Control buttons
    const btnMic = document.getElementById('btnMic');
    const btnCam = document.getElementById('btnCam');
    const btnScreen = document.getElementById('btnScreen');
    
    // Tab switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            panes.forEach(p => p.classList.remove('active'));
            
            tab.classList.add('active');
            const activePane = document.getElementById(tab.dataset.tab);
            activePane.classList.add('active');
            
            // Resize whiteboard canvas if switching to board tab
            if (tab.dataset.tab === 'tab-whiteboard' && window.boardInstance) {
                window.boardInstance.resizeCanvas();
            }
        });
    });

    // ----------------------------------------------------
    // Collaborative Whiteboard setup
    // ----------------------------------------------------
    const board = new CollaborativeWhiteboard('whiteboardCanvas');
    window.boardInstance = board;
    
    // Broadcast draws using WebRTC Data Channels
    board.onDrawStroke = (x0, y0, x1, y1, color, size) => {
        broadcastData({
            type: 'draw',
            coords: { x0, y0, x1, y1 },
            color: color,
            size: size
        });
    };
    
    // Broadcast clear canvas using Data Channels
    board.onClearBoard = () => {
        broadcastData({ type: 'clear' });
    };

    // ----------------------------------------------------
    // WebRTC Variables & Media Configurations
    // ----------------------------------------------------
    let localStream = null;
    let screenStream = null;
    let isMicActive = true;
    let isCamActive = true;
    let isSharingScreen = false;
    
    const peers = {}; // username -> RTCPeerConnection
    const dataChannels = {}; // username -> RTCDataChannel
    
    const rtcConfig = {
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' },
            { urls: 'stun:stun2.l.google.com:19302' }
        ]
    };

    // Initialize media streams
    async function startMedia() {
        try {
            localStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });
            document.getElementById('localVideo').srcObject = localStream;
            
            // Register control handlers
            btnMic.classList.add('active');
            btnCam.classList.add('active');
            
            btnMic.onclick = toggleMicrophone;
            btnCam.onclick = toggleCamera;
            btnScreen.onclick = toggleScreenShare;
            
            // Join Room and alert other peers
            sendSignal('all', 'join', JSON.stringify({ username: CURRENT_USER, color: USER_COLOR }));
            
            // Start Signaling Poll loop
            setInterval(pollSignals, 1500);
            
        } catch (err) {
            console.error('Failed to access user media: ', err);
            alert('Could not access microphone/camera. Collaboration features will load, but video conferencing is disabled.');
            
            // Still join the room for drawing/chat/files
            sendSignal('all', 'join', JSON.stringify({ username: CURRENT_USER, color: USER_COLOR }));
            setInterval(pollSignals, 1500);
        }
    }
    
    startMedia();

    // ----------------------------------------------------
    // WebRTC Connections Management
    // ----------------------------------------------------
    function createPeerConnection(peerUsername) {
        if (peers[peerUsername]) return peers[peerUsername];
        
        console.log(`Creating RTCPeerConnection to: ${peerUsername}`);
        const pc = new RTCPeerConnection(rtcConfig);
        peers[peerUsername] = pc;
        
        // Add tracks
        if (localStream) {
            localStream.getTracks().forEach(track => {
                pc.addTrack(track, localStream);
            });
        }
        
        // ICE Candidate handling
        pc.onicecandidate = (event) => {
            if (event.candidate) {
                sendSignal(peerUsername, 'candidate', JSON.stringify(event.candidate));
            }
        };
        
        // Remote track handling
        pc.ontrack = (event) => {
            console.log(`Received remote media track from ${peerUsername}`);
            createOrUpdateRemoteVideo(peerUsername, event.streams[0]);
        };
        
        // On connection status change
        pc.onconnectionstatechange = () => {
            console.log(`Connection state with ${peerUsername}: ${pc.connectionState}`);
            if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed' || pc.connectionState === 'closed') {
                removeRemoteVideo(peerUsername);
                delete peers[peerUsername];
                delete dataChannels[peerUsername];
            }
        };
        
        return pc;
    }
    
    // Set up Data Channel for non-media updates
    function setupDataChannel(peerUsername, channel) {
        dataChannels[peerUsername] = channel;
        
        channel.onmessage = (event) => {
            handleDataChannelMessage(peerUsername, JSON.parse(event.data));
        };
        
        channel.onopen = () => {
            console.log(`Data Channel open with: ${peerUsername}`);
        };
        
        channel.onclose = () => {
            console.log(`Data Channel closed with: ${peerUsername}`);
            delete dataChannels[peerUsername];
        };
    }
    
    // ----------------------------------------------------
    // Signaling Server Integration (Database queues)
    // ----------------------------------------------------
    async function sendSignal(receiver, messageType, content) {
        try {
            await fetch(SIGNALING_SEND_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ receiver, message_type: messageType, content })
            });
        } catch (e) {
            console.error('Signaling send error:', e);
        }
    }
    
    async function pollSignals() {
        try {
            const res = await fetch(SIGNALING_GET_URL);
            const data = await res.json();
            
            for (const sig of data.signals) {
                const sender = sig.sender;
                const type = sig.message_type;
                const content = JSON.parse(sig.content);
                
                console.log(`Signaling Event: ${type} from ${sender}`);
                
                if (type === 'join') {
                    // New user joined: We initiate WebRTC handshake with them
                    const pc = createPeerConnection(sender);
                    
                    // Create local data channel
                    const dc = pc.createDataChannel('sync-channel');
                    setupDataChannel(sender, dc);
                    
                    // Create Offer
                    const offer = await pc.createOffer();
                    await pc.setLocalDescription(offer);
                    sendSignal(sender, 'offer', JSON.stringify(offer));
                    
                } else if (type === 'offer') {
                    // Remote user sent offer: We accept it, configure peer, and send answer
                    const pc = createPeerConnection(sender);
                    
                    // Receive remote data channel
                    pc.ondatachannel = (event) => {
                        setupDataChannel(sender, event.channel);
                    };
                    
                    await pc.setRemoteDescription(new RTCSessionDescription(content));
                    const answer = await pc.createAnswer();
                    await pc.setLocalDescription(answer);
                    sendSignal(sender, 'answer', JSON.stringify(answer));
                    
                } else if (type === 'answer') {
                    // Answer received from peer: finish handshake
                    const pc = peers[sender];
                    if (pc) {
                        await pc.setRemoteDescription(new RTCSessionDescription(content));
                    }
                    
                } else if (type === 'candidate') {
                    // Receive ICE candidate
                    const pc = peers[sender];
                    if (pc) {
                        await pc.addIceCandidate(new RTCIceCandidate(content));
                    }
                }
            }
        } catch (e) {
            console.error('Signaling polling error:', e);
        }
    }

    // ----------------------------------------------------
    // Audio / Video UI Management
    // ----------------------------------------------------
    function createOrUpdateRemoteVideo(peerUsername, stream) {
        let tile = document.getElementById(`tile-${peerUsername}`);
        
        if (!tile) {
            const grid = document.getElementById('videoGrid');
            
            tile = document.createElement('div');
            tile.id = `tile-${peerUsername}`;
            tile.className = 'video-tile';
            tile.innerHTML = `
                <video id="video-${peerUsername}" autoplay playsinline></video>
                <div class="tile-tag">
                    <span class="user-avatar-dot" style="background-color: #3b82f6;"></span>
                    <span class="tile-username">${peerUsername}</span>
                </div>
                <div class="audio-indicator" id="audio-${peerUsername}">
                    <i class="fa-solid fa-microphone"></i>
                </div>
            `;
            grid.appendChild(tile);
        }
        
        const video = document.getElementById(`video-${peerUsername}`);
        if (video.srcObject !== stream) {
            video.srcObject = stream;
        }
    }
    
    function removeRemoteVideo(peerUsername) {
        const tile = document.getElementById(`tile-${peerUsername}`);
        if (tile) {
            tile.remove();
        }
    }

    // Controls
    function toggleMicrophone() {
        if (!localStream) return;
        isMicActive = !isMicActive;
        localStream.getAudioTracks().forEach(track => track.enabled = isMicActive);
        
        const indicator = document.getElementById('localAudioIndicator');
        if (isMicActive) {
            btnMic.classList.remove('muted');
            btnMic.classList.add('active');
            btnMic.innerHTML = '<i class="fa-solid fa-microphone"></i>';
            indicator.classList.remove('muted');
            indicator.innerHTML = '<i class="fa-solid fa-microphone"></i>';
        } else {
            btnMic.classList.add('muted');
            btnMic.classList.remove('active');
            btnMic.innerHTML = '<i class="fa-solid fa-microphone-slash"></i>';
            indicator.classList.add('muted');
            indicator.innerHTML = '<i class="fa-solid fa-microphone-slash"></i>';
        }
        
        // Alert peers via data channels
        broadcastData({ type: 'mute-update', username: CURRENT_USER, muted: !isMicActive });
    }
    
    function toggleCamera() {
        if (!localStream) return;
        isCamActive = !isCamActive;
        localStream.getVideoTracks().forEach(track => track.enabled = isCamActive);
        
        if (isCamActive) {
            btnCam.classList.remove('muted');
            btnCam.classList.add('active');
            btnCam.innerHTML = '<i class="fa-solid fa-video"></i>';
        } else {
            btnCam.classList.add('muted');
            btnCam.classList.remove('active');
            btnCam.innerHTML = '<i class="fa-solid fa-video-slash"></i>';
        }
    }
    
    async function toggleScreenShare() {
        if (!isSharingScreen) {
            try {
                screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                isSharingScreen = true;
                btnScreen.classList.add('active');
                
                const screenTrack = screenStream.getVideoTracks()[0];
                
                // Replace video track for all peers
                Object.values(peers).forEach(pc => {
                    const senders = pc.getSenders();
                    const videoSender = senders.find(s => s.track && s.track.kind === 'video');
                    if (videoSender) {
                        videoSender.replaceTrack(screenTrack);
                    }
                });
                
                // Update local preview
                document.getElementById('localVideo').srcObject = screenStream;
                
                // Handle user stopping screen share from standard browser bar
                screenTrack.onended = () => {
                    stopScreenSharing();
                };
                
            } catch (err) {
                console.error("Failed to share screen:", err);
            }
        } else {
            stopScreenSharing();
        }
    }
    
    function stopScreenSharing() {
        if (!isSharingScreen) return;
        isSharingScreen = false;
        btnScreen.classList.remove('active');
        
        if (screenStream) {
            screenStream.getTracks().forEach(t => t.stop());
        }
        
        // Revert to web cam video track on connections
        if (localStream) {
            const camTrack = localStream.getVideoTracks()[0];
            Object.values(peers).forEach(pc => {
                const senders = pc.getSenders();
                const videoSender = senders.find(s => s.track && s.track.kind === 'video');
                if (videoSender && camTrack) {
                    videoSender.replaceTrack(camTrack);
                }
            });
            document.getElementById('localVideo').srcObject = localStream;
        }
    }

    // ----------------------------------------------------
    // Data Channel Messaging Logic
    // ----------------------------------------------------
    function broadcastData(data) {
        const payload = JSON.stringify(data);
        Object.values(dataChannels).forEach(channel => {
            if (channel.readyState === 'open') {
                channel.send(payload);
            }
        });
    }
    
    function handleDataChannelMessage(sender, data) {
        if (data.type === 'draw') {
            board.drawRemoteStroke(
                data.coords.relX0, data.coords.relY0,
                data.coords.relX1, data.coords.relY1,
                data.color, data.size
            );
        } else if (data.type === 'clear') {
            board.clearLocal();
        } else if (data.type === 'chat') {
            appendChatMessage(data.sender, data.text, data.time, 'incoming');
        } else if (data.type === 'file') {
            appendSharedFileLink(data.sender, data.filename, data.url, data.time);
        } else if (data.type === 'mute-update') {
            const indicator = document.getElementById(`audio-${data.username}`);
            if (indicator) {
                if (data.muted) {
                    indicator.classList.add('muted');
                    indicator.innerHTML = '<i class="fa-solid fa-microphone-slash"></i>';
                } else {
                    indicator.classList.remove('muted');
                    indicator.innerHTML = '<i class="fa-solid fa-microphone"></i>';
                }
            }
        }
    }

    // ----------------------------------------------------
    // Chat System UI
    // ----------------------------------------------------
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text) return;
        
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        // Local echo
        appendChatMessage(CURRENT_USER, text, timeStr, 'outgoing');
        
        // Broadcast
        broadcastData({
            type: 'chat',
            sender: CURRENT_USER,
            text: text,
            time: timeStr
        });
        
        chatInput.value = '';
    });
    
    function appendChatMessage(sender, text, time, direction) {
        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${direction}`;
        bubble.innerHTML = `
            <span class="message-sender">${sender}</span>
            <div class="message-text">${text}</div>
            <span class="message-time">${time}</span>
        `;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // ----------------------------------------------------
    // Files System UI & Uploads
    // ----------------------------------------------------
    // Drop Zone Click
    fileDropZone.addEventListener('click', () => fileInput.click());
    
    // File Input change
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });
    
    // Drag & Drop
    fileDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileDropZone.classList.add('dragover');
    });
    
    fileDropZone.addEventListener('dragleave', () => {
        fileDropZone.classList.remove('dragover');
    });
    
    fileDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        fileDropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
    
    async function handleFileUpload(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const progressBar = document.getElementById('uploadProgressBar');
        const progressFill = progressBar.querySelector('.progress-fill');
        progressBar.style.display = 'block';
        progressFill.style.width = '0%';
        
        try {
            // Upload to Django
            const response = await fetch(FILE_UPLOAD_URL, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            progressBar.style.display = 'none';
            
            if (data.status === 'success') {
                // Add to local UI
                appendSharedFileLink(data.sender, data.filename, data.url, data.uploaded_at);
                
                // Broadcast file availability to active peers
                broadcastData({
                    type: 'file',
                    sender: data.sender,
                    filename: data.filename,
                    url: data.url,
                    time: data.uploaded_at
                });
            } else {
                alert(`Upload failed: ${data.message}`);
            }
        } catch (err) {
            progressBar.style.display = 'none';
            console.error('File upload error:', err);
            alert('File upload encountered an error.');
        }
    }
    
    function appendSharedFileLink(sender, filename, url, time) {
        if (emptyFilesMessage) {
            emptyFilesMessage.remove();
        }
        
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `
            <div class="file-info">
                <i class="fa-solid fa-file-lines text-muted"></i>
                <div class="file-meta">
                    <a href="${url}" target="_blank" class="file-name" download>${filename}</a>
                    <small>Shared by ${sender} • ${time}</small>
                </div>
            </div>
            <a href="${url}" download class="btn-download" title="Download"><i class="fa-solid fa-download"></i></a>
        `;
        sharedFilesList.prepend(item);
    }
});
