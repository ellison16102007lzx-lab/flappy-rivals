# Flappy Rivals visual design

Link `style.css` from the application HTML and place the interface inside `.fr-shell`. Use `.fr-screen` for each top-level view. Set the HTML `hidden` attribute on inactive views and remove it when the game switches views. Use semantic headings, real buttons, and normal DOM elements around the canvas so status and controls remain accessible.

## Palette and typography

| Token | Color | Use |
| --- | --- | --- |
| `--fr-bg` | `#0B1020` | Page and arena background |
| `--fr-pilot` | `#5DE8FF` | Pilot, microphone energy, primary menu action |
| `--fr-architect` | `#FFC66D` | Architect and current level |
| `--fr-prediction` | `#C9AEFF` | Predicted position and trajectory |
| `--fr-bluff` | `#FF88B8` | Bluff alert and game-over accent |

System monospace fonts give the interface an arcade style without a font download. Use `.fr-title` for screen headings, `.fr-label` for short labels, and `.fr-value` for counters and telemetry. Headings, square controls, offset panel shadows, and dark surfaces establish the visual hierarchy. Pair color with explicit labels and status text.

## Screens and components

| Area | Class composition and behavior |
| --- | --- |
| Main menu | Use `.fr-screen.fr-menu` with a title, brief game instructions, and `.fr-actions` for the start control. Use `.fr-button.fr-button--primary` for Start. |
| Five-level progression | Use an ordered list with `.fr-progression` and five `.fr-level` items. Apply `aria-current="step"` to the active item, `.fr-level--complete` to completed items, and `.fr-level--locked` to locked items. Include state text such as “Current” or “Locked” in each applicable item. |
| Game HUD | Use `.fr-screen` with a `.fr-hud` above `.fr-play-layout`. Give each score or level indicator `.fr-stat` and place the number or “Level 2 of 5” in `.fr-value`. |
| Arena and player roles | Put the `.fr-canvas` canvas in `.fr-stage` as the first child of `.fr-play-layout`. Use `.fr-sidebar` as the second child. Within it, place both roles in `.fr-roles` using `.fr-role.fr-pilot` and `.fr-role.fr-architect`. Put the role name in an element with `.fr-accent`. |
| Microphone energy | Use a labeled native `<progress>` with `.fr-meter.fr-pilot`, `max="1"`, and a numeric value clamped to 0–1. Show “Microphone unavailable” separately when input is unavailable. Keep high-frequency meter changes out of live announcements. |
| AI prediction | Use `.fr-panel.fr-feedback.fr-prediction` for a labeled forecast readout. Show predicted vertical position and horizon when available. If plotting on canvas, use a dashed violet trajectory or an outlined target so the prediction is distinguishable by shape. |
| AI Bluff | Use `.fr-panel.fr-feedback.fr-bluff` with a text label and optional absolute deviation. Keep an empty `role="status"` element mounted and update its text when bluff state changes. Let the game control when feedback clears. |
| Game over and winner | Use `.fr-screen.fr-result` and add `.fr-result--game-over` or `.fr-result--winner`. Apply `.fr-accent` to the heading or outcome label. Show final score and level, name the winning role where relevant, and provide available replay and menu actions. Move focus to the heading or primary action on view changes. |

## Responsive layout

Above 48rem the arena and sidebar sit side by side. At 48rem and below they stack, with the HUD before the arena and role and telemetry panels after it. The progression uses five columns above 28rem and wraps into three columns at narrower widths. Actions wrap and buttons have a minimum height of 44px. Aim to keep keyboard access and visible focus available in every view.

Set the canvas HTML width and height to establish an intrinsic aspect ratio. The stylesheet scales its displayed width to the arena. The renderer owns coordinate scaling, backing resolution, and any pointer coordinate conversion. Read theme colors from `getComputedStyle(canvas).getPropertyValue("--fr-prediction").trim()` or the corresponding token when drawing, since canvas drawing commands require resolved colors. The game and PyScript code own DOM updates, role assignment, level transitions, microphone sampling, and ML result timing.
