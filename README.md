# Retro Remix: Old Tech, New Tricks 🎮

A Flappy Bird-style game themed around student life obstacles, built for the **First Year Hackathon**.

## 🎯 Game Features

- **Bird** affected by gravity — press **Space** to jump
- **Student-life obstacles** moving from right to left:
  - 📄 **Assignments** — stacks of papers
  - 📝 **Exams** — test papers with red X marks
  - 📅 **Deadlines** — calendars with warning signs
  - ☕ **Coffee Cups** — your lifeline (or obstacle!)
- **Collision detection** with obstacles and screen boundaries
- **Score** increases when you successfully pass an obstacle
- **Stress Meter** that gradually increases difficulty over time:
  - Obstacles move faster
  - Gaps between obstacles shrink
  - Obstacles spawn more frequently
- **Start screen** with instructions
- **Game Over screen** showing final score and stress level
- **Restart** by pressing **R**

## 📋 Requirements

- Python 3.6 or higher
- Pygame library (use `pygame-ce` for Python 3.14+)

## 🚀 Installation

1. **Install Python** (if not already installed):
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Install Pygame**:
   
   For Python 3.13 and earlier:
   ```bash
   pip install pygame
   ```
   
   For Python 3.14+ (use the community edition):
   ```bash
   pip install pygame-ce
   ```
   
   > **Note:** Both `pygame` and `pygame-ce` are imported the same way (`import pygame`), so the game code works with either.

## 🎮 How to Play

1. **Run the game**:
   ```bash
   python FirstYearHackathon.py
   ```

2. **Controls**:
   - **Space** — Jump (also starts the game from the start screen)
   - **R** — Restart after Game Over

3. **Objective**:
   - Dodge the student-life obstacles by flying through the gaps
   - Your score increases for each obstacle you pass
   - Watch your Stress Meter — the longer you survive, the harder it gets!

## 📁 Project Structure

```
FirstYearHackathon/
├── FirstYearHackathon.py   # Main game file (single file, all classes included)
├── README.md               # This file
└── src/                    # Source directory (for future expansion)
```

## 🏗️ Code Structure

The game is organized into well-documented classes:

- **`Bird`** — Player-controlled bird with gravity and jump mechanics
- **`Obstacle`** — Student-life themed obstacles with different visual styles
- **`StressMeter`** — Manages progressive difficulty increase
- **`Game`** — Main game loop, state management, and rendering

## 💡 Tips

- Time your jumps carefully — the gaps get smaller as stress increases!
- Don't fly too high or too low — screen boundaries will end your run
- The Stress Meter starts at 0% and increases over time, making the game progressively harder

## 🎨 Theme

This game is themed for the **"Retro Remix: Old Tech, New Tricks"** hackathon, replacing traditional pipes with relatable student-life obstacles that every student can recognize!
