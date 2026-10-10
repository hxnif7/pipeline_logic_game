import pygame
import math
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, HUD_HEIGHT,
    COLOR_BG, COLOR_HUD_BG, COLOR_HUD_BORDER, COLOR_DOT_GRID,
    COLOR_TILE_SOCKET, COLOR_TILE_BORDER, COLOR_TILE_INNER,
    COLOR_WALL, COLOR_WALL_BORDER, COLOR_WALL_HIGHLIGHT,
    COLOR_PIPE_CHANNEL, COLOR_PIPE_WALL, COLOR_COUPLING,
    COLOR_FLOW_AURA, COLOR_FLOW_CORE, COLOR_PACKET_GLOW,
    COLOR_SOURCE_BASE, COLOR_SOURCE_GLOW, COLOR_SOURCE_CORE,
    COLOR_SINK_STANDBY, COLOR_SINK_ACTIVE, COLOR_SINK_CORE,
    COLOR_LEAK_PULSE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED, COLOR_TEXT_ACCENT, COLOR_SUCCESS,
    COLOR_PILL_BG, COLOR_PILL_BORDER, COLOR_KEYCAP_BG, COLOR_KEYCAP_BORDER,
    DIR_OFFSETS
)

class UIRenderer:
    def __init__(self, surface):
        self.surface = surface
        self.font_brand = pygame.font.SysFont("Segoe UI, SF Pro Display, Arial", 18, bold=True)
        self.font_tag = pygame.font.SysFont("Segoe UI, SF Pro Display, Arial", 10, bold=True)
        self.font_chip = pygame.font.SysFont("Segoe UI, SF Pro Display, Arial", 12, bold=True)
        self.font_main = pygame.font.SysFont("Segoe UI, SF Pro Display, Arial", 14)
        self.font_key = pygame.font.SysFont("Consolas, SF Mono, monospace", 11, bold=True)
        self.font_modal_title = pygame.font.SysFont("Segoe UI, SF Pro Display, Arial", 24, bold=True)
        self.font_modal_sub = pygame.font.SysFont("Segoe UI, SF Pro Display, Arial", 14)

    def get_layout(self, board):
        avail_w = WINDOW_WIDTH - 90
        avail_h = WINDOW_HEIGHT - HUD_HEIGHT - 90
        cell_size = min(avail_w // board.cols, avail_h // board.rows, 94)
        grid_w = board.cols * cell_size
        grid_h = board.rows * cell_size
        ox = (WINDOW_WIDTH - grid_w) // 2
        oy = HUD_HEIGHT + (WINDOW_HEIGHT - HUD_HEIGHT - grid_h) // 2
        return cell_size, ox, oy

    def render(self, board, powered_tiles, powered_sinks, leaks, flow_edges, status, moves, is_won, tick):
        self.surface.fill(COLOR_BG)
        cell_size, ox, oy = self.get_layout(board)

        self.draw_ambient_dots()
        self.draw_hud(board, powered_sinks, leaks, status, moves)
        self.draw_chassis(board, cell_size, ox, oy)
        self.draw_conduits(board, powered_tiles, leaks, flow_edges, cell_size, ox, oy, tick)
        self.draw_nodes(board, powered_sinks, cell_size, ox, oy, tick)

        if is_won:
            self.draw_modal(moves, tick)

    def draw_ambient_dots(self):
        # Subtle tech dot-grid pattern in background
        spacing = 30
        for x in range(15, WINDOW_WIDTH, spacing):
            for y in range(HUD_HEIGHT + 15, WINDOW_HEIGHT, spacing):
                self.surface.set_at((x, y), COLOR_DOT_GRID)

    def draw_chip(self, label, value, x, y, accent=None, dot=None):
        l_surf = self.font_tag.render(label, True, COLOR_TEXT_MUTED)
        v_surf = self.font_chip.render(value, True, accent or COLOR_TEXT_PRIMARY)
        w = l_surf.get_width() + v_surf.get_width() + (26 if dot else 18)
        h = 26
        rx = x - w
        rect = pygame.Rect(rx, y, w, h)

        pygame.draw.rect(self.surface, COLOR_PILL_BG, rect, border_radius=13)
        pygame.draw.rect(self.surface, COLOR_PILL_BORDER, rect, 1, border_radius=13)

        cx = rect.x + 9
        if dot:
            pygame.draw.circle(self.surface, dot, (cx + 3, rect.centery), 3.5)
            cx += 12

        self.surface.blit(l_surf, (cx, rect.centery - l_surf.get_height() // 2))
        cx += l_surf.get_width() + 4
        self.surface.blit(v_surf, (cx, rect.centery - v_surf.get_height() // 2))
        return w

    def draw_hud(self, board, powered_sinks, leaks, status, moves):
        pygame.draw.rect(self.surface, COLOR_HUD_BG, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
        pygame.draw.line(self.surface, COLOR_HUD_BORDER, (0, HUD_HEIGHT), (WINDOW_WIDTH, HUD_HEIGHT), 1)

        # Brand mark
        brand_surf = self.font_brand.render("FLUXROUTER", True, COLOR_TEXT_PRIMARY)
        self.surface.blit(brand_brand := brand_surf, (28, 16))

        tag_rect = pygame.Rect(28 + brand_brand.get_width() + 10, 18, 44, 18)
        pygame.draw.rect(self.surface, (12, 45, 68), tag_rect, border_radius=9)
        self.surface.blit(self.font_tag.render("ONLINE", True, COLOR_TEXT_ACCENT), (tag_rect.x + 6, tag_rect.y + 2))

        ch_info = f"// SECTOR 0{board.level_index + 1}: {board.title.upper()}"
        self.surface.blit(self.font_main.render(ch_info, True, COLOR_TEXT_MUTED), (tag_rect.right + 12, 17))

        # Status Chips
        total_sinks = len(board.sinks)
        p_count = len(powered_sinks)
        sink_col = COLOR_SUCCESS if p_count == total_sinks else COLOR_TEXT_ACCENT
        leak_col = COLOR_LEAK_PULSE if len(leaks) > 0 else COLOR_SUCCESS

        curr_x = WINDOW_WIDTH - 28
        curr_x -= self.draw_chip("MOVES", str(moves), curr_x, 14) + 8
        curr_x -= self.draw_chip("LEAKS", str(len(leaks)), curr_x, 14, leak_col, leak_col) + 8
        curr_x -= self.draw_chip("TERMINALS", f"{p_count}/{total_sinks}", curr_x, 14, sink_col, sink_col)

        # Active Telemetry String
        self.surface.blit(self.font_main.render(status, True, COLOR_TEXT_ACCENT), (28, 46))

        # Minimal Keycaps
        keys = [
            ("L-CLICK", "Rotate"),
            ("R-CLICK", "Reverse"),
            ("H", "AI Solve"),
            ("U", "Undo"),
            ("R", "Reset"),
            ("N", "Next")
        ]
        kx = 28
        for k, action in keys:
            k_surf = self.font_key.render(k, True, COLOR_TEXT_PRIMARY)
            a_surf = self.font_key.render(f" {action}  ", True, COLOR_TEXT_MUTED)
            kw = k_surf.get_width() + 10
            rect = pygame.Rect(kx, 70, kw, 18)
            pygame.draw.rect(self.surface, COLOR_KEYCAP_BG, rect, border_radius=4)
            pygame.draw.rect(self.surface, COLOR_KEYCAP_BORDER, rect, 1, border_radius=4)
            self.surface.blit(k_surf, (kx + 5, 72))
            self.surface.blit(a_surf, (kx + kw + 2, 72))
            kx += kw + a_surf.get_width() + 6

    def draw_chassis(self, board, size, ox, oy):
        for r in range(board.rows):
            for c in range(board.cols):
                rect = pygame.Rect(ox + c * size + 3, oy + r * size + 3, size - 6, size - 6)
                if (r, c) in board.walls:
                    # Obsidian Wall Barrier
                    pygame.draw.rect(self.surface, COLOR_WALL, rect, border_radius=10)
                    pygame.draw.rect(self.surface, COLOR_WALL_BORDER, rect, 1, border_radius=10)
                    # Subtle chamfer highlight line
                    pygame.draw.line(self.surface, COLOR_WALL_HIGHLIGHT, (rect.x + 8, rect.y + 4), (rect.right - 8, rect.y + 4), 1)
                else:
                    # Recessed Glass Tile Socket
                    pygame.draw.rect(self.surface, COLOR_TILE_SOCKET, rect, border_radius=10)
                    pygame.draw.rect(self.surface, COLOR_TILE_BORDER, rect, 1, border_radius=10)
                    inner = rect.inflate(-12, -12)
                    pygame.draw.rect(self.surface, COLOR_TILE_INNER, inner, border_radius=6)

    def draw_conduits(self, board, powered_tiles, leaks, flow_edges, size, ox, oy, tick):
        glow_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pipe_w = max(18, size // 3)
        stream_w = max(7, pipe_w // 2)

        for (r, c), mask in board.pipes.items():
            cx = ox + c * size + size // 2
            cy = oy + r * size + size // 2
            is_active = (r, c) in powered_tiles

            # 1. Dark Recessed Metal Casing
            pygame.draw.circle(self.surface, COLOR_PIPE_WALL, (cx, cy), pipe_w // 2 + 2)
            pygame.draw.circle(self.surface, COLOR_PIPE_CHANNEL, (cx, cy), pipe_w // 2)

            for d_idx, (dr, dc) in enumerate(DIR_OFFSETS):
                if mask & (1 << d_idx):
                    ex = cx + dc * (size // 2)
                    ey = cy + dr * (size // 2)

                    rect_shell = pygame.Rect(
                        min(cx, ex) - pipe_w // 2 - 1, min(cy, ey) - pipe_w // 2 - 1,
                        abs(ex - cx) + pipe_w + 2, abs(ey - cy) + pipe_w + 2
                    )
                    pygame.draw.rect(self.surface, COLOR_PIPE_WALL, rect_shell, border_radius=3)

                    rect_channel = pygame.Rect(
                        min(cx, ex) - pipe_w // 2, min(cy, ey) - pipe_w // 2,
                        abs(ex - cx) + pipe_w, abs(ey - cy) + pipe_w
                    )
                    pygame.draw.rect(self.surface, COLOR_PIPE_CHANNEL, rect_channel, border_radius=2)

                    # Metallic coupling lip
                    c_x = cx + dc * (size // 2 - 4)
                    c_y = cy + dr * (size // 2 - 4)
                    if dr != 0:
                        pygame.draw.line(self.surface, COLOR_COUPLING, (c_x - pipe_w // 2 + 3, c_y), (c_x + pipe_w // 2 - 3, c_y), 2)
                    else:
                        pygame.draw.line(self.surface, COLOR_COUPLING, (c_x, c_y - pipe_w // 2 + 3), (c_x, c_y + pipe_w // 2 - 3), 2)

            # Central recessed anchor
            pygame.draw.circle(self.surface, (14, 20, 32), (cx, cy), max(3, pipe_w // 5))

            # 2. Glowing Neon Flow
            if is_active:
                pulse = math.sin(tick * 0.12)
                alpha_corona = int(75 + 25 * pulse)

                pygame.draw.circle(self.surface, COLOR_FLOW_AURA, (cx, cy), stream_w // 2 + 1)
                pygame.draw.circle(self.surface, COLOR_FLOW_CORE, (cx, cy), max(2, stream_w // 4))

                for d_idx, (dr, dc) in enumerate(DIR_OFFSETS):
                    if mask & (1 << d_idx):
                        neighbor = (r + dr, c + dc)
                        has_flow = frozenset([(r, c), neighbor]) in flow_edges or ((r, c), d_idx) in leaks
                        if has_flow:
                            ex = cx + dc * (size // 2)
                            ey = cy + dr * (size // 2)

                            # Wide atmospheric halo
                            pygame.draw.line(glow_surf, (*COLOR_FLOW_AURA, alpha_corona // 2), (cx, cy), (ex, ey), stream_w + 16)
                            # Tight energetic core
                            pygame.draw.line(glow_surf, (*COLOR_FLOW_AURA, alpha_corona), (cx, cy), (ex, ey), stream_w + 6)
                            # Solid fluid beam
                            pygame.draw.line(self.surface, COLOR_FLOW_AURA, (cx, cy), (ex, ey), stream_w)
                            # Laser hot-spot
                            pygame.draw.line(self.surface, COLOR_FLOW_CORE, (cx, cy), (ex, ey), max(2, stream_w // 4))

                            # Traveling Energy Packets (Animated sci-fi signal)
                            packet_prog = ((tick * 0.04) + (r * 0.2 + c * 0.3)) % 1.0
                            px = cx + (ex - cx) * packet_prog
                            py = cy + (ey - cy) * packet_prog
                            pygame.draw.circle(glow_surf, (*COLOR_PACKET_GLOW, 200), (int(px), int(py)), 6)
                            pygame.draw.circle(self.surface, (255, 255, 255), (int(px), int(py)), 3)

            # 3. Dynamic Leak Warning
            for d_idx, (dr, dc) in enumerate(DIR_OFFSETS):
                if ((r, c), d_idx) in leaks:
                    lx = cx + dc * (size // 2 - 3)
                    ly = cy + dr * (size // 2 - 3)
                    l_pulse = int(abs(math.sin(tick * 0.22)) * 8) + 4
                    pygame.draw.circle(glow_surf, (*COLOR_LEAK_PULSE, 120), (lx, ly), l_pulse + 6)
                    pygame.draw.circle(self.surface, COLOR_LEAK_PULSE, (lx, ly), 5)
                    pygame.draw.circle(self.surface, (255, 255, 255), (lx, ly), 2)

        self.surface.blit(glow_surf, (0, 0))

    def draw_nodes(self, board, powered_sinks, size, ox, oy, tick):
        pipe_w = max(18, size // 3)

        # Source Reactor (Sun Core)
        for (r, c), mask in board.sources.items():
            cx = ox + c * size + size // 2
            cy = oy + r * size + size // 2

            for d_idx, (dr, dc) in enumerate(DIR_OFFSETS):
                if mask & (1 << d_idx):
                    ex = cx + dc * (size // 2)
                    ey = cy + dr * (size // 2)
                    pygame.draw.line(self.surface, COLOR_PIPE_WALL, (cx, cy), (ex, ey), pipe_w)
                    pygame.draw.line(self.surface, COLOR_SOURCE_BASE, (cx, cy), (ex, ey), pipe_w - 6)

            # Animated reactor housing
            pulse = math.sin(tick * 0.14) * 3
            pygame.draw.circle(self.surface, COLOR_PIPE_WALL, (cx, cy), size // 3 + 3)
            pygame.draw.circle(self.surface, (30, 22, 12), (cx, cy), size // 3)
            pygame.draw.circle(self.surface, COLOR_SOURCE_GLOW, (cx, cy), max(3, int(size // 4 + pulse)))
            pygame.draw.circle(self.surface, COLOR_SOURCE_CORE, (cx, cy), size // 8)

        # Sinks (High-Tech Holographic Terminals)
        for (r, c), mask in board.sinks.items():
            cx = ox + c * size + size // 2
            cy = oy + r * size + size // 2
            is_active = (r, c) in powered_sinks

            for d_idx, (dr, dc) in enumerate(DIR_OFFSETS):
                if mask & (1 << d_idx):
                    ex = cx + dc * (size // 2)
                    ey = cy + dr * (size // 2)
                    pygame.draw.line(self.surface, COLOR_PIPE_WALL, (cx, cy), (ex, ey), pipe_w)

            col = COLOR_SINK_ACTIVE if is_active else COLOR_SINK_STANDBY
            c_rad = size // 3

            # Outer ring chassis
            pygame.draw.circle(self.surface, COLOR_PIPE_WALL, (cx, cy), c_rad + 2)
            pygame.draw.circle(self.surface, (12, 16, 26), (cx, cy), c_rad)

            # Active Holo Glow
            if is_active:
                holo_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(holo_surf, (*COLOR_SINK_ACTIVE, 60), (size, size), c_rad + 8)
                self.surface.blit(holo_surf, (cx - size, cy - size))

            # Reticle Arc Beacons
            pygame.draw.circle(self.surface, col, (cx, cy), c_rad - 2, 2)
            pygame.draw.circle(self.surface, col, (cx, cy), size // 6, 2)

            if is_active:
                pygame.draw.circle(self.surface, COLOR_SINK_CORE, (cx, cy), size // 10)
                # Rotating scanner ticks
                angle = tick * 0.08
                for i in range(4):
                    a = angle + (math.pi / 2) * i
                    tx = cx + math.cos(a) * (c_rad - 3)
                    ty = cy + math.sin(a) * (c_rad - 3)
                    pygame.draw.circle(self.surface, (255, 255, 255), (int(tx), int(ty)), 2)

    def draw_modal(self, moves, tick):
        dim_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((8, 10, 16, 220))
        self.surface.blit(dim_surf, (0, 0))

        mw, mh = 480, 220
        rect = pygame.Rect((WINDOW_WIDTH - mw) // 2, (WINDOW_HEIGHT - mh) // 2, mw, mh)
        pygame.draw.rect(self.surface, COLOR_HUD_BG, rect, border_radius=16)
        pygame.draw.rect(self.surface, COLOR_SUCCESS, rect, 2, border_radius=16)

        # Pulse accent halo
        glow = pygame.Surface((mw + 24, mh + 24), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*COLOR_SUCCESS, 30), glow.get_rect(), border_radius=20)
        self.surface.blit(glow, (rect.x - 12, rect.y - 12))

        title = self.font_modal_title.render("TOPOLOGY SYNCHRONIZED", True, COLOR_SUCCESS)
        self.surface.blit(title, (rect.centerx - title.get_width() // 2, rect.y + 34))

        stats = f"Circuit closed in {moves} rotations with 0 active leaks."
        sub = self.font_modal_sub.render(stats, True, COLOR_TEXT_PRIMARY)
        self.surface.blit(sub, (rect.centerx - sub.get_width() // 2, rect.y + 80))

        bw, bh = 240, 42
        btn = pygame.Rect(rect.centerx - bw // 2, rect.y + 132, bw, bh)
        pygame.draw.rect(self.surface, COLOR_SUCCESS, btn, border_radius=21)
        btn_txt = self.font_chip.render("PRESS [N] FOR NEXT SECTOR", True, (8, 10, 16))
        self.surface.blit(btn_txt, (btn.centerx - btn_txt.get_width() // 2, btn.y + 13))