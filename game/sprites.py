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
        super().__init__()

        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.world_x = x * TILESIZE
        self.world_y = y * TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.max_health = 100
        self.health = self.max_health

        self.facing = 'left'

        self.rect = pygame.Rect(self.world_x, self.world_y, TILESIZE, TILESIZE)

        self.image = self.game.character_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)

    def update(self):
        self.movement()

        self.world_x += self.x_change
        self.collide_blocks('x')
        self.world_y += self.y_change
        self.collide_blocks('y')

        self.x_change = 0
        self.y_change = 0

    def movement(self):
        keys = pygame.key.get_pressed()
        new_facing = self.facing

        self.x_change = 0
        self.y_change = 0

        if keys[pygame.K_a]:
            self.x_change = -PLAYER_SPEED
            new_facing = 'left'
        if keys[pygame.K_d]:
            self.x_change = PLAYER_SPEED
            new_facing = 'right'
        if keys[pygame.K_w]:
            self.y_change = -PLAYER_SPEED
        if keys[pygame.K_s]:
            self.y_change = PLAYER_SPEED

        if new_facing != self.facing:
            self.image = pygame.transform.flip(self.image, True, False)
            self.facing = new_facing


    def collide_blocks(self, direction):
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

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            # Handle player death
            self.game.playing = False  # End the game when player dies

    def draw_health_bar(self, surface):
        health_ratio = self.health / self.max_health
        bar_width = TILESIZE
        bar_height = 5
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 10, bar_width * health_ratio, bar_height))

    def attack(self):
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Convert screen position to world position
        world_mouse_x = mouse_pos[0] + self.game.camera_offset_x
        world_mouse_y = mouse_pos[1] + self.game.camera_offset_y

        # Calculate direction to mouse
        dx = world_mouse_x - self.world_x
        dy = world_mouse_y - self.world_y
        direction = math.atan2(dy, dx)

        # Create attack object
        Attack(self.game, self.world_x + TILESIZE / 2, self.world_y + TILESIZE / 2, direction)


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
        self.image = self.game.enemy_spritesheet.get_sprite(64, 0, TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK)

        self.max_health = 50
        self.health = self.max_health

        self.path = []
        self.path_index = 0
        self.path_update_time = 0
        self.path_update_delay = 1000

        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.2
        self.deceleration = 0.1
        self.max_speed = ENEMY_SPEED

    def update(self):
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
                self.game.player.take_damage(10)  # Damage amount

    def detect_and_handle_corner_stuck(self, prev_x, prev_y):
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

        if self.stuck_count > 5 and current_time - self.last_stuck_time > 500:
            self.last_stuck_time = current_time
            self.corner_adjustment_active = True
            self.corner_adjustment_time = current_time

            self.find_corner_adjustment_direction()

        if self.corner_adjustment_active:
            if current_time - self.corner_adjustment_time < 500:
                self.apply_corner_adjustment()
            else:
                self.corner_adjustment_active = False
                self.update_path()
                self.path_update_time = current_time

    def find_corner_adjustment_direction(self):
        directions = []
        test_distance = TILESIZE * 1.5

        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            test_x = self.world_x + dx * test_distance
            test_y = self.world_y + dy * test_distance

            test_rect = pygame.Rect(test_x, test_y, TILESIZE, TILESIZE)

            clear = True
            for block in self.game.blocks:
                block_rect = pygame.Rect(block.world_x, block.world_y, TILESIZE, TILESIZE)
                if test_rect.colliderect(block_rect):
                    clear = False
                    break

            if clear:
                directions.append((dx, dy))

        if directions:
            perpendicular = []
            for dx, dy in directions:
                if abs(self.velocity_x) > abs(self.velocity_y):
                    if dy != 0 and dx == 0:
                        perpendicular.append((dx, dy))
                else:
                    if dx != 0 and dy == 0:
                        perpendicular.append((dx, dy))

            if perpendicular:
                self.corner_adjustment_direction = random.choice(perpendicular)
            else:
                self.corner_adjustment_direction = random.choice(directions)
        else:
            diagonals = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dx, dy in diagonals:
                test_x = self.world_x + dx * test_distance
                test_y = self.world_y + dy * test_distance

                test_rect = pygame.Rect(test_x, test_y, TILESIZE, TILESIZE)

                clear = True
                for block in self.game.blocks:
                    block_rect = pygame.Rect(block.world_x, block.world_y, TILESIZE, TILESIZE)
                    if test_rect.colliderect(block_rect):
                        clear = False
                        break

                if clear:
                    self.corner_adjustment_direction = (dx, dy)
                    return

            self.corner_adjustment_direction = (-self.velocity_x, -self.velocity_y)

    def apply_corner_adjustment(self):
        if self.corner_adjustment_direction:
            dx, dy = self.corner_adjustment_direction

            adjustment_strength = 1.5

            self.world_x += dx * ENEMY_SPEED * adjustment_strength
            self.world_y += dy * ENEMY_SPEED * adjustment_strength

            self.velocity_x = dx * self.max_speed
            self.velocity_y = dy * self.max_speed

    def movement(self):
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

    def has_line_of_sight_to_player(self):
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

    def update_path(self):
        grid = self.game.get_grid()
        start = (int(self.world_x // TILESIZE), int(self.world_y // TILESIZE))
        goal = (int(self.game.player.world_x // TILESIZE), int(self.game.player.world_y // TILESIZE))

        self.path = astar_pathfinding(start, goal, grid)
        self.path_index = 0

    def collide_blocks(self, direction):
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
                    self.velocity_x = 0

                if direction == 'y':
                    if self.y_change > 0:
                        self.world_y = block_rect.top - TILESIZE
                    if self.y_change < 0:
                        self.world_y = block_rect.bottom
                    self.y_change = 0
                    self.velocity_y = 0

    def collide_enemies(self, direction):
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

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()  # Remove the enemy sprite when health reaches 0

    def draw_health_bar(self, surface):
        health_ratio = self.health / self.max_health
        bar_width = TILESIZE
        bar_height = 5
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 10, bar_width * health_ratio, bar_height))


class Attack(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites, game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.world_x = x
        self.world_y = y
        self.direction = direction  # Angle in radians

        # Create an arc-shaped attack area
        self.radius = TILESIZE * 1.5
        self.arc_width = math.pi / 2  # 90-degree arc
        self.lifetime = 200  # milliseconds
        self.damage = 25
        self.creation_time = pygame.time.get_ticks()

        # Create a surface for the attack visualization
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        # Draw the arc
        start_angle = self.direction - self.arc_width / 2
        end_angle = self.direction + self.arc_width / 2
        pygame.draw.arc(self.image, (255, 255, 255, 128),
                        (0, 0, self.radius * 2, self.radius * 2),
                        start_angle, end_angle, width=self.radius)

        # Store hitbox for collision detection
        self.hitbox_points = []
        for angle in numpy.linspace(start_angle, end_angle, 10):
            self.hitbox_points.append((
                x + math.cos(angle) * self.radius,
                y + math.sin(angle) * self.radius
            ))

    def update(self):
        # Check if attack lifetime is over
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.kill()
            return

        # Update position with camera
        self.rect.x = self.world_x - self.game.camera_offset_x - self.radius
        self.rect.y = self.world_y - self.game.camera_offset_y - self.radius

        # Check for collisions with enemies
        for enemy in self.game.enemies:
            enemy_center = (enemy.world_x + TILESIZE / 2, enemy.world_y + TILESIZE / 2)
            distance = math.sqrt((enemy_center[0] - self.world_x) ** 2 +
                                 (enemy_center[1] - self.world_y) ** 2)

            # Check if enemy is within radius
            if distance <= self.radius:
                # Check if enemy is within arc
                angle_to_enemy = math.atan2(enemy_center[1] - self.world_y,
                                            enemy_center[0] - self.world_x)

                # Normalize angle difference
                angle_diff = (angle_to_enemy - self.direction) % (2 * math.pi)
                if angle_diff > math.pi:
                    angle_diff = 2 * math.pi - angle_diff

                if angle_diff <= self.arc_width / 2:
                    enemy.take_damage(self.damage)