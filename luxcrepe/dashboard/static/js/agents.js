/**
 * SEADOG Command Center - Agents JavaScript
 * Agent monitoring and control interface
 */

class SEADOGAgents {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.agentData = {};
        
        this.init();
    }
    
    init() {
        console.log('SEADOG Agents interface initializing...');
        this.connectWebSocket();
        this.startAgentSimulation();
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected to agents interface');
            this.isConnected = true;
            this.updateConnectionStatus('CONNECTED', 'status-online');
            
            this.sendMessage({ type: 'get_agents' });
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onclose = () => {
            this.isConnected = false;
            this.updateConnectionStatus('DISCONNECTED', 'status-offline');
        };
    }
    
    sendMessage(message) {
        if (this.isConnected && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'agent_status':
                this.updateAgentData(data.data);
                break;
            case 'monitoring_update':
                this.updateAgentData(data.agent_status);
                break;
        }
    }
    
    updateAgentData(agentData) {
        this.agentData = agentData;
        this.updateAgentDisplay();
    }
    
    updateAgentDisplay() {
        Object.keys(this.agentData).forEach(agentId => {
            const agent = this.agentData[agentId];
            
            // Update agent status elements
            this.updateElement(`${agentId.toLowerCase()}-status`, 
                agent.status === 'ONLINE' ? '● ONLINE' : '● OFFLINE'
            );
            this.updateElement(`${agentId.toLowerCase()}-task`, agent.current_task || 'STANDBY');
            this.updateElement(`${agentId.toLowerCase()}-success`, 
                `${(agent.success_rate * 100).toFixed(1)}%`
            );
            this.updateElement(`${agentId.toLowerCase()}-response`, 
                `${agent.avg_response_time.toFixed(1)}s`
            );
            this.updateElement(`${agentId.toLowerCase()}-errors`, agent.errors || 0);
        });
        
        // Update summary stats
        const totalAgents = Object.keys(this.agentData).length;
        const onlineAgents = Object.values(this.agentData).filter(a => a.status === 'ONLINE').length;
        const activeTasks = Object.values(this.agentData).filter(a => a.current_task !== 'STANDBY').length;
        
        this.updateElement('total-agents', totalAgents);
        this.updateElement('online-agents', onlineAgents);
        this.updateElement('active-tasks', activeTasks);
    }
    
    updateConnectionStatus(status, className) {
        const statusElement = document.getElementById('connection-status');
        const indicatorElement = document.getElementById('connection-indicator');
        
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = className;
        }
        
        if (indicatorElement) {
            indicatorElement.className = className === 'status-online' ? 'live-indicator' : 'live-indicator status-offline';
        }
    }
    
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }
    
    startAgentSimulation() {
        // Simulate agent activity for demo
        setInterval(() => {
            this.simulateAgentActivity();
        }, 3000);
    }
    
    simulateAgentActivity() {
        const agents = [
            'alpha-overlord', 'alpha-prophet', 'alpha-radio',
            'bravo-pathfinder', 'bravo-sledgehammer', 'bravo-hammer', 'bravo-sharpshooter',
            'charlie-tech', 'charlie-medic', 'charlie-logistics', 'charlie-engineer',
            'delta-ghost', 'delta-oracle'
        ];
        
        const tasks = ['STANDBY', 'RECONNAISSANCE', 'DATA_EXTRACTION', 'VALIDATION', 'MONITORING'];
        
        agents.forEach(agentId => {
            // Randomly update task
            if (Math.random() < 0.1) { // 10% chance
                const task = tasks[Math.floor(Math.random() * tasks.length)];
                this.updateElement(`${agentId}-task`, task);
            }
            
            // Simulate slight variations in metrics
            if (Math.random() < 0.2) { // 20% chance
                const successRate = (95 + Math.random() * 4).toFixed(1); // 95-99%
                this.updateElement(`${agentId}-success`, `${successRate}%`);
                
                const responseTime = (1.0 + Math.random() * 2.0).toFixed(1); // 1-3s
                this.updateElement(`${agentId}-response`, `${responseTime}s`);
            }
        });
        
        this.updateElement('last-update', new Date().toLocaleTimeString());
    }
}

// Global functions for button handlers
function deploySquad(squad) {
    console.log(`Deploying ${squad} squad...`);
    if (agents.isConnected) {
        agents.sendMessage({
            type: 'deploy_squad',
            squad: squad
        });
    }
}

function refreshAgents() {
    console.log('Refreshing agent status...');
    if (agents.isConnected) {
        agents.sendMessage({ type: 'get_agents' });
    }
}

function recallAllAgents() {
    console.log('Recalling all agents...');
    if (agents.isConnected) {
        agents.sendMessage({
            type: 'recall_agents',
            all: true
        });
    }
}

function emergencyStopAgents() {
    console.log('Emergency stop - all agents!');
    if (agents.isConnected) {
        agents.sendMessage({
            type: 'emergency_stop',
            target: 'agents'
        });
    }
}

// Initialize when page loads
let agents;
document.addEventListener('DOMContentLoaded', () => {
    agents = new SEADOGAgents();
});