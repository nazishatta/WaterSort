import sys
import os
import json
import pygame
from levels import LEVELS

pygame.init()

# ==================== CONFIG ====================
WIDTH, HEIGHT = 1080, 760
FPS = 60
TUBE_CAPACITY = 4
STATS_FILE = "watersort_stats.json"

BG_COLOR = (16, 22, 32)
PANEL_COLOR = (33, 43, 60)
CARD_COLOR = (28, 36, 52)
TEXT_COLOR = (240, 240, 240)
SUBTEXT_COLOR = (185, 198, 220)
SELECT_COLOR = (255, 215, 0)
EMPTY_SLOT = (60, 70, 92)
LOCK_COLOR = (120, 135, 160)
WIN_GREEN = (52, 170, 110)
WARN_AMBER = (255, 193, 74)

COLOR_MAP = {
    1: (239, 83, 80),    # red
    2: (66, 165, 245),   # blue
    3: (102, 187, 106),  # green
    4: (255, 202, 40),   # yellow
    5: (171, 71, 188),   # purple
    6: (255, 112, 67),   # orange
    7: (38, 198, 218),   # cyan
    8: (141, 110, 99),   # brown
}

FONT = pygame.font.SysFont("arial", 26)
SMALL_FONT = pygame.font.SysFont("arial", 18)
TITLE_FONT = pygame.font.SysFont("arial", 22, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 30, bold=True)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WaterSort+ (Puzzle Engine Edition)")
clock = pygame.time.Clock()


# ==================== STATS ====================
def load_stats():
    if not os.path.exists(STATS_FILE):
        return {"levels": {}, "total_restarts": 0, "total_hints": 0}
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "levels" not in data:
            data["levels"] = {}
        if "total_restarts" not in data:
            data["total_restarts"] = 0
        if "total_hints" not in data:
            data["total_hints"] = 0
        return data
    except Exception:
        return {"levels": {}, "total_restarts": 0, "total_hints": 0}


def save_stats(stats):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
    except Exception:
        pass


def ensure_level_stats(stats, level_id):
    if level_id not in stats["levels"]:
        stats["levels"][level_id] = {
            "wins": 0,
            "best_moves": None,
            "best_time_sec": None,
            "stars": 0,
        }


# ==================== HELPERS ====================
def clone_tubes(tubes):
    return [tube[:] for tube in tubes]


def clone_locks(locks):
    return dict(locks)


def is_tube_complete(tube):
    if len(tube) != TUBE_CAPACITY:
        return False
    return all(c == tube[0] for c in tube)


def check_win(tubes):
    for tube in tubes:
        if len(tube) == 0:
            continue
        if not is_tube_complete(tube):
            return False
    return True


def top_color_and_count(tube):
    if not tube:
        return None, 0
    color = tube[-1]
    count = 0
    for i in range(len(tube) - 1, -1, -1):
        if tube[i] == color:
            count += 1
        else:
            break
    return color, count


def can_pour(src, dst):
    if not src:
        return False
    if len(dst) >= TUBE_CAPACITY:
        return False
    src_color, _ = top_color_and_count(src)
    if not dst:
        return True
    return dst[-1] == src_color


def pour(src, dst):
    if not can_pour(src, dst):
        return 0
    _, src_count = top_color_and_count(src)
    space = TUBE_CAPACITY - len(dst)
    move_count = min(src_count, space)
    for _ in range(move_count):
        dst.append(src.pop())
    return move_count


def compute_stars(moves, par_moves, hints_used=False):
    # Simple judge-friendly star system
    penalty = 2 if hints_used else 0
    effective = moves + penalty
    if effective <= par_moves:
        return 3
    if effective <= par_moves + 3:
        return 2
    return 1


def star_string(n):
    return "★" * n + "☆" * (3 - n)


# ==================== LAYOUT ====================
def get_tube_rects(num_tubes):
    rects = []
    cols = min(6, num_tubes)

    tube_w = 82
    tube_h = 260
    gap_x = 34
    gap_y = 52

    total_w = cols * tube_w + (cols - 1) * gap_x
    start_x = (WIDTH - total_w) // 2
    start_y = 170

    for i in range(num_tubes):
        row = i // cols
        col = i % cols
        x = start_x + col * (tube_w + gap_x)
        y = start_y + row * (tube_h + gap_y)
        rects.append(pygame.Rect(x, y, tube_w, tube_h))
    return rects


