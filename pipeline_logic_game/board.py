import random
from constants import (
    DIR_OFFSETS, OPPOSITE_DIR,
    PIPE_LINE, PIPE_CORNER, PIPE_TEE, PIPE_CROSS, PIPE_CAP,
    MASK_N, MASK_E, MASK_S, MASK_W
)

def rotate_mask(mask, times=1):
    m = mask
    for _ in range(times % 4):
        m = ((m << 1) & 0b1111) | (m >> 3)
    return m

# Map Symbols:
# '#' = Wall
# 'S_U', 'S_R', 'S_D', 'S_L' = Source Generator facing Up, Right, Down, Left
# 'T_U', 'T_R', 'T_D', 'T_L' = Terminal/Sink facing Up, Right, Down, Left
# 'I' = Straight Line
# 'L' = Corner Elbow
# 'T' = T-Junction
# 'X' = 4-Way Cross

LEVELS = [
    # Level 1: Substation Feed (Verified S-Curve)
    {
        "title": "Substation Feed",
        "grid": [
            ["#", "#", "#", "#", "#", "#"],
            ["#", "S_R", "I", "L", "#", "#"],
            ["#", "#", "#", "L", "L", "#"],
            ["#", "#", "#", "#", "T_U", "#"],
            ["#", "#", "#", "#", "#", "#"]
        ]
    },
    # Level 2: Dual Manifold Routing (Verified Fork)
    {
        "title": "Dual Core Splice",
        "grid": [
            ["#", "#", "#", "#", "#", "#", "#"],
            ["#", "T_D", "#", "S_D", "#", "T_D", "#"],
            ["#", "L", "I", "T", "I", "L", "#"],
            ["#", "#", "#", "#", "#", "#", "#"]
        ]
    },
    # Level 3: Dual-Feed Pressure Loop (Verified Topology)
    {
        "title": "Cooling Matrix",
        "grid": [
            ["#", "#", "#", "#", "#", "#"],
            ["#", "S_R", "T", "I", "L", "#"],
            ["#", "#", "L", "I", "T", "#"],
            ["#", "#", "#", "#", "T_U", "#"],
            ["#", "#", "#", "#", "#", "#"]
        ]
    },
    # Level 4: 4-Way Cross Power Distribution (Verified 3-Terminal Sink)
    {
        "title": "Quantum Reactor Flow",
        "grid": [
            ["#", "#", "#", "#", "#", "#", "#"],
            ["#", "T_D", "#", "S_D", "#", "T_D", "#"],
            ["#", "L", "I", "X", "I", "L", "#"],
            ["#", "#", "#", "I", "#", "#", "#"],
            ["#", "#", "#", "T_U", "#", "#", "#"],
            ["#", "#", "#", "#", "#", "#", "#"]
        ]
    }
]

class Board:
    def __init__(self, level_index=0):
        self.load_level(level_index)

    def load_level(self, index):
        self.level_index = index % len(LEVELS)
        data = LEVELS[self.level_index]
        self.title = data["title"]
        raw = data["grid"]

        self.rows = len(raw)
        self.cols = max(len(r) for r in raw)

        self.walls = set()
        self.sources = {}
        self.sinks = {}
        self.pipes = {}
        self.base_shapes = {}

        dir_map = {
            "U": MASK_N,
            "R": MASK_E,
            "D": MASK_S,
            "L": MASK_W
        }

        for r, row in enumerate(raw):
            for c, cell in enumerate(row):
                pos = (r, c)
                if cell == '#':
                    self.walls.add(pos)
                elif cell.startswith("S_"):
                    d = cell.split("_")[1]
                    self.sources[pos] = dir_map[d]
                elif cell.startswith("T_"):
                    d = cell.split("_")[1]
                    self.sinks[pos] = dir_map[d]
                elif cell == "I":
                    self.base_shapes[pos] = PIPE_LINE
                    self.pipes[pos] = rotate_mask(PIPE_LINE, random.randint(0, 3))
                elif cell == "L":
                    self.base_shapes[pos] = PIPE_CORNER
                    self.pipes[pos] = rotate_mask(PIPE_CORNER, random.randint(0, 3))
                elif cell == "T":
                    self.base_shapes[pos] = PIPE_TEE
                    self.pipes[pos] = rotate_mask(PIPE_TEE, random.randint(0, 3))
                elif cell == "X":
                    self.base_shapes[pos] = PIPE_CROSS
                    self.pipes[pos] = PIPE_CROSS

    def rotate_pipe(self, pos, clockwise=True):
        if pos in self.pipes:
            curr = self.pipes[pos]
            self.pipes[pos] = rotate_mask(curr, 1 if clockwise else 3)
            return True
        return False