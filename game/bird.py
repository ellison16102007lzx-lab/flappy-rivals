"""
Flappy Rivals - Bird Module

Manages bird physics, rendering, and state for the Flappy Bird-style game.
"""

import math


class Bird:
    """The player-controlled bird affected by gravity."""

    # Bird dimensions
    WIDTH = 30
    HEIGHT = 24

    # Colors
    BODY_COLOR = (255, 255, 0)       # Yellow
    WING_COLOR = (255, 165, 0)       # Orange
    EYE_COLOR = (0, 0, 0)            # Black
    BEAK_COLOR = (255, 165, 0)       # Orange

    def __init__(self, x, y):
        """
        Initialize the bird at the given position.

        Args:
            x: Horizontal position (fixed during gameplay)
            y: Initial vertical position
        """
        self.x = x
        self.y = y
        self.velocity = 0.0
        self.width = self.WIDTH
        self.height = self.HEIGHT
        self.rotation = 0.0

    def jump(self, strength=-8.0):
        """
        Apply upward velocity to simulate a jump/flap.

        Args:
            strength: The upward impulse (negative = upward). Default: -8.0
        """
        self.velocity = strength

    def update(self, gravity=0.5):
        """
        Update bird position and velocity based on gravity.

        Args:
            gravity: Gravitational acceleration per frame. Default: 0.5
        """
        self.velocity += gravity
        self.y += self.velocity
        # Rotate based on velocity: tilt up when rising, down when falling
        self.rotation = max(-30.0, min(30.0, self.velocity * 3.0))

    def get_bounds(self):
        """
        Return the bounding rectangle for collision detection.

        Returns:
            tuple: (x, y, width, height) bounding box
        """
        return (self.x, self.y, self.width, self.height)

    def get_center(self):
        """
        Return the center position of the bird.

        Returns:
            tuple: (center_x, center_y)
        """
        return (self.x + self.width / 2.0, self.y + self.height / 2.0)

    def draw(self, ctx):
        """
        Draw the bird on the HTML Canvas context.

        Args:
            ctx: HTML Canvas 2D rendering context
        """
        ctx.save()

        # Translate to bird center for rotation
        cx = self.x + self.width / 2.0
        cy = self.y + self.height / 2.0
        ctx.translate(cx, cy)
        ctx.rotate(math.radians(self.rotation))
        ctx.translate(-cx, -cy)

        # Body - ellipse
        ctx.fillStyle = "#%02x%02x%02x" % self.BODY_COLOR
        ctx.beginPath()
        ctx.ellipse(cx, cy, self.width / 2.0, self.height / 2.0, 0, 0, 2 * math.pi)
        ctx.fill()

        # Wing
        ctx.fillStyle = "#%02x%02x%02x" % self.WING_COLOR
        ctx.beginPath()
        ctx.ellipse(self.x + 10, cy + 2, 8, 5, 0, 0, 2 * math.pi)
        ctx.fill()

        # Eye
        ctx.fillStyle = "#%02x%02x%02x" % self.EYE_COLOR
        ctx.beginPath()
        ctx.arc(self.x + 22, self.y + 7, 3, 0, 2 * math.pi)
        ctx.fill()

        # Beak
        ctx.fillStyle = "#%02x%02x%02x" % self.BEAK_COLOR
        ctx.beginPath()
        ctx.moveTo(self.x + 28, self.y + 10)
        ctx.lineTo(self.x + 38, self.y + 14)
        ctx.lineTo(self.x + 28, self.y + 18)
        ctx.closePath()
        ctx.fill()

        ctx.restore()

    def reset(self, x, y):
        """
        Reset the bird to initial position with zero velocity.

        Args:
            x: Horizontal position to reset to
            y: Vertical position to reset to
        """
        self.x = x
        self.y = y
        self.velocity = 0.0
        self.rotation = 0.0
