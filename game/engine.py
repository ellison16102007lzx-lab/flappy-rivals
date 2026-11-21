"""
Flappy Rivals - Game Engine

Core game engine managing updates, rendering, collision detection, and level transitions.
Provides integration interfaces for voice and ML modules.
"""

import math
from game.bird import Bird
from game.pipes import PipeManager
from game.levels import LevelManager, get_level_config


# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500

# Colors
SKY_BLUE = (135, 206, 235)
GROUND_COLOR = (139, 90, 43)
GROUND_HEIGHT = 40
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GRAY = (50, 50, 50)


def rgb(color):
    """Convert an RGB tuple to a CSS color string."""
    return "#%02x%02x%02x" % color


class GameEngine:
    """
    Main game engine that manages the game loop, state, rendering, and integration.

    Game States:
        - "start": Start screen waiting for player
        - "playing": Active gameplay
        - "gameover": Game over screen
        - "levelcomplete": Level completion screen
    """

    def __init__(self, canvas, ctx):
        """
        Initialize the game engine.

        Args:
            canvas: HTML Canvas element
            ctx: HTML Canvas 2D rendering context
        """
        self.canvas = canvas
        self.ctx = ctx

        # Game state
        self.state = "start"  # start, playing, gameover, levelcomplete
        self.score = 0
        self.game_over = False
        self.winner = None

        # Common game state dictionary (shared interface)
        self.game_state = {
            "level": 1,
            "bird_y": 200.0,
            "bird_velocity": 0.0,
            "pipe_gap_y": 180.0,
            "score": 0,
            "game_over": False,
            "energy": 100.0,
            "voice_level": 0.0,
            "prediction": None,
            "winner": None,
        }

        # Bird
        self.bird = Bird(150, SCREEN_HEIGHT / 2 - 30)

        # Pipes
        self.pipe_manager = PipeManager(SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT)

        # Levels
        self.level_manager = LevelManager()

        # Voice integration (placeholder)
        self.voice_level = 0.0
        self.energy = 100.0

        # ML integration (placeholder)
        self.prediction = None
        self.bluff_feedback = None

        # Animation frame tracking
        self.frame_count = 0

        # Apply initial level configuration
        self._apply_level_config()

    def _apply_level_config(self):
        """Apply the current level's configuration to game components."""
        config = self.level_manager.get_config()

        self.pipe_manager.configure(
            speed=config["pipe_speed"],
            gap_size=config["gap_size"],
            spawn_interval=config["spawn_interval"],
            obstacles_to_clear=config["obstacles_to_clear"],
            branching_enabled=config["branching_enabled"],
        )

        self.game_state["level"] = self.level_manager.current_level

    def start(self):
        """Start or restart the game."""
        self.state = "playing"
        self.score = 0
        self.game_over = False
        self.winner = None
        self.frame_count = 0
        self.energy = 100.0
        self.voice_level = 0.0
        self.prediction = None
        self.bluff_feedback = None

        # Reset bird
        self.bird.reset(150, SCREEN_HEIGHT / 2 - 30)

        # Reset pipes
        self.pipe_manager.reset()

        # Reset level progress
        self.level_manager.reset_level()

        # Apply level config
        self._apply_level_config()

        # Update game state
        self._update_game_state()

    def restart(self):
        """Restart from the current level."""
        self.state = "playing"
        self.score = 0
        self.game_over = False
        self.winner = None
        self.frame_count = 0
        self.energy = 100.0

        # Reset bird
        self.bird.reset(150, SCREEN_HEIGHT / 2 - 30)

        # Reset pipes
        self.pipe_manager.reset()

        # Reset level progress
        self.level_manager.reset_level()

        # Apply level config
        self._apply_level_config()

        # Update game state
        self._update_game_state()

    def set_level(self, level):
        """
        Set the current level.

        Args:
            level: Level number (1-5)
        """
        self.level_manager.set_level(level)
        self._apply_level_config()
        self._update_game_state()

    def jump(self):
        """Make the bird jump (called on Space press)."""
        if self.state == "start":
            self.start()
        elif self.state == "playing":
            config = self.level_manager.get_config()
            self.bird.jump(config["jump_strength"])
        elif self.state == "gameover":
            self.restart()
        elif self.state == "levelcomplete":
            # Advance to next level
            next_lvl = self.level_manager.next_level()
            if next_lvl is not None:
                self._apply_level_config()
                self.start()
            else:
                # Already at max level, restart current
                self.restart()

    def update(self):
        """
        Update game state for one frame.
        Called each frame by the animation loop.
        """
        if self.state != "playing":
            return

        self.frame_count += 1
        config = self.level_manager.get_config()

        # Update bird physics
        self.bird.update(config["gravity"])

        # Update pipes
        self.pipe_manager.update()

        # Check for passed pipes (scoring)
        passed = self.pipe_manager.check_passed(self.bird.x, self.bird.width)
        if passed > 0:
            self.score += passed
            self.level_manager.record_obstacle_cleared()

        # Check collision
        if self._check_collision():
            self.state = "gameover"
            self.game_over = True
            self.winner = "AI"  # AI wins on collision
        else:
            # Check screen boundaries
            play_height = SCREEN_HEIGHT - GROUND_HEIGHT
            if self.bird.y < 0 or self.bird.y + self.bird.height > play_height:
                self.state = "gameover"
                self.game_over = True
                self.winner = "AI"

        # Check level completion
        if self.level_manager.is_level_complete() and self.state == "playing":
            self.state = "levelcomplete"
            self.winner = "Player"

        # Update game state dictionary
        self._update_game_state()

    def _check_collision(self):
        """
        Check if the bird collides with any pipe.

        Returns:
            bool: True if collision detected
        """
        bird_rect = self.bird.get_bounds()
        pipe_rects = self.pipe_manager.get_collision_rects()

        for px, py, pw, ph in pipe_rects:
            if self._rects_overlap(bird_rect, (px, py, pw, ph)):
                return True
        return False

    def _rects_overlap(self, r1, r2):
        """
        Check if two rectangles overlap.

        Args:
            r1: (x, y, w, h) first rectangle
            r2: (x, y, w, h) second rectangle

        Returns:
            bool: True if rectangles overlap
        """
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2

    def _update_game_state(self):
        """Update the shared game state dictionary."""
        self.game_state["bird_y"] = float(self.bird.y)
        self.game_state["bird_velocity"] = float(self.bird.velocity)
        self.game_state["score"] = self.score
        self.game_state["game_over"] = self.game_over
        self.game_state["energy"] = self.energy
        self.game_state["voice_level"] = self.voice_level
        self.game_state["prediction"] = self.prediction
        self.game_state["winner"] = self.winner
        self.game_state["level"] = self.level_manager.current_level

        # Update pipe gap Y from the first pipe if available
        if self.pipe_manager.pipes:
            self.game_state["pipe_gap_y"] = float(self.pipe_manager.pipes[0].gap_y)

    def draw(self):
        """Draw the current game state on the canvas."""
        ctx = self.ctx

        # Clear canvas
        ctx.fillStyle = rgb(SKY_BLUE)
        ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Draw background elements
        self._draw_background()

        if self.state == "start":
            self._draw_start_screen()
        elif self.state == "playing":
            self._draw_gameplay()
        elif self.state == "gameover":
            self._draw_gameplay()
            self._draw_game_over()
        elif self.state == "levelcomplete":
            self._draw_gameplay()
            self._draw_level_complete()

    def _draw_background(self):
        """Draw the background (sky gradient and ground)."""
        ctx = self.ctx

        # Ground
        ctx.fillStyle = rgb(GROUND_COLOR)
        ctx.fillRect(0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)

        # Ground line
        ctx.strokeStyle = rgb(DARK_GRAY)
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(0, SCREEN_HEIGHT - GROUND_HEIGHT)
        ctx.lineTo(SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT)
        ctx.stroke()

        # Simple clouds
        ctx.fillStyle = "rgba(255, 255, 255, 0.6)"
        self._draw_cloud(100, 60, 40)
        self._draw_cloud(350, 100, 35)
        self._draw_cloud(600, 50, 45)
        self._draw_cloud(750, 120, 30)

    def _draw_cloud(self, x, y, size):
        """Draw a simple cloud shape."""
        ctx = self.ctx
        ctx.beginPath()
        ctx.arc(x, y, size, 0, 2 * math.pi)
        ctx.arc(x + size, y - size // 3, size * 0.7, 0, 2 * math.pi)
        ctx.arc(x + size * 1.5, y, size * 0.8, 0, 2 * math.pi)
        ctx.fill()

    def _draw_gameplay(self):
        """Draw the active gameplay elements."""
        # Draw pipes
        self.pipe_manager.draw(self.ctx)

        # Draw bird
        self.bird.draw(self.ctx)

        # Draw HUD
        self._draw_hud()

    def _draw_hud(self):
        """Draw the heads-up display (score, level, energy)."""
        ctx = self.ctx

        # Score
        ctx.fillStyle = rgb(WHITE)
        ctx.strokeStyle = rgb(BLACK)
        ctx.lineWidth = 3
        ctx.font = "bold 28px monospace"
        ctx.textAlign = "center"
        ctx.strokeText(f"Score: {self.score}", SCREEN_WIDTH // 2, 40)
        ctx.fillText(f"Score: {self.score}", SCREEN_WIDTH // 2, 40)

        # Level
        ctx.font = "bold 20px monospace"
        ctx.textAlign = "left"
        level_name = self.level_manager.get_config()["name"]
        ctx.strokeText(f"Lvl {self.level_manager.current_level}: {level_name}", 15, 30)
        ctx.fillText(f"Lvl {self.level_manager.current_level}: {level_name}", 15, 30)

        # Progress
        cleared, total = self.level_manager.get_progress()
        ctx.textAlign = "right"
        ctx.strokeText(f"Pipes: {cleared}/{total}", SCREEN_WIDTH - 15, 30)
        ctx.fillText(f"Pipes: {cleared}/{total}", SCREEN_WIDTH - 15, 30)

        # Energy bar (for voice integration)
        bar_x = SCREEN_WIDTH - 160
        bar_y = 40
        bar_w = 140
        bar_h = 12
        ctx.fillStyle = rgb(DARK_GRAY)
        ctx.fillRect(bar_x, bar_y, bar_w, bar_h)
        energy_w = max(0, (self.energy / 100.0) * bar_w)
        ctx.fillStyle = rgb(GREEN)
        ctx.fillRect(bar_x, bar_y, energy_w, bar_h)
        ctx.strokeStyle = rgb(BLACK)
        ctx.lineWidth = 1
        ctx.strokeRect(bar_x, bar_y, bar_w, bar_h)

        # Voice level indicator
        if self.voice_level > 0:
            ctx.fillStyle = rgb(RED)
            ctx.font = "14px monospace"
            ctx.textAlign = "right"
            ctx.fillText(f"Voice: {self.voice_level:.2f}", SCREEN_WIDTH - 15, 70)

    def _draw_start_screen(self):
        """Draw the start screen."""
        ctx = self.ctx

        # Overlay
        ctx.fillStyle = "rgba(0, 0, 0, 0.5)"
        ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Title
        ctx.fillStyle = rgb(WHITE)
        ctx.strokeStyle = rgb(BLACK)
        ctx.lineWidth = 4
        ctx.font = "bold 48px monospace"
        ctx.textAlign = "center"
        ctx.strokeText("Flappy Rivals", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)
        ctx.fillText("Flappy Rivals", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)

        # Instructions
        ctx.font = "20px monospace"
        ctx.lineWidth = 2
        ctx.strokeText("Press SPACE to start", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
        ctx.fillText("Press SPACE to start", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)

        ctx.strokeText("Press SPACE to flap", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
        ctx.fillText("Press SPACE to flap", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)

        # Level selection hint
        ctx.font = "16px monospace"
        ctx.strokeText("Press 1-5 to select level", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
        ctx.fillText("Press 1-5 to select level", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)

        # Draw bird preview
        self.bird.draw(ctx)

    def _draw_game_over(self):
        """Draw the game over screen."""
        ctx = self.ctx

        # Overlay
        ctx.fillStyle = "rgba(0, 0, 0, 0.6)"
        ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Game Over text
        ctx.fillStyle = rgb(RED)
        ctx.strokeStyle = rgb(BLACK)
        ctx.lineWidth = 4
        ctx.font = "bold 48px monospace"
        ctx.textAlign = "center"
        ctx.strokeText("Game Over", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        ctx.fillText("Game Over", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)

        # Score
        ctx.fillStyle = rgb(WHITE)
        ctx.font = "28px monospace"
        ctx.lineWidth = 2
        ctx.strokeText(f"Score: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        ctx.fillText(f"Score: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # Restart
        ctx.font = "20px monospace"
        ctx.strokeText("Press SPACE to restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        ctx.fillText("Press SPACE to restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

    def _draw_level_complete(self):
        """Draw the level complete screen."""
        ctx = self.ctx

        # Overlay
        ctx.fillStyle = "rgba(0, 0, 0, 0.6)"
        ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Level Complete text
        ctx.fillStyle = rgb(GREEN)
        ctx.strokeStyle = rgb(BLACK)
        ctx.lineWidth = 4
        ctx.font = "bold 40px monospace"
        ctx.textAlign = "center"
        ctx.strokeText("Level Complete!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        ctx.fillText("Level Complete!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)

        # Score
        ctx.fillStyle = rgb(WHITE)
        ctx.font = "24px monospace"
        ctx.lineWidth = 2
        ctx.strokeText(f"Score: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        ctx.fillText(f"Score: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # Next level
        ctx.font = "20px monospace"
        ctx.strokeText("Press SPACE for next level", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        ctx.fillText("Press SPACE for next level", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

    # --- Integration Interfaces ---

    def apply_obstacle_command(self, command, value=0.0):
        """
        Apply an obstacle movement command (from voice/ML modules).

        Args:
            command: Command type string (e.g., "move_gap_up", "move_gap_down", "narrow_gap")
            value: Command value (0.0-1.0 normalized)
        """
        if self.state != "playing":
            return

        shift = value * 50  # Max 50 pixel shift
        for pipe in self.pipe_manager.pipes:
            if command == "move_gap_up":
                pipe.gap_y = max(pipe.gap_size / 2 + 10, pipe.gap_y - shift)
            elif command == "move_gap_down":
                play_height = SCREEN_HEIGHT - GROUND_HEIGHT
                pipe.gap_y = min(play_height - pipe.gap_size / 2 - 10, pipe.gap_y + shift)
            elif command == "narrow_gap":
                pipe.gap_size = max(80, pipe.gap_size - value * 40)

    def apply_voice_powerup(self, voice_level, energy_cost=5.0):
        """
        Apply a voice power-up command.

        Args:
            voice_level: Normalized voice level (0.0-1.0)
            energy_cost: Energy cost for the power-up
        """
        self.voice_level = voice_level
        if voice_level > 0.5 and self.energy >= energy_cost:
            self.energy -= energy_cost
            # Strong voice narrows gaps
            self.apply_obstacle_command("narrow_gap", voice_level)
        self._update_game_state()

    def set_prediction(self, prediction):
        """
        Set the ML prediction for the bird's future position.

        Args:
            prediction: Predicted Y position (float) or None
        """
        self.prediction = prediction
        self.game_state["prediction"] = prediction

    def set_bluff_feedback(self, feedback):
        """
        Set the AI bluff feedback.

        Args:
            feedback: Bluff feedback string or None
        """
        self.bluff_feedback = feedback

    def get_bird_position(self):
        """
        Get the current bird position.

        Returns:
            tuple: (x, y) bird position
        """
        return (self.bird.x, self.bird.y)

    def get_bird_velocity(self):
        """
        Get the current bird velocity.

        Returns:
            float: Bird's vertical velocity
        """
        return self.bird.velocity

    def get_game_state(self):
        """
        Get the shared game state dictionary.

        Returns:
            dict: Current game state
        """
        return self.game_state.copy()

    def get_collision_status(self):
        """
        Check if a collision has occurred.

        Returns:
            bool: True if collision detected
        """
        return self.game_over

    def get_score(self):
        """
        Get the current score.

        Returns:
            int: Current score
        """
        return self.score

    def handle_key(self, key):
        """
        Handle keyboard input.

        Args:
            key: The key that was pressed (string)
        """
        if key == " ":
            self.jump()
        elif key in ("1", "2", "3", "4", "5"):
            level = int(key)
            self.level_manager.set_level(level)
            self._apply_level_config()
            if self.state == "playing":
                self.restart()
