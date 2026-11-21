"use strict";

// Each entry is a scripted snapshot. The preview has no simulation loop.
const samples = [
  { score: 0, energy: 0.28, y: 225, forecast: 203, deviation: null, pilot: "Lining up for the first gate", architect: "Opening gate set" },
  { score: 3, energy: 0.54, y: 186, forecast: 170, deviation: 17, pilot: "Holding altitude", architect: "High gate placed" },
  { score: 7, energy: 0.84, y: 240, forecast: 190, deviation: 51, pilot: "Making a late climb", architect: "Offset gates placed" },
  { score: 12, energy: 0.39, y: 161, forecast: 178, deviation: 14, pilot: "Settling into the gap", architect: "Narrow gate placed" },
  { score: 18, energy: 0.68, y: 205, forecast: 188, deviation: 22, pilot: "Approaching the finish", architect: "Final gate placed" },
];

const byId = (id) => document.getElementById(id);
const setText = (id, value) => { byId(id).textContent = value; };
const screens = ["menu", "game", "result"];
const canvas = byId("arena");
const context = canvas.getContext("2d");
const levelItems = samples.map((_, index) => {
  const item = document.createElement("li");
  const label = document.createElement("strong");
  label.className = "preview-level-name";
  label.textContent = `Level ${index + 1}`;
  const status = document.createElement("span");
  status.className = "preview-note";
  item.append(label, status);
  byId("progression").append(item);
  return { item, status };
});

const players = ["bird", "saboteur"];
const controlLabels = { voice: "Voice", keyboard: "Keyboard" };

// Engine-facing values are lowercase and both assignments change together.
let control_config = { bird: "keyboard", saboteur: "voice" };
let step = 0;
let previousBluff = false;

function showScreen(active) {
  for (const screen of screens) {
    byId(screen).hidden = screen !== active;
  }
  byId(`${active}-title`).focus();
}

function drawArena(sample) {
  if (!context) return;

  // Draw on a four-pixel grid while keeping the original Canvas coordinates.
  const { width, height } = canvas;
  const theme = getComputedStyle(canvas);
  const color = (token) => theme.getPropertyValue(`--fr-${token}`).trim();
  const block = (fill, x, y, w, h) => {
    context.fillStyle = fill;
    context.fillRect(x, y, w, h);
  };
  const snap = (value) => Math.round(value / 4) * 4;
  const ground = height - 56;
  const outline = color("border");
  const grass = color("pipe");

  block(color("sky"), 0, 0, width, height);

  for (const [x, y] of [[44, 72], [204, 40], [466, 92], [632, 52]]) {
    block(color("beige"), x, y + 16, 64, 12);
    block(color("panel"), x, y + 12, 60, 12);
    block(color("panel"), x + 12, y + 4, 36, 12);
    block(color("panel"), x + 20, y, 16, 8);
  }

  // A low, stepped landscape keeps the flight path easy to read.
  for (let x = 0; x < width; x += 48) {
    const rise = [12, 24, 36, 28, 20][Math.floor(x / 48) % 5];
    block(color("pipe"), x, ground - rise, 48, rise);
  }

  function pipe(x, top, bottom, rim) {
    block(outline, x, top, 48, bottom - top);
    block(color("pipe"), x + 4, top, 40, bottom - top);
    block(color("green"), x + 8, top, 8, bottom - top);
    block(color("architect"), x + 36, top, 8, bottom - top);
    block(outline, x - 4, rim, 56, 20);
    block(color("pipe"), x, rim + 4, 48, 12);
    block(color("green"), x + 4, rim + 4, 40, 4);
    block(color("architect"), x + 40, rim + 8, 8, 8);
  }

  for (const [x, gapY] of [[360, snap(sample.forecast - 58)], [576, snap(125 + step * 12)]]) {
    const gapBottom = snap(gapY + 132 - step * 6);
    pipe(x, 0, gapY, gapY - 20);
    pipe(x, gapBottom, ground, gapBottom);
  }

  block(outline, 0, ground, width, 4);
  block(color("green"), 0, ground + 4, width, 8);
  block(grass, 0, ground + 12, width, 12);
  block(color("beige"), 0, ground + 24, width, 32);
  for (let x = 0; x < width; x += 24) {
    block(color("architect"), x, ground + 16, 12, 8);
    block(color("terracotta"), x + 8, ground + 36, 8, 4);
  }

  const pilotX = 156;
  const pilotY = snap(sample.y);
  const forecastX = 316;
  const forecastY = snap(sample.forecast);
  const prediction = color("prediction");
  for (let x = pilotX + 28; x < forecastX - 12; x += 16) {
    const fraction = (x - pilotX) / (forecastX - pilotX);
    const y = snap(pilotY + (forecastY - pilotY) * fraction);
    block(prediction, x, y, 8, 4);
  }
  block(prediction, forecastX - 12, forecastY - 12, 24, 24);
  block(color("panel"), forecastX - 8, forecastY - 8, 16, 16);
  block(prediction, forecastX - 2, forecastY - 2, 4, 4);

  // Original Pilot sprite, with a terracotta body and a square wing.
  block(color("border"), pilotX - 16, pilotY - 12, 28, 24);
  block(color("border"), pilotX - 20, pilotY - 8, 40, 16);
  block(color("terracotta"), pilotX - 16, pilotY - 4, 32, 12);
  block(color("beige"), pilotX - 12, pilotY - 8, 24, 8);
  block(color("panel"), pilotX - 16, pilotY, 12, 8);
  block(color("panel"), pilotX + 4, pilotY - 8, 8, 8);
  block(color("border"), pilotX + 8, pilotY - 8, 4, 4);
  block(color("terracotta"), pilotX + 16, pilotY, 8, 4);

  context.font = "bold 16px monospace";
  block(color("panel"), 16, 12, 124, 28);
  context.fillStyle = color("text");
  context.fillText(`SECTOR 0${step + 1}`, 24, 32);
}

