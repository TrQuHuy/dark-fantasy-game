import pygame
from enum import Enum

# Character classes
class CharacterClass(Enum):
    WARRIOR = "Kiếm sĩ"
    MAGE = "Pháp sư"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
LIGHT_BLUE = (173, 216, 230)

class Stats:
    def __init__(self, character_class):
        self.character_class = character_class
        self.upgrade_points = 5  # Starting upgrade points
        
        # Initialize stats based on character class
        if character_class == CharacterClass.WARRIOR:
            self.stats = {
                "STR": 15,  # Sát thương vật lý
                "DEX": 12,  # Độ chính xác vật lý
                "VIT": 14,  # Phòng thủ vật lý
                "INT": 5,   # Sát thương phép thuật
                "PIE": 7,   # Độ chính xác phép
                "MND": 6    # Phòng thủ phép
            }
        elif character_class == CharacterClass.MAGE:
            self.stats = {
                "STR": 5,   # Sát thương vật lý
                "DEX": 8,   # Độ chính xác vật lý
                "VIT": 7,   # Phòng thủ vật lý
                "INT": 15,  # Sát thương phép thuật
                "PIE": 14,  # Độ chính xác phép
                "MND": 13   # Phòng thủ phép
            }
        
        # Derived stats
        self.update_derived_stats()
        
        # UI elements
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        self.stat_buttons = {}  # Will store rect objects for the + buttons
    
    def update_derived_stats(self):
        """Update all derived stats based on base stats"""
        # Health and other derived stats - Tăng máu cho người chơi
        self.max_health = 200 + (self.stats["VIT"] * 15)
        self.current_health = self.max_health
        
        # Combat stats
        if self.character_class == CharacterClass.WARRIOR:
            self.physical_damage = 15 + (self.stats["STR"] * 2.5)
            self.magic_damage = 5 + (self.stats["INT"] * 1)
        else:  # Pháp sư
            self.physical_damage = 5 + (self.stats["STR"] * 1)
            self.magic_damage = 15 + (self.stats["INT"] * 2.5)
        
        self.physical_accuracy = 70 + (self.stats["DEX"] * 2)
        self.magic_accuracy = 70 + (self.stats["PIE"] * 2)
        self.physical_defense = 10 + (self.stats["VIT"] * 3)  # Tăng phòng thủ
        self.magic_defense = 10 + (self.stats["MND"] * 3)     # Tăng phòng thủ phép
        self.dodge_chance = self.stats["DEX"] * 1.5
        self.energy_regen = 5 + (self.stats["PIE"] * 0.5)
    
    def increase_stat(self, stat_name):
        """Increase a stat if upgrade points are available"""
        if self.upgrade_points > 0:
            self.stats[stat_name] += 1
            self.upgrade_points -= 1
            self.update_derived_stats()
            print(f"Increased {stat_name} to {self.stats[stat_name]}")
            return True
        return False
    
    def draw_stats_panel(self, screen, x, y, width=300, height=400):
        """Draw the stats panel at the specified position"""
        # Get screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Adjust position to ensure panel stays on screen
        x = max(10, min(x, screen_width - width - 10))
        y = max(10, min(y, screen_height - height - 10))
        
        # Draw semi-transparent background
        stats_surface = pygame.Surface((width, height))
        stats_surface.set_alpha(230)
        stats_surface.fill(BLACK)
        screen.blit(stats_surface, (x, y))
        
        # Draw title
        title_text = self.font.render(f"{self.character_class.value} Stats", True, YELLOW)
        screen.blit(title_text, (x + 20, y + 10))
        
        # Draw remaining points
        points_text = self.small_font.render(f"Điểm nâng cấp còn lại: {self.upgrade_points}", True, GREEN)
        screen.blit(points_text, (x + 20, y + 40))
        
        # Draw stats and + buttons
        y_pos = y + 80
        self.stat_buttons.clear()  # Clear previous buttons
        
        for stat, value in self.stats.items():
            # Stat name and value
            stat_text = self.font.render(f"{stat}: {value}", True, WHITE)
            screen.blit(stat_text, (x + 20, y_pos))
            
            # + button
            if self.upgrade_points > 0:
                plus_button = pygame.Rect(x + 150, y_pos, 30, 30)
                pygame.draw.rect(screen, GREEN, plus_button)
                plus_text = self.font.render("+", True, BLACK)
                screen.blit(plus_text, (x + 160, y_pos + 5))
                self.stat_buttons[stat] = plus_button
            
            y_pos += 40
        
        # Draw derived stats
        y_pos += 20
        derived_title = self.font.render("Derived Stats:", True, YELLOW)
        screen.blit(derived_title, (x + 20, y_pos))
        y_pos += 30
        
        derived_stats = [
            f"Health: {self.max_health}",
            f"Physical DMG: {self.physical_damage}",
            f"Magic DMG: {self.magic_damage}",
            f"Physical DEF: {self.physical_defense}",
            f"Magic DEF: {self.magic_defense}",
            f"Accuracy: {self.physical_accuracy}%",
            f"Magic Acc: {self.magic_accuracy}%",
            f"Dodge: {self.dodge_chance}%"
        ]
        
        for stat in derived_stats:
            stat_text = self.small_font.render(stat, True, GRAY)
            screen.blit(stat_text, (x + 20, y_pos))
            y_pos += 25
    
    def handle_click(self, pos):
        """Handle mouse clicks on the stats panel"""
        for stat, button in self.stat_buttons.items():
            if button.collidepoint(pos):
                if self.increase_stat(stat):
                    return True
        return False
