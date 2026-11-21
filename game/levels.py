"""
Flappy Rivals - Levels Module

Configuration-driven level system for the five progressively harder levels.
Each level defines pipe behavior, obstacles to clear, and special features.
"""


# Level configurations
LEVELS = {
    1: {
        "name": "First Rival",
        "description": "Basic bird movement. Wide pipe gaps. Slow obstacles.",
        "pipe_speed": 2.0,
        "gap_size": 180,
        "spawn_interval": 140,
        "obstacles_to_clear": 3,
        "branching_enabled": False,
        "voice_powerup": False,
        "ml_prediction": False,
        "ai_bluff": False,
        "gravity": 0.5,
        "jump_strength": -8.0,
    },
    2: {
        "name": "Sound Battle",
        "description": "Faster obstacles. Voice power-up commands from Architect.",
        "pipe_speed": 3.0,
        "gap_size": 160,
        "spawn_interval": 120,
        "obstacles_to_clear": 4,
        "branching_enabled": False,
        "voice_powerup": True,
        "ml_prediction": False,
        "ai_bluff": False,
        "gravity": 0.5,
        "jump_strength": -8.0,
    },
    3: {
        "name": "Split Paths",
        "description": "Two possible routes through special obstacles. One route always passable.",
        "pipe_speed": 3.0,
        "gap_size": 130,
        "spawn_interval": 110,
        "obstacles_to_clear": 5,
        "branching_enabled": True,
        "voice_powerup": True,
        "ml_prediction": False,
        "ai_bluff": False,
        "gravity": 0.5,
        "jump_strength": -8.0,
    },
    4: {
        "name": "Predictive Rival",
        "description": "ML predictions influence obstacle behavior.",
        "pipe_speed": 3.5,
        "gap_size": 140,
        "spawn_interval": 100,
        "obstacles_to_clear": 5,
        "branching_enabled": False,
        "voice_powerup": True,
        "ml_prediction": True,
        "ai_bluff": False,
        "gravity": 0.5,
        "jump_strength": -8.0,
    },
    5: {
        "name": "Outsmart the AI",
        "description": "Combined advanced mechanics. AI Bluff active.",
        "pipe_speed": 4.0,
        "gap_size": 130,
        "spawn_interval": 90,
        "obstacles_to_clear": 7,
        "branching_enabled": True,
        "voice_powerup": True,
        "ml_prediction": True,
        "ai_bluff": True,
        "gravity": 0.55,
        "jump_strength": -8.5,
    },
}


def get_level_config(level):
    """
    Get the configuration dictionary for a given level.

    Args:
        level: Level number (1-5)

    Returns:
        dict: Level configuration dictionary

    Raises:
        ValueError: If level is out of range
    """
    if level not in LEVELS:
        raise ValueError(f"Invalid level: {level}. Must be between 1 and 5.")
    return LEVELS[level]


def get_all_levels():
    """
    Get all available levels as a list of (level_number, config) tuples.

    Returns:
        list: List of (int, dict) tuples
    """
    return [(num, cfg) for num, cfg in sorted(LEVELS.items())]


def is_valid_level(level):
    """
    Check if a level number is valid.

    Args:
        level: Level number to check

    Returns:
        bool: True if level is valid (1-5)
    """
    return level in LEVELS


def get_level_names():
    """
    Get a list of level names in order.

    Returns:
        list: List of level name strings
    """
    return [cfg["name"] for _, cfg in get_all_levels()]


class LevelManager:
    """
    Manages level progression and configuration application.
    """

    def __init__(self):
        """Initialize the level manager at level 1."""
        self.current_level = 1
        self.obstacles_cleared = 0
        self.level_complete = False

    def get_config(self):
        """
        Get the current level's configuration.

        Returns:
            dict: Current level configuration
        """
        return get_level_config(self.current_level)

    def set_level(self, level):
        """
        Set the current level.

        Args:
            level: Level number (1-5)
        """
        if is_valid_level(level):
            self.current_level = level
            self.obstacles_cleared = 0
            self.level_complete = False

    def next_level(self):
        """
        Advance to the next level if available.

        Returns:
            int or None: The new level number, or None if already at max level
        """
        if self.current_level < 5:
            self.current_level += 1
            self.obstacles_cleared = 0
            self.level_complete = False
            return self.current_level
        return None

    def record_obstacle_cleared(self):
        """
        Record that an obstacle has been cleared. Check for level completion.
        """
        self.obstacles_cleared += 1
        config = self.get_config()
        if self.obstacles_cleared >= config["obstacles_to_clear"]:
            self.level_complete = True

    def is_level_complete(self):
        """
        Check if the current level is complete.

        Returns:
            bool: True if enough obstacles have been cleared
        """
        return self.level_complete

    def reset_level(self):
        """Reset the current level's progress."""
        self.obstacles_cleared = 0
        self.level_complete = False

    def reset(self):
        """Reset to level 1."""
        self.current_level = 1
        self.obstacles_cleared = 0
        self.level_complete = False

    def get_progress(self):
        """
        Get the current progress towards level completion.

        Returns:
            tuple: (obstacles_cleared, obstacles_to_clear)
        """
        config = self.get_config()
        return (self.obstacles_cleared, config["obstacles_to_clear"])
