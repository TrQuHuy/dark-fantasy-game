import pygame
import random
from dark_fantasy_game.src.player_enhanced import Player
from dark_fantasy_game.src.monster import Monster, MonsterType
from dark_fantasy_game.src.wave_manager import WaveManager
from dark_fantasy_game.src.map import Map
from dark_fantasy_game.src.day_night_cycle import DayNightCycle
from dark_fantasy_game.src.status_effects import StatusEffect, StatusEffectType
from dark_fantasy_game.src.stats import CharacterClass

# Game states
class State:
    MAIN_MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    VICTORY = 4

class GameState:
    def __init__(self):
        self.state = State.MAIN_MENU
        self.player = Player(400, 300, CharacterClass.WARRIOR)
        self.monsters = []
        self.wave_manager = WaveManager()
        self.score = 0
        self.level = 1
        self.infinity_mode = False
        
        # Tạo map mới
        self.game_map = Map(50, 50)  # Map 50x50 tiles
        
        # Camera position
        self.camera_x = 0
        self.camera_y = 0
        
        # Day/night cycle
        self.day_night_cycle = DayNightCycle()
        
        # UI elements
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.buttons = {}
        
        # Screen dimensions
        self.screen_width = 800
        self.screen_height = 600
        
        # Initialize main menu buttons
        self.init_main_menu()
        
    def init_main_menu(self):
        """Initialize main menu buttons"""
        self.buttons = {
            "start": pygame.Rect(300, 200, 200, 50),
            "warrior": pygame.Rect(250, 300, 150, 50),
            "mage": pygame.Rect(450, 300, 150, 50),
            "infinity": pygame.Rect(300, 350, 200, 50),
            "quit": pygame.Rect(300, 450, 200, 50)
        }
        
    def handle_event(self, event, scale_x=1.0, scale_y=1.0):
        """Handle game events"""
        if self.state == State.PLAYING:
            # Pass events to player when playing
            self.player.handle_event(event, scale_x, scale_y)
            
            # Handle pause
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = State.PAUSED
            
            # Toggle minimap visibility with M key
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.game_map.minimap.toggle_zoom()
                
        elif self.state == State.MAIN_MENU:
            # Handle main menu clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Sử dụng tọa độ chuột thực tế, không chia cho tỷ lệ
                    pos = event.pos
                    
                    # Kiểm tra va chạm với các nút đã được điều chỉnh tỷ lệ
                    for name, rect in self.buttons.items():
                        scaled_rect = pygame.Rect(
                            int(rect.x * scale_x),
                            int(rect.y * scale_y),
                            int(rect.width * scale_x),
                            int(rect.height * scale_y)
                        )
                        
                        if scaled_rect.collidepoint(pos):
                            if name == "start":
                                self.state = State.PLAYING
                                self.start_game()
                            elif name == "warrior":
                                self.player = Player(400, 300, CharacterClass.WARRIOR)
                            elif name == "mage":
                                self.player = Player(400, 300, CharacterClass.MAGE)
                            elif name == "infinity":
                                self.infinity_mode = self.wave_manager.toggle_infinity_mode()
                            elif name == "quit":
                                return False  # Signal to quit
                        
        elif self.state == State.PAUSED:
            # Handle unpausing
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = State.PLAYING
                
        elif self.state in [State.GAME_OVER, State.VICTORY]:
            # Handle restart from game over or victory
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.state = State.MAIN_MENU
                self.init_main_menu()
                
        return True
        
    def handle_continuous_input(self, scale_x=1.0, scale_y=1.0):
        """Handle continuous input (keys held down)"""
        if self.state == State.PLAYING:
            # Player movement is handled in player.update()
            pass
            
    def start_game(self):
        """Start a new game"""
        self.monsters = []
        self.score = 0
        self.level = 1
        self.wave_manager.start_wave(self.level)
        
    def update(self):
        """Update game state"""
        if self.state == State.PLAYING:
            # Update day/night cycle
            self.day_night_cycle.update()
            
            # Update player with delta time for animations
            self.player.update(1/60, self.game_map)
            
            # Update camera to follow player
            self.update_camera()
            
            # Update monsters
            for monster in list(self.monsters):
                monster.update(self.player, self.game_map)
                
                # Check for collisions with player attack
                attack_rect = self.player.get_attack_rect()
                if attack_rect and self.player.attack_animation_timer > 0:
                    # Tạo một bản sao của attack_rect để không ảnh hưởng đến rect gốc
                    real_attack_rect = pygame.Rect(
                        attack_rect.x, 
                        attack_rect.y,
                        attack_rect.width,
                        attack_rect.height
                    )
                    
                    # Tạo một bản sao của monster rect để kiểm tra va chạm
                    monster_rect = pygame.Rect(
                        monster.x,
                        monster.y,
                        monster.width,
                        monster.height
                    )
                    
                    # Kiểm tra va chạm
                    if real_attack_rect.colliderect(monster_rect):
                        # Player hit monster with attack
                        damage = self.player.stats.physical_damage if self.player.character_class == CharacterClass.WARRIOR else self.player.stats.magic_damage
                        print(f"Hit monster! Damage: {damage}")
                        monster.take_damage(damage)
                        
                        # Apply status effects based on character class
                        if self.player.character_class == CharacterClass.WARRIOR:
                            # Warriors have a chance to apply stun
                            if random.random() < 0.2:  # 20% chance
                                monster.add_status_effect(StatusEffectType.STUN, 60)  # 1 second stun
                        else:  # Mage
                            # Mages have a chance to apply burn
                            if random.random() < 0.3:  # 30% chance
                                monster.add_status_effect(StatusEffectType.BURN, 180, 0.5)  # 3 seconds burn
                        
                        if monster.health <= 0:
                            self.monsters.remove(monster)
                            self.score += monster.score_value
                            
                            # Add experience to player
                            self.player.add_experience(monster.score_value // 2)
                
                # Check if monster is attacking player
                if monster.is_attacking and monster.is_player_in_range(self.player):
                    # Monster hit player
                    self.player.take_damage(monster.damage)
                    
                    # Monsters have a chance to apply status effects
                    if monster.monster_type == MonsterType.GOBLIN:
                        if random.random() < 0.1:  # 10% chance
                            self.player.add_status_effect(StatusEffectType.POISON, 180, 0.5)
                    elif monster.monster_type == MonsterType.SKELETON:
                        if random.random() < 0.15:  # 15% chance
                            self.player.add_status_effect(StatusEffectType.SLOW, 120, 0.3)
                    
                    if self.player.stats.current_health <= 0:
                        self.state = State.GAME_OVER
            
            # Check if wave is complete
            if len(self.monsters) == 0 and self.wave_manager.is_wave_complete():
                if not self.infinity_mode and self.level >= self.wave_manager.max_waves:
                    self.state = State.VICTORY
                else:
                    self.level += 1
                    self.wave_manager.start_wave(self.level)
                    
            # Spawn monsters if needed
            new_monster = self.wave_manager.update()
            if new_monster:
                # Spawn monster at a valid location on the map
                self.spawn_monster_at_valid_location(new_monster)
                
    def spawn_monster_at_valid_location(self, monster):
        """Spawn monster at a valid location on the map"""
        max_attempts = 50
        attempts = 0
        
        while attempts < max_attempts:
            # Try to find a valid spawn location
            if monster.x < 0:  # Left side
                monster.x = random.randint(50, 150)
            elif monster.x > 800:  # Right side
                monster.x = random.randint(650, 750)
            elif monster.y < 0:  # Top
                monster.y = random.randint(50, 150)
            else:  # Bottom
                monster.y = random.randint(450, 550)
                
            # Check if location is valid
            if self.game_map.is_passable(monster.x, monster.y):
                self.monsters.append(monster)
                return
                
            attempts += 1
            
        # If no valid location found, just add the monster anyway
        self.monsters.append(monster)
        
    def update_camera(self):
        """Update camera position to follow player"""
        # Center camera on player
        target_x = self.player.x - self.screen_width / 2
        target_y = self.player.y - self.screen_height / 2
        
        # Smooth camera movement
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        # Keep camera within map bounds
        max_camera_x = self.game_map.width * self.game_map.tile_size - self.screen_width
        max_camera_y = self.game_map.height * self.game_map.tile_size - self.screen_height
        
        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))
    
    def update_scale(self, scale_x, scale_y):
        """Update scale factors for UI elements"""
        # Update screen dimensions
        self.screen_width = int(800 * scale_x)
        self.screen_height = int(600 * scale_y)
                
    def draw(self, screen, scale_x=1.0, scale_y=1.0):
        """Draw the current game state"""
        if self.state == State.MAIN_MENU:
            self.draw_main_menu(screen, scale_x, scale_y)
        elif self.state == State.PLAYING:
            self.draw_game(screen, scale_x, scale_y)
        elif self.state == State.PAUSED:
            self.draw_game(screen, scale_x, scale_y)
            self.draw_pause_screen(screen, scale_x, scale_y)
        elif self.state == State.GAME_OVER:
            self.draw_game_over(screen, scale_x, scale_y)
        elif self.state == State.VICTORY:
            self.draw_victory(screen, scale_x, scale_y)
            
    def draw_main_menu(self, screen, scale_x, scale_y):
        """Draw the main menu"""
        # Title
        title_font = pygame.font.SysFont(None, int(72 * min(scale_x, scale_y)))
        title_text = title_font.render("Dark Fantasy Stickman", True, (255, 215, 0))
        title_x = (self.screen_width - title_text.get_width()) // 2
        screen.blit(title_text, (title_x, int(100 * scale_y)))
        
        # Draw buttons
        for name, rect in self.buttons.items():
            scaled_rect = pygame.Rect(
                int(rect.x * scale_x),
                int(rect.y * scale_y),
                int(rect.width * scale_x),
                int(rect.height * scale_y)
            )
            
            # Button background
            color = (100, 100, 200)
            
            # Highlight selected options
            if name == "warrior" and self.player.character_class == CharacterClass.WARRIOR:
                color = (150, 150, 255)
            elif name == "mage" and self.player.character_class == CharacterClass.MAGE:
                color = (150, 150, 255)
            elif name == "infinity" and self.infinity_mode:
                color = (150, 150, 255)
            
            pygame.draw.rect(screen, color, scaled_rect)
            pygame.draw.rect(screen, (200, 200, 200), scaled_rect, 2)
            
            # Button text
            button_text = self.font.render(name.capitalize(), True, (255, 255, 255))
            text_x = scaled_rect.centerx - button_text.get_width() // 2
            text_y = scaled_rect.centery - button_text.get_height() // 2
            screen.blit(button_text, (text_x, text_y))
            
        # Instructions
        instructions = [
            "Choose your character class and press Start",
            "Use WASD to move, SPACE to attack",
            "Press TAB to view stats, I for inventory",
            "Press 1-3 to select abilities, Q to activate",
            "Infinity mode: Endless waves with increasing difficulty"
        ]
        
        y_pos = int(480 * scale_y)
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, (200, 200, 200))
            inst_x = (self.screen_width - inst_text.get_width()) // 2
            screen.blit(inst_text, (inst_x, y_pos))
            y_pos += int(25 * scale_y)
            
    def draw_game(self, screen, scale_x, scale_y):
        """Draw the main gameplay screen"""
        # Draw map
        self.game_map.draw(screen, self.camera_x, self.camera_y, scale_x, scale_y)
        
        # Draw monsters
        for monster in self.monsters:
            # Adjust position for camera
            monster_x = monster.x
            monster_y = monster.y
            monster.x = monster_x - self.camera_x
            monster.y = monster_y - self.camera_y
            monster.draw(screen, scale_x, scale_y)
            monster.x, monster.y = monster_x, monster_y
            
        # Draw player (adjusted for camera)
        player_x = self.player.x
        player_y = self.player.y
        self.player.x -= self.camera_x
        self.player.y -= self.camera_y
        self.player.draw(screen, scale_x, scale_y)
        self.player.x, self.player.y = player_x, player_y
        
        # Apply day/night lighting
        self.day_night_cycle.apply_lighting(screen)
        
        # Draw minimap
        self.game_map.minimap.draw(screen, player_x, player_y)
        
        # Draw HUD
        self.draw_hud(screen, scale_x, scale_y)
        
    def draw_hud(self, screen, scale_x, scale_y):
        """Draw the heads-up display"""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (int(20 * scale_x), int(20 * scale_y)))
        
        # Level/Wave
        if self.infinity_mode and self.level > self.wave_manager.max_waves:
            level_text = self.font.render(f"Infinity Wave: {self.level}", True, (255, 215, 0))
        else:
            level_text = self.font.render(f"Wave: {self.level}/{self.wave_manager.max_waves}", True, (255, 255, 255))
        screen.blit(level_text, (int(20 * scale_x), int(60 * scale_y)))
        
        # Player level and experience
        level_text = self.font.render(f"Level: {self.player.level}", True, (255, 255, 255))
        screen.blit(level_text, (int(20 * scale_x), int(100 * scale_y)))
        
        # Time of day
        time_text = self.font.render(f"Time: {self.day_night_cycle.get_time_string()} ({self.day_night_cycle.get_time_of_day().capitalize()})", 
                                    True, (255, 255, 255))
        time_x = self.screen_width - time_text.get_width() - int(20 * scale_x)
        screen.blit(time_text, (time_x, int(60 * scale_y)))
        
        # Health
        health_text = self.font.render(f"HP: {self.player.stats.current_health}/{self.player.stats.max_health}", True, (255, 0, 0))
        health_x = self.screen_width - health_text.get_width() - int(20 * scale_x)
        screen.blit(health_text, (health_x, int(20 * scale_y)))
        
        # Character class
        class_text = self.font.render(f"Class: {self.player.character_class.value}", True, (255, 255, 255))
        class_x = self.screen_width - class_text.get_width() - int(20 * scale_x)
        screen.blit(class_text, (class_x, int(100 * scale_y)))
        
    def draw_pause_screen(self, screen, scale_x, scale_y):
        """Draw the pause screen overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font.render("PAUSED", True, (255, 255, 255))
        pause_x = (self.screen_width - pause_text.get_width()) // 2
        pause_y = (self.screen_height - pause_text.get_height()) // 2 - int(50 * scale_y)
        screen.blit(pause_text, (pause_x, pause_y))
        
        # Instructions
        instructions = [
            "Press ESC to resume",
            "Press TAB to view stats",
            "Press I to view inventory",
            "Press 1-3 to select abilities, Q to activate"
        ]
        
        y_pos = pause_y + int(50 * scale_y)
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, (200, 200, 200))
            inst_x = (self.screen_width - inst_text.get_width()) // 2
            screen.blit(inst_text, (inst_x, y_pos))
            y_pos += int(30 * scale_y)
            
    def draw_game_over(self, screen, scale_x, scale_y):
        """Draw the game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_font = pygame.font.SysFont(None, int(72 * min(scale_x, scale_y)))
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        game_over_x = (self.screen_width - game_over_text.get_width()) // 2
        game_over_y = (self.screen_height - game_over_text.get_height()) // 2 - int(50 * scale_y)
        screen.blit(game_over_text, (game_over_x, game_over_y))
        
        # Score
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        score_x = (self.screen_width - score_text.get_width()) // 2
        score_y = game_over_y + int(100 * scale_y)
        screen.blit(score_text, (score_x, score_y))
        
        # Wave reached
        if self.infinity_mode and self.level > self.wave_manager.max_waves:
            wave_text = self.font.render(f"Infinity Wave Reached: {self.level}", True, (255, 215, 0))
        else:
            wave_text = self.font.render(f"Wave Reached: {self.level}/{self.wave_manager.max_waves}", True, (255, 255, 255))
        wave_x = (self.screen_width - wave_text.get_width()) // 2
        wave_y = score_y + int(50 * scale_y)
        screen.blit(wave_text, (wave_x, wave_y))
        
        # Player level
        level_text = self.font.render(f"Player Level: {self.player.level}", True, (255, 255, 255))
        level_x = (self.screen_width - level_text.get_width()) // 2
        level_y = wave_y + int(50 * scale_y)
        screen.blit(level_text, (level_x, level_y))
        
        # Restart instructions
        restart_text = self.font.render("Press R to return to main menu", True, (200, 200, 200))
        restart_x = (self.screen_width - restart_text.get_width()) // 2
        restart_y = level_y + int(100 * scale_y)
        screen.blit(restart_text, (restart_x, restart_y))
        
    def draw_victory(self, screen, scale_x, scale_y):
        """Draw the victory screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Victory text
        victory_font = pygame.font.SysFont(None, int(72 * min(scale_x, scale_y)))
        victory_text = victory_font.render("VICTORY!", True, (0, 255, 0))
        victory_x = (self.screen_width - victory_text.get_width()) // 2
        victory_y = (self.screen_height - victory_text.get_height()) // 2 - int(50 * scale_y)
        screen.blit(victory_text, (victory_x, victory_y))
        
        # Score
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        score_x = (self.screen_width - score_text.get_width()) // 2
        score_y = victory_y + int(100 * scale_y)
        screen.blit(score_text, (score_x, score_y))
        
        # Player level
        level_text = self.font.render(f"Player Level: {self.player.level}", True, (255, 255, 255))
        level_x = (self.screen_width - level_text.get_width()) // 2
        level_y = score_y + int(50 * scale_y)
        screen.blit(level_text, (level_x, level_y))
        
        # Try infinity mode message
        if not self.infinity_mode:
            infinity_text = self.font.render("Try Infinity Mode for endless challenges!", True, (255, 215, 0))
            infinity_x = (self.screen_width - infinity_text.get_width()) // 2
            infinity_y = level_y + int(50 * scale_y)
            screen.blit(infinity_text, (infinity_x, infinity_y))
        
        # Restart instructions
        restart_text = self.font.render("Press R to return to main menu", True, (200, 200, 200))
        restart_x = (self.screen_width - restart_text.get_width()) // 2
        restart_y = level_y + int(100 * scale_y)
        screen.blit(restart_text, (restart_x, restart_y))
