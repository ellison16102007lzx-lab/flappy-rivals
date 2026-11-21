"""
Flappy Rivals - Pipes Module

Manages obstacle (pipe) creation, movement, rendering, and collision detection.
Supports branching paths for Level 3.
"""

import random


class Pipe:
    """
    Represents a single pipe obstacle with a gap.

    For branching paths (Level 3), a pipe can have two gaps.
    """

    # Pipe dimensions
    WIDTH = 60
    THICKNESS = 6  # Cap thickness

    # Colors
    PIPE_COLOR = (34, 139, 34)        # Dark green
    PIPE_HIGHLIGHT = (50, 180, 50)    # Lighter green
    PIPE_BORDER = (20, 100, 20)       # Darker green

    def __init__(self, x, gap_y, gap_size, speed, second_gap_y=None):
        """
        Initialize a pipe obstacle.

        Args:
            x: Initial horizontal position (right side of screen)
            gap_y: Center Y position of the gap
            gap_size: Height of the gap in pixels
            speed: Horizontal scroll speed (pixels per frame)
            second_gap_y: Optional second gap center for branching paths (Level 3)
        """
        self.x = x
        self.gap_y = gap_y
        self.gap_size = gap_size
        self.speed = speed
        self.width = self.WIDTH
        self.scored = False  # Track if this pipe has already been scored
        self.second_gap_y = second_gap_y  # None unless branching path

    def update(self):
        """Move the pipe left by its speed."""
        self.x -= self.speed

    def is_off_screen(self):
        """Check if the pipe has moved completely off the left side."""
        return self.x + self.width < -10

    def is_passed(self, bird_x, bird_width):
        """
        Check if the bird has passed this pipe (for scoring).

        Args:
            bird_x: Bird's x position
            bird_width: Bird's width

        Returns:
            bool: True if the bird's right edge passed the pipe's left edge
        """
        return bird_x > self.x + self.width and not self.scored

    def get_collision_rects(self, screen_height):
        """
        Get the collision rectangles for this pipe.

        For normal pipes: top segment and bottom segment.
        For branching pipes: up to 3 segments (top, middle, bottom).

        Args:
            screen_height: Total height of the game screen

        Returns:
            list: List of (x, y, width, height) tuples for collision detection
        """
        rects = []
        half_gap = self.gap_size / 2.0

        if self.second_gap_y is not None:
            # Branching path: two gaps
            gap1_top = self.gap_y - half_gap
            gap1_bottom = self.gap_y + half_gap
            gap2_top = self.second_gap_y - half_gap
            gap2_bottom = self.second_gap_y + half_gap

            # Sort gaps by Y position
            if gap1_top > gap2_top:
                gap1_top, gap2_top = gap2_top, gap1_top
                gap1_bottom, gap2_bottom = gap2_bottom, gap1_bottom

            # Top segment (above first gap)
            if gap1_top > 0:
                rects.append((self.x, 0, self.width, gap1_top))
            # Middle segment (between two gaps)
            if gap2_bottom > gap1_bottom:
                rects.append((self.x, gap1_bottom, self.width, gap2_top - gap1_bottom))
            # Bottom segment (below second gap)
            if gap2_bottom < screen_height:
                rects.append((self.x, gap2_bottom, self.width, screen_height - gap2_bottom))
        else:
            # Normal pipe: one gap
            top_end = self.gap_y - half_gap
            bottom_start = self.gap_y + half_gap

            # Top segment
            if top_end > 0:
                rects.append((self.x, 0, self.width, top_end))
            # Bottom segment
            if bottom_start < screen_height:
                rects.append((self.x, bottom_start, self.width, screen_height - bottom_start))

        return rects

    def draw(self, ctx, screen_height):
        """
        Draw the pipe on the HTML Canvas context.

        Args:
            ctx: HTML Canvas 2D rendering context
            screen_height: Total height of the game screen
        """
        half_gap = self.gap_size / 2.0

        if self.second_gap_y is not None:
            # Branching path: two gaps
            gap1_top = self.gap_y - half_gap
            gap1_bottom = self.gap_y + half_gap
            gap2_top = self.second_gap_y - half_gap
            gap2_bottom = self.second_gap_y + half_gap

            if gap1_top > gap2_top:
                gap1_top, gap2_top = gap2_top, gap1_top
                gap1_bottom, gap2_bottom = gap2_bottom, gap1_bottom

            segments = []
            if gap1_top > 0:
                segments.append((self.x, 0, self.width, gap1_top))
            if gap2_bottom > gap1_bottom:
                segments.append((self.x, gap1_bottom, self.width, gap2_top - gap1_bottom))
            if gap2_bottom < screen_height:
                segments.append((self.x, gap2_bottom, self.width, screen_height - gap2_bottom))
        else:
            # Normal pipe: one gap
            top_end = self.gap_y - half_gap
            bottom_start = self.gap_y + half_gap

            segments = []
            if top_end > 0:
                segments.append((self.x, 0, self.width, top_end))
            if bottom_start < screen_height:
                segments.append((self.x, bottom_start, self.width, screen_height - bottom_start))

        # Draw each segment
        for seg_x, seg_y, seg_w, seg_h in segments:
            if seg_h <= 0:
                continue

            # Main pipe body
            ctx.fillStyle = "#%02x%02x%02x" % self.PIPE_COLOR
            ctx.fillRect(seg_x, seg_y, seg_w, seg_h)

            # Highlight (right edge)
            ctx.fillStyle = "#%02x%02x%02x" % self.PIPE_HIGHLIGHT
            ctx.fillRect(seg_x + seg_w - 6, seg_y, 6, seg_h)

            # Border (left edge)
            ctx.fillStyle = "#%02x%02x%02x" % self.PIPE_BORDER
            ctx.fillRect(seg_x, seg_y, 4, seg_h)

            # Draw cap at the edge of the gap
            cap_height = self.THICKNESS
            if seg_y + seg_h == top_end or (self.second_gap_y is None and seg_y + seg_h == gap1_top):
                # Cap on top pipe (bottom edge)
                ctx.fillStyle = "#%02x%02x%02x" % self.PIPE_COLOR
                ctx.fillRect(seg_x - 4, seg_y + seg_h - cap_height, seg_w + 8, cap_height)
                ctx.fillStyle = "#%02x%02x%02x" % self.PIPE_BORDER
                ctx.fillRect(seg_x - 4, seg_y + seg_h - cap_height, 4, cap_height)


