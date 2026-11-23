"""Browser adapter for the team's Python game."""
from js import document
from game.engine import GameEngine
from voice.controller import Microphone

canvas = document.getElementById("gameCanvas")
engine = GameEngine(canvas, canvas.getContext("2d"))
mic = Microphone()
armed = True
elements = {key: document.getElementById(key) for key in
            ("state", "levelSelect", "ability", "energy", "volume", "forecast")}
level_state = {"start": "Press Space to start", "playing": "In flight",
               "gameover": "Architect Win · Press Space to retry",
               "levelcomplete": "Pilot Win · Press Space to continue"}


def tick(axis, pressed, sensitivity, role):
    global armed
    volume = mic.read(sensitivity)
    elements["volume"].value = volume
    if volume <= 0.35:
        armed = True
    if role == "pilot" and armed and volume >= 0.65:
        armed = False
        if engine.state == "playing":
            engine.jump()
    engine.update(volume if role == "architect" else 0, axis, pressed)


def show():
    engine.draw()
    level = engine.level_manager.current_level
    elements["levelSelect"].value = str(level)
    elements["state"].textContent = level_state[engine.state]
    elements["energy"].value = engine.energy
    pulse = engine.architect.pulse
    if engine.protected:
        ability = "Crossing guard"
    elif engine.architect.recovering:
        ability = "Reopening · Release ↑ and lower your voice"
    elif pulse.remaining:
        ability = f"Pulse ×2 · {pulse.remaining:.1f}s"
    else:
        ability = "Basic controls" if level == 1 else "Pulse ready" if pulse.energy >= 40 else "Recharging"
    elements["ability"].textContent = f"{ability} · {engine.energy:.0f}/100"
    if level < 4:
        message = "Forecasts start in Level 4. Bluff detection starts in Level 5."
    elif engine.prediction is None:
        message = "Waiting for the next pipe to enter forecast range…"
    else:
        message = f"Predicted crossing height: {engine.prediction:.0f} px · Training samples: {engine.model.samples_seen}"
        if engine.bluff_feedback:
            message += " · " + engine.bluff_feedback
    elements["forecast"].textContent = message
