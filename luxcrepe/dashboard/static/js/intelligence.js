/**
 * SEADOG Command Center - Intelligence JavaScript
 * Intelligence monitoring and analysis interface
 */

class SEADOGIntelligence {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.intelligenceData = [];
        this.currentFilter = 'ALL';
        
        this.init();
    }
    
    init() {
        console.log('SEADOG Intelligence interface initializing...');
        this.connectWebSocket();
        this.startIntelligenceSimulation();
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected to intelligence interface');
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
            case 'intelligence_update':
                this.handleIntelligenceUpdate(data);
                break;
            case 'threat_alert':
                this.handleThreatAlert(data);
                break;
        }
    }
    
    updateConnectionStatus(status) {
        const connectionElement = document.getElementById('connection-status');
        const indicatorElement = document.getElementById('connection-indicator');
        
        if (connectionElement) connectionElement.textContent = status;
        
        if (indicatorElement) {
            indicatorElement.className = status === 'CONNECTED' ? 'live-indicator' : 'live-indicator status-offline';
        }
        
        // Update agent statuses
        this.updateElement('oracle-status', status === 'CONNECTED' ? 'ONLINE' : 'OFFLINE');
        this.updateElement('ghost-status', status === 'CONNECTED' ? 'OPERATIONAL' : 'STANDBY');
    }
    
    handleIntelligenceUpdate(data) {
        this.intelligenceData.push(data.intelligence);
        this.updateIntelligenceFeed();
    }
    
    handleThreatAlert(data) {
        this.addIntelligenceEntry('THREAT', data.message, 'HIGH');
        this.updateThreatMetrics(data);
    }
    
    addIntelligenceEntry(type, message, priority = 'NORMAL') {
        const timestamp = new Date().toLocaleTimeString();
        const entry = {
            timestamp,
            type,
            message,
            priority
        };
        
        this.intelligenceData.unshift(entry);
        this.updateIntelligenceFeed();
        
        // Keep only last 100 entries
        if (this.intelligenceData.length > 100) {
            this.intelligenceData = this.intelligenceData.slice(0, 100);
        }
    }
    
    updateIntelligenceFeed() {
        const feedElement = document.getElementById('live-intel-feed');
        if (!feedElement) return;
        
        // Filter data based on current filter
        let filteredData = this.intelligenceData;
        if (this.currentFilter !== 'ALL') {
            filteredData = this.intelligenceData.filter(entry => entry.type === this.currentFilter);
        }
        
        // Update feed display
        feedElement.innerHTML = '';
        filteredData.slice(0, 20).forEach(entry => {
            const entryElement = document.createElement('div');
            entryElement.className = 'intel-entry';
            entryElement.innerHTML = `
                <span class="intel-time">${entry.timestamp}</span>
                <span class="intel-type ${entry.type}">${entry.type}</span>
                <span class="intel-message">${entry.message}</span>
            `;
            feedElement.appendChild(entryElement);
        });
    }
    
    updateThreatMetrics(threatData) {
        if (threatData.level) {
            this.updateElement('threat-level', threatData.level);
        }
        if (threatData.activeThreats !== undefined) {
            this.updateElement('active-threats', threatData.activeThreats);
        }
    }
    
    startIntelligenceSimulation() {
        // Simulate intelligence gathering for demo
        setInterval(() => {
            this.simulateIntelligenceActivity();
        }, 4000);
        
        // Update metrics periodically
        setInterval(() => {
            this.updateMetrics();
        }, 2000);
    }
    
    simulateIntelligenceActivity() {
        const intelTypes = ['INTEL', 'THREAT', 'ALERT', 'DATA', 'OPSEC', 'PERF'];
        const messages = {
            'INTEL': [
                'API endpoint discovered',
                'Authentication method analyzed',
                'Rate limit policy detected',
                'Server technology identified',
                'Security headers analyzed'
            ],
            'THREAT': [
                'Rate limiting threshold approaching',
                'Unusual response pattern detected',
                'Potential bot detection triggered',
                'IP address flagged for monitoring',
                'Captcha challenge encountered'
            ],
            'ALERT': [
                'Agent response time increased',
                'Connection timeout occurred',
                'Retry attempt initiated',
                'Backup endpoint activated',
                'Error recovery in progress'
            ],
            'DATA': [
                'Product schema updated',
                'Data extraction completed',
                'Validation rules modified',
                'Export format optimized',
                'Quality check passed'
            ],
            'OPSEC': [
                'Stealth protocols activated',
                'User-agent rotation executed',
                'Proxy connection established',
                'Request signature randomized',
                'Timing patterns adjusted'
            ],
            'PERF': [
                'Response time optimized',
                'Throughput increased',
                'Memory usage stable',
                'CPU utilization normal',
                'Network latency reduced'
            ]
        };
        
        if (Math.random() < 0.4) { // 40% chance
            const type = intelTypes[Math.floor(Math.random() * intelTypes.length)];
            const messageList = messages[type];
            const message = messageList[Math.floor(Math.random() * messageList.length)];
            
            this.addIntelligenceEntry(type, message);
        }
    }
    
    updateMetrics() {
        // Update threat metrics
        const threatLevel = ['LOW', 'MODERATE', 'HIGH'][Math.floor(Math.random() * 3)];
        const activeThreats = Math.floor(Math.random() * 5);
        const blockedAttempts = Math.floor(Math.random() * 20);
        const stealthScore = Math.floor(Math.random() * 20) + 80; // 80-100%
        
        this.updateElement('threat-level', threatLevel);
        this.updateElement('active-threats', activeThreats);
        this.updateElement('blocked-attempts', blockedAttempts);
        this.updateElement('stealth-score', `${stealthScore}%`);
        
        // Update stealth progress bar
        const stealthProgress = document.getElementById('stealth-progress');
        if (stealthProgress) {
            stealthProgress.style.width = `${stealthScore}%`;
            stealthProgress.className = stealthScore < 60 ? 'progress-fill danger' : 
                                       stealthScore < 80 ? 'progress-fill warning' : 'progress-fill';
        }
        
        // Update intelligence control metrics
        this.updateElement('collection-rate', `${Math.floor(Math.random() * 10) + 8}/min`);
        this.updateElement('data-points', (Math.floor(Math.random() * 500) + 1000).toLocaleString());
        this.updateElement('last-update', new Date().toLocaleTimeString());
    }
    
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }
}