def tube_at_pos(pos, tube_rects):
    for i, rect in enumerate(tube_rects):
        if rect.collidepoint(pos):
            return i
    return None


# ==================== DRAW UTILS ====================
def draw_text(text, x, y, font=FONT, color=TEXT_COLOR, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)


def draw_panel(rect, fill=PANEL_COLOR):
    pygame.draw.rect(screen, fill, rect, border_radius=16)
    gloss = pygame.Rect(rect.x + 6, rect.y + 5, rect.width - 12, 10)
    pygame.draw.rect(screen, (56, 70, 95), gloss, border_radius=6)


def draw_button(rect, label, mouse_pos, enabled=True, accent=(74, 133, 191)):
    hovered = rect.collidepoint(mouse_pos) and enabled

    if not enabled:
        fill = (88, 95, 110)
        edge = (150, 160, 180)
        txt = (180, 185, 195)
    else:
        base = accent
        hover = tuple(min(255, c + 18) for c in accent)
        fill = hover if hovered else base
        edge = (220, 230, 245)
        txt = (245, 248, 252)

    pygame.draw.rect(screen, fill, rect, border_radius=12)
    pygame.draw.rect(screen, edge, rect, 2, border_radius=12)
    hi = pygame.Rect(rect.x + 4, rect.y + 4, rect.width - 8, 6)
    pygame.draw.rect(screen, (220, 240, 255), hi, border_radius=4)

    draw_text(label, rect.centerx, rect.centery, font=SMALL_FONT, color=txt, center=True)


def draw_lock_badge(rect, remaining_moves):
    badge = pygame.Rect(rect.right - 26, rect.y + 8, 20, 20)
    pygame.draw.rect(screen, LOCK_COLOR, badge, border_radius=6)
    pygame.draw.rect(screen, (220, 230, 240), badge, 1, border_radius=6)
    # simple lock icon
    pygame.draw.rect(screen, (235, 240, 245), (badge.x + 5, badge.y + 9, 10, 7), border_radius=2)
    pygame.draw.arc(
        screen, (235, 240, 245),
        (badge.x + 5, badge.y + 3, 10, 10),
        3.14, 0, 2
    )
    # remaining moves text
    if remaining_moves > 0:
        draw_text(str(remaining_moves), rect.centerx, rect.y - 14, font=SMALL_FONT, color=WARN_AMBER, center=True)


