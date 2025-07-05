/**
 * SEADOG Command Center - Dashboard JavaScript
 * Real-time monitoring and WebSocket communication
 */

class SEADOGDashboard {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        
        // Initialize on page load
        this.init();
    }
    
    init() {
        console.log('SEADOG Dashboard initializing...');
        this.connectWebSocket();
        this.setupEventListeners();
        this.startHeartbeat();
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        console.log(`Connecting to WebSocket: ${wsUrl}`);
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = (event) => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus('CONNECTED', 'status-online');
                
                // Request initial status
                this.sendMessage({
                    type: 'get_status'
                });
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = (event) => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus('DISCONNECTED', 'status-offline');
                
                // Attempt to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                    setTimeout(() => this.connectWebSocket(), this.reconnectDelay);
                } else {
                    console.error('Max reconnection attempts reached');
                    this.updateConnectionStatus('FAILED', 'status-offline');
                }
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('ERROR', 'status-offline');
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.updateConnectionStatus('FAILED', 'status-offline');
        }
    }
    
    sendMessage(message) {
        if (this.isConnected && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected, cannot send message:', message);
        }
    }
    
    handleWebSocketMessage(data) {
        console.log('Received WebSocket message:', data.type);
        
        switch (data.type) {
            case 'system_status':
                this.updateSystemStatus(data.data);
                break;
                
            case 'agent_status':
                this.updateAgentStatus(data.data);
                break;
                
            case 'monitoring_update':
                this.updateSystemStatus(data.system_status);
                this.updateAgentStatus(data.agent_status);
                break;
                
            case 'operation_start':
                this.handleOperationStart(data);
                break;
                
            case 'operation_stopped':
                this.handleOperationStop(data);
                break;
                
            case 'test_started':
                this.handleTestStart(data);
                break;
                
            case 'heartbeat':
                // Update last update time
                this.updateElement('last-update', new Date().toLocaleTimeString());
                break;
                
            default:
                console.log('Unknown message type:', data.type);
        }
    }
    
    updateSystemStatus(status) {
        if (!status) return;
        
        // Update system status indicators
        this.updateElement('integration-status', 
            status.integration_active ? 
            '<span class="status-online">● ONLINE</span>' : 
            '<span class="status-offline">● OFFLINE</span>'
        );
        
        this.updateElement('intelligence-status', 
            status.intelligence_active ? 
            '<span class="status-online">● ACTIVE</span>' : 
            '<span class="status-offline">● STANDBY</span>'
        );
        
        this.updateElement('agents-online', status.agents_online || 0);
        this.updateElement('active-ops', status.active_operations || 0);
        this.updateElement('system-uptime', status.uptime || 'CALCULATING...');
        
        // Update squad counts
        this.updateSquadCounts(status.agents_online || 0);
    }
    
    updateAgentStatus(agentStatus) {
        if (!agentStatus) return;
        
        // Count agents by squad
        const squadCounts = {
            ALPHA: 0,
            BRAVO: 0,
            CHARLIE: 0,
            DELTA: 0
        };
        
        Object.values(agentStatus).forEach(agent => {
            if (agent.squad && squadCounts.hasOwnProperty(agent.squad)) {
                squadCounts[agent.squad]++;
            }
        });
        
        // Update squad status displays
        Object.keys(squadCounts).forEach(squad => {
            this.updateElement(`${squad.toLowerCase()}-count`, squadCounts[squad]);
            this.updateElement(`${squad.toLowerCase()}-status`, 'READY');
        });
    }
    
    updateSquadCounts(totalAgents) {
        // Default squad distribution
        const squadSizes = { ALPHA: 3, BRAVO: 4, CHARLIE: 4, DELTA: 2 };
        
        Object.keys(squadSizes).forEach(squad => {
            this.updateElement(`${squad.toLowerCase()}-count`, squadSizes[squad]);
        });
    }
    
    updateConnectionStatus(status, className) {
        const statusElement = document.getElementById('connection-status');
        const indicatorElement = document.getElementById('connection-indicator');
        const websocketElement = document.getElementById('websocket-status');
        
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = className;
        }
        
        if (indicatorElement) {
            indicatorElement.className = className === 'status-online' ? 'live-indicator' : 'live-indicator status-offline';
        }
        
        if (websocketElement) {
            websocketElement.textContent = status;
        }
    }
    
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            if (typeof content === 'string' && content.includes('<')) {
                element.innerHTML = content;
            } else {
                element.textContent = content;
            }
        }
    }
    
    handleOperationStart(data) {
        this.updateElement('last-operation', data.operation_id);
        this.updateElement('operation-status', 'RUNNING');
        console.log('Operation started:', data.operation_id);
    }
    
    handleOperationStop(data) {
        this.updateElement('operation-status', 'COMPLETED');
        console.log('Operation stopped:', data.operation_id);
    }
    
    handleTestStart(data) {
        this.updateElement('last-operation', data.operation_id);
        this.updateElement('operation-status', 'TESTING');
        console.log('Test started:', data.operation_id);
    }
    
    setupEventListeners() {
        // Add event listeners for control buttons
        const refreshBtn = document.querySelector('button[onclick="refreshStatus()"]');
        if (refreshBtn) {
            refreshBtn.onclick = () => this.refreshStatus();
        }
    }
    
    startHeartbeat() {
        // Send periodic heartbeat to maintain connection
        setInterval(() => {
            if (this.isConnected) {
                this.sendMessage({ type: 'heartbeat' });
            }
        }, 30000); // 30 seconds
    }
    
    // Public methods for button handlers
    refreshStatus() {
        console.log('Refreshing status...');
        this.sendMessage({ type: 'get_status' });
        this.sendMessage({ type: 'get_agents' });
    }
    
    startReconnaissance() {
        console.log('Starting reconnaissance...');
        this.sendMessage({
            type: 'start_test',
            config: {
                type: 'RECONNAISSANCE',
                targets: ['https://jsonplaceholder.typicode.com/posts/1'],
                intensity: 'MODERATE'
            }
        });
    }
    
    startFullSpectrum() {
        console.log('Starting full spectrum test...');
        this.sendMessage({
            type: 'start_test',
            config: {
                type: 'FULL_SPECTRUM',
                targets: ['https://jsonplaceholder.typicode.com/posts/1'],
                intensity: 'HIGH'
            }
        });
    }
    
    emergencyStop() {
        console.log('Emergency stop activated!');
        this.sendMessage({
            type: 'stop_operation',
            operation_id: 'ALL'
        });
        this.updateElement('operation-status', 'EMERGENCY STOP');
    }
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new SEADOGDashboard();
    
    // Simulate real-time metrics updates
    startMetricsSimulation();
});

