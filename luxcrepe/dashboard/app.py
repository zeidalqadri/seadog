"""
SEADOG Command Center - Minimalist Military Dashboard
Real-time monitoring and control interface for SEADOG-Luxcrepe integration
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

from ..integration import LuxcrepeSEADOGIntegration, IntegrationConfig
from ..intelligence import SEADOGIntelligenceSystem
from ..config import get_seadog_configurations
from ..validation import RealWorldValidator


class SEADOGCommandCenter:
    """SEADOG Command Center - Military-style monitoring dashboard"""
    
    def __init__(self):
        self.app = FastAPI(title="SEADOG Command Center", description="Military Testing Dashboard")
        self.logger = logging.getLogger("SEADOG.CommandCenter")
        
        # Dashboard state
        self.active_connections: List[WebSocket] = []
        self.system_status = {
            "integration_active": False,
            "intelligence_active": False,
            "agents_online": 0,
            "active_operations": 0,
            "total_targets": 0,
            "uptime_start": datetime.now(),
            "last_update": datetime.now()
        }
        
        # Active components
        self.integration: Optional[LuxcrepeSEADOGIntegration] = None
        self.intelligence_system: Optional[SEADOGIntelligenceSystem] = None
        self.validator: Optional[RealWorldValidator] = None
        
        # Metrics storage
        self.metrics_history: List[Dict[str, Any]] = []
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        self.operation_log: List[Dict[str, Any]] = []
        self.intelligence_feed: List[Dict[str, Any]] = []
        
        # Setup FastAPI app
        self._setup_routes()
        self._setup_static_files()
        
        # Start background monitoring
        self.monitoring_task: Optional[asyncio.Task] = None
        
        self.logger.info("SEADOG Command Center initialized")
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        # Template configuration
        templates_dir = Path(__file__).parent / "templates"
        self.templates = Jinja2Templates(directory=str(templates_dir))
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Main dashboard view"""
            return self.templates.TemplateResponse("dashboard.html", {
                "request": request,
                "title": "SEADOG Command Center",
                "system_status": self.system_status
            })
        
        @self.app.get("/agents", response_class=HTMLResponse)
        async def agents_view(request: Request):
            """Agent status and control view"""
            return self.templates.TemplateResponse("agents.html", {
                "request": request,
                "title": "Agent Dashboard",
                "agent_status": self.agent_status
            })
        
        @self.app.get("/tests", response_class=HTMLResponse)
        async def tests_view(request: Request):
            """Test execution monitoring view"""
            return self.templates.TemplateResponse("tests.html", {
                "request": request,
                "title": "Test Execution Monitor",
                "operation_log": self.operation_log[-20:]  # Last 20 operations
            })
        
        @self.app.get("/intel", response_class=HTMLResponse)
        async def intelligence_view(request: Request):
            """Intelligence feed and analysis view"""
            return self.templates.TemplateResponse("intelligence.html", {
                "request": request,
                "title": "Intelligence Center",
                "intelligence_feed": self.intelligence_feed[-50:]  # Last 50 entries
            })
        
        @self.app.get("/api/status")
        async def api_status():
            """System status API endpoint"""
            return {
                "status": "OPERATIONAL",
                "timestamp": datetime.now().isoformat(),
                "system_status": self.system_status,
                "metrics_count": len(self.metrics_history),
                "operations_count": len(self.operation_log)
            }
        
        @self.app.get("/api/agents")
        async def api_agents():
            """Agent status API endpoint"""
            return {
                "agents": self.agent_status,
                "total_agents": len(self.agent_status),
                "online_agents": sum(1 for agent in self.agent_status.values() if agent.get("status") == "ONLINE"),
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/api/metrics")
        async def api_metrics():
            """Performance metrics API endpoint"""
            recent_metrics = self.metrics_history[-100:]  # Last 100 data points
            return {
                "metrics": recent_metrics,
                "summary": self._calculate_metrics_summary(),
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/api/operations/start")
        async def start_operation(operation_data: dict):
            """Start a new operation"""
            try:
                operation_id = f"OP_{int(time.time())}"
                
                # Log operation start
                self.operation_log.append({
                    "operation_id": operation_id,
                    "type": operation_data.get("type", "UNKNOWN"),
                    "targets": operation_data.get("targets", []),
                    "status": "STARTING",
                    "timestamp": datetime.now().isoformat(),
                    "parameters": operation_data.get("parameters", {})
                })
                
                # Broadcast to connected clients
                await self._broadcast_update({
                    "type": "operation_start",
                    "operation_id": operation_id,
                    "data": operation_data
                })
                
                return {
                    "status": "SUCCESS",
                    "operation_id": operation_id,
                    "message": "Operation started successfully"
                }
                
            except Exception as e:
                self.logger.error(f"Failed to start operation: {str(e)}")
                return {
                    "status": "ERROR",
                    "message": str(e)
                }
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await self._handle_websocket(websocket)
    
    def _setup_static_files(self):
        """Setup static file serving"""
        static_dir = Path(__file__).parent / "static"
        self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    async def _handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connections for real-time updates"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        try:
            # Send initial system state
            await websocket.send_json({
                "type": "system_status",
                "data": self.system_status
            })
            
            await websocket.send_json({
                "type": "agent_status",
                "data": self.agent_status
            })
            
            # Keep connection alive and handle messages
            while True:
                try:
                    # Wait for client messages with timeout
                    message = await asyncio.wait_for(websocket.receive_json(), timeout=1.0)
                    await self._handle_websocket_message(websocket, message)
                except asyncio.TimeoutError:
                    # Send heartbeat
                    await websocket.send_json({
                        "type": "heartbeat",
                        "timestamp": datetime.now().isoformat()
                    })
                    
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
            self.logger.info("WebSocket client disconnected")
        except Exception as e:
            self.logger.error(f"WebSocket error: {str(e)}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
    
    async def _handle_websocket_message(self, websocket: WebSocket, message: dict):
        """Handle incoming WebSocket messages"""
        message_type = message.get("type")
        
        if message_type == "get_status":
            await websocket.send_json({
                "type": "system_status",
                "data": self.system_status
            })
        
        elif message_type == "get_agents":
            await websocket.send_json({
                "type": "agent_status", 
                "data": self.agent_status
            })
        
        elif message_type == "start_test":
            # Handle test start request
            test_config = message.get("config", {})
            await self._handle_test_start(test_config)
        
        elif message_type == "stop_operation":
            # Handle operation stop request
            operation_id = message.get("operation_id")
            await self._handle_operation_stop(operation_id)
    
    async def _broadcast_update(self, update_data: dict):
        """Broadcast update to all connected WebSocket clients"""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(update_data)
            except Exception as e:
                self.logger.warning(f"Failed to send update to client: {str(e)}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)
    
    async def start_monitoring(self):
        """Start background monitoring task"""
        if self.monitoring_task:
            return
        
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Background monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring task"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
        
        self.logger.info("Background monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                # Update system status
                await self._update_system_status()
                
                # Update agent status
                await self._update_agent_status()
                
                # Collect performance metrics
                await self._collect_metrics()
                
                # Update intelligence feed
                await self._update_intelligence_feed()
                
                # Broadcast updates to clients
                await self._broadcast_update({
                    "type": "monitoring_update",
                    "system_status": self.system_status,
                    "agent_status": self.agent_status,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Sleep for monitoring interval
                await asyncio.sleep(2.0)  # 2-second monitoring cycle
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
                await asyncio.sleep(5.0)  # Error recovery delay
    
    async def _update_system_status(self):
        """Update overall system status"""
        current_time = datetime.now()
        
        self.system_status.update({
            "integration_active": self.integration is not None and self.integration.is_active,
            "intelligence_active": self.intelligence_system is not None and self.intelligence_system.is_active,
            "agents_online": len([a for a in self.agent_status.values() if a.get("status") == "ONLINE"]),
            "active_operations": len([op for op in self.operation_log if op.get("status") in ["RUNNING", "STARTING"]]),
            "total_targets": sum(len(op.get("targets", [])) for op in self.operation_log),
            "uptime": str(current_time - self.system_status["uptime_start"]),
            "last_update": current_time.isoformat()
        })
    
    async def _update_agent_status(self):
        """Update individual agent status"""
        # Initialize default agent status if not exists
        agent_squads = {
            "ALPHA": ["OVERLORD", "PROPHET", "RADIO"],
            "BRAVO": ["PATHFINDER", "SLEDGEHAMMER", "HAMMER", "SHARPSHOOTER"], 
            "CHARLIE": ["TECH", "MEDIC", "LOGISTICS", "ENGINEER"],
            "DELTA": ["GHOST", "ORACLE"]
        }
        
        for squad, agents in agent_squads.items():
            for agent in agents:
                agent_id = f"{squad}_{agent}"
                if agent_id not in self.agent_status:
                    self.agent_status[agent_id] = {
                        "squad": squad,
                        "call_sign": agent,
                        "status": "ONLINE",
                        "current_task": "STANDBY",
                        "success_rate": 0.95 + (hash(agent_id) % 10) / 200,  # Simulated
                        "avg_response_time": 1.5 + (hash(agent_id) % 30) / 10,  # Simulated
                        "errors": hash(agent_id) % 3,  # Simulated
                        "last_activity": datetime.now().isoformat()
                    }
    
    async def _collect_metrics(self):
        """Collect system performance metrics"""
        current_time = datetime.now()
        
        # Simulate performance metrics (in real implementation, get from actual system)
        import random
        import psutil
        
        metrics = {
            "timestamp": current_time.isoformat(),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "response_time": 2.0 + random.uniform(-0.5, 1.5),
            "success_rate": 0.94 + random.uniform(-0.05, 0.05),
            "throughput": 8.5 + random.uniform(-2, 3),
            "active_connections": len(self.active_connections),
            "operations_count": len(self.operation_log)
        }
        
        self.metrics_history.append(metrics)
        
        # Keep only last 1000 metrics points
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    async def _update_intelligence_feed(self):
        """Update intelligence feed with new entries"""
        current_time = datetime.now()
        
        # Simulate intelligence entries (in real implementation, get from intelligence system)
        import random
        
        intelligence_types = ["THREAT", "INTEL", "METRIC", "ALERT", "DATA", "OPSEC", "PERF"]
        sample_messages = {
            "THREAT": ["Rate limiting detected", "Unusual response patterns", "Security headers missing"],
            "INTEL": ["Technology identified", "API structure mapped", "Authentication method detected"],
            "METRIC": ["Response time spike", "Throughput increase", "Error rate change"],
            "ALERT": ["Agent retry attempt", "Operation timeout", "Connection failure"],
            "DATA": ["Product extraction complete", "Data validation passed", "Schema analysis complete"],
            "OPSEC": ["Stealth score", "Detection probability", "Operational security"],
            "PERF": ["Throughput", "Memory usage", "CPU utilization"]
        }
        
        # Add random intelligence entry occasionally
        if random.random() < 0.3:  # 30% chance per cycle
            intel_type = random.choice(intelligence_types)
            message = random.choice(sample_messages[intel_type])
            
            self.intelligence_feed.append({
                "timestamp": current_time.strftime("%H:%M:%S"),
                "type": intel_type,
                "message": message,
                "details": f"Sample intelligence data - {random.randint(1, 100)}"
            })
            
            # Keep only last 200 intelligence entries
            if len(self.intelligence_feed) > 200:
                self.intelligence_feed = self.intelligence_feed[-200:]
    
    def _calculate_metrics_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics from metrics history"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.metrics_history[-20:]  # Last 20 data points
        
        return {
            "avg_response_time": sum(m["response_time"] for m in recent_metrics) / len(recent_metrics),
            "avg_success_rate": sum(m["success_rate"] for m in recent_metrics) / len(recent_metrics),
            "avg_throughput": sum(m["throughput"] for m in recent_metrics) / len(recent_metrics),
            "current_cpu": recent_metrics[-1]["cpu_usage"] if recent_metrics else 0,
            "current_memory": recent_metrics[-1]["memory_usage"] if recent_metrics else 0
        }
    
    async def _handle_test_start(self, test_config: dict):
        """Handle test start request from WebSocket"""
        try:
            # Create and start test operation
            operation_id = f"TEST_{int(time.time())}"
            
            self.operation_log.append({
                "operation_id": operation_id,
                "type": "TEST_EXECUTION",
                "status": "RUNNING",
                "config": test_config,
                "start_time": datetime.now().isoformat(),
                "targets": test_config.get("targets", [])
            })
            
            # Broadcast test start
            await self._broadcast_update({
                "type": "test_started",
                "operation_id": operation_id,
                "config": test_config
            })
            
        except Exception as e:
            self.logger.error(f"Failed to start test: {str(e)}")
    
    async def _handle_operation_stop(self, operation_id: str):
        """Handle operation stop request"""
        for operation in self.operation_log:
            if operation["operation_id"] == operation_id:
                operation["status"] = "STOPPED"
                operation["end_time"] = datetime.now().isoformat()
                break
        
        await self._broadcast_update({
            "type": "operation_stopped",
            "operation_id": operation_id
        })


# Global command center instance
command_center = SEADOGCommandCenter()


async def start_command_center(host: str = "127.0.0.1", port: int = 8000):
    """Start the SEADOG Command Center"""
    await command_center.start_monitoring()
    
    config = uvicorn.Config(
        app=command_center.app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(config)
    await server.serve()


async def stop_command_center():
    """Stop the SEADOG Command Center"""
    await command_center.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(start_command_center())