import pygame
import math
from enum import Enum

class SkillType(Enum):
    ACTIVE = "Active"
    PASSIVE = "Passive"
    ULTIMATE = "Ultimate"

class SkillElement(Enum):
    PHYSICAL = "Physical"
    FIRE = "Fire"
    ICE = "Ice"
    LIGHTNING = "Lightning"

class Skill:
    def __init__(self, id, name, description, skill_type, element, level_req=1):
        self.id = id
        self.name = name
        self.description = description
        self.skill_type = skill_type
        self.element = element
        self.level_req = level_req
        self.unlocked = False
        self.level = 0
        self.max_level = 5
        self.position = (0, 0)
        
    def draw_icon(self, screen, x, y, size, scale_x=1.0, scale_y=1.0):
        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)
        scaled_size = int(size * min(scale_x, scale_y))
        
        # Draw background
        bg_color = (50, 50, 150) if self.skill_type == SkillType.ACTIVE else (50, 150, 50)
        pygame.draw.rect(screen, bg_color, (scaled_x, scaled_y, scaled_size, scaled_size))
        
        # Draw border
        border_width = 3 if self.unlocked else 1
        pygame.draw.rect(screen, (200, 200, 200), (scaled_x, scaled_y, scaled_size, scaled_size), border_width)

class SkillTree:
    def __init__(self, character_class):
        self.character_class = character_class
        self.skills = {}
        self.skill_points = 5  # Start with some skill points for testing
        self.show_skill_tree = False
        
    def toggle_skill_tree(self):
        self.show_skill_tree = not self.show_skill_tree
        print(f"Skill tree toggled: {self.show_skill_tree}")
        
    def update(self, player_level=1):
        pass
        
    def draw_skill_tree(self, screen, player_level, scale_x=1.0, scale_y=1.0):
        if not self.show_skill_tree:
            return {}
            
        # Draw a simple skill tree UI
        tree_width = int(600 * scale_x)
        tree_height = int(500 * scale_y)
        tree_x = (screen.get_width() - tree_width) // 2
        tree_y = (screen.get_height() - tree_height) // 2
        
        # Create surface with transparency
        tree_surface = pygame.Surface((tree_width, tree_height), pygame.SRCALPHA)
        tree_surface.fill((0, 0, 0, 230))
        
        # Draw border
        pygame.draw.rect(tree_surface, (200, 200, 200), (0, 0, tree_width, tree_height), 2)
        
        # Draw title
        font_large = pygame.font.SysFont(None, int(36 * min(scale_x, scale_y)))
        title_text = font_large.render(f"{self.character_class.value} Skill Tree", True, (255, 215, 0))
        title_x = (tree_width - title_text.get_width()) // 2
        tree_surface.blit(title_text, (title_x, 10))
        
        # Draw skill points
        points_text = font_large.render(f"Skill Points: {self.skill_points}", True, (255, 255, 255))
        points_x = (tree_width - points_text.get_width()) // 2
        tree_surface.blit(points_text, (points_x, 50))
        
        # Draw instructions
        font_small = pygame.font.SysFont(None, int(20 * min(scale_x, scale_y)))
        instructions = font_small.render("Press K to close", True, (200, 200, 200))
        inst_x = (tree_width - instructions.get_width()) // 2
        tree_surface.blit(instructions, (inst_x, tree_height - 30))
        
        # Draw skill tree
        screen.blit(tree_surface, (tree_x, tree_y))
        
        return {}  # No clickable areas for now
