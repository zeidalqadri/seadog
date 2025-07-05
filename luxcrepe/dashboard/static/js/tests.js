/**
 * SEADOG Command Center - Tests JavaScript
 * Test execution monitoring and control
 */

class SEADOGTests {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.currentTest = null;
        
        this.init();
    }
    
    init() {
        console.log('SEADOG Tests interface initializing...');
        this.connectWebSocket();
        this.setupEventListeners();
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected to tests interface');
            this.isConnected = true;
            this.updateConnectionStatus('CONNECTED');
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onclose = () => {
            this.isConnected = false;
            this.updateConnectionStatus('DISCONNECTED');
        };
    }
    
    sendMessage(message) {
        if (this.isConnected && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'test_started':
                this.handleTestStarted(data);
                break;
            case 'test_progress':
                this.updateTestProgress(data);
                break;
            case 'test_completed':
                this.handleTestCompleted(data);
                break;
        }
    }
    
    setupEventListeners() {
        // Update last update time periodically
        setInterval(() => {
            document.getElementById('last-update')?.textContent = new Date().toLocaleTimeString();
        }, 1000);
    }
    
    updateConnectionStatus(status) {
        const connectionElement = document.getElementById('connection-status');
        const indicatorElement = document.getElementById('connection-indicator');
        const engineElement = document.getElementById('engine-status');
        
        if (connectionElement) connectionElement.textContent = status;
        if (engineElement) engineElement.textContent = status === 'CONNECTED' ? 'READY' : 'OFFLINE';
        
        if (indicatorElement) {
            indicatorElement.className = status === 'CONNECTED' ? 'live-indicator' : 'live-indicator status-offline';
        }
    }
    
    handleTestStarted(data) {
        this.currentTest = data;
        this.updateElement('current-test', data.config?.type || 'UNKNOWN');
        this.updateElement('test-status', 'RUNNING');
        this.addLogEntry('Test started', 'STARTED');
    }
    
    updateTestProgress(data) {
        const progress = data.progress || 0;
        this.updateElement('test-progress', `${progress}%`);
        
        const progressBar = document.getElementById('progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    }
    
    handleTestCompleted(data) {
        this.updateElement('test-status', 'COMPLETED');
        this.updateElement('test-progress', '100%');
        this.addLogEntry('Test completed', 'COMPLETED');
        
        // Update results summary
        if (data.results) {
            this.updateTestResults(data.results);
        }
    }
    
    updateTestResults(results) {
        this.updateElement('last-test-id', results.test_id || 'UNKNOWN');
        this.updateElement('targets-tested', results.targets_count || 0);
        this.updateElement('last-success-rate', `${(results.success_rate * 100).toFixed(1)}%`);
        this.updateElement('last-duration', `${results.duration || 0}s`);
        this.updateElement('recommendations-count', results.recommendations?.length || 0);
    }
    
    addLogEntry(message, status) {
        const output = document.getElementById('test-output');
        if (!output) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.innerHTML = `
            <span class="log-timestamp">${timestamp}</span>
            <span class="log-message">${message}</span>
            <span class="log-status">${status}</span>
        `;
        
        output.insertBefore(entry, output.firstChild);
        
        // Keep only last 20 entries
        const entries = output.children;
        if (entries.length > 20) {
            output.removeChild(entries[entries.length - 1]);
        }
    }
    
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }
}

// Global functions for button handlers
function startTest(type) {
    console.log(`Starting ${type} test...`);
    
    const targetUrls = document.getElementById('target-urls')?.value.split('\n').filter(url => url.trim());
    const intensity = document.getElementById('test-intensity')?.value || 'MODERATE';
    const timeout = parseInt(document.getElementById('test-timeout')?.value || '60');
    const parallel = document.getElementById('parallel-execution')?.checked;
    
    if (tests.isConnected) {
        tests.sendMessage({
            type: 'start_test',
            config: {
                type: type,
                targets: targetUrls,
                intensity: intensity,
                timeout: timeout,
                parallel: parallel
            }
        });
    }
    
    tests.addLogEntry(`Starting ${type} test with ${targetUrls?.length || 0} targets`, 'STARTING');
}

function pauseTest() {
    console.log('Pausing test...');
    if (tests.isConnected) {
        tests.sendMessage({ type: 'pause_test' });
    }
    tests.addLogEntry('Test paused', 'PAUSED');
}

function stopTest() {
    console.log('Stopping test...');
    if (tests.isConnected) {
        tests.sendMessage({ type: 'stop_test' });
    }
    tests.addLogEntry('Test stopped', 'STOPPED');
    tests.updateElement('test-status', 'STOPPED');
}

function loadPresetUrls(preset) {
    const urlTextarea = document.getElementById('target-urls');
    if (!urlTextarea) return;
    
    const presets = {
        'SAFE_APIS': [
            'https://jsonplaceholder.typicode.com/posts/1',
            'https://httpbin.org/json',
            'https://httpbin.org/get'
        ].join('\n'),
        'ECOMMERCE_DEMO': [
            'https://fakestoreapi.com/products',
            'https://dummyjson.com/products'
        ].join('\n')
    };
    
    urlTextarea.value = presets[preset] || '';
    console.log(`Loaded ${preset} preset URLs`);
}

function exportResults() {
    console.log('Exporting test results...');
    // In real implementation, this would download results
    tests.addLogEntry('Results exported', 'EXPORTED');
}

function clearLog() {
    const output = document.getElementById('test-output');
    if (output) {
        output.innerHTML = `
            <div class="log-entry">
                <span class="log-timestamp">--:--:--</span>
                <span class="log-message">Log cleared</span>
                <span class="log-status">CLEAR</span>
            </div>
        `;
    }
}

function resetAllTests() {
    console.log('Resetting all tests...');
    if (tests.isConnected) {
        tests.sendMessage({ type: 'reset_all' });
    }
    
    tests.updateElement('current-test', 'NONE');
    tests.updateElement('test-status', 'STANDBY');
    tests.updateElement('test-progress', '0%');
    
    const progressBar = document.getElementById('progress-bar');
    if (progressBar) {
        progressBar.style.width = '0%';
    }
    
    clearLog();
}

// Initialize when page loads
let tests;
document.addEventListener('DOMContentLoaded', () => {
    tests = new SEADOGTests();
});