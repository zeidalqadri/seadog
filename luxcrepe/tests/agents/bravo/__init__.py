# Bravo Fire Team - Direct Action Testing

from .breacher import BreacherAgent
from .assault import AssaultAgent  
from .designated_marksman import DesignatedMarksmanAgent

# Export the agents that other modules are looking for
BreacherAgent = BreacherAgent
AssaultSpecialistAgent = AssaultAgent  # Alias for AssaultAgent
DesignatedMarksmanAgent = DesignatedMarksmanAgent

__all__ = [
    "BreacherAgent",
    "AssaultAgent",
    "AssaultSpecialistAgent", 
    "DesignatedMarksmanAgent"
]