#!/usr/bin/env python3
"""
SEADOG Command Center Dashboard Launcher
Simple launcher script to run the dashboard with proper imports
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    # Import dashboard components
    from luxcrepe.dashboard.app import command_center
    import uvicorn
    
    if __name__ == "__main__":
        print("🚀 Starting SEADOG Command Center Dashboard...")
        print("=" * 60)
        print("Dashboard will be available at: http://127.0.0.1:8000")
        print("Navigation:")
        print("  • Dashboard: http://127.0.0.1:8000/")
        print("  • Agents:    http://127.0.0.1:8000/agents")
        print("  • Tests:     http://127.0.0.1:8000/tests")
        print("  • Intel:     http://127.0.0.1:8000/intel")
        print("=" * 60)
        print()
        
        # Start the command center monitoring
        asyncio.run(command_center.start_monitoring())
        
        # Run the web server
        uvicorn.run(
            command_center.app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=True
        )

except ImportError as e:
    print(f"❌ Import error: {e}")
    print()
    print("Creating a standalone dashboard version...")
    
    # Create a standalone version without the complex imports
    from fastapi import FastAPI, Request
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from fastapi.responses import HTMLResponse
    import uvicorn
    
    # Create simple standalone app
    app = FastAPI(title="SEADOG Command Center", description="Military Testing Dashboard")
    
    # Setup templates and static files
    templates_dir = Path(__file__).parent / "templates"
    static_dir = Path(__file__).parent / "static"
    
    templates = Jinja2Templates(directory=str(templates_dir))
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Simple system status for demo
    system_status = {
        "integration_active": True,
        "intelligence_active": True,
        "agents_online": 13,
        "active_operations": 2,
        "uptime": "2h 45m",
        "last_update": "14:32:15"
    }
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "title": "SEADOG Command Center",
            "system_status": system_status
        })
    
    @app.get("/agents", response_class=HTMLResponse)
    async def agents_view(request: Request):
        return templates.TemplateResponse("agents.html", {
            "request": request,
            "title": "Agent Dashboard",
            "agent_status": {}
        })
    
    @app.get("/tests", response_class=HTMLResponse)
    async def tests_view(request: Request):
        return templates.TemplateResponse("tests.html", {
            "request": request,
            "title": "Test Execution Monitor",
            "operation_log": []
        })
    
    @app.get("/intel", response_class=HTMLResponse)
    async def intelligence_view(request: Request):
        return templates.TemplateResponse("intelligence.html", {
            "request": request,
            "title": "Intelligence Center",
            "intelligence_feed": []
        })
    
    @app.get("/api/status")
    async def api_status():
        return {
            "status": "OPERATIONAL",
            "system_status": system_status
        }
    
    if __name__ == "__main__":
        print("🚀 Starting SEADOG Command Center Dashboard (Standalone Mode)...")
        print("=" * 60)
        print("Dashboard available at: http://127.0.0.1:8000")
        print("=" * 60)
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=True
        )