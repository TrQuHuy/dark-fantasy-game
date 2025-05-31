import pygame
import os

class Animation:
    def __init__(self, sprite_sheet_path, frame_width, frame_height, frame_count, loop=True):
        self.frames = []
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_count = frame_count
        self.current_frame = 0
        self.animation_speed = 0.1  # Seconds per frame
        self.animation_timer = 0
        self.loop = loop
        self.finished = False
        
        # Load sprite sheet
        self.load_frames(sprite_sheet_path)
        
    def load_frames(self, sprite_sheet_path):
        try:
            # Ensure path exists
            if not os.path.exists(sprite_sheet_path):
                # Create a placeholder frame for missing sprite sheets
                placeholder = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                placeholder.fill((255, 0, 255, 128))  # Purple semi-transparent
                for i in range(self.frame_count):
                    self.frames.append(placeholder)
                return
                
            # Load sprite sheet
            sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
            
            # Extract frames
            for i in range(self.frame_count):
                frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (i * self.frame_width, 0, self.frame_width, self.frame_height))
                self.frames.append(frame)
                
        except Exception as e:
            # Create a placeholder frame for error cases
            placeholder = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            placeholder.fill((255, 0, 0, 128))  # Red semi-transparent
            for i in range(self.frame_count):
                self.frames.append(placeholder)
            
    def update(self, dt):
        if self.finished:
            return
            
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
                    
    def draw(self, screen, x, y, flip_x=False):
        if not self.frames:
            return
            
        frame = self.frames[self.current_frame]
        
        if flip_x:
            frame = pygame.transform.flip(frame, True, False)
            
        screen.blit(frame, (x, y))
        
    def reset(self):
        self.current_frame = 0
        self.animation_timer = 0
        self.finished = False
