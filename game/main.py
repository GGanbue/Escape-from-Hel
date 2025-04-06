import pygame, sys, random
from config import *
from sprites import *
from items import initialize_items


class Game:
    def __init__(self, game_state=None):
        pygame.init()
        self.screen = pygame.display.set_mode((WW, WH))
        self.clock = pygame.time.Clock()
        self.running = True
        pygame.display.set_caption("Escape from Hel")
        if game_state is None:
            self.game_state = GameState()
        else:
            self.game_state = game_state
        self.character_spritesheet = Spritesheet('img/32rogues/rogues.png')
        self.terrain_spritesheet = Spritesheet('img/32rogues/tiles.png')
        self.enemy_spritesheet = Spritesheet('img/32rogues/monsters.png')
        self.item_spritesheet = Spritesheet('img/32rogues/items.png')
        self.alt_item_spritesheet = Spritesheet('img/32rogues/items-palette-swaps.png')
        self.fireball = Spritesheet('img/shot_fireball.png')
        self.dagger = Spritesheet('rogue_skill4_frame4.png')
        self.sword_swing = Spritesheet('rogue_skill2_frame2.png')

        self.block_textures = {
            1: self.terrain_spritesheet.get_sprite(0, 32, TILESIZE, TILESIZE),
            2: self.terrain_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE),
            3: self.terrain_spritesheet.get_sprite(0, 128, TILESIZE, TILESIZE),
            4: self.terrain_spritesheet.get_sprite(96, 608, TILESIZE, TILESIZE),
            5: self.terrain_spritesheet.get_sprite(0, 96, TILESIZE, TILESIZE)
        }

        self.enemy_textures = {
            1: self.enemy_spritesheet.get_sprite(64, 0, TILESIZE, TILESIZE),
            2: self.enemy_spritesheet.get_sprite(0, 32, TILESIZE, TILESIZE),
            3: self.enemy_spritesheet.get_sprite(224, 192, TILESIZE, TILESIZE),
            4: self.enemy_spritesheet.get_sprite(0, 320, TILESIZE, TILESIZE),
            5: self.enemy_spritesheet.get_sprite(96, 128, TILESIZE, TILESIZE)
        }

        self.ground_textures = {
            1: self.terrain_spritesheet.get_sprite(0, 192, TILESIZE, TILESIZE),
            2: self.terrain_spritesheet.get_sprite(0, 480, TILESIZE, TILESIZE),
            3: self.terrain_spritesheet.get_sprite(0, 352, TILESIZE, TILESIZE),
            4: self.terrain_spritesheet.get_sprite(0, 416, TILESIZE, TILESIZE),
            5: self.terrain_spritesheet.get_sprite(500, 320, TILESIZE, TILESIZE)
        }

        self.boss_textures = {
            1: self.enemy_spritesheet.get_sprite(128, 0, TILESIZE, TILESIZE),
            2: self.enemy_spritesheet.get_sprite(64, 32, TILESIZE, TILESIZE),
            3: self.enemy_spritesheet.get_sprite(128, 192, TILESIZE, TILESIZE),
            4: self.enemy_spritesheet.get_sprite(32, 320, TILESIZE, TILESIZE),
            5: self.enemy_spritesheet.get_sprite(0, 352, TILESIZE, TILESIZE)
        }

        self.weapon_textures = {
            'mage': self.fireball,
            'warrior': self.item_spritesheet.get_sprite(32, 96, 32, 32),
            'rogue': self.item_spritesheet.get_sprite(32, 0, 32, 32)  # Adjust coordinates to match your dagger sprite
        }

        self.warrior_attack_sprite = pygame.image.load("rogue_skill2_frame2.png").convert_alpha()
        self.rogue_attack_sprite = pygame.image.load("rogue_skill4_frame4.png").convert_alpha()
        self.mage_attack_sprite = pygame.image.load("img/shot_fireball.png").convert_alpha()


        self.title_screen = TitleScreen(self)
        self.game_over_screen = GameOverScreen(self)
        pygame.mixer.init()
        self.ui = UI(self)
        self.gold = 0
        self.wave = 1
        self.weapons, self.armors = initialize_items(self)

        self.wave_complete_timer = 0
        self.wave_complete_delay = 0
        self.wave_transition_pending = False
        self.next_wave = 0

        self.direct_notification = None
        self.direct_notification_time = 0
        self.direct_notification_duration = 0

    def createTilemap(self, tilemap=None):
        if tilemap is None:
            tilemap = level1_map
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                Ground(self, j, i, self.ground_textures.get(self.current_level, self.ground_textures[1]))
                if column == 'B':
                    Block(self, j, i, self.block_textures.get(self.current_level, self.block_textures[1]))
                if column == 'P':
                    self.player = Player(self, j, i, self.player_class)

    def set_direct_notification(self, text, duration=5000):
        self.direct_notification = text
        self.direct_notification_time = pygame.time.get_ticks()
        self.direct_notification_duration = duration

    def draw_direct_notification(self, surface):
        if self.direct_notification:
            current_time = pygame.time.get_ticks()
            if current_time - self.direct_notification_time < self.direct_notification_duration:
                font = pygame.font.Font(None, 36)
                text_surf = font.render(self.direct_notification, True, (255, 255, 0))
                text_rect = text_surf.get_rect(center=(surface.get_width() // 2, 100))

                surface.blit(text_surf, text_rect)
            else:
                self.direct_notification = None

    def new(self):
        if hasattr(self, 'all_sprites'):
            for sprite in self.all_sprites:
                sprite.kill()
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()

        self.player = Player(self, WW // 2, WH // 2, self.player_class)

        self.load_level(self.game_state.current_level)

    def load_level(self, level_number):
        self.current_level = level_number
        if hasattr(self, 'player'):
            old_inventory = self.player.inventory.copy()
            old_equipped_weapon = self.player.equipped_weapon
            old_equipped_armor = self.player.equipped_armor
        else:
            old_inventory = []
            old_equipped_weapon = None
            old_equipped_armor = None

        if hasattr(self, 'all_sprites'):
            for sprite in self.all_sprites:
                sprite.kill()

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()

        if self.game_state.current_wave == 5:
            if level_number == 1:
                self.createTilemap(level1_boss_map)
            elif level_number == 2:
                self.createTilemap(level2_boss_map)
            elif level_number == 3:
                self.createTilemap(level3_boss_map)
            elif level_number == 4:
                self.createTilemap(level4_boss_map)
            elif level_number == 5:
                self.createTilemap(level5_boss_map)
            else:
                self.createTilemap(level1_boss_map)
        else:
            shape_types = ['rectangle', 'circle']
            random_shape = random.choice(shape_types)
            random_map = generate_shaped_map(40, 30, shape_type=random_shape)
            self.createTilemap(random_map)

        if level_number == 1:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('Macky Gee - Obsessive.mp3')
            pygame.mixer.music.play(-1, 37)
        elif level_number == 2:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('Macky Gee - Moments.mp3')
            pygame.mixer.music.play(-1, 60)
        elif level_number == 3:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('Macky Gee - Tour.mp3')
            pygame.mixer.music.play(-1, 61)
        elif level_number == 4:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('Macky Gee Ft. Stuart Rowe - Aftershock.mp3')
            pygame.mixer.music.play(-1, 170)
        elif level_number == 5:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('Nettspend - Nothing Like U (Official Music Video).mp3')
            pygame.mixer.music.play(-1, 0)
        else:
            level_number == 1

        self.spawn_wave(level_number, self.game_state.current_wave)

        self.game_state.current_levels = level_number
        if level_number > self.game_state.max_level_reached:
            self.game_state.max_level_reached = level_number

        if hasattr(self, 'player'):
            self.player.inventory = old_inventory
            self.player.equipped_weapon = old_equipped_weapon
            self.player.equipped_armor = old_equipped_armor

            if self.player.equipped_weapon:
                self.player.damage = self.player.damage + self.player.equipped_weapon.damage

    def spawn_wave(self, level, wave):
        for enemy in self.enemies:
            enemy.kill()

        player_level = self.game_state.player_level

        if wave == 5:
            boss_x = 15
            boss_y = 8
            boss_texture = self.boss_textures.get(level, self.boss_textures[1])
            boss_level = min(50,player_level + 5)

            boss = Enemy(self, boss_x, boss_y, boss_texture, level=boss_level)
            boss.max_health = 500 + (level * 70)
            boss.health = boss.max_health
            boss.damage = 20
            boss.damage = int(boss.damage * (1 + (boss.level * 0.15)))
            boss.max_speed = ENEMY_SPEED * 1.5
        else:
            enemy_texture = self.enemy_textures.get(level, self.enemy_textures[1])
            num_enemies = 4 + wave
            enemy_level = wave * level + int(player_level / 2)
            for _ in range(num_enemies):
                valid_pos = self.find_valid_position()
                if valid_pos:
                    Enemy(self, valid_pos[0], valid_pos[1], enemy_texture, level=enemy_level)

        self.game_state.current_wave = wave
        self.ui.wave = wave

    def is_valid_position(self, x, y):
        if x < 0 or x >= 40 or y < 0 or y >= 30:
            return False

        for block in self.blocks:
            block_x = block.world_x // TILESIZE
            block_y = block.world_y // TILESIZE
            if x == block_x and y == block_y:
                return False

        player_x = self.player.world_x // TILESIZE
        player_y = self.player.world_y // TILESIZE
        if abs(x - player_x) < 3 and abs(y - player_y) < 3:
            return False

        return True

    def find_valid_position(self, start_x=None, start_y=None):
        center_x = 20
        center_y = 15
        radius = min(40, 30) // 2 - 3

        if start_x is None or start_y is None:
            for _ in range(100):
                angle = random.uniform(0, 2 * 3.14159)
                distance = random.uniform(0, radius)
                x = int(center_x + distance * math.cos(angle))
                y = int(center_y + distance * math.sin(angle))

                if self.is_valid_position(x, y):
                    return (x, y)
        else:
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    x = start_x + dx
                    y = start_y + dy

                    distance_from_center = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                    if distance_from_center < radius and self.is_valid_position(x, y):
                        return (x, y)

        return None

    def check_wave_complete(self):
        if len(self.enemies) == 0 and self.playing and not self.wave_transition_pending:
            self.wave_transition_pending = True

            if self.game_state.current_wave < self.game_state.max_waves_per_level.get(self.game_state.current_level, 5):
                self.next_wave = self.game_state.current_wave + 1

                if self.next_wave == 5:
                    self.wave_complete_delay = 3000
                else:
                    self.wave_complete_delay = 3000
            else:
                self.next_wave = 1
                self.wave_complete_delay = 5000

            self.wave_complete_timer = pygame.time.get_ticks()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.player.attack()

    def pause_game(self):
        pause_menu = PauseMenu(self)
        pause_menu.run()
        if hasattr(pause_menu, 'open_inventory') and pause_menu.open_inventory:
            from items import InventoryScreen
            inventory_screen = InventoryScreen(self)
            inventory_screen.run()

    def update(self):
        self.all_sprites.update()
        self.camera_offset_x = self.player.world_x - WW // 2 + TILESIZE // 2
        self.camera_offset_y = self.player.world_y - WH // 2 + TILESIZE // 2
        for sprite in self.all_sprites:
            sprite.rect.x = sprite.world_x - self.camera_offset_x
            sprite.rect.y = sprite.world_y - self.camera_offset_y

        if self.wave_transition_pending:
            current_time = pygame.time.get_ticks()
            if current_time - self.wave_complete_timer >= self.wave_complete_delay:
                self.wave_transition_pending = False

                if self.next_wave == 1:
                    self.game_state.current_level += 1
                    self.game_state.current_wave = 1
                    self.load_level(self.game_state.current_level)
                elif self.next_wave == 5:
                    self.game_state.current_wave = self.next_wave
                    self.load_level(self.game_state.current_level)
                else:
                    self.game_state.current_wave = self.next_wave
                    self.spawn_wave(self.game_state.current_level, self.game_state.current_wave)

        self.check_wave_complete()

    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw_health_bar(self.screen)
        self.player.draw_health_bar(self.screen)
        for attack in self.attacks:
            self.screen.blit(attack.image, attack.rect)
        self.ui.gold = self.gold
        self.ui.wave = self.game_state.current_wave
        self.ui.draw(self.screen)
        self.draw_direct_notification(self.screen)
        self.clock.tick(FPS)
        pygame.display.update()

    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def game_over(self):
        self.game_over_screen.run()

    def intro_screen(self):
        self.title_screen.run()

    def get_grid(self):
        grid = [[0] * (WW // TILESIZE) for _ in range(WH // TILESIZE)]

        for block in self.blocks:
            grid_x = int(block.world_x // TILESIZE)
            grid_y = int(block.world_y // TILESIZE)
            if 0 <= grid_y < len(grid) and 0 <= grid_x < len(grid[0]):
                grid[grid_y][grid_x] = 1
        return grid

    def run(self):
        self.intro_screen()
        if self.running:
            self.new()
            while self.running:
                self.main()
                if not self.playing and self.running:
                    self.game_over()


class GameState:
    def __init__(self):
        self.current_level = 1
        self.current_wave = 1
        self.max_waves_per_level = {1: 5, 2: 5, 3: 5, 4: 5, 5: 5}
        self.gold = 0
        self.max_level_reached = 1

        # Player leveling attributes
        self.player_level = 1
        self.player_exp = 0
        self.available_points = 0
        self.health_points = 0
        self.stamina_points = 0
        self.damage_points = 0


class PauseMenu:
    def __init__(self, game):
        self.game = game
        self.running = True
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.selected_option = 0
        self.options = ["Health", "Stamina", "Damage", "Inventory", "Resume Game"]
        self.option_rects = []
        self.open_inventory = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.select_option()
                elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    self.adjust_stat(event.key)

    def adjust_stat(self, key):
        if self.game.game_state.available_points <= 0 and key == pygame.K_RIGHT:
            return  # No points to spend

        if self.selected_option == 0:  # Health
            if key == pygame.K_RIGHT:
                self.game.game_state.health_points += 1
                self.game.game_state.available_points -= 1
                self.game.player.max_health += 10
                self.game.player.health += 10
            elif key == pygame.K_LEFT and self.game.game_state.health_points > 0:
                self.game.game_state.health_points -= 1
                self.game.game_state.available_points += 1
                self.game.player.max_health -= 10
                self.game.player.health = min(self.game.player.health, self.game.player.max_health)

        elif self.selected_option == 1:  # Stamina
            if key == pygame.K_RIGHT:
                self.game.game_state.stamina_points += 1
                self.game.game_state.available_points -= 1
                self.game.player.max_stamina += 5
            elif key == pygame.K_LEFT and self.game.game_state.stamina_points > 0:
                self.game.game_state.stamina_points -= 1
                self.game.game_state.available_points += 1
                self.game.player.max_stamina -= 5
                self.game.player.stamina = min(self.game.player.stamina, self.game.player.max_stamina)

        elif self.selected_option == 2:  # Damage
            if key == pygame.K_RIGHT:
                self.game.game_state.damage_points += 1
                self.game.game_state.available_points -= 1
                self.game.player.damage += 2
            elif key == pygame.K_LEFT and self.game.game_state.damage_points > 0:
                self.game.game_state.damage_points -= 1
                self.game.game_state.available_points += 1
                self.game.player.damage -= 2

    def select_option(self):
        if self.options[self.selected_option] == "Resume Game":
            self.running = False
        elif self.options[self.selected_option] == "Inventory":
            self.open_inventory = True
            self.running = False

    def draw(self):
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WW, WH))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.game.screen.blit(overlay, (0, 0))

        # Draw title
        title_text = self.title_font.render("Character Stats", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WW // 2, 80))
        self.game.screen.blit(title_text, title_rect)

        # Draw player level and points
        level_text = self.font.render(f"Level: {self.game.game_state.player_level}", True, (255, 255, 255))
        self.game.screen.blit(level_text, (WW // 2 - 150, 130))

        exp_text = self.font.render(f"EXP: {int(self.game.player.exp)}/{int(self.game.player.exp_to_next_level)}", True,
                                    (255, 255, 255))
        self.game.screen.blit(exp_text, (WW // 2 + 50, 130))

        points_text = self.font.render(f"Available Points: {self.game.game_state.available_points}", True,
                                       (255, 215, 0))
        self.game.screen.blit(points_text, (WW // 2 - points_text.get_width() // 2, 170))

        # Draw stat options
        self.option_rects = []
        y_pos = 220
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)

            if i < 3:  # Stats options
                if i == 0:
                    value = self.game.game_state.health_points
                    effect = f"(Health: {self.game.player.max_health})"
                elif i == 1:
                    value = self.game.game_state.stamina_points
                    effect = f"(Stamina: {self.game.player.max_stamina})"
                else:
                    value = self.game.game_state.damage_points
                    effect = f"(Damage: {self.game.player.damage})"

                text = self.font.render(f"{option}: {value} {effect}", True, color)
            else:
                text = self.font.render(option, True, color)

            rect = text.get_rect(center=(WW // 2, y_pos))
            self.game.screen.blit(text, rect)
            self.option_rects.append(rect)
            y_pos += 50

        # Draw controls hint
        hint_text = self.font.render("Use ← → to adjust stats, ↑↓ to navigate", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(WW // 2, WH - 50))
        self.game.screen.blit(hint_text, hint_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()


class TitleScreen:
    def __init__(self, game):
        self.game = game
        self.running = True
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.running = False
                    # Show class selection screen after pressing enter
                    class_selection = ClassSelectionScreen(self.game)
                    class_selection.run()

    def draw(self):
        self.game.screen.fill(BLACK)

        # Draw title
        title_text = self.title_font.render("RPG Adventure", True, WHITE)
        title_rect = title_text.get_rect(center=(WW // 2, 200))
        self.game.screen.blit(title_text, title_rect)

        # Draw instructions
        instructions = self.font.render("Press ENTER to start", True, WHITE)
        instructions_rect = instructions.get_rect(center=(WW // 2, WH - 100))
        self.game.screen.blit(instructions, instructions_rect)

        pygame.display.update()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.game.clock.tick(FPS)

class ClassSelectionScreen:
    def __init__(self, game):
        self.game = game
        self.running = True
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        self.selected_class = 0
        self.classes = [
            {
                'name': 'Mage',
                'description': 'Magic user with ranged attacks and low health.',
                'stats': {'health': 100, 'damage': 20, 'stamina': 120},
                'image': None  # Will use your character spritesheet
            },
            {
                'name': 'Warrior',
                'description': 'High health melee fighter who can hit multiple enemies with axes and greatswords.',
                'stats': {'health': 150, 'damage': 15, 'stamina': 100},
                'image': None  # Will use your character spritesheet
            },
            {
                'name': 'Rogue',
                'description': 'Fast dagger-wielding fighter with high single-target damage.',
                'stats': {'health': 120, 'damage': 18, 'stamina': 110},
                'image': None  # Will use your character spritesheet
            }
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selected_class = (self.selected_class - 1) % len(self.classes)
                if event.key == pygame.K_RIGHT:
                    self.selected_class = (self.selected_class + 1) % len(self.classes)
                if event.key == pygame.K_RETURN:
                    self.game.player_class = self.classes[self.selected_class]['name'].lower()
                    self.running = False

    def draw(self):
        self.game.screen.fill(BLACK)

        title_text = self.title_font.render("Select Your Class", True, WHITE)
        title_rect = title_text.get_rect(center=(WW // 2, 100))
        self.game.screen.blit(title_text, title_rect)

        for i, class_info in enumerate(self.classes):
            box_color = BLUE if i == self.selected_class else LIGHTGREY
            box_rect = pygame.Rect(WW // 2 - 150 + (i - 1) * 300, 200, 250, 300)
            pygame.draw.rect(self.game.screen, box_color, box_rect, 0 if i == self.selected_class else 2)

            name_text = self.font.render(class_info['name'], True, WHITE)
            name_rect = name_text.get_rect(center=(box_rect.centerx, box_rect.top + 30))
            self.game.screen.blit(name_text, name_rect)

            y_offset = 80
            for stat, value in class_info['stats'].items():
                stat_text = self.font.render(f"{stat.capitalize()}: {value}", True, WHITE)
                stat_rect = stat_text.get_rect(center=(box_rect.centerx, box_rect.top + y_offset))
                self.game.screen.blit(stat_text, stat_rect)
                y_offset += 30

            words = class_info['description'].split()
            lines = []
            line = []
            for word in words:
                test_line = ' '.join(line + [word])
                if self.font.size(test_line)[0] <= 230:
                    line.append(word)
                else:
                    lines.append(' '.join(line))
                    line = [word]
            if line:
                lines.append(' '.join(line))

            for i, line in enumerate(lines):
                desc_text = self.font.render(line, True, WHITE)
                desc_rect = desc_text.get_rect(center=(box_rect.centerx, box_rect.top + 180 + i * 25))
                self.game.screen.blit(desc_text, desc_rect)

        instructions = self.font.render("Use arrow keys to select, Enter to confirm", True, WHITE)
        instructions_rect = instructions.get_rect(center=(WW // 2, WH - 100))
        self.game.screen.blit(instructions, instructions_rect)

        pygame.display.update()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.game.clock.tick(FPS)
        return self.game.player_class


class GameOverScreen:
    def __init__(self, game):
        self.game = game
        self.running = True
        self.font = pygame.font.Font(None, 74)
        self.menu_font = pygame.font.Font(None, 36)
        self.selected_option = 0
        self.options = ["Retry", "Quit"]
        self.option_rects = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.select_option()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_mouse_click(event.pos)

    def handle_mouse_click(self, pos):
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(pos):
                self.selected_option = i
                self.select_option()
                break

    def select_option(self):
        if self.options[self.selected_option] == "Retry":
            self.running = False
            self.game.running = False
            self.game.restart_requested = True
        elif self.options[self.selected_option] == "Quit":
            self.running = False
            self.game.running = False

    def draw(self):
        self.game.screen.fill((0, 0, 0))

        title_text = self.font.render("Game Over", True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(self.game.screen.get_width() // 2, 100))
        self.game.screen.blit(title_text, title_rect)

        self.option_rects = []
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            text = self.menu_font.render(option, True, color)
            rect = text.get_rect(center=(self.game.screen.get_width() // 2, 250 + i * 50))
            self.game.screen.blit(text, rect)
            self.option_rects.append(rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()


if __name__=="__main__":
    game_state = GameState()
    g = Game(game_state)
    restart = True
    while restart:
        g.run()
        if hasattr(g, 'restart_requested') and g.restart_requested:
            game_state = g.game_state
            pygame.mixer.music.stop()
            pygame.event.clear()
            del g
            g = Game(game_state)
            restart = True
        else:
            restart = False
    pygame.quit()
    sys.exit()