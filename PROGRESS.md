# 📋 SHIFT — Project Status & Developer Log

> **Last Updated**: September 7, 2026  
> **Repository**: [https://github.com/Snigdha-0210/Shift](https://github.com/Snigdha-0210/Shift)  
> **Current Engine**: Python 3.12+ & Pygame 2.6.x  
> **Architecture Version**: 2.0 (Buffered Input & Settings System)

---

## 📌 Executive Summary

**SHIFT** is a fast-paced cyberpunk 3-lane reflex obstacle dodger. The codebase has evolved into a modular, state-driven arcade game with synthesized procedural audio, particle physics, camera shake, visual impact feedback, persistent high-score tracking, and an interactive Settings menu.

---

## 🎮 Current Feature State

### 1. Game State Machine (`game_state`)
- `MENU`: Title screen with animated starfield, best score display, and navigation (`SPACE` to start, `S` for settings, `ESC` to quit).
- `SETTINGS`: Interactive menu to toggle audio (`ON`/`OFF`), view keybindings, or return to the main menu.
- `CONTROLS`: Visual keyboard mapping card.
- `COUNTDOWN`: 3-second animated transition before the run begins.
- `PLAYING`: Core reflex gameplay with continuous lane interpolation, speed lines, animated obstacles, HUD scoring, and difficulty scaling.
- `GAME_OVER`: Crash state with visual screen flash, explosion particles, camera shake, and score summary (`SPACE` to restart, `ESC` for menu).

### 2. Physics & Player Mechanics
- **Lanes**: 3 defined lanes centered at $X = [300, 500, 700]$ on a $1000 \times 700$ screen canvas.
- **Interpolation Speed**: $1200\text{ px/s}$ continuous lerp toward `player_target_x`.
- **Hitbox**: $70 \times 100\text{ px}$ player polygon and $85 \times 100\text{ px}$ barrier hitboxes.

### 3. Obstacle & Fairness Engine
- **Procedural Spawner**: Guarantees at least 1 open lane at all times.
- **Pattern Memory**: Avoids repeating identical patterns consecutively.
- **6+ Difficulty Tiers**:
  - Speed scales from $300\text{ px/s}$ up to $750\text{ px/s}$ ($+50\text{ px/s}$ per level).
  - Spawn interval tightens from $1.25\text{s}$ down to $0.45\text{s}$.
  - Level 1-2: Single hazards. Level 3+: Dual barricades.

### 4. Visual Effects & Polish
- 🌌 **Starfield Engine**: 80 independent depth-scaled stars.
- ⚡ **Speed Lines**: 20 animated transit stream lines.
- 💥 **Particle System**: Gravity-assisted explosion bursts on crash and level-up.
- 📳 **Camera Shake & Impact Flash**: Rendered via an off-screen world buffer surface.
- 🟢 **Floating Floating Popups**: `+1` text floating on score increase.
- 🏆 **Level-Up Notifications**: Banner announcement and chime when advancing tiers.

### 5. Persistence & Input Abstraction
- **High-Score**: Automatically saved to / loaded from `highscore.txt`.
- **Input System**: Buffered command queue (`submit_input(direction)` $\rightarrow$ `process_input_commands()`).
- **Hardware Ready**: `read_hardware_input()` stub ready for Arduino, ESP32, or Bluetooth controllers.

---

## 📁 Key File Map

| File | Role |
| :--- | :--- |
| `main.py` | Complete game loop, state handlers, rendering engine, and math helpers. |
| `highscore.txt` | Local high-score storage file. |
| `assets/banner.jpg` | High-resolution cyber banner for README and promotional use. |
| `assets/icon.jpg` | Application icon and badge. |
| `requirements.txt` | Pinned dependencies (`pygame>=2.6.0`). |
| `README.md` | Full repository presentation with architecture diagrams. |
| `sync.ps1` | One-click PowerShell Git push automation script. |
| `PROGRESS.md` | *This file* — dev journal, architecture summary, and continuation guide. |

---

## 🚀 Where We Left Off (Ready for Next Session)

### Priority Features to Implement Next:
1. **Power-Up System**:
   - 🛡️ *Shield Pickup* (Absorb 1 collision).
   - ⏱️ *Slow-Mo / EMP* (Temporarily decelerate obstacles).
   - ⚡ *Hyper-Drive Boost* (Invulnerability and auto-lane dodge for 3 seconds).
2. **Custom Vehicle Skins / Cyber Garage**:
   - Unlockable neon vehicle hulls (Cyan, Crimson, Emerald, Gold) stored in settings.
3. **Sound Effects Polish**:
   - Background synthwave bassline loops or chiptune track.
4. **Hardware Controller Integration**:
   - Connect physical buttons or tilt accelerometer via Serial / PySerial in `read_hardware_input()`.

---

## 🌐 Deployment Plan

### Option 1: Web Deployment via WebAssembly (Pygbag) — *Recommended for Web*
Run Python Pygame directly in any web browser without installation:
1. Install `pygbag`: `pip install pygbag`
2. Test web build locally: `pygbag .` (runs a local web server at `http://localhost:8000`)
3. Deploy to **GitHub Pages** or **Itch.io** automatically via GitHub Actions.

### Option 2: Standalone Windows Desktop Executable (`.exe`)
Package the game as a single portable `.exe` for Windows users:
1. Install PyInstaller: `pip install pyinstaller`
2. Build executable: `pyinstaller --onefile --noconsole --name "SHIFT" main.py`
3. The executable will be generated in `dist/SHIFT.exe`.

---

## 🛠️ Quick Commands

```powershell
# Run the game
python main.py

# Push future changes to GitHub
.\sync.ps1 "Your commit message"
```
