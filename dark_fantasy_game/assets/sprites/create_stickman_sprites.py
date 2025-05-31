import pygame
import os
import sys

# Initialize pygame
pygame.init()

# Create sprites directory if it doesn't exist
sprites_dir = "/home/huy/dark_fantasy_game/assets/sprites"
if not os.path.exists(sprites_dir):
    os.makedirs(sprites_dir)

# Function to create a stickman warrior sprite sheet with sword attack animation
def create_warrior_attack_sheet():
    # Create a surface for the sprite sheet (6 frames, 32x32 each)
    width = 32 * 6
    height = 32
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Colors
    BLACK = (0, 0, 0)
    SILVER = (192, 192, 192)
    ORANGE = (255, 165, 0)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)
    
    for i in range(6):
        frame_x = i * 32
        
        # Draw stickman body (always present)
        # Head
        pygame.draw.circle(surface, BLACK, (frame_x + 16, 8), 4)
        
        # Body position changes based on frame
        if i == 0:  # Preparing stance
            # Body
            pygame.draw.line(surface, BLACK, (frame_x + 16, 12), (frame_x + 16, 22), 2)
            # Arms - right arm back for swing
            pygame.draw.line(surface, BLACK, (frame_x + 16, 15), (frame_x + 22, 10), 2)
            # Sword behind
            pygame.draw.line(surface, SILVER, (frame_x + 22, 10), (frame_x + 28, 5), 2)
            # Legs
            pygame.draw.line(surface, BLACK, (frame_x + 16, 22), (frame_x + 13, 30), 2)
            pygame.draw.line(surface, BLACK, (frame_x + 16, 22), (frame_x + 19, 30), 2)
            
        elif i == 1:  # Starting swing
            # Body leaning
            pygame.draw.line(surface, BLACK, (frame_x + 16, 12), (frame_x + 15, 22), 2)
            # Arms - right arm moving forward
            pygame.draw.line(surface, BLACK, (frame_x + 15, 15), (frame_x + 20, 13), 2)
            # Sword moving
            pygame.draw.line(surface, SILVER, (frame_x + 20, 13), (frame_x + 26, 10), 2)
            # Legs
            pygame.draw.line(surface, BLACK, (frame_x + 15, 22), (frame_x + 12, 30), 2)
            pygame.draw.line(surface, BLACK, (frame_x + 15, 22), (frame_x + 18, 30), 2)
            
        elif i == 2:  # Mid swing
            # Body leaning more
            pygame.draw.line(surface, BLACK, (frame_x + 16, 12), (frame_x + 14, 22), 2)
            # Arms - right arm extended
            pygame.draw.line(surface, BLACK, (frame_x + 14, 15), (frame_x + 20, 16), 2)
            # Sword horizontal
            pygame.draw.line(surface, SILVER, (frame_x + 20, 16), (frame_x + 28, 16), 2)
            # Sword trail
            pygame.draw.arc(surface, ORANGE, (frame_x + 18, 10, 10, 12), 0, 3.14/2, 2)
            # Legs
            pygame.draw.line(surface, BLACK, (frame_x + 14, 22), (frame_x + 11, 30), 2)
            pygame.draw.line(surface, BLACK, (frame_x + 14, 22), (frame_x + 17, 30), 2)
            
        elif i == 3:  # Full swing
            # Body fully leaned
            pygame.draw.line(surface, BLACK, (frame_x + 16, 12), (frame_x + 13, 22), 2)
            # Arms - right arm fully extended
            pygame.draw.line(surface, BLACK, (frame_x + 13, 15), (frame_x + 19, 19), 2)
            # Sword diagonal down
            pygame.draw.line(surface, SILVER, (frame_x + 19, 19), (frame_x + 26, 24), 2)
            # Sword trail
            pygame.draw.arc(surface, ORANGE, (frame_x + 16, 14, 12, 12), 3.14/4, 3.14, 2)
            pygame.draw.arc(surface, YELLOW, (frame_x + 16, 14, 12, 12), 3.14/4, 3.14, 1)
            # Legs
            pygame.draw.line(surface, BLACK, (frame_x + 13, 22), (frame_x + 10, 30), 2)
            pygame.draw.line(surface, BLACK, (frame_x + 13, 22), (frame_x + 16, 30), 2)
            
        elif i == 4:  # Recovery
            # Body returning
            pygame.draw.line(surface, BLACK, (frame_x + 16, 12), (frame_x + 15, 22), 2)
            # Arms - right arm returning
            pygame.draw.line(surface, BLACK, (frame_x + 15, 15), (frame_x + 18, 20), 2)
            # Sword returning
            pygame.draw.line(surface, SILVER, (frame_x + 18, 20), (frame_x + 22, 24), 2)
            # Fading trail
            pygame.draw.arc(surface, YELLOW, (frame_x + 16, 16, 8, 10), 3.14/4, 3.14, 1)
            # Legs
            pygame.draw.line(surface, BLACK, (frame_x + 15, 22), (frame_x + 12, 30), 2)
            pygame.draw.line(surface, BLACK, (frame_x + 15, 22), (frame_x + 18, 30), 2)
            
        else:  # Return to stance
            # Body
            pygame.draw.line(surface, BLACK, (frame_x + 16, 12), (frame_x + 16, 22), 2)
            # Arms - normal position
            pygame.draw.line(surface, BLACK, (frame_x + 16, 15), (frame_x + 12, 18), 2)
            pygame.draw.line(surface, BLACK, (frame_x + 16, 15), (frame_x + 20, 18), 2)
            # Sword at side
            pygame.draw.line(surface, SILVER, (frame_x + 20, 18), (frame_x + 24, 22), 2)
            # Legs
            pygame.draw.line(surface, BLACK, (frame_x + 16, 22), (frame_x + 13, 30), 2)
            pygame.draw.line(surface, BLACK, (frame_x + 16, 22), (frame_x + 19, 30), 2)
    
    # Save the sprite sheet
    pygame.image.save(surface, os.path.join(sprites_dir, "warrior_attack_stickman.png"))
    return "Created warrior attack sprite sheet"

