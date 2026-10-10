# Window & Grid Display
WINDOW_WIDTH = 980
WINDOW_HEIGHT = 800
HUD_HEIGHT = 96
FPS = 60

# Ultra-Dark OLED & Carbon Palette
COLOR_BG = (9, 11, 17)
COLOR_HUD_BG = (14, 18, 28)
COLOR_HUD_BORDER = (28, 36, 56)
COLOR_DOT_GRID = (25, 33, 50)

# Recessed Tile Sockets & Barriers
COLOR_TILE_SOCKET = (16, 22, 35)
COLOR_TILE_BORDER = (29, 39, 61)
COLOR_TILE_INNER = (21, 29, 46)
COLOR_WALL = (20, 26, 38)
COLOR_WALL_BORDER = (38, 49, 72)
COLOR_WALL_HIGHLIGHT = (50, 65, 96)

# Unpowered Conduit Chassis
COLOR_PIPE_CHANNEL = (24, 32, 49)
COLOR_PIPE_WALL = (41, 53, 79)
COLOR_COUPLING = (62, 79, 115)

# Hyper-Vibrant Neon Plasma Flow
COLOR_FLOW_AURA = (0, 229, 255)          # Electric Aqua
COLOR_FLOW_CORE = (255, 255, 255)        # Hot White Laser
COLOR_PACKET_GLOW = (125, 245, 255)

# Power Core (Source) & Dynamic Reticle Sinks
COLOR_SOURCE_BASE = (245, 158, 11)       # Amber Solar Core
COLOR_SOURCE_GLOW = (251, 191, 36)
COLOR_SOURCE_CORE = (255, 251, 235)

COLOR_SINK_STANDBY = (244, 63, 94)       # Coral Rose
COLOR_SINK_ACTIVE = (16, 185, 129)       # Emerald Mint
COLOR_SINK_CORE = (236, 253, 245)

COLOR_LEAK_PULSE = (244, 63, 94)

# Modern Typography & UI Chips
COLOR_TEXT_PRIMARY = (248, 250, 252)
COLOR_TEXT_MUTED = (130, 145, 170)
COLOR_TEXT_ACCENT = (0, 229, 255)
COLOR_SUCCESS = (16, 185, 129)

COLOR_PILL_BG = (19, 26, 41)
COLOR_PILL_BORDER = (34, 46, 71)
COLOR_KEYCAP_BG = (27, 36, 56)
COLOR_KEYCAP_BORDER = (47, 62, 94)

# Network Directions & Topological Masks
DIR_NORTH = 0
DIR_EAST  = 1
DIR_SOUTH = 2
DIR_WEST  = 3

DIR_OFFSETS = [
    (-1, 0),  # North
    (0, 1),   # East
    (1, 0),   # South
    (0, -1)   # West
]

OPPOSITE_DIR = [2, 3, 0, 1]

MASK_N = 1
MASK_E = 2
MASK_S = 4
MASK_W = 8

# Pipe Types
PIPE_LINE   = MASK_N | MASK_S
PIPE_CORNER = MASK_N | MASK_E
PIPE_TEE    = MASK_N | MASK_E | MASK_W
PIPE_CROSS  = MASK_N | MASK_E | MASK_S | MASK_W
PIPE_CAP    = MASK_N