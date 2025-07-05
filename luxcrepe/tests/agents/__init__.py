# SEADOG Military Testing Framework - Agent Squads

# Alpha Squad - Reconnaissance & Surveillance
from .alpha import ReconSpecialistAgent, SurveillanceSpecialistAgent

# Bravo Squad - Fire Team Operations
from .bravo import BreacherAgent, AssaultSpecialistAgent, DesignatedMarksmanAgent

# Charlie Squad - Support Operations
from .charlie import InfrastructureSpecialistAgent, RecoverySpecialistAgent, ResourceManagerAgent

# Delta Squad - Intelligence & Recovery
from .delta import StealthTesterAgent, IntelAnalystAgent

__all__ = [
    # Alpha Squad
    "ReconSpecialistAgent",
    "SurveillanceSpecialistAgent",
    
    # Bravo Squad
    "BreacherAgent",
    "AssaultSpecialistAgent", 
    "DesignatedMarksmanAgent",
    
    # Charlie Squad
    "InfrastructureSpecialistAgent",
    "RecoverySpecialistAgent",
    "ResourceManagerAgent",
    
    # Delta Squad
    "StealthTesterAgent",
    "IntelAnalystAgent"
]