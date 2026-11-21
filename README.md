# Flappy Rivals — Team Demo

Open this folder in JetBrains Air and run `run_demo.py` with Python 3.10 or later. From the project terminal, run `python run_demo.py`. The launcher opens the game in your browser. Stop the launcher to shut down the local server. The browser downloads Pyodide 0.27.7 from jsDelivr and loads the team's Python code from the local server. No pip packages are required.

## Controls

- Pilot: press Space or click the arena to flap. Architect: hold ↑ to narrow the gap, hold ↓ to open it, and press X for a pulse.
- Select **Enable microphone** to control the gap with your voice. Adjust the sensitivity slider to suit the room. Switch voice control to Pilot to flap with short sounds while the Architect uses the keyboard.
- At half width or less, the gap drains 60 energy per second. A pulse costs 40 energy and doubles the movement speed for 0.8 seconds. The gap reopens when energy runs out. Hitting a pipe ends the round immediately. During a clean crossing, the gap can only widen until the bird's tail clears the exit.
- Press Space to start, retry, or advance. After Level 5, press Space to start a new run. For a live demo, select a level from the menu or press 1–5.

## Levels

Level 1 introduces the duel. Level 2 unlocks voice powers. Level 3 offers two routes. In Level 4 the model predicts the bird's height at the pipe entrance. In Level 5 an error of at least 40 pixels triggers a Bluff. The model learns from observed crossings and retains its samples for the browser session.

## Team modules

Member A's `game/` handles physics, collisions, scoring, and levels. Member B's `voice/` handles the microphone, energy, powers, and crossing protection. Member C's `ml/` and `style.css` provide online learning, bluff detection, and the UI theme. The game starts at `index.html`. The browser adapter in `boot.js` loads Python and advances the simulation at 60 Hz. The `main.py` module connects controls, the game engine, and the HUD. The visual prototype is in `ui-preview/`, and the standalone voice demo is in `demos/voice/`.

## Tests

Run `python -B -m unittest discover -s tests -v` from the project root. Integration tests cover pipe contact, crossing protection, level progression, and forecast scoring at the crossing.
