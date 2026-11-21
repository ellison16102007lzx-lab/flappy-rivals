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
level_state = {"start": "按 Space 开始", "playing": "飞行中",
               "gameover": "Architect Win · 按 Space 重试",
               "levelcomplete": "Pilot Win · 按 Space 继续"}


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
        ability = "穿越保护"
    elif engine.architect.recovering:
        ability = "强制张开 · 松开收窄键并降低音量"
    elif pulse.remaining:
        ability = f"脉冲 ×2 · {pulse.remaining:.1f}s"
    else:
        ability = "基础控制" if level == 1 else "脉冲就绪" if pulse.energy >= 40 else "能量恢复中"
    elements["ability"].textContent = f"{ability} · {engine.energy:.0f}/100"
    if level < 4:
        message = "第 4 关开启预测，第 5 关开启 Bluff。"
    elif engine.prediction is None:
        message = "等待下一根管道进入预测范围…"
    else:
        message = f"预计过管 Y = {engine.prediction:.0f} px · 已学习 {engine.model.samples_seen} 次"
        if engine.bluff_feedback:
            message += " · " + engine.bluff_feedback
    elements["forecast"].textContent = message
