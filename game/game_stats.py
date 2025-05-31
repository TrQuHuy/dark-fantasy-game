import pygame
import sys

# Initialize pygame with error handling
try:
    pygame.init()
except pygame.error as e:
    print(f"Error initializing pygame: {e}")
    sys.exit(1)

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RPG Game - Kiếm sĩ & Pháp sư")
except pygame.error as e:
    print(f"Error creating display: {e}")
    sys.exit(1)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Fonts with error handling
try:
    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 24)
except pygame.error as e:
    print(f"Error loading fonts: {e}")
    # Fallback to default font if available
    try:
        font = pygame.font.Font(None, 32)
        small_font = pygame.font.Font(None, 24)
    except:
        print("Could not load any fonts")
        sys.exit(1)

class Character:
    def __init__(self, character_class):
        self.character_class = character_class
        self.upgrade_points = 5  # Starting upgrade points
        
        # Initialize stats based on character class
        if character_class == "Kiếm sĩ":
            self.stats = {
                "STR": 15,  # Sát thương vật lý
                "DEX": 12,  # Độ chính xác vật lý
                "VIT": 14,  # Phòng thủ vật lý
                "INT": 5,   # Sát thương phép thuật
                "PIE": 7,   # Độ chính xác phép
                "MND": 6    # Phòng thủ phép
            }
        elif character_class == "Pháp sư":
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
    
    def update_derived_stats(self):
        """Update all derived stats based on base stats"""
        # Health and other derived stats
        self.max_health = 100 + (self.stats["VIT"] * 10)
        self.current_health = self.max_health
        
        # Combat stats
        if self.character_class == "Kiếm sĩ":
            self.physical_damage = 10 + (self.stats["STR"] * 2)
            self.magic_damage = 5 + (self.stats["INT"] * 1)
        else:  # Pháp sư
            self.physical_damage = 5 + (self.stats["STR"] * 1)
            self.magic_damage = 10 + (self.stats["INT"] * 2)
        
        self.physical_accuracy = 70 + (self.stats["DEX"] * 2)
        self.magic_accuracy = 70 + (self.stats["PIE"] * 2)
        self.physical_defense = self.stats["VIT"] * 2
        self.magic_defense = self.stats["MND"] * 2
        self.dodge_chance = self.stats["DEX"] * 1.5
        self.energy_regen = 5 + (self.stats["PIE"] * 0.5)
    
    def increase_stat(self, stat_name):
        """Increase a stat if upgrade points are available"""
        if self.upgrade_points > 0 and stat_name in self.stats:
            self.stats[stat_name] += 1
            self.upgrade_points -= 1
            self.update_derived_stats()
            return True
        return False

