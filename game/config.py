WW = 640
WH = 480
TILESIZE = 32
FPS = 60

PLAYER_LAYER = 4
ENEMY_LAYER = 3
BLOCK_LAYER = 2
GROUND_LAYER = 1
PLAYER_SPEED = 3
ENEMY_SPEED = 4

RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHTGREY = (150, 150, 150)
WHITE = (255, 255, 255)

level1_wave1_enemies = [(3, 2), (16, 12)]  # List of (x, y) coordinates for enemies
level1_wave2_enemies = [(5, 3), (15, 7), (10, 10)]
level1_wave3_enemies = [(2, 2), (17, 2), (2, 12)]
level1_wave4_enemies = [(5, 5), (15, 5), (5, 10), (15, 10)]
level1_wave5_enemies = [(3, 3), (16, 3), (3, 12), (16, 12)]

# Define wave maps for level 2
level2_wave1_enemies = [(5, 3), (15, 7)]
# Add more waves for level 2...

# Group waves by level
level_waves = {
    1: [level1_wave1_enemies, level1_wave2_enemies, level1_wave3_enemies, level1_wave4_enemies, level1_wave5_enemies],
    2: [level2_wave1_enemies]  # Add more waves for level 2
}

level1_map = [
    'BBBBBBBBBBBBBBBBBBBB',
    'B..E...............B',
    'B..................B',
    'B....BBB...........B',
    'B..................B',
    'B........P.........B',
    'B..................B',
    'B..................B',
    'B.....BBB..........B',
    'B.......B..........B',
    'B.......B.....E....B',
    'B..................B',
    'B..................B',
    'B..................B',
    'BBBBBBBBBBBBBBBBBBBB',

]


level2_map = [
    'BBBBBBBBBBBBBBBBBBBB',
    'B..................B',
    'B..BBB.............B',
    'B.........E........B',
    'B........P.........B',
    'B..................B',
    'B.........E........B',
    'B..................B',
    'B..................B',
    'BBBBBBBBBBBBBBBBBBBB'
]