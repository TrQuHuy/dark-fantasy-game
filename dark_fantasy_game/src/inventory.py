import pygame

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
GOLD = (255, 215, 0)

class Item:
    def __init__(self, name, description, item_type, value, stats_bonus=None):
        self.name = name
        self.description = description
        self.item_type = item_type  # weapon, armor, potion, etc.
        self.value = value  # gold value
        self.stats_bonus = stats_bonus or {}  # dictionary of stat bonuses
        self.equipped = False
        
    def __str__(self):
        return f"{self.name} ({self.item_type})"
        
    def use(self, player):
        """Use the item on the player"""
        if self.item_type == "potion":
            # Healing potions
            if "heal" in self.stats_bonus:
                player.heal(self.stats_bonus["heal"])
                return True  # Item was consumed
        return False  # Item was not consumed
        
    def equip(self, player):
        """Equip the item if it's equipment"""
        if self.item_type in ["weapon", "armor", "accessory"]:
            self.equipped = True
            # Apply stat bonuses
            for stat, bonus in self.stats_bonus.items():
                if stat in player.stats.stats:
                    player.stats.stats[stat] += bonus
            player.stats.update_derived_stats()
            return True
        return False
        
    def unequip(self, player):
        """Unequip the item"""
        if self.equipped:
            self.equipped = False
            # Remove stat bonuses
            for stat, bonus in self.stats_bonus.items():
                if stat in player.stats.stats:
                    player.stats.stats[stat] -= bonus
            player.stats.update_derived_stats()
            return True
        return False

class Inventory:
    def __init__(self, max_items=20):
        self.items = []
        self.max_items = max_items
        self.gold = 100
        self.selected_item = None
        
        # UI elements
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 32)
        self.item_rects = []  # For click detection
        
        # Add some starter items
        self.add_item(Item("Wooden Sword", "A basic training sword", "weapon", 10, {"STR": 1}))
        self.add_item(Item("Leather Armor", "Basic protection", "armor", 15, {"VIT": 1}))
        self.add_item(Item("Health Potion", "Restores 50 health", "potion", 20, {"heal": 50}))
        
    def add_item(self, item):
        """Add an item to the inventory"""
        if len(self.items) < self.max_items:
            self.items.append(item)
            return True
        return False
        
    def remove_item(self, item):
        """Remove an item from the inventory"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
        
    def use_item(self, item, player):
        """Use an item on the player"""
        if item in self.items:
            if item.use(player):
                self.remove_item(item)
                return True
        return False
        
    def equip_item(self, item, player):
        """Equip an item on the player"""
        if item in self.items:
            # Unequip any other items of the same type
            for other_item in self.items:
                if other_item.item_type == item.item_type and other_item.equipped:
                    other_item.unequip(player)
            
            # Equip the new item
            if item.equip(player):
                print(f"Equipped {item.name}")
                return True
        return False
        
    def draw(self, screen, x, y, width=350, height=400):
        """Draw the inventory at the specified position"""
        # Get screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Adjust position to ensure panel stays on screen
        x = max(10, min(x, screen_width - width - 10))
        y = max(10, min(y, screen_height - height - 10))
        
        # Draw background
        inventory_surface = pygame.Surface((width, height))
        inventory_surface.set_alpha(230)
        inventory_surface.fill(BLACK)
        screen.blit(inventory_surface, (x, y))
        
        # Draw title
        title_text = self.title_font.render("Inventory", True, GOLD)
        screen.blit(title_text, (x + 20, y + 10))
        
        # Draw gold
        gold_text = self.font.render(f"Gold: {self.gold}", True, GOLD)
        screen.blit(gold_text, (x + width - 120, y + 10))
        
        # Draw items
        item_y = y + 50
        self.item_rects = []
        
        for i, item in enumerate(self.items):
            # Item background
            item_rect = pygame.Rect(x + 10, item_y, width - 20, 30)
            self.item_rects.append((item_rect, item))
            
            # Highlight selected item
            if item == self.selected_item:
                pygame.draw.rect(screen, GRAY, item_rect)
            else:
                pygame.draw.rect(screen, DARK_GRAY, item_rect)
                
            # Item name and type
            equipped_text = " [E]" if item.equipped else ""
            item_text = self.font.render(f"{item.name}{equipped_text}", True, WHITE)
            screen.blit(item_text, (x + 20, item_y + 5))
            
            # Item type
            type_text = self.font.render(item.item_type, True, GRAY)
            screen.blit(type_text, (x + width - 100, item_y + 5))
            
            item_y += 35
            
        # Draw selected item details
        if self.selected_item:
            detail_y = y + height - 100
            
            # Draw separator line
            pygame.draw.line(screen, GRAY, (x + 10, detail_y - 10), (x + width - 10, detail_y - 10))
            
            # Item description
            desc_text = self.font.render(self.selected_item.description, True, WHITE)
            screen.blit(desc_text, (x + 20, detail_y))
            
            # Item value
            value_text = self.font.render(f"Value: {self.selected_item.value} gold", True, GOLD)
            screen.blit(value_text, (x + 20, detail_y + 25))
            
            # Item stat bonuses
            bonus_y = detail_y + 50
            for stat, bonus in self.selected_item.stats_bonus.items():
                bonus_text = self.font.render(f"{stat}: +{bonus}", True, WHITE)
                screen.blit(bonus_text, (x + 20, bonus_y))
                bonus_y += 20
    
    def handle_click(self, pos):
        """Handle mouse clicks on the inventory"""
        for rect, item in self.item_rects:
            if rect.collidepoint(pos):
                self.selected_item = item
                print(f"Selected item: {item.name}")
                return True
        return False