function renderGame(announceLevel = false) {
  const sample = samples[step];
  const level = step + 1;
  setText("score", sample.score);
  setText("level", `Level ${level} of ${samples.length}`);
  setText("pilot-status", sample.pilot);
  setText("architect-status", sample.architect);
  byId("energy").value = sample.energy;
  setText("energy-value", `${Math.round(sample.energy * 100)}% energy`);
  setText("prediction", `Vertical position: ${sample.forecast} px · 10 ticks ahead`);

  const isBluff = sample.deviation !== null && sample.deviation >= 40;
  const deviation = sample.deviation === null ? "Awaiting a matched observation" : `Deviation: ${sample.deviation} px`;
  const bluffLabel = sample.deviation === null ? "Pending" : isBluff ? "Bluff flagged" : "No bluff";
  setText("bluff", `${bluffLabel} · ${deviation}`);
  if (isBluff !== previousBluff) {
    setText("bluff-status", isBluff ? "Mock bluff alert" : "Mock bluff alert cleared");
  }
  previousBluff = isBluff;

  levelItems.forEach(({ item, status }, index) => {
    item.className = "fr-level";
    item.removeAttribute("aria-current");
    if (index === step) {
      item.setAttribute("aria-current", "step");
      status.textContent = "Current";
    } else {
      item.classList.add(index < step ? "fr-level--complete" : "fr-level--locked");
      status.textContent = index < step ? "Complete" : "Locked";
    }
  });

  byId("previous").disabled = step === 0;
  setText("advance", level === samples.length ? "Finish Run" : "Next Level");
  if (announceLevel) {
    setText("round-status", `Level ${level} of ${samples.length}. Score ${sample.score}.`);
  }
  drawArena(sample);
}

function selectControl(player, method) {
  const otherPlayer = player === "bird" ? "saboteur" : "bird";
  const otherMethod = method === "voice" ? "keyboard" : "voice";
  control_config = { ...control_config, [player]: method, [otherPlayer]: otherMethod };

  for (const name of players) {
    for (const choice of Object.keys(controlLabels)) {
      byId(`${name}-${choice}`).setAttribute("aria-pressed", String(choice === control_config[name]));
    }
  }
  setText("control-status", `Bird uses ${controlLabels[control_config.bird]}. Saboteur uses ${controlLabels[control_config.saboteur]}.`);
}

function startRun() {
  for (const player of players) {
    setText(`${player}-control`, `Control · ${controlLabels[control_config[player]]}`);
  }
  step = 0;
  previousBluff = false;
  setText("bluff-status", "");
  setText("round-status", "");
  showScreen("game");
  renderGame();
}

function showResult(pilotWon) {
  const result = byId("result");
  result.classList.toggle("fr-result--winner", pilotWon);
  result.classList.toggle("fr-result--game-over", !pilotWon);
  setText("result-title", pilotWon ? "Winner" : "Game Over");
  setText("winner", pilotWon ? "Pilot wins the mock round" : "Architect wins the mock round");
  setText("final-score", samples[step].score);
  setText("final-level", `Level ${step + 1} of ${samples.length} · Simulated result`);
  showScreen("result");
}

for (const player of players) {
  for (const method of Object.keys(controlLabels)) {
    byId(`${player}-${method}`).addEventListener("click", () => selectControl(player, method));
  }
}
byId("start").addEventListener("click", startRun);
byId("replay").addEventListener("click", startRun);
byId("back").addEventListener("click", () => showScreen("menu"));
byId("end").addEventListener("click", () => showResult(false));
byId("previous").addEventListener("click", () => {
  if (step === 0) return;
  step -= 1;
  const moveFocus = step === 0 && document.activeElement === byId("previous");
  renderGame(true);
  if (moveFocus) byId("advance").focus();
});
byId("advance").addEventListener("click", () => {
  if (step === samples.length - 1) {
    showResult(true);
    return;
  }
  step += 1;
  renderGame(true);
});
