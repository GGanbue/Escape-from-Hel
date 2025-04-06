import pygame
from config import *


class Item:
    def __init__(self, name, image, item_class, level_req=1):
        self.name = name
        self.image = image
        self.item_class = item_class
        self.level_req = level_req


class Weapon(Item):
    def __init__(self, name, image, item_class, damage, level_req=1):
        super().__init__(name, image, item_class, level_req)
        self.damage = damage
        self.type = "weapon"


class Armor(Item):
    def __init__(self, name, image, item_class, health, level_req=1):
        super().__init__(name, image, item_class, level_req)
        self.health = health
        self.type = "armor"


def initialize_items(game):
    weapons = {
        "warrior": [
            Weapon("Iron Shortsword", game.item_spritesheet.get_sprite(0, 32, TILESIZE, TILESIZE), "warrior", 15),
            Weapon("Steel Axe", game.item_spritesheet.get_sprite(0, 96, TILESIZE, TILESIZE), "warrior", 20),
            Weapon("War Hammer", game.item_spritesheet.get_sprite(0, 128, TILESIZE, TILESIZE), "warrior", 25),
            Weapon("Halberd", game.item_spritesheet.get_sprite(64, 128, TILESIZE, TILESIZE), "warrior", 25),
            Weapon("Great Sword", game.item_spritesheet.get_sprite(128, 0, TILESIZE, TILESIZE), "warrior", 35),
            Weapon("Battle Axe", game.item_spritesheet.get_sprite(32, 96, TILESIZE, TILESIZE), "warrior", 40),
            Weapon("Club", game.item_spritesheet.get_sprite(64, 256, TILESIZE, TILESIZE), "warrior", 45),
            Weapon("Trident", game.item_spritesheet.get_sprite(96, 192, TILESIZE, TILESIZE), "warrior", 40),
            Weapon("Dragon Slayer", game.item_spritesheet.get_sprite(192, 32, TILESIZE, TILESIZE), "warrior", 70),
            Weapon("Blade of the Ruined King", game.item_spritesheet.get_sprite(256, 0, TILESIZE, TILESIZE), "warrior", 65)
        ],
        "mage": [
            Weapon("Apprentice Staff", game.item_spritesheet.get_sprite(0, 320, TILESIZE, TILESIZE), "mage", 5),
            Weapon("Sun Wand", game.item_spritesheet.get_sprite(32, 320, TILESIZE, TILESIZE), "mage", 5),
            Weapon("Thorn Staff", game.item_spritesheet.get_sprite(64, 320, TILESIZE, TILESIZE), "mage", 7),
            Weapon("Water Wand", game.item_spritesheet.get_sprite(96, 320, TILESIZE, TILESIZE), "mage", 7),
            Weapon("Lightning Staff", game.item_spritesheet.get_sprite(128, 320, TILESIZE, TILESIZE), "mage", 10),
            Weapon("Blood Staff", game.item_spritesheet.get_sprite(160, 320, TILESIZE, TILESIZE), "mage", 10),
            Weapon("Soul Flame Staff", game.item_spritesheet.get_sprite(192, 320, TILESIZE, TILESIZE), "mage", 15),
            Weapon("Azure Stone Staff", game.item_spritesheet.get_sprite(224, 320, TILESIZE, TILESIZE), "mage", 15),
            Weapon("Staff of the Elite", game.item_spritesheet.get_sprite(256, 320, TILESIZE, TILESIZE), "mage", 20),
            Weapon("Shillelagh of the Old One", game.item_spritesheet.get_sprite(288, 320, TILESIZE, TILESIZE), "mage", 20)
        ],
        "rogue": [
            Weapon("Rusty Dagger", game.item_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE), "rogue", 20),
            Weapon("Large Dagger", game.item_spritesheet.get_sprite(32, 0, TILESIZE, TILESIZE), "rogue", 20),
            Weapon("Sickle", game.item_spritesheet.get_sprite(0, 64, TILESIZE, TILESIZE), "rogue", 30),
            Weapon("Kukri", game.item_spritesheet.get_sprite(128, 64, TILESIZE, TILESIZE), "rogue", 30),
            Weapon("Small Cutlass", game.item_spritesheet.get_sprite(32, 64, TILESIZE, TILESIZE), "rogue", 35),
            Weapon("Molten Dagger", game.item_spritesheet.get_sprite(192, 0, TILESIZE, TILESIZE), "rogue", 35),
            Weapon("Shadow Dagger", game.alt_item_spritesheet.get_sprite(0, 256, TILESIZE, TILESIZE), "rogue", 45),
            Weapon("Mythril Dagger", game.alt_item_spritesheet.get_sprite(0, 512, TILESIZE, TILESIZE), "rogue", 45),
            Weapon("Dagger of Ullr", game.item_spritesheet.get_sprite(224, 0, TILESIZE, TILESIZE), "rogue", 60),
            Weapon("Soulflame Blade", game.item_spritesheet.get_sprite(320, 0, TILESIZE, TILESIZE), "rogue", 60)
        ]
    }

    armors = {
        "warrior": [
            Armor("Leather Plate", game.item_spritesheet.get_sprite(0, 384, TILESIZE, TILESIZE), "warrior", 10),
            Armor("Iron Chainmail", game.item_spritesheet.get_sprite(128, 384, TILESIZE, TILESIZE), "warrior", 15),
            Armor("Knight's Helm", game.item_spritesheet.get_sprite(160, 480, TILESIZE, TILESIZE), "warrior", 20),
            Armor("Knight's Gauntlets", game.item_spritesheet.get_sprite(96, 512, TILESIZE, TILESIZE), "warrior", 25),
            Armor("Warlord's Plate", game.item_spritesheet.get_sprite(160, 384, TILESIZE, TILESIZE), "warrior", 30)
        ],
        "mage": [
            Armor("Cloth Robe", game.item_spritesheet.get_sprite(0, 384, TILESIZE, TILESIZE), "mage", 5),
            Armor("Enchanted Cloak", game.item_spritesheet.get_sprite(64, 384, TILESIZE, TILESIZE), "mage", 8),
            Armor("Hat of Wizardry", game.item_spritesheet.get_sprite(64, 480, TILESIZE, TILESIZE), "mage", 11),
            Armor("Pendant of Sorcery", game.item_spritesheet.get_sprite(64, 512, TILESIZE, TILESIZE), "mage", 14),
            Armor("Ring of Hel", game.item_spritesheet.get_sprite(96, 544, TILESIZE, TILESIZE), "mage", 17),
        ],
        "rogue": [
            Armor("Leather Vest", game.item_spritesheet.get_sprite(0, 384, TILESIZE, TILESIZE), "rogue", 7),
            Armor("Shadow Garb", game.item_spritesheet.get_sprite(96, 160, TILESIZE, TILESIZE), "rogue", 12),
            Armor("Assassins Hood", game.item_spritesheet.get_sprite(0, 480, TILESIZE, TILESIZE), "rogue", 17),
            Armor("Pendant of Trickery", game.item_spritesheet.get_sprite(32, 512, TILESIZE, TILESIZE), "rogue", 22),
            Armor("Ring of Loki", game.item_spritesheet.get_sprite(0, 544, TILESIZE, TILESIZE), "rogue", 27),
        ]
    }

    return weapons, armors


