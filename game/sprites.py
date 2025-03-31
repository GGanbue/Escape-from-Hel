import pygame, math, random
from config import *
from pathfinding import astar_pathfinding

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0,0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return sprite

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):

        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.world_x = x * TILESIZE
        self.world_y = y * TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.facing = 'left'

        self.rect = pygame.Rect(self.world_x, self.world_y, TILESIZE, TILESIZE)

        self.image = self.game.character_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)

    def update(self):
        self.movement()
        self.collide_pe()

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')

        self.x_change = 0
        self.y_change = 0

    def movement(self):
        keys = pygame.key.get_pressed()
        new_horizontal_facing = self.facing

        if keys[pygame.K_a]:
            self.world_x -= PLAYER_SPEED
            new_horizontal_facing = 'left'
        if keys[pygame.K_d]:
            self.world_x += PLAYER_SPEED
            new_horizontal_facing = 'right'
        if keys[pygame.K_w]:
            self.world_y -= PLAYER_SPEED
        if keys[pygame.K_s]:
            self.world_y += PLAYER_SPEED

        if new_horizontal_facing != self.facing:
            self.image = pygame.transform.flip(self.image, True, False)
            self.facing = new_horizontal_facing

        self.game.camera_offset_x = self.world_x - WW // 2 + TILESIZE // 2
        self.game.camera_offset_y = self.world_y - WH // 2 + TILESIZE // 2

        self.rect.x = WW // 2 - TILESIZE // 2
        self.rect.y = WH // 2 - TILESIZE // 2

    def collide_blocks(self, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                 if self.x_change > 0:
                     self.rect.x = hits[0].rect.left - self.rect.width
                 if self.x_change < 0:
                     self.rect.x = hits[0].rect.right

        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom

    def collide_pe(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            self.kill()
            self.game.playing = False


class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.world_x = x * TILESIZE
        self.world_y = y * TILESIZE

        self.rect = pygame.Rect(self.world_x, self.world_y, TILESIZE, TILESIZE)

        self.image = self.game.terrain_spritesheet.get_sprite(0, 32, TILESIZE, TILESIZE)


class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.world_x = x * TILESIZE
        self.world_y = y * TILESIZE

        self.rect = pygame.Rect(self.world_x, self.world_y, TILESIZE, TILESIZE)

        self.image = self.game.terrain_spritesheet.get_sprite(0, 192, TILESIZE, TILESIZE)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.world_x = x * TILESIZE
        self.world_y = y * TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.facing = 'left'

        self.rect = pygame.Rect(self.world_x, self.world_y, TILESIZE, TILESIZE)

        self.image = self.game.enemy_spritesheet.get_sprite(64, 0, TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK)


    def update(self):
        self.movement()

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')

        self.x_change = 0
        self.y_change = 0

    def movement(self):
        enemy_pos = (int(self.world_x // TILESIZE), int(self.world_y // TILESIZE))
        player_pos = (int(self.game.player.world_x // TILESIZE), int(self.game.player.world_y // TILESIZE))

        grid = self.game.get_grid()

        path = astar_pathfinding(enemy_pos, player_pos, grid)

        if path:
            next_tile = path[0]
            next_x, next_y = next_tile[0] * TILESIZE, next_tile[1] * TILESIZE

            dx = next_x - self.world_x
            dy = next_y - self.world_y

            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance < TILESIZE / 4:
                return

            if distance != 0:
                dx /= distance
                dy /= distance

                self.world_x += dx * ENEMY_SPEED
                self.world_y += dy * ENEMY_SPEED

                if dx < 0 and self.facing != 'left':
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.facing = 'left'
                elif dx > 0 and self.facing != 'right':
                    self.image = pygame.transform.flip(self.image, False, False)

        for enemy in self.game.enemies:
            if enemy == self:
                continue

            enemy_dx = enemy.world_x - self.world_x
            enemy_dy = enemy.world_y - self.world_y
            distance_to_enemy = (enemy_dx ** 2 + enemy_dy ** 2) ** 0.5

            MIN_DISTANCE = TILESIZE / 2
            if distance_to_enemy < MIN_DISTANCE and distance_to_enemy != 0:
                enemy_dx /= distance_to_enemy
                enemy_dy /= distance_to_enemy

                REPULSION_FORCE = 1
                self.world_x -= enemy_dx * REPULSION_FORCE + 5
                self.world_y -= enemy_dy * REPULSION_FORCE


    def collide_blocks(self, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right

        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom

