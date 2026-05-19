import pygame

# Screen dimensions
WIDTH, HEIGHT = 800, 700
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
ANIMATION_FLASH_COLOR = (200, 200, 200)

# Tetromino shapes
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

SHAPE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

# UI Enhancements & State
MENU_TITLE_COLOR = (255, 255, 102) # Light Yellow
MENU_OPTION_COLOR = WHITE
MENU_OPTION_SELECTED_COLOR = (255, 100, 100) # Light Red
SCORE_COLOR = (255, 215, 0) # Gold

# Sound Paths (place your .wav or .ogg files here)
SOUNDS = {
    "clear": "assets/sounds/clear.wav",
    "drop": "assets/sounds/drop.wav",
    "hard_drop": "assets/sounds/hard_drop.wav",
    "rotate": "assets/sounds/rotate.wav",
    "combo": "assets/sounds/combo.wav",
    "powerup": "assets/sounds/powerup.wav",
    "game_over": "assets/sounds/game_over.wav",
    "music_slow": "assets/sounds/music_slow.ogg",
    "music_fast": "assets/sounds/music_fast.ogg"
}

# Highscore file
HIGHSCORE_FILE = "highscore.txt"
STATS_FILE = "user_stats.json"
CONFIG_FILE = "user_config.json"

# Power-up types and colors
POWERUP_TYPES = [
    'col_clear',    # Limpia columna
    'slow_time',    # Ralentiza el tiempo
    'bomb'          # Bomba 3x3
]
POWERUP_COLORS = {
    'col_clear': (255, 215, 0),   # Dorado
    'slow_time': (0, 255, 255),  # Cyan
    'bomb': (255, 80, 80)        # Rojo claro
}

# Temas visuales
THEMES = {
    'clasico': {
        'background': (128, 128, 128),
        'grid': (255, 255, 255),
        'piece_colors': SHAPE_COLORS,
        'ghost': (120, 220, 255),
    },
    'oscuro': {
        'background': (30, 30, 30),
        'grid': (80, 80, 80),
        'piece_colors': {
            'I': (0, 255, 255),
            'O': (255, 255, 100),
            'T': (200, 0, 200),
            'S': (0, 255, 100),
            'Z': (255, 80, 80),
            'J': (80, 80, 255),
            'L': (255, 180, 80)
        },
        'ghost': (80, 180, 255),
    },
    'neon': {
        'background': (10, 10, 30),
        'grid': (0, 255, 255),
        'piece_colors': {
            'I': (0, 255, 255),
            'O': (255, 255, 0),
            'T': (255, 0, 255),
            'S': (0, 255, 0),
            'Z': (255, 0, 0),
            'J': (0, 0, 255),
            'L': (255, 128, 0)
        },
        'ghost': (255, 255, 255),
    },
    'retro': {
        'background': (245, 222, 179),
        'grid': (139, 69, 19),
        'piece_colors': {
            'I': (0, 128, 128),
            'O': (255, 215, 0),
            'T': (128, 0, 128),
            'S': (85, 107, 47),
            'Z': (178, 34, 34),
            'J': (25, 25, 112),
            'L': (210, 105, 30)
        },
        'ghost': (139, 69, 19),
    }
}
THEME_LIST = list(THEMES.keys())
DEFAULT_THEME = 'clasico' 