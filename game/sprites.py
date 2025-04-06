import pygame, math, random, numpy
import pygame.gfxdraw
from config import *
from pathfinding import astar_pathfinding
from main import Game


class Spritesheet: # Initialize a spritesheet object with the given image file
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height): # Extract a sprite from the spritesheet at the specified coordinates and dimensions
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0,0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return sprite

class Player(pygame.sprite.Sprite): # Initialize the player character with position, class type, and base attributes
    def __init__(self, game, x, y, player_class):
        super().__init__()

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

        self.player_class = 'mage'
        self.inventory = []
        self.equipped_weapon = None
        self.equipped_armor = None
        self.projectile = None

        self.player_class = player_class if player_class else 'mage'

        if self.player_class == 'warrior':
            self.max_health = 150
            self.health = self.max_health
            self.damage = 30
            self.attack_cooldown = 800
        elif self.player_class == 'mage':
            self.max_health = 80
            self.health = self.max_health
            self.damage = 15
            self.attack_cooldown = 100
        elif self.player_class == 'rogue':
            self.max_health = 100
            self.health = self.max_health
            self.damage = 40
            self.attack_cooldown = 400

        self.last_attack_time = 0

        sprite_coordinates = {
            "warrior": (0, 96),
            "mage": (32, 128),
            "rogue": (96, 0)
        }

        x, y = sprite_coordinates.get(self.player_class, (32, 128))
        self.image = self.game.character_spritesheet.get_sprite(x, y, TILESIZE, TILESIZE)

        self.level = game.game_state.player_level
        self.exp = game.game_state.player_exp
        self.exp_to_next_level = 100 * (1 + (self.level * 0.5))

        self.base_max_health = 100
        self.base_max_stamina = 100

        self.health_points = game.game_state.health_points
        self.stamina_points = game.game_state.stamina_points
        self.damage_points = game.game_state.damage_points

        self.max_health = self.base_max_health + (self.health_points * 10)
        self.health = self.max_health
        self.max_stamina = self.base_max_stamina + (self.stamina_points * 5)
        self.stamina = self.max_stamina
        self.damage = self.damage + (self.damage_points * 2)
        self.stamina_regen_rate = 20


    def gain_exp(self, amount): # Add experience points to the player and check for level up
        self.exp += amount
        if self.exp >= self.exp_to_next_level:
            self.level_up()

    def level_up(self): # Increase player level, reset exp, and grant stat points
        self.exp -= self.exp_to_next_level
        self.level += 1
        self.game.game_state.player_level = self.level
        self.game.game_state.available_points += 3
        self.exp_to_next_level = 100 * (1 + (self.level * 0.5))

        if self.exp >= self.exp_to_next_level:
            self.level_up()

    def update(self): # Update player position, handle collisions, and regenerate stamina
        self.movement()

        self.world_x += self.x_change
        self.collide_blocks('x')
        self.world_y += self.y_change
        self.collide_blocks('y')

        self.x_change = 0
        self.y_change = 0

        if self.stamina < self.max_stamina:
            self.stamina += self.stamina_regen_rate * (1 / FPS)
            if self.stamina > self.max_stamina:
                self.stamina = self.max_stamina

        if self.projectile:
            self.world_x += math.cos(self.direction) * self.speed
            self.world_y += math.sin(self.direction) * self.speed

            self.rect.centerx = self.world_x - self.game.camera_offset_x
            self.rect.centery = self.world_y - self.game.camera_offset_y

        self.game.ui.stamina = self.stamina
        self.game.ui.max_stamina = self.max_stamina

    def movement(self): # Handle player movement input and apply speed modifiers
        keys = pygame.key.get_pressed()
        new_facing = self.facing
        current_time = pygame.time.get_ticks()

        self.x_change = 0
        self.y_change = 0

        speed_multiplier = 1.0

        if keys[pygame.K_LSHIFT] and self.stamina > 5:
            speed_multiplier = 1.7
            self.stamina -= 20 * (4/FPS)
            if self.stamina < 0:
                self.stamina = 0

        if keys[pygame.K_a]:
            self.x_change = -PLAYER_SPEED * speed_multiplier
            new_facing = 'left'
        if keys[pygame.K_d]:
            self.x_change = PLAYER_SPEED * speed_multiplier
            new_facing = 'right'
        if keys[pygame.K_w]:
            self.y_change = -PLAYER_SPEED * speed_multiplier
        if keys[pygame.K_s]:
            self.y_change = PLAYER_SPEED * speed_multiplier

        if new_facing != self.facing:
            self.image = pygame.transform.flip(self.image, True, False)
            self.facing = new_facing


    def collide_blocks(self, direction): # Check for collisions with blocks and adjust player position accordingly
        temp_rect = pygame.Rect(self.world_x, self.world_y, TILESIZE, TILESIZE)

        for block in self.game.blocks:
            block_rect = pygame.Rect(block.world_x, block.world_y, TILESIZE, TILESIZE)
            if temp_rect.colliderect(block_rect):
                if direction == 'x':
                    if self.x_change > 0:
                        self.world_x = block_rect.left - TILESIZE
                    if self.x_change < 0:
                        self.world_x = block_rect.right
                    self.x_change = 0

                if direction == 'y':
                    if self.y_change > 0:
                        self.world_y = block_rect.top - TILESIZE
                    if self.y_change < 0:
                        self.world_y = block_rect.bottom
                    self.y_change = 0

    def take_damage(self, amount): # Reduce player health when damaged and check for death
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.game.playing = False

    def draw_health_bar(self, surface): # Draw a health bar above the player
        health_ratio = self.health / self.max_health
        bar_width = TILESIZE
        bar_height = 5
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 10, bar_width * health_ratio, bar_height))

    def attack(self): # Create an attack based on player class and mouse position
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time

            mouse_x, mouse_y = pygame.mouse.get_pos()

            world_mouse_x = mouse_x + self.game.camera_offset_x
            world_mouse_y = mouse_y + self.game.camera_offset_y

            dir_x = world_mouse_x - self.world_x
            dir_y = world_mouse_y - self.world_y

            length = max(1, math.sqrt(dir_x * dir_x + dir_y * dir_y))
            dir_x = dir_x / length
            dir_y = dir_y / length

            angle = math.atan2(dir_y, dir_x)


            if self.player_class == 'mage':
                attack = Attack(
                    self.game,
                    self.world_x,
                    self.world_y,
                    angle,
                    self.game.fireball,
                    "fireball",
                    self.damage,
                    projectile=True
                )

            elif self.player_class == 'warrior':
                if self.facing == 'up':
                    attack_x = self.world_x
                    attack_y = self.world_y - TILESIZE / 2
                elif self.facing == 'down':
                    attack_x = self.world_x
                    attack_y = self.world_y + TILESIZE / 2
                elif self.facing == 'left':
                    attack_x = self.world_x - TILESIZE / 2
                    attack_y = self.world_y
                elif self.facing == 'right':
                    attack_x = self.world_x + TILESIZE / 2
                    attack_y = self.world_y

                attack = Attack(
                    self.game,
                    self.world_x + dir_x * TILESIZE / 2,
                    self.world_y + dir_y * TILESIZE / 2,
                    angle,
                    self.game.sword_swing,
                    "sword_swing",
                    self.damage,
                    projectile=False,
                    aoe=True,
                    aoe_radius=TILESIZE / 1.5
                )
            elif self.player_class == 'rogue':
                attack = Attack(
                    self.game,
                    self.world_x,
                    self.world_y,
                    angle,
                    self.game.dagger,
                    "dagger",
                    self.damage,
                    projectile=False
                )
                self.last_attack_time -= self.attack_cooldown * 0.2