# Function to create a stickman mage sprite sheet with fireball casting animation
def create_mage_cast_sheet():
    # Create a surface for the sprite sheet (6 frames, 32x32 each)
    width = 32 * 6
    height = 32
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Colors
    BLACK = (0, 0, 0)
    PURPLE = (128, 0, 128)
    LIGHT_PURPLE = (147, 112, 219)
    BLUE = (0, 255, 255)
    RED = (255, 0, 0)
    ORANGE = (255, 165, 0)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)
    
    for i in range(6):
        frame_x = i * 32
        
        # Draw stickman body (always present)
        # Head with hood
        pygame.draw.circle(surface, BLACK, (frame_x + 16, 8), 4)
        pygame.draw.arc(surface, PURPLE, (frame_x + 12, 4, 8, 8), 3.14, 2*3.14, 2)
        
        # Robe outline
        pygame.draw.line(surface, PURPLE, (frame_x + 13, 12), (frame_x + 19, 12), 1)
        
        if i == 0:  # Preparing stance
            # Body
            pygame.draw.line(surface, BLACK, (frame_x + 16, 12), (frame_x + 16, 22), 2)
            # Arms - raising staff
            pygame.draw.line(surface, BLACK, (frame_x + 16, 15), (frame_x + 22, 12), 2)
            # Staff
            pygame.draw.line(surface, LIGHT_PURPLE, (frame_x + 22, 12), (frame_x + 22, 4), 2)
            # Robe
            pygame.draw.line(surface, PURPLE, (frame_x + 13, 22), (frame_x + 11, 30), 2)
            pygame.draw.line(surface, PURPLE, (frame_x + 19, 22), (frame_x + 21, 30), 2)
            
        elif i == 1:  # Energy gathering
            # Body
            pygame.draw.line(surface, BLACK, (frame_x + 16, 12), (frame_x + 16, 22), 2)
            # Arms - staff raised
            pygame.draw.line(surface, BLACK, (frame_x + 16, 15), (frame_x + 20, 10), 2)
            # Staff
            pygame.draw.line(surface, LIGHT_PURPLE, (frame_x + 20, 10), (frame_x + 20, 2), 2)
            # Staff glow
            pygame.draw.circle(surface, BLUE, (frame_x + 20, 2), 2)
            # Robe
            pygame.draw.line(surface, PURPLE, (frame_x + 13, 22), (frame_x + 11, 30), 2)
            pygame.draw.line(surface, PURPLE, (frame_x + 19, 22), (frame_x + 21, 30), 2)
            
        elif i == 2:  # Fireball forming
            # Body leaning back
            pygame.draw.line(surface, BLACK, (frame_x + 16, 12), (frame_x + 15, 22), 2)
            # Arms - staff fully raised
            pygame.draw.line(surface, BLACK, (frame_x + 15, 15), (frame_x + 18, 8), 2)
            # Staff
            pygame.draw.line(surface, LIGHT_PURPLE, (frame_x + 18, 8), (frame_x + 18, 0), 2)
            # Fireball forming
            pygame.draw.circle(surface, RED, (frame_x + 18, 0), 3)
            pygame.draw.circle(surface, ORANGE, (frame_x + 18, 0), 2)
            # Robe
            pygame.draw.line(surface, PURPLE, (frame_x + 12, 22), (frame_x + 10, 30), 2)
            pygame.draw.line(surface, PURPLE, (frame_x + 18, 22), (frame_x + 20, 30), 2)
            
        elif i == 3:  # Casting fireball
            # Body leaning forward
            pygame.draw.line(surface, BLACK, (frame_x + 16, 12), (frame_x + 17, 22), 2)
            # Arms - pushing forward
            pygame.draw.line(surface, BLACK, (frame_x + 17, 15), (frame_x + 22, 10), 2)
            # Staff
            pygame.draw.line(surface, LIGHT_PURPLE, (frame_x + 22, 10), (frame_x + 24, 5), 2)
            # Fireball launching
            pygame.draw.circle(surface, RED, (frame_x + 26, 5), 4)
            pygame.draw.circle(surface, ORANGE, (frame_x + 26, 5), 3)
            pygame.draw.circle(surface, YELLOW, (frame_x + 26, 5), 2)
            # Robe
            pygame.draw.line(surface, PURPLE, (frame_x + 14, 22), (frame_x + 12, 30), 2)
            pygame.draw.line(surface, PURPLE, (frame_x + 20, 22), (frame_x + 22, 30), 2)
            
        elif i == 4:  # Fireball flying
            # Body still leaning
            pygame.draw.line(surface, BLACK, (frame_x + 16, 12), (frame_x + 17, 22), 2)
            # Arms - extended
            pygame.draw.line(surface, BLACK, (frame_x + 17, 15), (frame_x + 23, 12), 2)
            # Staff
            pygame.draw.line(surface, LIGHT_PURPLE, (frame_x + 23, 12), (frame_x + 25, 8), 2)
            # Fireball flying
            pygame.draw.circle(surface, RED, (frame_x + 30, 8), 4)
            pygame.draw.circle(surface, ORANGE, (frame_x + 30, 8), 3)
            pygame.draw.circle(surface, YELLOW, (frame_x + 30, 8), 2)
            # Fireball trail
            pygame.draw.line(surface, ORANGE, (frame_x + 26, 8), (frame_x + 28, 8), 2)
            # Robe
            pygame.draw.line(surface, PURPLE, (frame_x + 14, 22), (frame_x + 12, 30), 2)
            pygame.draw.line(surface, PURPLE, (frame_x + 20, 22), (frame_x + 22, 30), 2)
            
        else:  # Return to stance
            # Body
            pygame.draw.line(surface, BLACK, (frame_x + 16, 12), (frame_x + 16, 22), 2)
            # Arms - lowering
            pygame.draw.line(surface, BLACK, (frame_x + 16, 15), (frame_x + 20, 18), 2)
            # Staff
            pygame.draw.line(surface, LIGHT_PURPLE, (frame_x + 20, 18), (frame_x + 24, 14), 2)
            # Staff fading glow
            pygame.draw.circle(surface, BLUE, (frame_x + 24, 14), 1)
            # Robe
            pygame.draw.line(surface, PURPLE, (frame_x + 13, 22), (frame_x + 11, 30), 2)
            pygame.draw.line(surface, PURPLE, (frame_x + 19, 22), (frame_x + 21, 30), 2)
    
    # Save the sprite sheet
    pygame.image.save(surface, os.path.join(sprites_dir, "mage_cast_stickman.png"))
    return "Created mage cast sprite sheet"

# Create both sprite sheets
warrior_result = create_warrior_attack_sheet()
mage_result = create_mage_cast_sheet()

print(f"{warrior_result}\n{mage_result}")
print(f"Sprite sheets saved to {sprites_dir}")