// Global functions for button handlers
function refreshStatus() {
    if (dashboard) dashboard.refreshStatus();
}

function startReconnaissance() {
    if (dashboard) dashboard.startReconnaissance();
}

function startFullSpectrum() {
    if (dashboard) dashboard.startFullSpectrum();
}

function emergencyStop() {
    if (dashboard) dashboard.emergencyStop();
}

// Simulate metrics for demo purposes
function startMetricsSimulation() {
    setInterval(() => {
        // Simulate CPU usage
        const cpuUsage = Math.floor(Math.random() * 30) + 20; // 20-50%
        const cpuElement = document.getElementById('cpu-usage');
        const cpuProgress = document.getElementById('cpu-progress');
        
        if (cpuElement) cpuElement.textContent = `${cpuUsage}%`;
        if (cpuProgress) {
            cpuProgress.style.width = `${cpuUsage}%`;
            cpuProgress.className = cpuUsage > 80 ? 'progress-fill danger' : 
                                   cpuUsage > 60 ? 'progress-fill warning' : 'progress-fill';
        }
        
        // Simulate memory usage
        const memUsage = Math.floor(Math.random() * 25) + 35; // 35-60%
        const memElement = document.getElementById('memory-usage');
        const memProgress = document.getElementById('memory-progress');
        
        if (memElement) memElement.textContent = `${memUsage}%`;
        if (memProgress) {
            memProgress.style.width = `${memUsage}%`;
            memProgress.className = memUsage > 80 ? 'progress-fill danger' : 
                                   memUsage > 60 ? 'progress-fill warning' : 'progress-fill';
        }
        
        // Simulate other metrics
        const responseTime = (Math.random() * 3 + 1).toFixed(1); // 1-4s
        const successRate = (Math.random() * 10 + 90).toFixed(1); // 90-100%
        const throughput = (Math.random() * 5 + 8).toFixed(1); // 8-13 ops/min
        
        document.getElementById('response-time')?.textContent = `${responseTime}s`;
        document.getElementById('success-rate')?.textContent = `${successRate}%`;
        document.getElementById('throughput')?.textContent = `${throughput} ops/min`;
        
        // Update intelligence feed
        updateIntelligenceFeed();
        
    }, 5000); // Update every 5 seconds
}

function updateIntelligenceFeed() {
    const feedElement = document.getElementById('intelligence-feed');
    if (!feedElement) return;
    
    const intelTypes = ['THREAT', 'INTEL', 'METRIC', 'ALERT', 'DATA', 'OPSEC', 'PERF'];
    const messages = {
        'THREAT': ['Rate limiting detected', 'Unusual response patterns', 'Security headers missing'],
        'INTEL': ['Technology identified', 'API structure mapped', 'Authentication method detected'],
        'METRIC': ['Response time spike', 'Throughput increase', 'Error rate change'],
        'ALERT': ['Agent retry attempt', 'Operation timeout', 'Connection failure'],
        'DATA': ['Product extraction complete', 'Data validation passed', 'Schema analysis complete'],
        'OPSEC': ['Stealth protocols active', 'IP rotation executed', 'User-agent randomized'],
        'PERF': ['CPU utilization normal', 'Memory usage stable', 'Network latency low']
    };
    
    // Randomly add new intelligence entries
    if (Math.random() < 0.3) { // 30% chance
        const type = intelTypes[Math.floor(Math.random() * intelTypes.length)];
        const message = messages[type][Math.floor(Math.random() * messages[type].length)];
        const timestamp = new Date().toLocaleTimeString();
        
        const entry = document.createElement('div');
        entry.className = 'intel-entry';
        entry.innerHTML = `
            <span class="intel-time">${timestamp}</span>
            <span class="intel-type ${type}">${type}</span>
            <span class="intel-message">${message}</span>
        `;
        
        feedElement.insertBefore(entry, feedElement.firstChild);
        
        // Keep only last 10 entries
        const entries = feedElement.children;
        if (entries.length > 10) {
            feedElement.removeChild(entries[entries.length - 1]);
        }
    }
}