class Block(pygame.sprite.Sprite): # Initialize a block/wall object at the specified position
    def __init__(self, game, x, y, image=None):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.world_x = x * TILESIZE
        self.world_y = y * TILESIZE

        self.rect = pygame.Rect(self.world_x, self.world_y, TILESIZE, TILESIZE)

        if image:
            self.image = image
        else:
            self.image = self.game.terrain_spritesheet.get_sprite(0, 32, TILESIZE, TILESIZE)


class Ground(pygame.sprite.Sprite): # Initialize a ground tile at the specified position
    def __init__(self, game, x, y, image=None):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.world_x = x * TILESIZE
        self.world_y = y * TILESIZE

        self.rect = pygame.Rect(self.world_x, self.world_y, TILESIZE, TILESIZE)

        if image:
            self.image = image
        else:
            self.image = self.game.terrain_spritesheet.get_sprite(0, 192, TILESIZE, TILESIZE)


class Enemy(pygame.sprite.Sprite): # Initialize an enemy with position, image, and level-scaled attributes
    def __init__(self, game, x, y, image=None, level=None):
        super().__init__()

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

        if image:
            self.image = image
        else:
            self.image = self.game.enemy_spritesheet.get_sprite(64, 0, TILESIZE, TILESIZE)

        self.image.set_colorkey(BLACK)

        if level is None:
            self.level = min(50, game.game_state.current_wave * 2 + (game.game_state.current_level - 1) * 5)
        else:
            self.level = level

        self.gold_drop = self.level

        self.base_health = 50
        self.damage = 10
        self.max_health = int(self.base_health * (1 + (self.level * 0.15)))
        self.health = self.max_health
        self.damage = int(self.damage * (1 + (self.level * 0.1)))

        self.path = []
        self.path_index = 0
        self.path_update_time = 0
        self.path_update_delay = 1000

        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.2
        self.deceleration = 0.1
        self.max_speed = ENEMY_SPEED

    def update(self): # Update enemy position, handle collisions, and attack player on contact
        prev_x = self.world_x
        prev_y = self.world_y
        self.movement()

        self.world_x += self.x_change
        self.collide_blocks('x')
        self.collide_enemies('x')

        self.world_y += self.y_change
        self.collide_blocks('y')
        self.collide_enemies('y')

        self.detect_and_handle_corner_stuck(prev_x, prev_y)

        self.x_change = 0
        self.y_change = 0

        player_rect = pygame.Rect(self.game.player.world_x, self.game.player.world_y, TILESIZE, TILESIZE)
        enemy_rect = pygame.Rect(self.world_x, self.world_y, TILESIZE, TILESIZE)

        if enemy_rect.colliderect(player_rect):
            current_time = pygame.time.get_ticks()
            if not hasattr(self, 'last_attack_time') or current_time - self.last_attack_time > 1000:
                self.last_attack_time = current_time
                self.game.player.take_damage(self.damage)

    def detect_and_handle_corner_stuck(self, prev_x, prev_y): # Detect when enemy is stuck on corners and adjust movement to free it
        if not hasattr(self, 'stuck_count'):
            self.stuck_count = 0
            self.last_stuck_time = 0
            self.corner_adjustment_active = False
            self.corner_adjustment_direction = None
            self.corner_adjustment_time = 0

        current_time = pygame.time.get_ticks()

        actual_movement = math.sqrt((self.world_x - prev_x) ** 2 + (self.world_y - prev_y) ** 2)

        if actual_movement < 0.5 and (abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1):
            self.stuck_count += 1
        else:
            self.stuck_count = 0
            self.corner_adjustment_active = False

        if self.stuck_count > 3 and current_time - self.last_stuck_time > 300:
            self.last_stuck_time = current_time
            self.corner_adjustment_active = True
            self.corner_adjustment_time = current_time

            self.update_path()

            self.find_corner_adjustment_direction()

        if self.corner_adjustment_active:
            if current_time - self.corner_adjustment_time < 800:
                self.apply_corner_adjustment()
            else:
                self.corner_adjustment_active = False
                self.update_path()
                self.path_update_time = current_time

    def find_corner_adjustment_direction(self): # Find a valid direction to move when stuck on a corner
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        test_distance = TILESIZE * 2

        clear_directions = []

        for dx, dy in directions:
            test_x = self.world_x + dx * test_distance
            test_y = self.world_y + dy * test_distance

            if test_x < 0 or test_x >= 40 * TILESIZE or test_y < 0 or test_y >= 30 * TILESIZE:
                continue

            test_rect = pygame.Rect(test_x, test_y, TILESIZE, TILESIZE)

            clear = True
            for block in self.game.blocks:
                block_rect = pygame.Rect(block.world_x, block.world_y, TILESIZE, TILESIZE)
                if test_rect.colliderect(block_rect):
                    clear = False
                    break

            if clear:
                clear_directions.append((dx, dy))

        if clear_directions:
            current_dir = [0, 0]
            vel_magnitude = math.sqrt(self.velocity_x ** 2 + self.velocity_y ** 2)
            if vel_magnitude > 0.1:
                current_dir = [self.velocity_x / vel_magnitude, self.velocity_y / vel_magnitude]

            best_dir = None
            best_diff = -1
            for dx, dy in clear_directions:
                dir_diff = (dx - current_dir[0]) ** 2 + (dy - current_dir[1]) ** 2
                if dir_diff > best_diff:
                    best_diff = dir_diff
                    best_dir = (dx, dy)

            self.corner_adjustment_direction = best_dir
        else:
            self.corner_adjustment_direction = (-self.velocity_x, -self.velocity_y)

    def apply_corner_adjustment(self): # Apply movement adjustments to free enemy from being stuck
        if self.corner_adjustment_direction:
            dx, dy = self.corner_adjustment_direction

            adjustment_strength = 2.5

            self.world_x += dx * ENEMY_SPEED * adjustment_strength
            self.world_y += dy * ENEMY_SPEED * adjustment_strength

            self.velocity_x = dx * self.max_speed
            self.velocity_y = dy * self.max_speed

            if self.stuck_count > 10:
                valid_pos = self.game.find_valid_position(int(self.world_x // TILESIZE), int(self.world_y // TILESIZE))
                if valid_pos:
                    self.world_x = valid_pos[0] * TILESIZE
                    self.world_y = valid_pos[1] * TILESIZE
                    self.stuck_count = 0

    def movement(self): # Handle enemy movement toward player using pathfinding or direct line of sight
        current_time = pygame.time.get_ticks()

        if not hasattr(self, 'previous_positions'):
            self.previous_positions = []

        self.previous_positions.append((self.world_x, self.world_y))
        if len(self.previous_positions) > 10:
            self.previous_positions.pop(0)

        if len(self.previous_positions) == 10:
            positions_set = set([(int(x), int(y)) for x, y in self.previous_positions])
            if len(positions_set) <= 2:
                self.update_path()
                self.path_update_time = current_time

        if self.has_line_of_sight_to_player():
            dx = self.game.player.world_x - self.world_x
            dy = self.game.player.world_y - self.world_y

            distance = max(1, math.sqrt(dx * dx + dy * dy))
            target_vx = (dx / distance) * self.max_speed
            target_vy = (dy / distance) * self.max_speed
        else:
            if not self.path or current_time - self.path_update_time > self.path_update_delay:
                self.update_path()
                self.path_update_time = current_time

            target_vx = 0
            target_vy = 0

            if self.path and self.path_index < len(self.path):
                target_x, target_y = self.path[self.path_index]
                target_world_x = target_x * TILESIZE
                target_world_y = target_y * TILESIZE

                dx = target_world_x - self.world_x
                dy = target_world_y - self.world_y

                if abs(dx) < self.max_speed and abs(dy) < self.max_speed:
                    self.path_index += 1
                else:
                    distance = max(1, math.sqrt(dx * dx + dy * dy))
                    target_vx = (dx / distance) * self.max_speed
                    target_vy = (dy / distance) * self.max_speed

        if abs(target_vx - self.velocity_x) > self.acceleration:
            self.velocity_x += self.acceleration if target_vx > self.velocity_x else -self.acceleration
        else:
            self.velocity_x = target_vx

        if abs(target_vy - self.velocity_y) > self.acceleration:
            self.velocity_y += self.acceleration if target_vy > self.velocity_y else -self.acceleration
        else:
            self.velocity_y = target_vy

        if abs(self.velocity_x) < self.deceleration:
            self.velocity_x = 0
        if abs(self.velocity_y) < self.deceleration:
            self.velocity_y = 0

        self.x_change = self.velocity_x
        self.y_change = self.velocity_y

    def has_line_of_sight_to_player(self): # Check if enemy has direct line of sight to the player without obstacles
        start_x = self.world_x + TILESIZE // 2
        start_y = self.world_y + TILESIZE // 2
        end_x = self.game.player.world_x + TILESIZE // 2
        end_y = self.game.player.world_y + TILESIZE // 2

        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < TILESIZE:
            return True

        if distance > 0:
            dx /= distance
            dy /= distance

        steps = int(distance / (TILESIZE // 2))
        for i in range(1, steps):
            check_x = start_x + dx * i * (TILESIZE // 2)
            check_y = start_y + dy * i * (TILESIZE // 2)

            grid_x = int(check_x // TILESIZE)
            grid_y = int(check_y // TILESIZE)

            for block in self.game.blocks:
                block_grid_x = int(block.world_x // TILESIZE)
                block_grid_y = int(block.world_y // TILESIZE)

                if grid_x == block_grid_x and grid_y == block_grid_y:
                    return False

        return True

    def update_path(self): # Calculate a new pathfinding route to the player
        grid = self.game.get_grid()
        start = (int(self.world_x // TILESIZE), int(self.world_y // TILESIZE))
        goal = (int(self.game.player.world_x // TILESIZE), int(self.game.player.world_y // TILESIZE))

        self.path = astar_pathfinding(start, goal, grid)
        self.path_index = 0

    def collide_blocks(self, direction): # Handle collisions with blocks and adjust enemy position
        buffer = 2
        temp_rect = pygame.Rect(self.world_x, self.world_y, TILESIZE, TILESIZE)

        for block in self.game.blocks:
            block_rect = pygame.Rect(block.world_x, block.world_y, TILESIZE, TILESIZE)
            if temp_rect.colliderect(block_rect):
                if direction == 'x':
                    if self.x_change > 0:
                        self.world_x = block_rect.left - TILESIZE - buffer
                    if self.x_change < 0:
                        self.world_x = block_rect.right + buffer
                    self.x_change = 0
                    self.velocity_x = 0

                if direction == 'y':
                    if self.y_change > 0:
                        self.world_y = block_rect.top - TILESIZE - buffer
                    if self.y_change < 0:
                        self.world_y = block_rect.bottom + buffer
                    self.y_change = 0
                    self.velocity_y = 0

    def collide_enemies(self, direction): # Handle collisions with other enemies to prevent overlapping
        push_strength = 0.1
        separation_strength = 0.15
        collision_margin = TILESIZE * 0.8

        for enemy in self.game.enemies:
            if enemy != self:
                dx = self.world_x - enemy.world_x
                dy = self.world_y - enemy.world_y
                distance = math.sqrt(dx ** 2 + dy ** 2)

                if distance < collision_margin:
                    overlap = collision_margin - distance
                    if distance > 0:
                        push_x = (dx / distance) * overlap * push_strength
                        push_y = (dy / distance) * overlap * push_strength

                        self.world_x += push_x
                        self.world_y += push_y
                        enemy.world_x -= push_x
                        enemy.world_y -= push_y

                        self.x_change += (dx / distance) * separation_strength
                        self.y_change += (dy / distance) * separation_strength
                        enemy.x_change -= (dx / distance) * separation_strength
                        enemy.y_change -= (dy / distance) * separation_strength

        speed = math.sqrt(self.x_change ** 2 + self.y_change ** 2)
        if speed > ENEMY_SPEED:
            self.x_change = (self.x_change / speed) * ENEMY_SPEED
            self.y_change = (self.y_change / speed) * ENEMY_SPEED

    def take_damage(self, amount): # Reduce enemy health when damaged and handle death rewards
        was_boss = self.max_health >= 500
        self.health -= amount
        self.hit_time = pygame.time.get_ticks()

        if self.health <= 0:
            exp_reward = 50 + (self.level * 2)
            if was_boss:
                self.game.set_direct_notification("GOD SLAIN     ITEMS ADDED", 1500)
                exp_reward *= 5
                gold_drop = self.level * 5
                self.game.gold += gold_drop

                current_level = self.game.game_state.current_level
                if current_level <= 5:
                    player_class = self.game.player.player_class

                    armor_index = current_level - 1
                    if armor_index < len(self.game.armors[player_class]):
                        item = self.game.armors[player_class][armor_index]
                        self.game.player.inventory.append(item)

                    weapon_index = (current_level - 1) * 2
                    if random.random() < 0.5:
                        weapon_to_drop = weapon_index
                    else:
                        weapon_to_drop = weapon_index + 1

                    if weapon_to_drop < len(self.game.weapons[player_class]):
                        item = self.game.weapons[player_class][weapon_to_drop]
                        self.game.player.inventory.append(item)
            else:
                gold_drop = self.level
                self.game.gold += gold_drop

            self.game.player.gain_exp(exp_reward)
            self.kill()

    def draw_health_bar(self, surface): # Draw a health bar and level indicator above the enemy
        health_ratio = self.health / self.max_health
        bar_width = TILESIZE
        bar_height = 5
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 10, bar_width * health_ratio, bar_height))

        level_font = pygame.font.Font(None, 16)
        level_text = level_font.render(f"Lvl {self.level}", True, (255, 255, 255))
        surface.blit(level_text, (self.rect.x, self.rect.y - 25))


class Attack(pygame.sprite.Sprite): # Initialize an attack object with position, direction, and damage properties
    def __init__(self, game, x, y, direction, sprite_sheet, attack_type, damage, projectile=False, aoe=False,
                 aoe_radius=0):
        super().__init__()

        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.world_x = x
        self.world_y = y
        self.direction = direction
        self.attack_type = attack_type
        self.damage = damage
        self.speed = 10
        self.projectile = projectile
        self.aoe = aoe
        self.aoe_radius = aoe_radius

        if attack_type == "sword_swing":
            self.original_image = game.warrior_attack_sprite
            self.original_image.set_colorkey(BLACK)
        elif attack_type == "dagger":
            self.original_image = game.rogue_attack_sprite
            self.original_image.set_colorkey(BLACK)
        else:
            self.original_image = sprite_sheet.get_sprite(0, 0, TILESIZE, TILESIZE)
            self.original_image.set_colorkey(WHITE)



        angle_degrees = math.degrees(direction)
        self.image = pygame.transform.rotate(self.original_image, -angle_degrees)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.creation_time = pygame.time.get_ticks()
        if self.projectile:
            self.lifespan = 1000
        else:
            self.lifespan = 200

        if self.aoe:
            self.aoe_rect = pygame.Rect(0, 0, self.aoe_radius * 2, self.aoe_radius * 2)
            self.aoe_rect.center = self.rect.center

    def update(self): # Update attack position and check for collisions with enemies
        if pygame.time.get_ticks() - self.creation_time > self.lifespan:
            self.kill()
            return

        if self.projectile:
            self.world_x += math.cos(self.direction) * self.speed
            self.world_y += math.sin(self.direction) * self.speed

            screen_x = self.world_x - self.game.camera_offset_x
            screen_y = self.world_y - self.game.camera_offset_y
            self.rect.center = (screen_x, screen_y)

        hits = []
        for enemy in self.game.enemies:
            if self.aoe:
                self.aoe_rect.center = (self.world_x - self.game.camera_offset_x,
                                        self.world_y - self.game.camera_offset_y)
                if self.aoe_rect.colliderect(enemy.rect):
                    hits.append(enemy)
            else:
                if self.rect.colliderect(enemy.rect):
                    hits.append(enemy)
                    if not self.projectile:
                        break

        for enemy in hits:
            enemy.take_damage(self.damage)
            if not self.aoe and not self.projectile:
                self.kill()
                return
            elif self.projectile:
                self.kill()
                return


class UI: # Initialize the user interface with fonts and display elements
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

        self.health_color = (220, 50, 50)
        self.stamina_color = (50, 150, 220)
        self.gold_color = (255, 215, 0)
        self.ui_bg_color = (30, 30, 30, 180)

        self.item_slot = pygame.Surface((64, 64))
        self.item_slot.fill((50, 50, 50))
        pygame.draw.rect(self.item_slot, (100, 100, 100), (0, 0, 64, 64), 2)

        self.gold = 0
        self.wave = 1
        self.max_stamina = 100
        self.stamina = 100
        self.weapon = None
        self.armor = None

        self.message = ""
        self.message_timer = 0
        self.message_duration = 0

    def show_message(self, text, duration): # Display a temporary message on the screen
        self.message = text
        self.message_timer = pygame.time.get_ticks()
        self.message_duration = duration

    def draw(self, surface): # Draw all UI elements including health/stamina bars, inventory, and messages
        health_ratio = self.game.player.health / self.game.player.max_health
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = WW - health_bar_width - 20
        health_bar_y = 20

        pygame.draw.rect(surface, (0, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        pygame.draw.rect(surface, self.health_color,
                         (health_bar_x, health_bar_y, health_bar_width * health_ratio, health_bar_height))
        health_text = self.font.render(f"{int(self.game.player.health)}/{self.game.player.max_health}", True,
                                       (255, 255, 255))
        surface.blit(health_text, (health_bar_x + health_bar_width // 2 - health_text.get_width() // 2,
                                   health_bar_y + health_bar_height // 2 - health_text.get_height() // 2))

        stamina_ratio = self.stamina / self.max_stamina
        stamina_bar_width = 200
        stamina_bar_height = 10
        stamina_bar_x = health_bar_x
        stamina_bar_y = health_bar_y + health_bar_height + 5

        pygame.draw.rect(surface, (0, 0, 0), (stamina_bar_x, stamina_bar_y, stamina_bar_width, stamina_bar_height))
        pygame.draw.rect(surface, self.stamina_color,
                         (stamina_bar_x, stamina_bar_y, stamina_bar_width * stamina_ratio, stamina_bar_height))

        gold_text = self.font.render(f"Gold: {self.gold}", True, self.gold_color)
        surface.blit(gold_text, (WW - gold_text.get_width() - 20, stamina_bar_y + stamina_bar_height + 20))

        wave_text = self.font.render(f"Wave: {self.wave}", True, (255, 255, 255))
        surface.blit(wave_text, (WW // 2 - wave_text.get_width() // 2, 20))

        weapon_slot_x = WW // 2 - 70
        armor_slot_x = WW // 2 + 6
        slots_y = WH - 80

        surface.blit(self.item_slot, (weapon_slot_x, slots_y))
        weapon_text = self.small_font.render("Weapon", True, (200, 200, 200))
        surface.blit(weapon_text, (weapon_slot_x + 32 - weapon_text.get_width() // 2, slots_y + 70))

        surface.blit(self.item_slot, (armor_slot_x, slots_y))
        armor_text = self.small_font.render("Armor", True, (200, 200, 200))
        surface.blit(armor_text, (armor_slot_x + 32 - armor_text.get_width() // 2, slots_y + 70))

        exp_ratio = self.game.player.exp / self.game.player.exp_to_next_level
        exp_bar_width = 200
        exp_bar_height = 10
        exp_bar_x = stamina_bar_x
        exp_bar_y = stamina_bar_y + stamina_bar_height + 5

        pygame.draw.rect(surface, (0, 0, 0), (exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height))
        pygame.draw.rect(surface, (100, 100, 255), (exp_bar_x, exp_bar_y, exp_bar_width * exp_ratio, exp_bar_height))

        level_text = self.font.render(f"Level: {self.game.player.level}", True, (255, 255, 255))
        surface.blit(level_text, (exp_bar_x - level_text.get_width() - 10, exp_bar_y))

        current_time = pygame.time.get_ticks()
        if self.message and current_time - self.message_timer < self.message_duration:
            message_text = self.font.render(self.message, True, (255, 255, 255))
            message_bg = pygame.Surface((message_text.get_width() + 20, message_text.get_height() + 10))
            message_bg.set_alpha(180)
            message_bg.fill((0, 0, 0))

            x = WW // 2 - message_text.get_width() // 2
            y = WH // 4

            surface.blit(message_bg, (x - 10, y - 5))
            surface.blit(message_text, (x, y))

        weapon_slot_x = WW // 2 - 70
        armor_slot_x = WW // 2 + 6
        slots_y = WH - 80

        surface.blit(self.item_slot, (weapon_slot_x, slots_y))
        surface.blit(self.item_slot, (armor_slot_x, slots_y))

        if self.game.player.equipped_weapon:
            weapon_image = self.game.player.equipped_weapon.image
            surface.blit(weapon_image, (weapon_slot_x + 32 - weapon_image.get_width() // 2,
                                        slots_y + 32 - weapon_image.get_height() // 2))

        if self.game.player.equipped_armor:
            armor_image = self.game.player.equipped_armor.image
            surface.blit(armor_image, (armor_slot_x + 32 - armor_image.get_width() // 2,
                                       slots_y + 32 - armor_image.get_height() // 2))

        weapon_text = self.small_font.render("Weapon", True, (200, 200, 200))
        surface.blit(weapon_text, (weapon_slot_x + 32 - weapon_text.get_width() // 2, slots_y + 70))

        armor_text = self.small_font.render("Armor", True, (200, 200, 200))
        surface.blit(armor_text, (armor_slot_x + 32 - armor_text.get_width() // 2, slots_y + 70))






