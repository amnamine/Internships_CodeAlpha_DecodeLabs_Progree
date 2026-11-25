// Configure Marked.js with Highlight.js for code rendering
marked.setOptions({
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-'
});

// App State Management
let chats = [];
let activeChatId = null;
let models = [];
let recognition = null;
let isRecording = false;

// DOM Elements
const sidebar = document.getElementById('sidebar');
const sidebarOpenBtn = document.getElementById('sidebarOpenBtn');
const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
const newChatBtn = document.getElementById('newChatBtn');
const chatList = document.getElementById('chatList');
const modelSelect = document.getElementById('modelSelect');
const systemPrompt = document.getElementById('systemPrompt');
const activeChatTitle = document.getElementById('activeChatTitle');
const activeChatSubtitle = document.getElementById('activeChatSubtitle');
const clearChatBtn = document.getElementById('clearChatBtn');
const messagesContainer = document.getElementById('messagesContainer');
const welcomeScreen = document.getElementById('welcomeScreen');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const voiceInputBtn = document.getElementById('voiceInputBtn');
const typingIndicator = document.getElementById('typingIndicator');
const statMemory = document.getElementById('statMemory');
const statModel = document.getElementById('statModel');

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    loadChatsFromStorage();
    fetchModels();
    setupEventListeners();
    setupSpeechRecognition();
});

// Load chats from LocalStorage
function loadChatsFromStorage() {
    const storedChats = localStorage.getItem('aurora_chats');
    if (storedChats) {
        chats = JSON.parse(storedChats);
        renderChatList();
        
        // Load the last active chat, or create one if empty
        const storedActiveId = localStorage.getItem('aurora_active_chat_id');
        if (storedActiveId && chats.some(c => c.id === storedActiveId)) {
            switchChat(storedActiveId);
        } else if (chats.length > 0) {
            switchChat(chats[0].id);
        } else {
            createNewChat();
        }
    } else {
        createNewChat();
    }
}

// Save chats to LocalStorage
function saveChatsToStorage() {
    localStorage.setItem('aurora_chats', JSON.stringify(chats));
    localStorage.setItem('aurora_active_chat_id', activeChatId);
    renderChatList();
}

// Fetch models list from Python Backend
async function fetchModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();
        models = data.models;
        
        modelSelect.innerHTML = '';
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = model.name;
            option.title = model.desc;
            modelSelect.appendChild(option);
        });

        // Set select value based on active chat or default
        const activeChat = chats.find(c => c.id === activeChatId);
        if (activeChat && activeChat.model) {
            modelSelect.value = activeChat.model;
        } else {
            modelSelect.value = 'llama-3.3-70b-versatile'; // default
        }
        
        updateStats();
    } catch (e) {
        console.error("Error fetching models:", e);
    }
}

// Create a new chat session
function createNewChat() {
    const defaultModel = modelSelect.value || 'llama-3.3-70b-versatile';
    const defaultSystem = systemPrompt.value || "You are an AI assistant.";
    
    const newChat = {
        id: 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
        title: 'New Conversation',
        model: defaultModel,
        system_prompt: defaultSystem,
        messages: [] // Stores messages locally for UI restoration
    };
    
    chats.unshift(newChat);
    saveChatsToStorage();
    switchChat(newChat.id);
}

// Switch between conversation threads
function switchChat(chatId) {
    activeChatId = chatId;
    localStorage.setItem('aurora_active_chat_id', activeChatId);
    
    const chat = chats.find(c => c.id === chatId);
    if (!chat) return;
    
    // Update Sidebar Selection
    document.querySelectorAll('.chat-item').forEach(item => {
        item.classList.toggle('active', item.dataset.id === chatId);
    });
    
    // Load Settings for this chat
    if (chat.model) modelSelect.value = chat.model;
    if (chat.system_prompt) systemPrompt.value = chat.system_prompt;
    
    // Update Header
    activeChatTitle.textContent = chat.title;
    const modelObj = models.find(m => m.id === chat.model);
    activeChatSubtitle.textContent = `Running on ${modelObj ? modelObj.name : chat.model}`;
    
    // Load messages in viewport
    renderMessages(chat.messages);
    updateStats();
    
    // Close sidebar on mobile devices
    sidebar.classList.remove('open');
}

