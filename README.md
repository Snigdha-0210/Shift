<div align="center">

  <img src="assets/banner.jpg" alt="SHIFT Game Banner" width="100%" style="border-radius: 12px; box-shadow: 0 8px 32px rgba(0, 220, 255, 0.2);" />

  <br/><br/>

  <h1>⚡ S H I F T</h1>
  <p><strong>DODGE. SHIFT. SURVIVE.</strong></p>
  <p><em>An adrenaline-fueled, cyberpunk-themed 3-lane reflex obstacle dodger built with Python, Pygame, and WebAssembly.</em></p>

  <p>
    <a href="https://snigdha-0210.github.io/Shift/"><img src="https://img.shields.io/badge/🎮_Play_Live-WebAssembly-00E5FF?style=for-the-badge&logo=webassembly&logoColor=white" alt="Play Live in Browser"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
    <a href="https://www.pygame.org/"><img src="https://img.shields.io/badge/Pygame-2.6.x-00D4B2?style=for-the-badge&logo=gamemaker&logoColor=white" alt="Pygame 2.6.x"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-00E5FF?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="MIT License"></a>
    <img src="https://img.shields.io/badge/Platform-Web%20%7C%20Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge" alt="Cross Platform">
    <img src="https://img.shields.io/badge/FPS-60%20(Delta--Time)-FF0055?style=for-the-badge" alt="60 FPS">
  </p>

  <p>
    <a href="https://snigdha-0210.github.io/Shift/"><strong>🚀 Play Online Now</strong></a> •
    <a href="#-key-features">Features</a> •
    <a href="#-game-architecture">Architecture</a> •
    <a href="#-controls--mechanics">Controls</a> •
    <a href="#-difficulty-progression">Difficulty Curve</a> •
    <a href="#-installation--quickstart">Installation</a> •
    <a href="PROGRESS.md">Dev Progress Log</a>
  </p>

</div>

---

## 🌌 Overview

**SHIFT** places you in the cockpit of a glowing high-speed cyber-vehicle traversing an infinite neon speedway. Obstacles cascade in accelerating frequencies across three lanes. Your objective is pure reflex survival: switch lanes, avoid barricades, navigate multi-lane blockades, and climb the high-score leaderboard.

Designed with **delta-time physics**, **procedural sine-wave audio synthesis**, **particle physics**, and **fair spawning algorithms**, SHIFT delivers fluid, frame-rate-independent arcade action both natively on desktop and directly inside any web browser via **WebAssembly**.

<div align="center">
  <img src="assets/icon.jpg" alt="SHIFT Icon" width="180" style="border-radius: 20px; margin: 10px;" />
</div>

---

## ✨ Key Features