class InventoryScreen:
    def __init__(self, game):
        self.game = game
        self.running = True
        self.font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 40)
        self.selected_index = 0
        self.scroll_offset = 0
        self.items_per_page = 8

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = self.selected_index
                elif event.key == pygame.K_DOWN:
                    self.selected_index = min(len(self.game.player.inventory) - 1, self.selected_index + 1)
                    if self.selected_index >= self.scroll_offset + self.items_per_page:
                        self.scroll_offset = self.selected_index - self.items_per_page + 1
                elif event.key == pygame.K_RETURN:
                    self.equip_selected_item()

    def equip_selected_item(self):
        if 0 <= self.selected_index < len(self.game.player.inventory):
            item = self.game.player.inventory[self.selected_index]

            if self.game.player.level < item.level_req:
                self.game.set_direct_notification(f"Level {item.level_req} required to equip {item.name}")
                return

            if item.item_class != self.game.player.player_class:
                self.game.set_direct_notification(f"Only {item.item_class}s can equip {item.name}")
                return

            if item.type == "weapon":
                if self.game.player.equipped_weapon == item:
                    self.game.player.equipped_weapon = None
                    self.game.player.damage = self.game.player.damage
                    self.game.set_direct_notification(f"Unequipped {item.name}")
                else:
                    self.game.player.equipped_weapon = item
                    self.game.player.damage = self.game.player.damage + item.damage
                    self.game.set_direct_notification(f"Equipped {item.name}")

            elif item.type == "armor":
                if self.game.player.equipped_armor == item:
                    if self.game.player.equipped_armor:
                        self.game.player.max_health -= self.game.player.equipped_armor.health
                        self.game.player.health = min(self.game.player.health, self.game.player.max_health)
                    self.game.player.equipped_armor = None
                    self.game.set_direct_notification(f"Unequipped {item.name}")
                else:
                    if self.game.player.equipped_armor:
                        self.game.player.max_health -= self.game.player.equipped_armor.health

                    self.game.player.equipped_armor = item
                    self.game.player.max_health += item.health
                    self.game.player.health += item.health
                    self.game.set_direct_notification(f"Equipped {item.name}")

    def draw(self):
        overlay = pygame.Surface((WW, WH))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.game.screen.blit(overlay, (0, 0))

        title_text = self.title_font.render("Inventory", True, (255, 255, 255))
        self.game.screen.blit(title_text, (WW // 2 - title_text.get_width() // 2, 30))

        if not self.game.player.inventory:
            empty_text = self.font.render("Inventory is empty", True, (200, 200, 200))
            self.game.screen.blit(empty_text, (WW // 2 - empty_text.get_width() // 2, WH // 2))
        else:
            start_y = 100
            for i in range(self.scroll_offset,
                           min(self.scroll_offset + self.items_per_page, len(self.game.player.inventory))):
                item = self.game.player.inventory[i]
                bg_color = (100, 100, 255) if i == self.selected_index else (70, 70, 70)

                pygame.draw.rect(self.game.screen, bg_color,
                                 (WW // 4, start_y + (i - self.scroll_offset) * 50, WW // 2, 40))

                item_text = self.font.render(f"{item.name}", True, (255, 255, 255))
                self.game.screen.blit(item_text, (WW // 4 + 10, start_y + (i - self.scroll_offset) * 50 + 10))

                if hasattr(item, 'damage'):
                    stat_text = self.font.render(f"Damage: {item.damage}", True, (255, 200, 100))
                elif hasattr(item, 'health'):
                    stat_text = self.font.render(f"Health: {item.health}", True, (100, 200, 255))
                else:
                    stat_text = self.font.render("Item", True, (200, 200, 200))

                self.game.screen.blit(stat_text, (WW // 2, start_y + (i - self.scroll_offset) * 50 + 10))

            if self.scroll_offset > 0:
                up_text = self.font.render("▲", True, (255, 255, 255))
                self.game.screen.blit(up_text, (WW // 2, 70))

            if self.scroll_offset + self.items_per_page < len(self.game.player.inventory):
                down_text = self.font.render("▼", True, (255, 255, 255))
                self.game.screen.blit(down_text, (WW // 2, start_y + self.items_per_page * 50 + 10))

        if self.game.player.equipped_weapon:
            weapon_text = self.font.render(f"Equipped Weapon: {self.game.player.equipped_weapon.name}", True,
                                           (255, 200, 100))
            self.game.screen.blit(weapon_text, (50, WH - 80))

        if self.game.player.equipped_armor:
            armor_text = self.font.render(f"Equipped Armor: {self.game.player.equipped_armor.name}", True,
                                          (100, 200, 255))
            self.game.screen.blit(armor_text, (50, WH - 50))

        hint_text = self.font.render("↑↓: Navigate | Enter: Equip | ESC: Back", True, (200, 200, 200))
        self.game.screen.blit(hint_text, (WW // 2 - hint_text.get_width() // 2, WH - 30))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()