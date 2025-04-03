import pygame, sys, random
from config import *
from sprites import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WW, WH))
        self.clock = pygame.time.Clock()
        self.running = True
        pygame.display.set_caption("Escape from Maldo")

        self.character_spritesheet = Spritesheet('img/warrior still.PNG')
        self.terrain_spritesheet = Spritesheet('img/32rogues/tiles.png')
        self.enemy_spritesheet = Spritesheet('img/32rogues/monsters.png')

        self.title_screen = TitleScreen(self)

    def createTilemap(self):
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                Ground(self, j, i)
                if column == 'B':
                    Block(self, j, i)
                if column == "E":
                    Enemy(self, j, i)
                if column == 'P':
                    self.player = Player(self, j, i)


    def new(self):
        #new game start
        self.playing = True

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()

        self.createTilemap()

    def events(self):
        #game loop events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def update(self):
        #game loop updates
        self.all_sprites.update()
        self.camera_offset_x = self.player.world_x - WW // 2 + TILESIZE // 2
        self.camera_offset_y = self.player.world_y - WH // 2 + TILESIZE // 2
        for sprite in self.all_sprites:
            sprite.rect.x = sprite.world_x - self.camera_offset_x
            sprite.rect.y = sprite.world_y - self.camera_offset_y

    def draw(self):
        #game loop draw
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.clock.tick(FPS)
        pygame.display.update()

    def main(self):
        #game loop
        while self.playing:
            self.events()
            self.update()
            self.draw()
        self.running = False

    def game_over(self):
        pass

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
                self.game_over()


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

        title_text = self.font.render("Escape from Hel", True, (255, 255, 255))
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
    g = Game()
    g.run()
    pygame.quit()
    sys.exit()