- 🌐 **WebAssembly Instant Play**: Play straight in your web browser with zero installation at [https://snigdha-0210.github.io/Shift/](https://snigdha-0210.github.io/Shift/).
- 🏎️ **Continuous Smooth Interpolation**: Smooth lane transitioning physics ($1200\text{ px/s}$) with responsive target dampening.
- ⚙️ **Interactive Settings & Audio Toggle**: Full in-game Settings menu allowing you to toggle synthesized sound effects, inspect controls, and navigate menus.
- 🧠 **Fair Spawning Heuristics & Pattern Memory**: Guarantees at least one open escape lane at all times while preventing repetitive patterns.
- 📈 **Dynamic Difficulty Tiers (Levels 1–10)**: Real-time velocity acceleration from $300\text{ px/s}$ to $750\text{ px/s}$ with spawn intervals tightening down to $0.45\text{s}$.
- 💥 **Visual Impact Feedback**: Directional camera screen shake, red impact flash overlay, and gravity-driven particle explosion bursts.
- 🌌 **Atmospheric Starfield & Speed Lines**: 80 depth-scrolling background stars and 20 neon speed lines for high-velocity immersion.
- 💾 **Disk High-Score Persistence**: Automatic session and disk high-score tracking via `highscore.txt`.
- 🔌 **Hardware Controller Ready**: Abstracted input queue architecture with hooks for Arduino, ESP32, and Bluetooth hardware inputs.

---

## 📐 Game Architecture

SHIFT is built on a modular finite state machine:

### 1. State Machine Flow
```mermaid
stateDiagram-v2
    [*] --> MENU
    MENU --> SETTINGS : S Pressed
    SETTINGS --> CONTROLS : CONTROLS Selected
    CONTROLS --> SETTINGS : ESC Pressed
    SETTINGS --> MENU : ESC or BACK Selected
    MENU --> COUNTDOWN : SPACE Pressed
    COUNTDOWN --> PLAYING : 3-Second Timer Finishes
    PLAYING --> GAME_OVER : Player-Obstacle Collision
    PLAYING --> MENU : ESC Pressed
    GAME_OVER --> COUNTDOWN : SPACE Pressed (Restart)
    GAME_OVER --> MENU : ESC Pressed
```

### 2. Frame Execution Pipeline
```mermaid
sequenceDiagram
    autonumber
    actor Player
    participant EventLoop as Input System & Hardware Buffer
    participant PhysicsEngine as Movement & Delta-Time
    participant Spawner as Fair Pattern Spawner
    participant CollisionSystem as Collision & Scorer
    participant Renderer as Offscreen World & Shake Pipeline

    Player->>EventLoop: Keyboard / Hardware Input
    EventLoop->>PhysicsEngine: Submit & Process Input Queue
    PhysicsEngine->>PhysicsEngine: Lerp Player X (1200 px/s * dt)
    PhysicsEngine->>PhysicsEngine: Update Starfield, Speed Lines & Obstacles
    Spawner->>Spawner: Select Allowed Pattern (Level-Tiered)
    CollisionSystem->>CollisionSystem: Evaluate Player-Obstacle Hitboxes
    alt Collision Detected
        CollisionSystem->>Renderer: Trigger Crash Particles, Shake & Flash
        CollisionSystem->>EventLoop: Transition to GAME_OVER
    else Obstacle Passed
        CollisionSystem->>CollisionSystem: Increment Score, Level Up Check & Disk Save
    end
    Renderer->>Renderer: Render World Surface -> Apply Screen Shake Offset -> Draw Flash
    Renderer-->>Player: Flip Frame Buffer (60 FPS / WebAssembly)
```

---

## 🎮 Controls & Keybindings

| Keybinding | Action | Context |
| :--- | :--- | :--- |
| <kbd>A</kbd> or <kbd>←</kbd> | **Shift Left** | In-Game (`PLAYING`) |
| <kbd>D</kbd> or <kbd>→</kbd> | **Shift Right** | In-Game (`PLAYING`) |
| <kbd>SPACE</kbd> | **Start Game / Quick Restart** | Menu / Game Over |
| <kbd>S</kbd> | **Open Settings** | Main Menu (`MENU`) |
| <kbd>↑</kbd> / <kbd>↓</kbd> or <kbd>W</kbd> / <kbd>S</kbd> | **Navigate Settings** | Settings Menu (`SETTINGS`) |
| <kbd>ENTER</kbd> | **Toggle Sound / Select Option** | Settings Menu (`SETTINGS`) |
| <kbd>ESC</kbd> | **Back / Quit to Menu** | Global |

---

## 📊 Difficulty Scaling

The difficulty system dynamically scales obstacle speeds and spawn frequencies based on current score:

| Level | Score Range | Obstacle Speed | Spawn Interval | Hazard Distribution |
| :---: | :---: | :---: | :---: | :--- |
| **1** | 0 – 4 | $300\text{ px/s}$ | $1.25\text{ s}$ | Single Hazards (Tutorial) |
| **2** | 5 – 9 | $350\text{ px/s}$ | $1.17\text{ s}$ | Single Hazards (Accelerating) |
| **3** | 10 – 14 | $400\text{ px/s}$ | $1.09\text{ s}$ | Dual Barricades Introduced |
| **4** | 15 – 19 | $450\text{ px/s}$ | $1.01\text{ s}$ | Dual Barricades & Rapid Lane Traps |
| **5** | 20 – 24 | $500\text{ px/s}$ | $0.93\text{ s}$ | Advanced Mixed Patterns |
| **6+** | 25+ | Up to $750\text{ px/s}$ | Down to $0.45\text{ s}$ | Maximum Reflex Intensity |

---

## 🚀 Installation & Quickstart (Local Play)

### Prerequisites
- **Python 3.10** or higher
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/Snigdha-0210/Shift.git
cd Shift
```

### 2. Set Up Virtual Environment

#### On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### On macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Game
```bash
python main.py
```

---

## 🌐 Web Deployment (GitHub Pages)

The repository is equipped with an automated GitHub Actions CI/CD workflow (`.github/workflows/deploy.yml`) that compiles the Python source into WebAssembly via Pygbag on every push.

To enable GitHub Pages hosting:
1. Open your repository on GitHub: **`https://github.com/Snigdha-0210/Shift/settings/pages`**
2. Under **Build and deployment** $\rightarrow$ **Source**, select **GitHub Actions**.
3. Your game is live at **`https://snigdha-0210.github.io/Shift/`**!

---

## 📁 Project Structure

```text
SHIFT/
├── .github/
│   └── workflows/
│       └── deploy.yml      # Automated GitHub Pages WebAssembly CI/CD
├── assets/
│   ├── banner.jpg          # Repository header & promotional banner
│   └── icon.jpg            # Cyberpunk game badge & application icon
├── .gitignore              # Git ignore rules for Python, virtual environments & IDEs
├── CONTRIBUTING.md         # Open-source contribution guidelines
├── LICENSE                 # MIT Open-Source License
├── PROGRESS.md             # Developer progress log & roadmap notes
├── README.md               # Repository documentation
├── requirements.txt        # Pinned Python package dependencies
├── sync.ps1                # One-click PowerShell Git push automation
├── highscore.txt           # Local high score persistence file
└── main.py                 # Core game loop, rendering engine & state logic
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ and Pygame by <a href="https://github.com/Snigdha-0210">Snigdha</a>. Star ⭐ the repository if you enjoy playing!</sub>
</div>
