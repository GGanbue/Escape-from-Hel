import pygame, sys, random
from config import *
from sprites import *


class Game:
    def __init__(self, game_state=None):
        pygame.init()
        self.screen = pygame.display.set_mode((WW, WH))
        self.clock = pygame.time.Clock()
        self.running = True
        pygame.display.set_caption("Escape from Maldo")
        if game_state is None:
            self.game_state = GameState()
        else:
            self.game_state = game_state
        self.character_spritesheet = Spritesheet('img/32rogues/rogues.png')
        self.terrain_spritesheet = Spritesheet('img/32rogues/tiles.png')
        self.enemy_spritesheet = Spritesheet('img/32rogues/monsters.png')
        self.item_spritesheet = Spritesheet('img/32rogues/items.png')
        self.fireball = Spritesheet('img/shot_fireball.png')

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

        self.title_screen = TitleScreen(self)
        self.game_over_screen = GameOverScreen(self)
        pygame.mixer.init()
        self.ui = UI(self)
        self.gold = 0
        self.wave = 1

    def createTilemap(self, tilemap=None):
        if tilemap is None:
            tilemap = level1_map
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                Ground(self, j, i, self.ground_textures.get(self.current_level, self.ground_textures[1]))
                if column == 'B':
                    Block(self, j, i, self.block_textures.get(self.current_level, self.block_textures[1]))
                if column == 'P':
                    self.player = Player(self, j, i)

    def new(self):
        if hasattr(self, 'all_sprites'):
            for sprite in self.all_sprites:
                sprite.kill()
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()

        self.load_level(self.game_state.current_level)

    def load_level(self, level_number):
        self.current_level = level_number

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

        self.game_state.current_level = level_number
        if level_number > self.game_state.max_level_reached:
            self.game_state.max_level_reached = level_number

    def spawn_wave(self, level, wave):
        for enemy in self.enemies:
            enemy.kill()

        if wave == 5:
            boss_x = 15
            boss_y = 8
            boss_texture = self.boss_textures.get(level, self.boss_textures[1])

            boss = Enemy(self, boss_x, boss_y, boss_texture)
            boss.max_health = 300
            boss.health = boss.max_health
        else:
            enemy_texture = self.enemy_textures.get(level, self.enemy_textures[1])
            num_enemies = 4 + wave
            for _ in range(num_enemies):
                valid_pos = self.find_valid_position()
                if valid_pos:
                    Enemy(self, valid_pos[0], valid_pos[1], enemy_texture)

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
        if len(self.enemies) == 0 and self.playing:
            if self.game_state.current_wave < self.game_state.max_waves_per_level.get(self.game_state.current_level, 1):
                next_wave = self.game_state.current_wave + 1

                if next_wave == 5:
                    self.game_state.current_wave = next_wave
                    self.load_level(self.game_state.current_level)
                else:
                    self.game_state.current_wave = next_wave
                    self.spawn_wave(self.game_state.current_level, self.game_state.current_wave)
            else:
                self.game_state.current_level += 1
                self.game_state.current_wave = 1
                self.load_level(self.game_state.current_level)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.player.attack()

    def update(self):
        self.all_sprites.update()
        self.camera_offset_x = self.player.world_x - WW // 2 + TILESIZE // 2
        self.camera_offset_y = self.player.world_y - WH // 2 + TILESIZE // 2
        for sprite in self.all_sprites:
            sprite.rect.x = sprite.world_x - self.camera_offset_x
            sprite.rect.y = sprite.world_y - self.camera_offset_y
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


class TitleScreen:
    def __init__(self, game):
        self.game = game
        self.running = True
        self.font = pygame.font.Font(None, 74)
        self.menu_font = pygame.font.Font(None, 36)
        self.selected_option = 0
        self.options = ["Start Game", "Options", "Quit"]
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
        if self.options[self.selected_option] == "Start Game":
            self.running = False
        elif self.options[self.selected_option] == "Options":
            print("Options menu (to be implemented)")
        elif self.options[self.selected_option] == "Quit":
            self.running = False
            self.game.running = False

    def draw(self):
        self.game.screen.fill((0, 0, 0))

        title_text = self.font.render("Escape from Maldo Goblin", True, (255, 255, 255))
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