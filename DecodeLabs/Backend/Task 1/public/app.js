document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const tabButtons = document.querySelectorAll('.tab-btn');
  const conceptContents = document.querySelectorAll('.concept-content');
  
  const requestMethod = document.getElementById('request-method');
  const requestPath = document.getElementById('request-path');
  const sendBtn = document.getElementById('send-request-btn');
  const requestBody = document.getElementById('request-body');
  const requestBodyContainer = document.getElementById('request-body-container');
  const jsonValidity = document.getElementById('json-validity');
  
  const packet = document.getElementById('packet');
  const clientNode = document.querySelector('.node-client .node-icon');
  const serverNode = document.querySelector('.node-server .node-icon');
  
  const responseStatus = document.getElementById('response-status');
  const responseTime = document.getElementById('response-time');
  const responseTabs = document.querySelectorAll('.resp-tab-btn');
  const responseContents = document.querySelectorAll('.response-content');
  const responseBodyOutput = document.getElementById('response-body-output');
  const responseHeadersOutput = document.getElementById('response-headers-output');
  const badgeDot = document.querySelector('.badge-dot');

  // Scenario Templates
  const templates = {
    'tpl-get-all': { method: 'GET', path: '/items', body: null },
    'tpl-get-single': { method: 'GET', path: '/items/1', body: null },
    'tpl-get-404': { method: 'GET', path: '/items/99', body: null },
    'tpl-post-valid': { 
      method: 'POST', 
      path: '/items', 
      body: {
        name: 'JSON Formatting',
        description: 'JavaScript Object Notation, standard format for REST response payloads.',
        category: 'HTTP Concept'
      }
    },
    'tpl-post-invalid': { 
      method: 'POST', 
      path: '/items', 
      body: {
        description: 'Missing required field name.',
        category: 'HTTP Concept'
      }
    }
  };

  // Server Status Checker
  const checkServerStatus = async () => {
    const statusDot = document.getElementById('server-status-dot');
    const statusText = document.getElementById('server-status-text');
    const apiHost = window.location.origin === 'null' || window.location.protocol === 'file:' ? 'http://localhost:3000' : '';
    
    try {
      const res = await fetch(`${apiHost}/api/status`);
      if (res.ok) {
        statusDot.className = 'status-indicator-dot online';
        statusText.textContent = 'Server Connected';
        statusText.style.color = 'var(--color-success)';
      } else {
        throw new Error();
      }
    } catch (e) {
      statusDot.className = 'status-indicator-dot offline';
      statusText.textContent = 'Server Offline (Run run.bat)';
      statusText.style.color = 'var(--color-error)';
    }
  };

  // Run initial server check
  checkServerStatus();
  setInterval(checkServerStatus, 5000);

  // Concept Tabs Toggling
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      conceptContents.forEach(c => c.classList.remove('active'));
      
      btn.classList.add('active');
      const targetId = `concept-${btn.getAttribute('data-concept')}`;
      document.getElementById(targetId).classList.add('active');
    });
  });

  // Response Tabs Toggling
  responseTabs.forEach(btn => {
    btn.addEventListener('click', () => {
      responseTabs.forEach(b => b.classList.remove('active'));
      responseContents.forEach(c => c.classList.remove('active'));
      
      btn.classList.add('active');
      const targetId = `resp-content-${btn.getAttribute('data-resp')}`;
      document.getElementById(targetId).classList.add('active');
    });
  });

  // Method Selection Styling and Visibility
  const updateMethodUI = (method) => {
    if (method === 'POST') {
      requestBodyContainer.classList.add('active');
      badgeDot.style.background = 'var(--color-post)';
      badgeDot.style.boxShadow = '0 0 10px var(--color-post)';
      sendBtn.style.background = 'linear-gradient(135deg, var(--color-post), #818cf8)';
      sendBtn.style.boxShadow = '0 4px 15px rgba(99, 102, 241, 0.4)';
    } else {
      requestBodyContainer.classList.remove('active');
      badgeDot.style.background = 'var(--color-get)';
      badgeDot.style.boxShadow = '0 0 10px var(--color-get)';
      sendBtn.style.background = 'linear-gradient(135deg, var(--color-get), #2dd4bf)';
      sendBtn.style.boxShadow = '0 4px 15px rgba(20, 184, 166, 0.4)';
    }
  };

  requestMethod.addEventListener('change', (e) => {
    updateMethodUI(e.target.value);
  });

  // JSON Validation Live Helper
  const checkJSONValidity = () => {
    try {
      if (requestBody.value.trim() === '') {
        jsonValidity.textContent = 'Empty Body';
        jsonValidity.className = 'validity-indicator invalid';
        return false;
      }
      JSON.parse(requestBody.value);
      jsonValidity.textContent = 'Valid JSON';
      jsonValidity.className = 'validity-indicator valid';
      return true;
    } catch (e) {
      jsonValidity.textContent = 'Invalid JSON';
      jsonValidity.className = 'validity-indicator invalid';
      return false;
    }
  };

  requestBody.addEventListener('input', checkJSONValidity);

  // Apply Scenarios
  Object.keys(templates).forEach(key => {
    document.getElementById(key).addEventListener('click', () => {
      const template = templates[key];
      requestMethod.value = template.method;
      requestPath.value = template.path;
      updateMethodUI(template.method);

      if (template.body) {
        requestBody.value = JSON.stringify(template.body, null, 2);
      }
      checkJSONValidity();
      
      // Auto scroll slightly to request bar if needed
      document.querySelector('.request-bar').scrollIntoView({ behavior: 'smooth', block: 'nearest' });

      // Trigger request automatically for instant feedback!
      setTimeout(() => {
        sendBtn.click();
      }, 100);
    });
  });

  // Send Request & Animate Flow
  sendBtn.addEventListener('click', async () => {
    if (sendBtn.disabled) return;
    
    const method = requestMethod.value;
    const path = requestPath.value.trim();
    
    // Check validation if POST
    if (method === 'POST' && !checkJSONValidity()) {
      alert('Please correct the JSON format before sending.');
      return;
    }

    // Set animation colors
    const methodColor = method === 'POST' ? 'var(--color-post)' : 'var(--color-get)';
    packet.style.setProperty('--packet-color', methodColor);
    
    // Disable inputs during roundtrip
    sendBtn.disabled = true;
    
    // Reset packet animation classes
    packet.className = 'flow-packet';
    void packet.offsetWidth; // Trigger reflow
    packet.classList.add('packet-animating');
    
    // Pulse Client Node initially
    clientNode.classList.add('node-pulse');
    setTimeout(() => clientNode.classList.remove('node-pulse'), 800);

    const startTime = performance.now();
    let responseData = null;
    let responseHeaders = [];
    let status = 0;
    let duration = 0;
    
    try {
      // Build request params
      const fetchOptions = {
        method,
        headers: {
          'Content-Type': 'application/json'
        }
      };

      if (method === 'POST') {
        fetchOptions.body = requestBody.value;
      }

      // Execute request (detect if running locally from filesystem and map to localhost:3000)
      const apiHost = window.location.origin === 'null' || window.location.protocol === 'file:' ? 'http://localhost:3000' : '';
      const response = await fetch(`${apiHost}/api${path}`, fetchOptions);
      status = response.status;
      duration = Math.round(performance.now() - startTime);

      // Parse headers
      for (let pair of response.headers.entries()) {
        responseHeaders.push({ key: pair[0], value: pair[1] });
      }

      // Add dummy fallback content type if missing
      if (!response.headers.get('content-type')) {
        responseHeaders.push({ key: 'content-type', value: 'application/json' });
      }

      responseData = await response.json();
    } catch (error) {
      status = 500;
      duration = Math.round(performance.now() - startTime);
      responseData = {
        success: false,
        message: 'Could not connect to the server. Make sure node server.js is running.',
        error: error.message
      };
      responseHeaders = [
        { key: 'connection', value: 'close' },
        { key: 'error', value: 'connection_failed' }
      ];
    }

    // Set packet response color
    const isSuccess = status >= 200 && status < 300;
    const responseColor = isSuccess ? 'var(--color-success)' : 'var(--color-error)';
    packet.style.setProperty('--response-color', responseColor);

    // Sync UI with Server node hit (45% through animation duration)
    setTimeout(() => {
      serverNode.classList.add('node-pulse');
      setTimeout(() => serverNode.classList.remove('node-pulse'), 800);
    }, 810); // 1.8s * 0.45 = 810ms

    // Sync UI with Client response arrival (100% of animation duration)
    setTimeout(() => {
      // Pulse client on response back
      clientNode.classList.add('node-pulse');
      setTimeout(() => clientNode.classList.remove('node-pulse'), 800);
      
      // Update badge metadata
      responseStatus.textContent = status;
      responseStatus.className = 'status-badge ' + (isSuccess ? 'status-2xx' : 'status-4xx');
      responseTime.textContent = `${duration}ms`;

      // Render JSON Response body
      responseBodyOutput.textContent = JSON.stringify(responseData, null, 2);

      // Render Response Headers
      responseHeadersOutput.innerHTML = '';
      if (responseHeaders.length > 0) {
        responseHeaders.forEach(header => {
          const row = document.createElement('tr');
          const tdKey = document.createElement('td');
          tdKey.textContent = header.key;
          const tdVal = document.createElement('td');
          tdVal.textContent = header.value;
          row.appendChild(tdKey);
          row.appendChild(tdVal);
          responseHeadersOutput.appendChild(row);
        });
      } else {
        responseHeadersOutput.innerHTML = `<tr><td colspan="2" class="table-placeholder">No headers returned.</td></tr>`;
      }

      // Re-enable send button
      sendBtn.disabled = false;
    }, 1800);
  });
});
