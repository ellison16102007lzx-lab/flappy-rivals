# Architect integration guide

From the project root, start `python -m http.server 8000 --bind 127.0.0.1` and visit http://localhost:8000/demos/voice/. The demo loads Pyodide 0.27.7 online. Its four Python voice files must be available in the browser runtime under the same package paths as on disk. See the loader in this folder's index.html. PyScript projects can also map these paths through their files configuration.

## Game loop

Create one Architect per round. Keep one Microphone across levels. On a user click, await mic.start() and allow keyboard play if access fails. Call await mic.stop() when leaving the game. Prevent arrow keys from scrolling the page. Queue X on the initial key press and consume it on the next simulation tick.

```python
from voice.controller import Microphone
from voice.versus import Architect, guarded_gap, winner

mic = Microphone()
architect = Architect()

# Once per active tick. Time is in seconds, and Y increases downward.
axis = int(down_held) - int(up_held)
volume = mic.read(sensitivity)  # Range 0.25–3.0, default 1.0.
scale = architect.update(dt, volume, axis, x_pressed, powers_enabled)

# For each pipe, use the original gap height saved at spawn.
# Test contact with the existing wall before the guard can widen the gap.
pipe.gap_size, protected = guarded_gap(
    original_gap_size, scale, pipe.gap_size,
    pipe.x - (bird.x + bird.width), pipe.x + pipe.width - bird.x,
    pipe.speed * 60, bird.height,
)
# Use the resulting gap for drawing and collision detection.
result = winner(collided, passed_this_level, target_for_this_level)
```

A fully open gap takes about 1.25 seconds to close at normal speed. Loud sounds narrow the gap. Arrow keys apply the same rules as voice. A pulse narrows the target further and doubles the movement speed. Level 1 uses basic controls. Each later level enables powers through its configuration. Each route in a split pipe retains its own center. Skip updates while paused and reset the Architect on a retry or level change.

## HUD and energy

Read pulse.energy (0–100), pulse.remaining (seconds), the current tick's volume (0–1), and the round result. A pulse costs 40 energy, lasts 0.8 seconds, and triggers at a volume of 0.78 or above. The sound trigger rearms at 0.45 or below. Energy normally regenerates at 8 points per second.

At half width or less, the gap drains 60 energy per second. An empty bar forces the gap open. Recovery ends when the gap is fully open, energy is at least 20, and the narrowing input is at most 0.45. Show a reopening message during recovery. During a pulse, show “Pulse ×2” and the remaining time. Use the same adjusted volume for the meter and the game logic.

## Crossing guard

Check each pipe separately. Protection starts when the bird reaches the entrance (distance_to_entry <= 0) and ends when its tail clears the exit (distance_to_exit < 0). During that interval the gap can only widen. The guard allows clearance equal to the bird's height plus 12 pixels, capped at the original gap height. The bird must still enter through the opening. Use the returned protected flag to display “Crossing guard.”