// Delete a conversation thread
function deleteChat(chatId, event) {
    if (event) event.stopPropagation();
    
    const index = chats.findIndex(c => c.id === chatId);
    if (index === -1) return;
    
    // Call server to clear its in-memory storage for this chat
    fetch('/api/clear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId })
    }).catch(err => console.error("Error clearing session history:", err));

    chats.splice(index, 1);
    
    if (chats.length === 0) {
        createNewChat();
    } else {
        if (activeChatId === chatId) {
            switchChat(chats[0].id);
        } else {
            saveChatsToStorage();
        }
    }
}

// Clear active chat contents
function clearActiveChat() {
    const chat = chats.find(c => c.id === activeChatId);
    if (!chat) return;
    
    if (confirm("Are you sure you want to clear this conversation's memory and messages?")) {
        chat.messages = [];
        chat.title = 'New Conversation';
        
        // Notify backend to clean memory
        fetch('/api/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id: activeChatId })
        });
        
        saveChatsToStorage();
        switchChat(activeChatId);
    }
}

// Render the sidebar chat history items
function renderChatList() {
    chatList.innerHTML = '';
    
    chats.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.className = `chat-item ${chat.id === activeChatId ? 'active' : ''}`;
        chatItem.dataset.id = chat.id;
        chatItem.onclick = () => switchChat(chat.id);
        
        const titleContainer = document.createElement('div');
        titleContainer.className = 'chat-item-title';
        
        const icon = document.createElement('i');
        icon.className = 'fa-regular fa-message';
        titleContainer.appendChild(icon);
        
        const titleSpan = document.createElement('span');
        titleSpan.textContent = chat.title;
        titleContainer.appendChild(titleSpan);
        
        chatItem.appendChild(titleContainer);
        
        // Delete button
        const actions = document.createElement('div');
        actions.className = 'chat-item-actions';
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'chat-item-action';
        deleteBtn.innerHTML = '<i class="fa-regular fa-trash-can"></i>';
        deleteBtn.title = 'Delete conversation';
        deleteBtn.onclick = (e) => deleteChat(chat.id, e);
        actions.appendChild(deleteBtn);
        
        chatItem.appendChild(actions);
        chatList.appendChild(chatItem);
    });
}

// Render messages in chat pane
function renderMessages(messages) {
    // Clear display except welcome screen
    messagesContainer.innerHTML = '';
    
    if (!messages || messages.length === 0) {
        messagesContainer.appendChild(welcomeScreen);
        welcomeScreen.style.display = 'block';
        return;
    }
    
    welcomeScreen.style.display = 'none';
    
    messages.forEach(msg => {
        appendMessageUI(msg.role, msg.content, false);
    });
    
    scrollToBottom();
}

