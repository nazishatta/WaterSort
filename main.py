import sys
import pygame
from levels import LEVELS

pygame.init()

WIDTH, HEIGHT = 900, 650
FPS = 60
TUBE_CAPACITY = 4

BG_COLOR = (16, 22, 32)
PANEL_COLOR = (33, 43, 60)
EMPTY_SLOT = (60, 70, 92)


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

FONT = pygame.font.SysFont("arial", 24)
SMALL_FONT = pygame.font.SysFont("arial", 18)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Water Sort Puzzle")
clock = pygame.time.Clock()


def clone_level(level_data):
    return [tube[:] for tube in level_data]


def is_tube_complete(tube):
    if len(tube) != TUBE_CAPACITY:
        return False
    return all(color == tube[0] for color in tube)


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


def get_tube_rects(num_tubes):
    rects = []
    cols = min(6, num_tubes)
    tube_w = 70
    tube_h = 220
    gap_x = 35
    gap_y = 40

    total_w = cols * tube_w + (cols - 1) * gap_x
    start_x = (WIDTH - total_w) // 2
    start_y = 110

    for i in range(num_tubes):
        row = i // cols
        col = i % cols
        x = start_x + col * (tube_w + gap_x)
        y = start_y + row * (tube_h + gap_y)
        rects.append(pygame.Rect(x, y, tube_w, tube_h))
    return rects


def draw_text(text, x, y, font=FONT, color=TEXT_COLOR, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)


def draw_button(rect, label):
    pygame.draw.rect(screen, (70, 130, 180), rect, border_radius=10)
    pygame.draw.rect(screen, (220, 220, 220), rect, 2, border_radius=10)
    draw_text(label, rect.centerx, rect.centery, font=SMALL_FONT, center=True)


def draw_tube(rect, tube, selected=False):
    # Colors for glass look
    glass_outer = (230, 240, 255)
    glass_inner = (22, 28, 38)
    glass_shine = (180, 220, 255)
    glow_color = (255, 220, 80)

    # Selection glow
    if selected:
        glow_rect = rect.inflate(10, 10)
        pygame.draw.rect(screen, glow_color, glow_rect, 4, border_radius=16)

    # Outer tube border (glass)
    pygame.draw.rect(screen, glass_outer, rect, 3, border_radius=14)

    # Inner area
    padding = 8
    inner = rect.inflate(-padding * 2, -padding * 2)
    pygame.draw.rect(screen, glass_inner, inner, border_radius=11)

    # Vertical glass highlights (left and right)
    left_shine = pygame.Rect(inner.x + 4, inner.y + 6, 4, inner.height - 12)
    right_shine = pygame.Rect(inner.right - 8, inner.y + 12, 2, inner.height - 24)
    pygame.draw.rect(screen, (210, 235, 255), left_shine, border_radius=3)
    pygame.draw.rect(screen, (120, 160, 200), right_shine, border_radius=2)

    # Slot geometry
    slot_gap = 5
    slot_h = (inner.height - (TUBE_CAPACITY + 1) * slot_gap) // TUBE_CAPACITY
    slot_w = inner.width - 10
    slot_x = inner.x + 5

    # Draw empty slots + liquid layers (bottom -> top)
    for level in range(TUBE_CAPACITY):
        y = inner.bottom - slot_gap - (level + 1) * slot_h - level * slot_gap
        slot_rect = pygame.Rect(slot_x, y, slot_w, slot_h)

        # Empty slot shadow
        pygame.draw.rect(screen, (52, 60, 78), slot_rect, border_radius=8)

        if level < len(tube):
            color_id = tube[level]
            base = COLOR_MAP.get(color_id, (200, 200, 200))

            # Main liquid layer
            pygame.draw.rect(screen, base, slot_rect, border_radius=8)

            # Top liquid highlight (makes it look glossy/wet)
            top_highlight = pygame.Rect(slot_rect.x + 3, slot_rect.y + 3, slot_rect.width - 6, 6)
            pygame.draw.rect(screen, (255, 255, 255), top_highlight, border_radius=4)

            # Lower shadow for depth
            bottom_shadow = pygame.Rect(slot_rect.x + 2, slot_rect.bottom - 6, slot_rect.width - 4, 4)
            pygame.draw.rect(screen, (0, 0, 0), bottom_shadow, border_radius=3)

            # Thin outline
            pygame.draw.rect(screen, (245, 245, 245), slot_rect, 1, border_radius=8)

    # Tube lip (top rim) for glass effect
    lip_rect = pygame.Rect(rect.x + 6, rect.y - 2, rect.width - 12, 8)
    pygame.draw.rect(screen, glass_shine, lip_rect, border_radius=5)


def tube_at_pos(pos, tube_rects):
    for i, rect in enumerate(tube_rects):
        if rect.collidepoint(pos):
            return i
    return None


class Game:
    def __init__(self):
        self.level_index = 0
        self.load_level(self.level_index)

    def load_level(self, index):
        self.level_index = index % len(LEVELS)
        self.initial_state = clone_level(LEVELS[self.level_index])
        self.tubes = clone_level(LEVELS[self.level_index])
        self.selected_tube = None
        self.moves = 0
        self.won = False

    def restart(self):
        self.tubes = clone_level(self.initial_state)
        self.selected_tube = None
        self.moves = 0
        self.won = False

    def next_level(self):
        self.load_level((self.level_index + 1) % len(LEVELS))

    def handle_tube_click(self, idx):
        if self.won:
            return

        if self.selected_tube is None:
            if self.tubes[idx]:
                self.selected_tube = idx
            return

        if idx == self.selected_tube:
            self.selected_tube = None
            return

        src_idx = self.selected_tube
        dst_idx = idx
        moved = pour(self.tubes[src_idx], self.tubes[dst_idx])

        if moved > 0:
            self.moves += 1
            self.won = check_win(self.tubes)

        self.selected_tube = None


def main():
    game = Game()

    restart_btn = pygame.Rect(60, 25, 120, 45)
    next_btn = pygame.Rect(200, 25, 140, 45)

    while True:
        clock.tick(FPS)
        tube_rects = get_tube_rects(len(game.tubes))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.restart()
                elif event.key == pygame.K_n:
                    game.next_level()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if restart_btn.collidepoint(mouse_pos):
                    game.restart()
                    continue

                if next_btn.collidepoint(mouse_pos):
                    game.next_level()
                    continue

                idx = tube_at_pos(mouse_pos, tube_rects)
                if idx is not None:
                    game.handle_tube_click(idx)

        screen.fill(BG_COLOR)

        pygame.draw.rect(screen, PANEL_COLOR, (20, 15, WIDTH - 40, 65), border_radius=14)
        draw_button(restart_btn, "Restart")
        draw_button(next_btn, "Next Level")
        draw_text(f"Level: {game.level_index + 1}", 380, 35, font=SMALL_FONT)
        draw_text(f"Moves: {game.moves}", 500, 35, font=SMALL_FONT)

        if game.won:
            draw_text("You Win! 🎉", 700, 35, font=SMALL_FONT, color=(120, 255, 120))

        draw_text("Click a tube to select, then click another tube to pour", 60, 85, font=SMALL_FONT)

        for i, rect in enumerate(tube_rects):
            draw_tube(rect, game.tubes[i], selected=(i == game.selected_tube))

        pygame.display.flip()


if __name__ == "__main__":
    main()