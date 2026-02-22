# WaterSort# WaterSort+ (Puzzle Engine Edition)

A polished **Pygame puzzle game** inspired by water-sorting mechanics, extended with **custom puzzle-engine features** like **demo mode**, **locked tubes**, **hint system**, **par moves + stars**, and **local stats tracking**.

This project is built for fast playtesting and competition demos, with a clean UI, animated tubes/liquids, and metadata-driven levels. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1}

---

##  Game Description

In **WaterSort+**, your goal is to sort colored liquid layers into separate tubes so that each non-empty tube contains only **one color**.

You can only pour liquid when:
- the source tube is not empty
- the destination tube has space
- the top color of the destination matches the color being poured (or the destination is empty)

This version adds a **puzzle engine layer** on top of the classic mechanic:
- curated **demo levels**
- **locked tube** mechanics (unlock after a number of successful moves)
- **level metadata** (difficulty, tags, par moves)
- **hint** and **undo** systems
- **stars** and **best-score tracking** :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3}

---

##  Features

### Core Gameplay
- Color sorting puzzle mechanics (tube pour rules + win detection)
- Multiple handcrafted levels
- Level navigation (Prev / Next)
- Restart level
- Undo moves :contentReference[oaicite:4]{index=4}

### Puzzle Engine Features
- **Metadata-driven levels** (`id`, `name`, `difficulty`, `par_moves`, `tags`, `is_demo_level`, `unlock_after_moves`, `tubes`) :contentReference[oaicite:5]{index=5}
- **Demo Mode** for judge-friendly curated showcases (`is_demo_level`) :contentReference[oaicite:6]{index=6} :contentReference[oaicite:7]{index=7}
- **Locked Tube Mechanic** (tube unlocks after N successful pours) via `unlock_after_moves` :contentReference[oaicite:8]{index=8} :contentReference[oaicite:9]{index=9}
- **Hint System** (suggests a valid next move) :contentReference[oaicite:10]{index=10}
- **Par Moves + Star Rating** (with hint penalty support) :contentReference[oaicite:11]{index=11}

### UX / Presentation
- Polished Pygame UI with top/bottom control panels
- Animated liquid bubbles + surface effects
- Tube highlights (selection + hints)
- Win banner and level stats display
- Keyboard shortcuts + mouse controls :contentReference[oaicite:12]{index=12}

### Progress Tracking
- Local JSON stats file (`watersort_stats.json`) tracks:
  - wins
  - best moves
  - best time
  - stars
  - total restarts
  - total hints used :contentReference[oaicite:13]{index=13}

---

##  Unique Mechanics (What makes this version different)

### 1) Locked Tubes
Some levels include **locked tubes** that cannot be used until you complete a required number of successful pours.  
This adds planning pressure and improves puzzle originality. (`unlock_after_moves`) :contentReference[oaicite:14]{index=14} :contentReference[oaicite:15]{index=15}

### 2) Demo Mode (Competition/Judge Friendly)
A dedicated **Demo Mode** cycles through levels marked `is_demo_level=True`, making it easy to present a curated run without randomness or confusion. :contentReference[oaicite:16]{index=16} :contentReference[oaicite:17]{index=17}

### 3) Hint System
Use the in-game hint feature to get a suggested valid move. Hints can affect the star rating (hint penalty) to preserve challenge. :contentReference[oaicite:18]{index=18}

---

##  Controls

### Mouse
- **Click a tube** to select it
- **Click another tube** to pour (if the move is valid)
- Click UI buttons for:
  - Restart
  - Undo
  - Hint
  - Prev
  - Next
  - Demo Mode toggle :contentReference[oaicite:19]{index=19}

### Keyboard
- `R` → Restart level
- `U` → Undo
- `H` → Hint
- `B` → Previous level
- `N` → Next level
- `D` → Toggle Demo Mode
- `Esc` → Quit :contentReference[oaicite:20]{index=20}

---

## 🛠️ Installation & Run

### Requirements
This project currently depends on **Pygame** (`requirements.txt` contains `pygame`). :contentReference[oaicite:21]{index=21}

### Setup
```bash
pip install -r requirements.txt