// Append message element to UI
function appendMessageUI(role, content, animate = true) {
    const welcome = document.getElementById('welcomeScreen');
    if (welcome) welcome.style.display = 'none';
    
    const messageRow = document.createElement('div');
    messageRow.className = `message-row ${role}`;
    if (animate) {
        messageRow.style.animation = 'fadeInUp 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    }
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    // Header (Sender title + icon)
    const header = document.createElement('div');
    header.className = 'message-bubble-header';
    
    const icon = document.createElement('i');
    if (role === 'user') {
        icon.className = 'fa-solid fa-circle-user';
        header.appendChild(icon);
        header.appendChild(document.createTextNode(' You'));
    } else {
        icon.className = 'fa-solid fa-wand-magic-sparkles';
        header.appendChild(icon);
        header.appendChild(document.createTextNode(' Aurora'));
    }
    bubble.appendChild(header);
    
    // Body Content (Render Markdown)
    const body = document.createElement('div');
    body.className = 'message-content';
    
    // Parse Markdown safely
    body.innerHTML = marked.parse(content);
    bubble.appendChild(body);
    
    // Utility Buttons for response bubbles (Copy, Speak, TTS)
    if (role === 'assistant') {
        const actionBar = document.createElement('div');
        actionBar.className = 'message-actions-bar';
        
        // Copy text button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'msg-utility-btn';
        copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy';
        copyBtn.onclick = () => {
            navigator.clipboard.writeText(content);
            copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied';
            setTimeout(() => {
                copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy';
            }, 2000);
        };
        actionBar.appendChild(copyBtn);
        
        // Text to Speech (TTS) Read Aloud Button
        const speakBtn = document.createElement('button');
        speakBtn.className = 'msg-utility-btn';
        speakBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i> Speak';
        speakBtn.onclick = () => speakMessage(content, speakBtn);
        actionBar.appendChild(speakBtn);
        
        bubble.appendChild(actionBar);
    }
    
    messageRow.appendChild(bubble);
    messagesContainer.appendChild(messageRow);
    
    // Add copy button logic on rendered code blocks
    addCodeBlockCopyButtons(body);
    
    scrollToBottom();
}

// Add Copy Buttons to Preformatted Code Blocks
function addCodeBlockCopyButtons(container) {
    const preBlocks = container.querySelectorAll('pre');
    preBlocks.forEach(pre => {
        // Skip if already has header
        if (pre.previousElementSibling && pre.previousElementSibling.classList.contains('code-header')) return;
        
        // Determine code language if any
        const codeElement = pre.querySelector('code');
        let lang = 'code';
        if (codeElement) {
            const classes = Array.from(codeElement.classList);
            const langClass = classes.find(c => c.startsWith('language-'));
            if (langClass) {
                lang = langClass.replace('language-', '');
            }
        }
        
        // Create Code Header
        const header = document.createElement('div');
        header.className = 'code-header';
        header.innerHTML = `
            <span>${lang.toUpperCase()}</span>
            <button class="copy-code-btn"><i class="fa-regular fa-copy"></i> Copy code</button>
        `;
        
        // Attach click listener
        header.querySelector('.copy-code-btn').onclick = (e) => {
            const btn = e.currentTarget;
            const codeText = codeElement ? codeElement.innerText : pre.innerText;
            navigator.clipboard.writeText(codeText);
            btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            setTimeout(() => {
                btn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy code';
            }, 2000);
        };
        
        pre.parentNode.insertBefore(header, pre);
    });
}

// Auto Scroll to Bottom of Messages
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Update settings and stats panel info
function updateStats() {
    const chat = chats.find(c => c.id === activeChatId);
    if (!chat) return;
    
    const count = chat.messages.length;
    statMemory.textContent = `${count} message${count !== 1 ? 's' : ''}`;
    
    const selectedModelName = modelSelect.options[modelSelect.selectedIndex]?.text || chat.model;
    statModel.textContent = selectedModelName;
}

// Send the active message payload to Backend
async function handleSendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    
    chatInput.value = '';
    chatInput.rows = 1;
    sendBtn.disabled = true;
    
    const chat = chats.find(c => c.id === activeChatId);
    if (!chat) return;
    
    // If the conversation title is 'New Conversation', update it to the first prompt
    if (chat.title === 'New Conversation') {
        chat.title = text.length > 25 ? text.substring(0, 25) + '...' : text;
        renderChatList();
    }
    
    // Add user message to UI and local session array
    chat.messages.push({ role: 'user', content: text });
    appendMessageUI('user', text);
    updateStats();
    saveChatsToStorage();
    
    // Show typing animation
    typingIndicator.style.display = 'flex';
    scrollToBottom();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                chat_id: activeChatId,
                model: modelSelect.value,
                system_prompt: systemPrompt.value
            })
        });
        
        const data = await response.json();
        
        // Hide typing animation
        typingIndicator.style.display = 'none';
        
        if (response.ok) {
            // Save response in session list
            chat.messages.push({ role: 'assistant', content: data.response });
            appendMessageUI('assistant', data.response);
            updateStats();
            saveChatsToStorage();
        } else {
            // Display error notification
            appendMessageUI('assistant', `⚠️ **Error from Groq API:** ${data.error || 'Unknown issue'}`);
            // Remove user message from local storage so it can be retried cleanly
            chat.messages.pop();
            saveChatsToStorage();
            updateStats();
        }
    } catch (err) {
        typingIndicator.style.display = 'none';
        appendMessageUI('assistant', `⚠️ **Network Error:** Could not connect to the backend server. Make sure Flask is running.`);
        chat.messages.pop();
        saveChatsToStorage();
        updateStats();
    } finally {
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

// Trigger predefined suggestions cards
function useSuggestion(text) {
    chatInput.value = text;
    chatInput.focus();
    handleSendMessage();
}

// Speech to Text (Web Speech API) setup
function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        voiceInputBtn.style.display = 'none'; // Not supported in this browser
        return;
    }
    
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    
    recognition.onstart = () => {
        isRecording = true;
        voiceInputBtn.classList.add('active');
        chatInput.placeholder = "Listening...";
    };
    
    recognition.onresult = (event) => {
        const resultText = event.results[0][0].transcript;
        chatInput.value = (chatInput.value + " " + resultText).trim();
        chatInput.dispatchEvent(new Event('input'));
    };
    
    recognition.onerror = (e) => {
        console.error("Speech recognition error:", e.error);
        stopSpeechRecognition();
    };
    
    recognition.onend = () => {
        stopSpeechRecognition();
    };
}

