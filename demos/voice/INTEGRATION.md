# 成员 B 接口交接

从项目根目录启动 `python -m http.server 8000 --bind 127.0.0.1`，访问 http://localhost:8000/demos/voice/ 。页面会联网加载 Pyodide 0.27.7。核心模块使用 Python 标准库。四个 voice 文件需要映射到正式页面的 Pyodide 虚拟文件系统，参考同目录 index.html 的加载代码。PyScript 项目可以通过其 files 配置映射相同目录结构。

## A 在游戏循环中的调用

下面的变量由引擎提供。每局创建一个 Architect。麦克风对象跨关复用，用户点击开启时 await mic.start()，失败时保留键盘操作，离开游戏时 await mic.stop()。方向键应阻止页面滚动，X 只在首次 keydown 时记一次，在下一帧消费。

```python
from voice.controller import Microphone
from voice.versus import Architect, gap_bounds, winner

mic = Microphone()
architect = Architect()

# 每个运行中的游戏帧调用一次；dt 单位为秒，画布 Y 向下。
axis = int(down_held) - int(up_held)
volume = mic.read()
scale = architect.update(dt, volume, axis, x_pressed, powers_enabled)
# base_gap 为生成时的原始缺口高度。以普通速度持续收窄约 1.25 秒可从全开变为闭合。
# 绘制与碰撞共用上下边缘，每帧以原始高度计算。
pipe.gap_top, pipe.gap_bottom = gap_bounds(pipe.base_y, pipe.base_gap, scale)
# A 完成本帧碰撞与计分后调用。None 表示继续，Pilot Win 表示本关通关。
result = winner(collided, passed_this_level, target_for_this_level)
```

第 1 关关闭技能，第 2、5 关开启，第 3、4 关由关卡配置控制。双路线关对每个缺口分别使用自己的固定中心和原始高度。声音越响缺口越窄，持续满格可完全闭合。↑ 收窄，↓ 恢复，脉冲额外收窄并使开合速度翻倍。Space 归 Pilot。重试和下一关各创建新的 Architect，暂停期间不调用 update。

## C 的 HUD

从同一个 Architect 对象读取 pulse.energy（0–100）和 pulse.remaining（秒）。使用 A 已读出的 volume（0–1）和 result。技能消耗 40 点，持续 0.8 秒，每秒恢复 8 点。声音大于等于 0.78 时触发，回落到 0.45 以下或等于该值后可再次触发。初始阈值可在现场测试后调整。