class PipeManager:
    """
    Manages a collection of pipes, handling spawning, movement, and cleanup.
    """

    def __init__(self, screen_width, screen_height):
        """
        Initialize the pipe manager.

        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pipes = []
        self.spawn_timer = 0
        self.spawn_interval = 120  # frames between spawns
        self.pipe_speed = 3.0
        self.gap_size = 160
        self.obstacles_to_clear = 3
        self.branching_enabled = False

    def spawn_pipe(self, second_gap_y=None):
        """
        Spawn a new pipe at the right edge of the screen.

        Args:
            second_gap_y: Optional second gap for branching paths
        """
        x = self.screen_width
        # Ensure gap is within reasonable bounds
        margin = self.gap_size / 2.0 + 20
        gap_y = random.uniform(margin, self.screen_height - margin)

        pipe = Pipe(x, gap_y, self.gap_size, self.pipe_speed, second_gap_y)
        self.pipes.append(pipe)

    def update(self):
        """Update all pipes: move them and remove off-screen ones."""
        self.spawn_timer += 1

        # Spawn new pipe when timer reaches interval
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            if self.branching_enabled:
                # For branching paths, create a second gap
                margin = self.gap_size / 2.0 + 20
                second_gap = random.uniform(margin, self.screen_height - margin)
                self.spawn_pipe(second_gap_y=second_gap)
            else:
                self.spawn_pipe()

        # Move all pipes
        for pipe in self.pipes:
            pipe.update()

        # Remove off-screen pipes
        self.pipes = [p for p in self.pipes if not p.is_off_screen()]

    def get_collision_rects(self):
        """
        Get all collision rectangles from all pipes.

        Returns:
            list: List of (x, y, width, height) tuples
        """
        rects = []
        for pipe in self.pipes:
            rects.extend(pipe.get_collision_rects(self.screen_height))
        return rects

    def draw(self, ctx):
        """Draw all pipes."""
        for pipe in self.pipes:
            pipe.draw(ctx, self.screen_height)

    def check_passed(self, bird_x, bird_width):
        """
        Check which pipes have been passed by the bird.

        Args:
            bird_x: Bird's x position
            bird_width: Bird's width

        Returns:
            int: Number of newly passed pipes (0 or 1)
        """
        count = 0
        for pipe in self.pipes:
            if pipe.is_passed(bird_x, bird_width):
                pipe.scored = True
                count += 1
        return count

    def reset(self):
        """Clear all pipes and reset the spawn timer."""
        self.pipes = []
        self.spawn_timer = 0

    def configure(self, speed=None, gap_size=None, spawn_interval=None,
                  obstacles_to_clear=None, branching_enabled=None):
        """
        Configure pipe behavior from level settings.

        Args:
            speed: Pipe scroll speed
            gap_size: Gap height in pixels
            spawn_interval: Frames between spawns
            obstacles_to_clear: Number of obstacles to clear for level completion
            branching_enabled: Whether to use branching paths
        """
        if speed is not None:
            self.pipe_speed = speed
        if gap_size is not None:
            self.gap_size = gap_size
        if spawn_interval is not None:
            self.spawn_interval = spawn_interval
        if obstacles_to_clear is not None:
            self.obstacles_to_clear = obstacles_to_clear
        if branching_enabled is not None:
            self.branching_enabled = branching_enabled