function startSpeechRecognition() {
    if (recognition) {
        try {
            recognition.start();
        } catch (e) {
            console.error(e);
        }
    }
}

function stopSpeechRecognition() {
    isRecording = false;
    if (voiceInputBtn) voiceInputBtn.classList.remove('active');
    if (chatInput) {
        chatInput.placeholder = "Message Aurora... (Press Shift+Enter for new line)";
        chatInput.focus();
    }
    if (recognition) {
        try {
            recognition.stop();
        } catch (e) {}
    }
}

// Text to Speech (TTS) reader
let currentSpeakingSpeech = null;

function speakMessage(text, buttonElement) {
    if ('speechSynthesis' in window) {
        // If already speaking, cancel it
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
            if (currentSpeakingSpeech === text) {
                buttonElement.innerHTML = '<i class="fa-solid fa-volume-high"></i> Speak';
                currentSpeakingSpeech = null;
                return;
            }
        }
        
        // Remove markdown tags before reading
        const cleanText = text.replace(/[*_`#\-~\[\]()]/g, '');
        
        const utterance = new SpeechSynthesisUtterance(cleanText);
        
        utterance.onend = () => {
            buttonElement.innerHTML = '<i class="fa-solid fa-volume-high"></i> Speak';
            currentSpeakingSpeech = null;
        };
        
        utterance.onerror = () => {
            buttonElement.innerHTML = '<i class="fa-solid fa-volume-high"></i> Speak';
            currentSpeakingSpeech = null;
        };
        
        buttonElement.innerHTML = '<i class="fa-solid fa-volume-xmark"></i> Stop';
        currentSpeakingSpeech = text;
        window.speechSynthesis.speak(utterance);
    } else {
        alert("Text-to-Speech is not supported in this browser.");
    }
}

// Event Bindings
function setupEventListeners() {
    // Send Message triggers
    sendBtn.onclick = handleSendMessage;
    
    chatInput.onkeydown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };
    
    // Auto-resizing input textarea
    chatInput.oninput = () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = (chatInput.scrollHeight) + 'px';
    };
    
    // New conversation trigger
    newChatBtn.onclick = createNewChat;
    
    // Clear chat trigger
    clearChatBtn.onclick = clearActiveChat;
    
    // Settings change handlers
    modelSelect.onchange = () => {
        const chat = chats.find(c => c.id === activeChatId);
        if (chat) {
            chat.model = modelSelect.value;
            saveChatsToStorage();
            
            const modelObj = models.find(m => m.id === chat.model);
            activeChatSubtitle.textContent = `Running on ${modelObj ? modelObj.name : chat.model}`;
            updateStats();
        }
    };
    
    systemPrompt.onchange = () => {
        const chat = chats.find(c => c.id === activeChatId);
        if (chat) {
            chat.system_prompt = systemPrompt.value;
            saveChatsToStorage();
        }
    };
    
    // Sidebar toggles for mobile view
    sidebarOpenBtn.onclick = () => sidebar.classList.add('open');
    sidebarCloseBtn.onclick = () => sidebar.classList.remove('open');
    
    // Voice recognition toggle
    voiceInputBtn.onclick = () => {
        if (isRecording) {
            stopSpeechRecognition();
        } else {
            startSpeechRecognition();
        }
    };
}