// Global functions for button handlers
function filterIntel(type) {
    console.log(`Filtering intelligence by: ${type}`);
    if (intelligence) {
        intelligence.currentFilter = type;
        intelligence.updateIntelligenceFeed();
    }
}

function clearFeed() {
    console.log('Clearing intelligence feed...');
    if (intelligence) {
        intelligence.intelligenceData = [];
        intelligence.updateIntelligenceFeed();
    }
}

function startIntelligenceGathering() {
    console.log('Starting intelligence gathering...');
    if (intelligence.isConnected) {
        intelligence.sendMessage({ type: 'start_intelligence' });
    }
    intelligence.updateElement('intel-status', 'GATHERING');
}

function refreshIntelligence() {
    console.log('Refreshing intelligence data...');
    if (intelligence.isConnected) {
        intelligence.sendMessage({ type: 'refresh_intelligence' });
    }
}

function exportIntelligence() {
    console.log('Exporting intelligence data...');
    // In real implementation, this would download intelligence data
    intelligence.addIntelligenceEntry('DATA', 'Intelligence data exported', 'INFO');
}

function stopIntelligence() {
    console.log('Stopping intelligence gathering...');
    if (intelligence.isConnected) {
        intelligence.sendMessage({ type: 'stop_intelligence' });
    }
    intelligence.updateElement('intel-status', 'STOPPED');
}

// Initialize when page loads
let intelligence;
document.addEventListener('DOMContentLoaded', () => {
    intelligence = new SEADOGIntelligence();
});