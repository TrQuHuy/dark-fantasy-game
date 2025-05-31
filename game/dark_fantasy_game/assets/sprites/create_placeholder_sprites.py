import pygame
import os

# Initialize pygame
pygame.init()

# Create sprites directory if it doesn't exist
sprites_dir = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(sprites_dir):
    os.makedirs(sprites_dir)

# Function to create a placeholder sprite sheet
def create_sprite_sheet(filename, frame_count, color, secondary_color=None):
    width = 64 * frame_count
    height = 64
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for i in range(frame_count):
        # Draw character base
        frame_x = i * 64
        
        # Body
        pygame.draw.rect(surface, color, (frame_x + 24, 16, 16, 32))
        
        # Head
        pygame.draw.circle(surface, color, (frame_x + 32, 12), 8)
        
        # Arms
        arm_y = 20 + (i % 2) * 4  # Make arms move slightly for animation
        pygame.draw.rect(surface, color, (frame_x + 16, arm_y, 8, 20))  # Left arm
        pygame.draw.rect(surface, color, (frame_x + 40, arm_y, 8, 20))  # Right arm
        
        # Legs
        leg_offset = (i % 3) * 2  # Make legs move for walking animation
        pygame.draw.rect(surface, color, (frame_x + 24, 48, 6, 16 - leg_offset))  # Left leg
        pygame.draw.rect(surface, color, (frame_x + 34, 48, 6, 16 + leg_offset))  # Right leg
        
        # Add secondary color elements if provided
        if secondary_color:
            # For warrior: sword
            if "warrior" in filename:
                sword_x = frame_x + 48 + (i % 2) * 2
                pygame.draw.rect(surface, secondary_color, (sword_x, 20, 4, 24))
                
                # Add sword glow for attack animation
                if "attack" in filename:
                    glow_size = 6 + (i % 3) * 2
                    pygame.draw.circle(surface, (255, 165, 0, 128), (sword_x + 2, 32), glow_size)
                
            # For mage: staff and glow
            elif "mage" in filename:
                staff_x = frame_x + 48
                pygame.draw.rect(surface, secondary_color, (staff_x, 16, 2, 32))
                
                # Add staff glow
                glow_size = 4 + (i % 3) * 2
                pygame.draw.circle(surface, (255, 255, 255, 200), (staff_x + 1, 16), glow_size)
                
                # Add projectile for cast animation
                if "cast" in filename and i >= 2:
                    proj_x = frame_x + 52 + (i * 3)
                    proj_y = 16 - (i * 2)
                    proj_size = 4 + i
                    pygame.draw.circle(surface, (138, 43, 226), (proj_x, proj_y), proj_size)
                    pygame.draw.circle(surface, (255, 255, 255), (proj_x, proj_y), proj_size // 2)
    
    # Save the sprite sheet
    pygame.image.save(surface, os.path.join(sprites_dir, filename))
    print(f"Created {filename}")

# Create warrior sprite sheets
create_sprite_sheet("warrior_idle.png", 4, (0, 0, 0), (139, 0, 0))
create_sprite_sheet("warrior_walk.png", 6, (0, 0, 0), (139, 0, 0))
create_sprite_sheet("warrior_attack.png", 4, (0, 0, 0), (255, 165, 0))
create_sprite_sheet("warrior_hurt.png", 2, (0, 0, 0), (139, 0, 0))
create_sprite_sheet("warrior_death.png", 5, (0, 0, 0), (139, 0, 0))

# Create mage sprite sheets
create_sprite_sheet("mage_idle.png", 4, (75, 0, 130), (138, 43, 226))
create_sprite_sheet("mage_glide.png", 6, (75, 0, 130), (138, 43, 226))
create_sprite_sheet("mage_cast.png", 5, (75, 0, 130), (138, 43, 226))
create_sprite_sheet("mage_hurt.png", 2, (75, 0, 130), (138, 43, 226))
create_sprite_sheet("mage_death.png", 6, (75, 0, 130), (138, 43, 226))

# Create monster sprite sheets
create_sprite_sheet("goblin_idle.png", 4, (0, 150, 0), (0, 100, 0))
create_sprite_sheet("goblin_walk.png", 6, (0, 150, 0), (0, 100, 0))
create_sprite_sheet("goblin_attack.png", 4, (0, 150, 0), (0, 100, 0))
create_sprite_sheet("goblin_hurt.png", 2, (0, 150, 0), (0, 100, 0))
create_sprite_sheet("goblin_death.png", 5, (0, 150, 0), (0, 100, 0))

create_sprite_sheet("skeleton_idle.png", 4, (200, 200, 200), (150, 150, 150))
create_sprite_sheet("skeleton_walk.png", 6, (200, 200, 200), (150, 150, 150))
create_sprite_sheet("skeleton_attack.png", 4, (200, 200, 200), (150, 150, 150))
create_sprite_sheet("skeleton_hurt.png", 2, (200, 200, 200), (150, 150, 150))
create_sprite_sheet("skeleton_death.png", 5, (200, 200, 200), (150, 150, 150))

print("All sprite sheets created successfully!")
pygame.quit()
