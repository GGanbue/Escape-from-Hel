# Configuration file for game settings, map generation, and level designs

import random

# Game window and display settings
WW = 1280
WH = 720
TILESIZE = 32
FPS = 60

# Layer settings for sprite rendering order and speed settings
PLAYER_LAYER = 4
ENEMY_LAYER = 3
BLOCK_LAYER = 2
GROUND_LAYER = 1
PLAYER_SPEED = 3
ENEMY_SPEED = 4

# Color definitions (RGB format)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHTGREY = (150, 150, 150)
WHITE = (255, 255, 255)


def generate_shaped_map(width, height, shape_type='rectangle'): # Function to procedurally generate a game map with specified shape and obstacles
    map = [['B' for _ in range(width)] for _ in range(height)]

    # Create the main playable area based on shape_type
    if shape_type == 'rectangle':
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                map[y][x] = '.'

    elif shape_type == 'circle':
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 1

        for y in range(height):
            for x in range(width):
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5

                if distance < radius:
                    map[y][x] = '.'

    num_shapes = random.randint(3, 7)

    # Add random block shapes within the playable area
    for _ in range(num_shapes):
        attempts = 0
        while attempts < 100:
            start_x = random.randint(5, width - 6)
            start_y = random.randint(5, height - 6)
            if map[start_y][start_x] == '.':
                break
            attempts += 1

        if attempts >= 100:
            continue

        # Chooses a random shape size
        shape_size = random.randint(10, 20)
        blocks_placed = 0
        blocks = [(start_x, start_y)]

        while blocks_placed < shape_size and blocks:
            x, y = blocks.pop(0)
            if map[y][x] == '.':
                map[y][x] = 'B'
                blocks_placed += 1

                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                random.shuffle(directions)

                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if (0 < nx < width - 1 and 0 < ny < height - 1 and
                            map[ny][nx] == '.' and
                            random.random() < 0.7):
                        blocks.append((nx, ny))

    px, py = width // 2, height // 2
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            ny, nx = py + dy, px + dx
            if 0 <= ny < height and 0 <= nx < width:
                map[ny][nx] = '.'

    map[py][px] = 'P'

    return [''.join(row) for row in map]

# Define enemy spawn positions for different levels and waves
level_waves = {
    1: {
        4: [
            (5, 5), (10, 5), (15, 5),
            (5, 10), (15, 10),
            (10, 12)
        ]
    },
    2: {
        4: [
            (5, 5), (10, 5), (15, 5),
            (5, 10), (15, 10),
            (10, 3), (10, 12)
        ]
    },
    3: {
        4: [
            (6, 6), (12, 6), (18, 6),
            (6, 10), (18, 10),
            (12, 3), (12, 12)
        ]
    },
    4: {
        4: [
            (5, 5), (10, 5), (15, 5),
            (5, 10), (15, 10),
            (10, 3), (10, 12),
            (3, 8), (18, 8)
        ]
    },
    5: {
        4: [
            (5, 5), (10, 5), (15, 5),
            (5, 10), (15, 10),
            (10, 3), (10, 12),
            (3, 8), (18, 8),
            (8, 8), (12, 8)
        ]
    }
}




# Predefined map layout for level X boss fight
level1_boss_map = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B...........P................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
]

level2_boss_map = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    'B............................B',
    'B............................B',
    'B.......BBBB......BBBB.......B',
    'B............................B',
    'B............................B',
    'B...........P................B',
    'B............................B',
    'B............................B',
    'B.......BBBB......BBBB.......B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
]

level3_boss_map = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    'B............................B',
    'B............................B',
    'B....BB................BB....B',
    'B...B..B..............B..B...B',
    'B...B..B..............B..B...B',
    'B...B..B......P.......B..B...B',
    'B...B..B..............B..B...B',
    'B...B..B..............B..B...B',
    'B....BB................BB....B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
]

level4_boss_map = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    'B............................B',
    'B............................B',
    'B...BBBBBB........BBBBBB.....B',
    'B...B.................B......B',
    'B...B.................B......B',
    'B...B........P........B......B',
    'B...B.................B......B',
    'B...B.................B......B',
    'B...BBBBBB........BBBBBB.....B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
]

level5_boss_map = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    'B............................B',
    'B............................B',
    'B............................B',
    'B......BBBBBBBBBBBBBB........B',
    'B............................B',
    'B.............P..............B',
    'B......B.....................B',
    'B......BBBBBBBBBBBBBB........B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'B............................B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
]
