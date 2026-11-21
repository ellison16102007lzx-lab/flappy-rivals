# Flappy Rivals — Team Demo

在 JetBrains Air 打开本目录，使用本机 Python 3.10+ 运行 `run_demo.py`。也可在项目终端运行 `python run_demo.py`。启动器打开一个本机浏览器页面，退出启动器即可停止服务。无需 pip 安装。浏览器需要联网从 jsDelivr 加载 Pyodide 0.27.7，项目的 Python 源码由本地服务提供。

## 双人操作

- Pilot 用 Space 或点击画面拍翅。Architect 用 ↑ 收窄、↓ 张开，X 发动脉冲。点击开启麦克风，可用声音控制缺口；滑块调节灵敏度。声音控制切换为 Pilot 后，短促发声控制拍翅，Architect 使用键盘。
- 缺口在半宽或以下每秒耗能 60 点。脉冲消耗 40 点，双速持续 0.8 秒。能量耗尽后缺口自动张开。鸟头碰到实体当帧判 Architect Win；从空隙进入后缺口只能张开，鸟尾越过出口后可恢复收窄。
- 按 Space 开始、重试或进入下一关。通关第五关后 Space 开始新一轮。现场展示可用下拉框或数字 1–5 直接开始指定关卡。
- 第一关展示基础对抗；第二关打开声音技能；第三关有两条路线；第四关预测到达管道入口时的高度；第五关评估实际高度与先前预测的误差。误差至少 40 像素时显示 Bluff。成功观测后才训练模型。模型在当前页面会话中积累样本。

## 团队模块

A 的 `game/` 控制物理、碰撞、计分和五关。B 的 `voice/` 控制麦克风、能量、技能和穿越保护。C 的 `ml/` 和 `style.css` 提供在线学习、Bluff 判定和界面主题。正式入口为根目录 `index.html`，`boot.js` 加载浏览器 Python 并以固定 60 Hz 更新，`main.py` 连接输入、游戏和 HUD。原型位于 `ui-preview/`，独立声音测试位于 `demos/voice/`。

## 验证

从项目根目录运行 `python -B -m unittest discover -s tests -v`。集成测试覆盖撞柱、入口保护、五关切换和预测在真实过管时刻的评分。
