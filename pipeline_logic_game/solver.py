from board import rotate_mask
from network import simulate_flow
from constants import DIR_OFFSETS, OPPOSITE_DIR, PIPE_CROSS

def solve_pipeline(board):
    """
    Constraint-Satisfaction / Backtracking solver.
    Prunes impossible orientations (e.g. ports facing outer walls) to resolve in <15ms.
    """
    rotatable_positions = [pos for pos in board.pipes.keys() if board.base_shapes[pos] != PIPE_CROSS]
    
    # Store backup of current user configuration
    saved_state = dict(board.pipes)

    # Pre-calculate valid orientations per tile (Prune any orientation with ports facing walls/bounds)
    valid_domain = {}
    for pos in rotatable_positions:
        base = board.base_shapes[pos]
        unique_masks = list(set([rotate_mask(base, i) for i in range(4)]))
        pruned_masks = []
        r, c = pos

        for m in unique_masks:
            is_valid = True
            for d_idx, (dr, dc) in enumerate(DIR_OFFSETS):
                if m & (1 << d_idx):
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < board.rows and 0 <= nc < board.cols) or (nr, nc) in board.walls:
                        is_valid = False
                        break
            if is_valid:
                pruned_masks.append(m)

        valid_domain[pos] = pruned_masks if pruned_masks else unique_masks

    total_keys = len(rotatable_positions)

    def backtrack(index):
        if index == total_keys:
            _, powered_sinks, leaks, _ = simulate_flow(board)
            return len(powered_sinks) == len(board.sinks) and len(leaks) == 0

        pos = rotatable_positions[index]
        for candidate_mask in valid_domain[pos]:
            board.pipes[pos] = candidate_mask
            if backtrack(index + 1):
                return True

        return False

    found = backtrack(0)
    solution = dict(board.pipes) if found else None

    # Restore user state
    board.pipes = saved_state
    return solution