class Game:
    def __init__(self):
        self.character = Character("Kiếm sĩ")  # Default character
        self.show_stats = False
        self.stat_buttons = {}  # Will store rect objects for the + buttons
    
    def switch_character_class(self):
        """Switch between Kiếm sĩ and Pháp sư"""
        if self.character.character_class == "Kiếm sĩ":
            self.character = Character("Pháp sư")
        else:
            self.character = Character("Kiếm sĩ")
    
    def draw_stats_panel(self):
        """Draw the stats panel when TAB is pressed"""
        if not self.show_stats:
            return
        
        try:
            # Draw semi-transparent background
            stats_surface = pygame.Surface((300, 400))
            stats_surface.set_alpha(230)
            stats_surface.fill(BLACK)
            screen.blit(stats_surface, (50, 50))
            
            # Draw title
            title_text = font.render(f"{self.character.character_class} Stats", True, YELLOW)
            screen.blit(title_text, (70, 60))
            
            # Draw remaining points
            points_text = small_font.render(f"Điểm nâng cấp còn lại: {self.character.upgrade_points}", True, GREEN)
            screen.blit(points_text, (70, 90))
            
            # Draw stats and + buttons
            y_pos = 130
            self.stat_buttons.clear()  # Clear previous buttons
            
            for stat, value in self.character.stats.items():
                # Stat name and value
                stat_text = font.render(f"{stat}: {value}", True, WHITE)
                screen.blit(stat_text, (70, y_pos))
                
                # + button
                if self.character.upgrade_points > 0:
                    plus_button = pygame.Rect(200, y_pos, 30, 30)
                    pygame.draw.rect(screen, GREEN, plus_button)
                    plus_text = font.render("+", True, BLACK)
                    screen.blit(plus_text, (210, y_pos + 5))
                    self.stat_buttons[stat] = plus_button
                
                y_pos += 40
            
            # Draw derived stats
            y_pos += 20
            derived_title = font.render("Derived Stats:", True, YELLOW)
            screen.blit(derived_title, (70, y_pos))
            y_pos += 30
            
            derived_stats = [
                f"Health: {self.character.max_health}",
                f"Physical DMG: {self.character.physical_damage}",
                f"Magic DMG: {self.character.magic_damage}",
                f"Physical DEF: {self.character.physical_defense}",
                f"Magic DEF: {self.character.magic_defense}",
                f"Accuracy: {self.character.physical_accuracy}%",
                f"Magic Acc: {self.character.magic_accuracy}%",
                f"Dodge: {self.character.dodge_chance}%"
            ]
            
            for stat in derived_stats:
                stat_text = small_font.render(stat, True, GRAY)
                screen.blit(stat_text, (70, y_pos))
                y_pos += 25
        except Exception as e:
            error_text = small_font.render(f"Error: {str(e)}", True, RED)
            screen.blit(error_text, (70, 130))
    
    def handle_click(self, pos):
        """Handle mouse clicks on the stats panel"""
        if not self.show_stats:
            return
        
        try:
            for stat, button in self.stat_buttons.items():
                if button.collidepoint(pos):
                    if self.character.increase_stat(stat):
                        print(f"Increased {stat} to {self.character.stats[stat]}")
        except Exception as e:
            print(f"Error handling click: {e}")
    
    def draw_game(self):
        """Draw the main game screen"""
        try:
            screen.fill((50, 50, 80))  # Dark blue background
            
            # Draw character info
            char_text = font.render(f"Character: {self.character.character_class}", True, WHITE)
            screen.blit(char_text, (20, 20))
            
            health_text = font.render(f"Health: {self.character.current_health}/{self.character.max_health}", True, RED)
            screen.blit(health_text, (20, 60))
            
            # Draw instructions
            instructions = [
                "Press TAB to toggle Stats Panel",
                "Press SPACE to switch character class",
                "Click [+] to increase stats"
            ]
            
            y_pos = 500
            for instruction in instructions:
                inst_text = small_font.render(instruction, True, YELLOW)
                screen.blit(inst_text, (20, y_pos))
                y_pos += 30
            
            # Draw the stats panel if active
            self.draw_stats_panel()
        except Exception as e:
            # Display error message
            screen.fill((50, 0, 0))  # Dark red background for error
            error_text = font.render(f"Error: {str(e)}", True, WHITE)
            screen.blit(error_text, (20, 20))
            
            # Recovery instructions
            recovery_text = small_font.render("Press ESC to quit, SPACE to reset", True, YELLOW)
            screen.blit(recovery_text, (20, 60))
    
    def run(self):
        """Main game loop"""
        running = True
        clock = pygame.time.Clock()
        
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_TAB:
                            self.show_stats = not self.show_stats
                        elif event.key == pygame.K_SPACE:
                            self.switch_character_class()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left click
                            self.handle_click(event.pos)
                
                self.draw_game()
                pygame.display.flip()
                clock.tick(60)
        except Exception as e:
            # Emergency error handling
            print(f"Critical error: {e}")
            
            # Display error screen
            screen.fill((50, 0, 0))  # Dark red background
            error_text = font.render(f"Critical error: {str(e)}", True, WHITE)
            screen.blit(error_text, (20, 20))
            
            # Recovery instructions
            recovery_text = small_font.render("Press any key to exit", True, YELLOW)
            screen.blit(recovery_text, (20, 60))
            
            pygame.display.flip()
            
            # Wait for key press to exit
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                        waiting = False
                clock.tick(30)
        
        pygame.quit()
        sys.exit()

# Start the game
if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        pygame.quit()
        sys.exit(1)
