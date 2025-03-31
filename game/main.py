import pygame, sys
from config import *
from sprites import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WW, WH))
        self.clock = pygame.time.Clock()
        self.running = True

        self.character_spritesheet = Spritesheet('img/warrior still.PNG')
        self.terrain_spritesheet = Spritesheet('img/32rogues/tiles.png')
        self.enemy_spritesheet = Spritesheet('img/32rogues/monsters.png')

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
        pass

    def get_grid(self):
        grid_width = WW // TILESIZE
        grid_height = WH // TILESIZE
        grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
        for block in self.blocks:
            grid[block.world_y // TILESIZE][block.world_x // TILESIZE] = 1
        return grid

#does it all
g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()
    g.game_over()

pygame.quit()
sys.exit()