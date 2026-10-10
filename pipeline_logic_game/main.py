import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from board import Board
from network import simulate_flow
from solver import solve_pipeline
from ui import UIRenderer

def get_clicked_tile(pos, board, ui):
    cell_size, ox, oy = ui.get_layout(board)
    mx, my = pos
    if ox <= mx < ox + board.cols * cell_size and oy <= my < oy + board.rows * cell_size:
        c = (mx - ox) // cell_size
        r = (my - oy) // cell_size
        return (r, c)
    return None

def main():
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("FluxRouter: Network Flow Matrix")
    clock = pygame.time.Clock()

    board = Board(level_index=0)
    ui = UIRenderer(surface)

    history = []
    moves = 0
    tick = 0
    status = "Route pressurized fluid to all terminals without leaks."

    running = True
    while running:
        clock.tick(FPS)
        tick += 1

        powered_tiles, powered_sinks, leaks, flow_edges = simulate_flow(board)
        is_won = (len(powered_sinks) == len(board.sinks)) and (len(leaks) == 0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Mouse Rotation Controls
            if event.type == pygame.MOUSEBUTTONDOWN and not is_won:
                tile = get_clicked_tile(event.pos, board, ui)
                if tile and tile in board.pipes:
                    if event.button == 1:   # Left click = Clockwise
                        history.append((tile, board.pipes[tile]))
                        board.rotate_pipe(tile, clockwise=True)
                        moves += 1
                        status = f"Rotated node {tile}."
                    elif event.button == 3: # Right click = Counter-Clockwise
                        history.append((tile, board.pipes[tile]))
                        board.rotate_pipe(tile, clockwise=False)
                        moves += 1
                        status = f"Reversed node {tile}."

            if event.type == pygame.KEYDOWN:
                # Undo
                if event.key == pygame.K_u and history:
                    last_tile, prev_mask = history.pop()
                    board.pipes[last_tile] = prev_mask
                    moves = max(0, moves - 1)
                    status = "Reverted previous rotation."

                # Reset
                elif event.key == pygame.K_r:
                    board.load_level(board.level_index)
                    history.clear()
                    moves = 0
                    status = "Network reset to scrambled state."

                # Next Level
                elif event.key == pygame.K_n or (is_won and event.key == pygame.K_SPACE):
                    board.load_level(board.level_index + 1)
                    history.clear()
                    moves = 0
                    status = "Loaded next substation circuit."

                # Previous Level
                elif event.key == pygame.K_p:
                    board.load_level(board.level_index - 1)
                    history.clear()
                    moves = 0
                    status = "Loaded previous substation circuit."

                # AI Constraint Solver
                elif event.key == pygame.K_h:
                    if not is_won:
                        status = "AI Computing topology constraint satisfaction..."
                        ui.render(board, powered_tiles, powered_sinks, leaks, flow_edges, status, moves, is_won, tick)
                        pygame.display.flip()

                        solution = solve_pipeline(board)
                        if solution:
                            board.pipes = solution
                            status = "AI Solver matched all terminal conduits with 0 leaks!"
                        else:
                            status = "No leak-free closed circuit possible in current topology."

        ui.render(board, powered_tiles, powered_sinks, leaks, flow_edges, status, moves, is_won, tick)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
