"""
Flappy Rivals - Main Entry Point

PyScript entry point that initializes the game engine and sets up the
browser animation loop and keyboard input handling.
"""

from js import document, window, console
from pyodide.ffi import create_proxy
from game.engine import GameEngine, SCREEN_WIDTH, SCREEN_HEIGHT


# Global game engine instance
engine = None


def game_loop(_timestamp):
    """
    Main game loop called each animation frame.

    Args:
        _timestamp: Browser timestamp (unused)
    """
    global engine
    if engine is not None:
        engine.update()
        engine.draw()
    window.requestAnimationFrame(game_loop_proxy)


def on_keydown(event):
    """
    Handle keyboard input events.

    Args:
        event: Keyboard event object
    """
    global engine
    if engine is not None:
        key = event.key
        # Prevent default for space to avoid scrolling
        if key == " ":
            event.preventDefault()
        engine.handle_key(key)


def init():
    """Initialize the game when PyScript is ready."""
    global engine

    console.log("Initializing Flappy Rivals...")

    # Get canvas and context
    canvas = document.getElementById("gameCanvas")
    if canvas is None:
        console.error("Canvas element not found!")
        return

    canvas.width = SCREEN_WIDTH
    canvas.height = SCREEN_HEIGHT

    ctx = canvas.getContext("2d")

    # Create game engine
    engine = GameEngine(canvas, ctx)

    # Set up keyboard listener
    keydown_proxy = create_proxy(on_keydown)
    window.addEventListener("keydown", keydown_proxy)

    # Start animation loop
    global game_loop_proxy
    game_loop_proxy = create_proxy(game_loop)
    window.requestAnimationFrame(game_loop_proxy)

    console.log("Flappy Rivals initialized successfully!")


# Run initialization
init()