def draw_tube(rect, tube, selected=False, tick=0, locked=False, remaining_lock_moves=0):
    glass_outer = (235, 243, 255)
    glass_inner = (20, 26, 36)
    glow_color = SELECT_COLOR if not locked else (180, 120, 120)

    if selected:
        glow_rect = rect.inflate(14, 14)
        pygame.draw.rect(screen, glow_color, glow_rect, 4, border_radius=18)

    border_color = (150, 160, 175) if locked else glass_outer
    pygame.draw.rect(screen, border_color, rect, 3, border_radius=15)

    padding = 8
    inner = rect.inflate(-padding * 2, -padding * 2)
    inner_fill = (28, 30, 34) if locked else glass_inner
    pygame.draw.rect(screen, inner_fill, inner, border_radius=12)

    # glass highlights
    pygame.draw.rect(screen, (210, 235, 255), pygame.Rect(inner.x + 4, inner.y + 8, 4, inner.height - 16), border_radius=3)
    pygame.draw.rect(screen, (105, 145, 185), pygame.Rect(inner.right - 8, inner.y + 14, 2, inner.height - 28), border_radius=2)

    slot_gap = 5
    slot_h = (inner.height - (TUBE_CAPACITY + 1) * slot_gap) // TUBE_CAPACITY
    slot_w = inner.width - 10
    slot_x = inner.x + 5

    # empty slots
    for level in range(TUBE_CAPACITY):
        y = inner.bottom - slot_gap - (level + 1) * slot_h - level * slot_gap
        slot_rect = pygame.Rect(slot_x, y, slot_w, slot_h)
        pygame.draw.rect(screen, EMPTY_SLOT if not locked else (70, 72, 78), slot_rect, border_radius=8)

    # liquid
    for level in range(len(tube)):
        y = inner.bottom - slot_gap - (level + 1) * slot_h - level * slot_gap
        slot_rect = pygame.Rect(slot_x, y, slot_w, slot_h)
        color_id = tube[level]
        base = COLOR_MAP.get(color_id, (200, 200, 200))

        if locked:
            # dim colors when locked
            base = tuple(max(30, c - 60) for c in base)

        pygame.draw.rect(screen, base, slot_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), (slot_rect.x + 3, slot_rect.y + 3, slot_rect.width - 6, 5), border_radius=4)
        pygame.draw.rect(screen, (20, 20, 20), (slot_rect.x + 2, slot_rect.bottom - 5, slot_rect.width - 4, 3), border_radius=2)
        pygame.draw.rect(screen, (245, 245, 245), slot_rect, 1, border_radius=8)

        # bubbles
        phase = (tick // 8 + level * 7 + color_id * 3) % 12
        bubble_y_offset = phase - 6
        b1 = (slot_rect.x + 11, slot_rect.centery + bubble_y_offset // 2)
        b2 = (slot_rect.right - 13, slot_rect.centery - 5 - bubble_y_offset // 3)
        b3 = (slot_rect.centerx + 6, slot_rect.bottom - 10 - (phase // 2))
        pygame.draw.circle(screen, (255, 255, 255), b1, 2)
        pygame.draw.circle(screen, (235, 245, 255), b2, 1)
        pygame.draw.circle(screen, (250, 250, 255), b3, 1)

    # surface ellipse on top layer
    if len(tube) > 0:
        top_level = len(tube) - 1
        y = inner.bottom - slot_gap - (top_level + 1) * slot_h - top_level * slot_gap
        top_rect = pygame.Rect(slot_x, y, slot_w, slot_h)
        wave_shift = ((tick // 6) % 5) - 2
        surface_rect = pygame.Rect(top_rect.x + 4, top_rect.y + 2, top_rect.width - 8, 10)
        surface_rect.x += wave_shift
        edge_col = (235, 235, 235) if locked else (255, 255, 255)
        pygame.draw.ellipse(screen, edge_col, surface_rect, 2)
        surface_inner = surface_rect.inflate(-4, -4)
        if surface_inner.width > 0 and surface_inner.height > 0:
            pygame.draw.ellipse(screen, (220, 240, 255), surface_inner, 1)

    # tube lip
    lip = pygame.Rect(rect.x + 6, rect.y - 2, rect.width - 12, 8)
    pygame.draw.rect(screen, (180, 220, 255), lip, border_radius=5)

    if locked:
        draw_lock_badge(rect, remaining_lock_moves)


# ==================== GAME ====================
class Game:
    def __init__(self):
        self.stats = load_stats()
        self.demo_only = False
        self.demo_indices = [i for i, lv in enumerate(LEVELS) if lv.get("is_demo_level")]
        if not self.demo_indices:
            self.demo_indices = [0]

        self.level_index = 0
        self.history = []
        self.hint_move = None
        self.hints_used_this_level = 0
        self.level_start_ticks = 0
        self.load_level(self.level_index)

    def current_level(self):
        return LEVELS[self.level_index]

    def level_time_sec(self):
        return max(0, (pygame.time.get_ticks() - self.level_start_ticks) // 1000)

    def load_level(self, index):
        self.level_index = index % len(LEVELS)
        meta = self.current_level()

        self.initial_state = clone_tubes(meta["tubes"])
        self.tubes = clone_tubes(meta["tubes"])
        self.selected_tube = None
        self.moves = 0
        self.won = False
        self.history = []
        self.hint_move = None
        self.hints_used_this_level = 0
        self.level_start_ticks = pygame.time.get_ticks()

        # lock configuration: tube index unlocks after N successful moves
        self.unlock_after_moves = dict(meta.get("unlock_after_moves", {}))
        self.lock_state = dict(self.unlock_after_moves)  # remaining moves until unlock

        ensure_level_stats(self.stats, meta["id"])
        save_stats(self.stats)

    def restart(self):
        self.tubes = clone_tubes(self.initial_state)
        self.selected_tube = None
        self.moves = 0
        self.won = False
        self.history = []
        self.hint_move = None
        self.hints_used_this_level = 0
        self.level_start_ticks = pygame.time.get_ticks()
        self.lock_state = dict(self.unlock_after_moves)
        self.stats["total_restarts"] += 1
        save_stats(self.stats)

    def next_level(self):
        if self.demo_only:
            # Cycle through demo levels only
            try:
                pos = self.demo_indices.index(self.level_index)
            except ValueError:
                pos = 0
            next_idx = self.demo_indices[(pos + 1) % len(self.demo_indices)]
            self.load_level(next_idx)
        else:
            self.load_level((self.level_index + 1) % len(LEVELS))

    def prev_level(self):
        if self.demo_only:
            try:
                pos = self.demo_indices.index(self.level_index)
            except ValueError:
                pos = 0
            prev_idx = self.demo_indices[(pos - 1) % len(self.demo_indices)]
            self.load_level(prev_idx)
        else:
            self.load_level((self.level_index - 1) % len(LEVELS))

    def toggle_demo_mode(self):
        self.demo_only = not self.demo_only
        if self.demo_only and self.level_index not in self.demo_indices:
            self.load_level(self.demo_indices[0])

    def is_locked(self, tube_idx):
        return self.lock_state.get(tube_idx, 0) > 0

    def remaining_lock_moves(self, tube_idx):
        return self.lock_state.get(tube_idx, 0)

    def decrement_locks_after_successful_move(self):
        changed = False
        for idx in list(self.lock_state.keys()):
            if self.lock_state[idx] > 0:
                self.lock_state[idx] -= 1
                changed = True
        if changed:
            # cleanup unlocked entries
            for idx in list(self.lock_state.keys()):
                if self.lock_state[idx] <= 0:
                    self.lock_state[idx] = 0

    def save_history(self):
        self.history.append((
            clone_tubes(self.tubes),
            self.moves,
            self.won,
            clone_locks(self.lock_state),
            self.hint_move,
            self.hints_used_this_level,
            self.level_start_ticks,
        ))

    def undo(self):
        if not self.history:
            return
        prev = self.history.pop()
        self.tubes = clone_tubes(prev[0])
        self.moves = prev[1]
        self.won = prev[2]
        self.lock_state = clone_locks(prev[3])
        self.hint_move = prev[4]
        self.hints_used_this_level = prev[5]
        self.level_start_ticks = prev[6]
        self.selected_tube = None

    def all_valid_moves(self):
        moves = []
        for src in range(len(self.tubes)):
            if self.is_locked(src):
                continue
            if not self.tubes[src]:
                continue
            for dst in range(len(self.tubes)):
                if src == dst:
                    continue
                if self.is_locked(dst):
                    continue
                if can_pour(self.tubes[src], self.tubes[dst]):
                    # optional heuristic: avoid pure no-op style move from complete tube to empty
                    if is_tube_complete(self.tubes[src]) and len(self.tubes[dst]) == 0:
                        continue
                    moves.append((src, dst))
        return moves

    def request_hint(self):
        if self.won:
            return
        valid = self.all_valid_moves()
        self.hint_move = valid[0] if valid else None
        if self.hint_move is not None:
            self.hints_used_this_level += 1
            self.stats["total_hints"] += 1
            save_stats(self.stats)

    def complete_level_if_needed(self):
        if not self.won:
            return
        meta = self.current_level()
        lid = meta["id"]
        ensure_level_stats(self.stats, lid)
        ls = self.stats["levels"][lid]

        ls["wins"] += 1
        if ls["best_moves"] is None or self.moves < ls["best_moves"]:
            ls["best_moves"] = self.moves

        t = self.level_time_sec()
        if ls["best_time_sec"] is None or t < ls["best_time_sec"]:
            ls["best_time_sec"] = t

        stars = compute_stars(self.moves, meta.get("par_moves", self.moves + 2), hints_used=self.hints_used_this_level > 0)
        if stars > ls.get("stars", 0):
            ls["stars"] = stars

        save_stats(self.stats)

    def handle_tube_click(self, idx):
        if self.won:
            return

        # cannot select locked tube
        if self.selected_tube is None:
            if self.is_locked(idx):
                return
            if self.tubes[idx]:
                self.selected_tube = idx
            return

        if idx == self.selected_tube:
            self.selected_tube = None
            return

        src_idx = self.selected_tube
        dst_idx = idx

        # locked destination blocks move
        if self.is_locked(dst_idx) or self.is_locked(src_idx):
            self.selected_tube = None
            return

        if can_pour(self.tubes[src_idx], self.tubes[dst_idx]):
            self.save_history()
            moved = pour(self.tubes[src_idx], self.tubes[dst_idx])
            if moved > 0:
                self.moves += 1
                self.hint_move = None
                self.decrement_locks_after_successful_move()
                self.won = check_win(self.tubes)
                if self.won:
                    self.complete_level_if_needed()

        self.selected_tube = None


# ==================== MAIN ====================
def main():
    game = Game()
    tick = 0

    # UI rects
    top_panel = pygame.Rect(18, 16, WIDTH - 36, 96)
    bottom_panel = pygame.Rect(18, HEIGHT - 88, WIDTH - 36, 70)

    restart_btn = pygame.Rect(30, 36, 118, 46)
    undo_btn    = pygame.Rect(160, 36, 102, 46)
    hint_btn    = pygame.Rect(274, 36, 102, 46)
    prev_btn    = pygame.Rect(388, 36, 90, 46)
    next_btn    = pygame.Rect(490, 36, 118, 46)
    demo_btn    = pygame.Rect(620, 36, 134, 46)

    while True:
        tick += 1
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        tube_rects = get_tube_rects(len(game.tubes))
        meta = game.current_level()
        lid = meta["id"]
        level_stats = game.stats["levels"].get(lid, {})
        par_moves = meta.get("par_moves", 0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.restart()
                elif event.key == pygame.K_u:
                    game.undo()
                elif event.key == pygame.K_n:
                    game.next_level()
                elif event.key == pygame.K_b:
                    game.prev_level()
                elif event.key == pygame.K_h:
                    game.request_hint()
                elif event.key == pygame.K_d:
                    game.toggle_demo_mode()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_btn.collidepoint(event.pos):
                    game.restart()
                    continue
                if undo_btn.collidepoint(event.pos):
                    game.undo()
                    continue
                if hint_btn.collidepoint(event.pos):
                    game.request_hint()
                    continue
                if prev_btn.collidepoint(event.pos):
                    game.prev_level()
                    continue
                if next_btn.collidepoint(event.pos):
                    game.next_level()
                    continue
                if demo_btn.collidepoint(event.pos):
                    game.toggle_demo_mode()
                    continue

                idx = tube_at_pos(event.pos, tube_rects)
                if idx is not None:
                    game.handle_tube_click(idx)

        # ---------- DRAW ----------
        screen.fill(BG_COLOR)

        draw_panel(top_panel)
        draw_panel(bottom_panel, fill=CARD_COLOR)

        draw_button(restart_btn, "Restart", mouse_pos, True, accent=(74, 133, 191))
        draw_button(undo_btn, "Undo", mouse_pos, enabled=(len(game.history) > 0 and not game.won), accent=(117, 92, 191))
        draw_button(hint_btn, "Hint", mouse_pos, enabled=not game.won, accent=(191, 138, 74))
        draw_button(prev_btn, "Prev", mouse_pos, True, accent=(95, 115, 150))
        draw_button(next_btn, "Next", mouse_pos, True, accent=(74, 160, 116))
        draw_button(demo_btn, f"Demo: {'ON' if game.demo_only else 'OFF'}", mouse_pos, True,
                    accent=(150, 92, 170) if game.demo_only else (95, 105, 125))

        # Header info
        draw_text("WaterSort+  •  Puzzle Engine Edition", 772, 30, font=TITLE_FONT, center=True)
        draw_text(
            f"{meta['name']}  |  {meta['difficulty']}  |  Par {par_moves}  |  Tags: {', '.join(meta.get('tags', [])) or 'none'}",
            772, 60, font=SMALL_FONT, color=SUBTEXT_COLOR, center=True
        )

        # Stats info
        elapsed = game.level_time_sec()
        draw_text(f"Level: {game.level_index + 1}/{len(LEVELS)}", 36, HEIGHT - 70, font=SMALL_FONT)
        draw_text(f"Moves: {game.moves}", 180, HEIGHT - 70, font=SMALL_FONT)
        draw_text(f"Time: {elapsed}s", 280, HEIGHT - 70, font=SMALL_FONT)
        draw_text(f"Par: {par_moves}", 380, HEIGHT - 70, font=SMALL_FONT)
        draw_text(f"Hints used: {game.hints_used_this_level}", 470, HEIGHT - 70, font=SMALL_FONT)

        best_moves = level_stats.get("best_moves")
        best_stars = level_stats.get("stars", 0)
        best_time = level_stats.get("best_time_sec")
        wins = level_stats.get("wins", 0)

        draw_text(f"Best moves: {best_moves if best_moves is not None else '-'}", 640, HEIGHT - 70, font=SMALL_FONT, color=SUBTEXT_COLOR)
        draw_text(f"Best time: {str(best_time)+'s' if best_time is not None else '-'}", 790, HEIGHT - 70, font=SMALL_FONT, color=SUBTEXT_COLOR)
        draw_text(f"Wins: {wins}", 930, HEIGHT - 70, font=SMALL_FONT, color=SUBTEXT_COLOR)
        draw_text(f"Stars: {star_string(best_stars)}", 36, HEIGHT - 44, font=SMALL_FONT, color=WARN_AMBER)

        controls_text = "Controls: Click pour | R restart | U undo | H hint | B prev | N next | D demo mode"
        draw_text(controls_text, WIDTH // 2, 128, font=SMALL_FONT, color=SUBTEXT_COLOR, center=True)

        # Hint line
        if game.hint_move is not None and not game.won:
            s, d = game.hint_move
            draw_text(f"Hint: Try pouring Tube {s + 1} -> Tube {d + 1}", WIDTH // 2, 148, font=SMALL_FONT, color=WARN_AMBER, center=True)

        # Draw tubes
        for i, rect in enumerate(tube_rects):
            locked = game.is_locked(i)
            remaining = game.remaining_lock_moves(i)
            draw_tube(
                rect,
                game.tubes[i],
                selected=(i == game.selected_tube),
                tick=tick,
                locked=locked,
                remaining_lock_moves=remaining
            )

            # Tube index label
            label_color = WARN_AMBER if locked else SUBTEXT_COLOR
            draw_text(str(i + 1), rect.centerx, rect.bottom + 12, font=SMALL_FONT, color=label_color, center=True)

            # Hint highlight
            if game.hint_move is not None:
                hs, hd = game.hint_move
                if i in (hs, hd):
                    hint_rect = rect.inflate(6, 6)
                    pygame.draw.rect(screen, (255, 180, 60), hint_rect, 2, border_radius=16)

        # Win banner
        if game.won:
            stars = compute_stars(game.moves, par_moves, hints_used=(game.hints_used_this_level > 0))
            banner = pygame.Rect(WIDTH // 2 - 300, HEIGHT - 160, 600, 60)
            pygame.draw.rect(screen, WIN_GREEN, banner, border_radius=14)
            pygame.draw.rect(screen, (170, 255, 210), banner, 2, border_radius=14)

            msg = f"Level Complete!  {star_string(stars)}  •  {game.moves} moves • {elapsed}s"
            if game.hints_used_this_level > 0:
                msg += " • hint penalty applied"
            draw_text(msg, banner.centerx, banner.centery, font=SMALL_FONT, color=(240, 255, 245), center=True)

        pygame.display.flip()


if __name__ == "__main__":
    main()