from collections import deque
from constants import DIR_OFFSETS, OPPOSITE_DIR

def simulate_flow(board):
    """
    Performs BFS traversal from Source nodes across matching bidirectional ports.
    Returns:
        powered_tiles: set of (r, c) active in the flow network
        powered_sinks: set of (r, c) target terminals energized
        leaks: set of ((r, c), dir_idx) active ports open to empty space or mismatch
        flow_edges: set of frozenset([(r1, c1), (r2, c2)]) conducting fluid
    """
    powered_tiles = set()
    powered_sinks = set()
    leaks = set()
    flow_edges = set()

    queue = deque()

    for s_pos, s_mask in board.sources.items():
        powered_tiles.add(s_pos)
        queue.append(s_pos)

    while queue:
        curr = queue.popleft()
        r, c = curr

        # Determine mask of current node
        if curr in board.sources:
            mask = board.sources[curr]
        elif curr in board.sinks:
            mask = board.sinks[curr]
        else:
            mask = board.pipes.get(curr, 0)

        for d_idx, (dr, dc) in enumerate(DIR_OFFSETS):
            # Does current node have an open port facing d_idx?
            if not (mask & (1 << d_idx)):
                continue

            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)
            opp_d = OPPOSITE_DIR[d_idx]

            # 1. Out of bounds or Wall -> LEAK
            if not (0 <= nr < board.rows and 0 <= nc < board.cols) or neighbor in board.walls:
                leaks.add((curr, d_idx))
                continue

            # Determine neighbor mask
            if neighbor in board.sources:
                n_mask = board.sources[neighbor]
            elif neighbor in board.sinks:
                n_mask = board.sinks[neighbor]
            elif neighbor in board.pipes:
                n_mask = board.pipes[neighbor]
            else:
                n_mask = 0

            # 2. Check if neighbor port connects back
            if n_mask & (1 << opp_d):
                edge = frozenset([curr, neighbor])
                flow_edges.add(edge)

                if neighbor not in powered_tiles:
                    powered_tiles.add(neighbor)
                    if neighbor in board.sinks:
                        powered_sinks.add(neighbor)
                    queue.append(neighbor)
            else:
                # Open pipe discharging fluid into unaligned neighbor -> LEAK
                leaks.add((curr, d_idx))

    return powered_tiles, powered_sinks, leaks, flow_edges
