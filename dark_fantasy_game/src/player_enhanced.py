import pygame
import math
import os
from dark_fantasy_game.src.stats import Stats, CharacterClass
from dark_fantasy_game.src.inventory import Inventory
from dark_fantasy_game.src.animation import Animation
from dark_fantasy_game.src.abilities import WhirlwindAbility, ShieldBashAbility, ChargeAbility, TeleportAbility, FrostNovaAbility, MeteorAbility
from dark_fantasy_game.src.status_effects import StatusEffect, StatusEffectType

class Player:
    def __init__(self, x=400, y=300, character_class=CharacterClass.WARRIOR):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64
        self.speed = 5
        self.character_class = character_class
        self.stats = Stats(character_class)
        self.inventory = Inventory()
        
        # Movement
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False
        
        # Combat
        self.attacking = False
        self.attack_cooldown = 0
        self.attack_cooldown_max = 30  # frames
        self.attack_direction = 1  # 1: right, -1: left
        self.attack_animation_timer = 0
        self.attack_animation_frames = 15  # frames for attack animation
        self.attack_range = 80  # attack range in pixels
        
        # UI
        self.show_stats = False
        self.show_inventory = False
        
        # Animation
        self.facing_right = True
        self.current_state = "idle"
        self.load_animations()
        
        # Status effects
        self.status_effects = []
        self.is_stunned = False
        self.speed_multiplier = 1.0
        self.attack_speed_multiplier = 1.0
        
        # Abilities
        self.init_abilities()
        
        # Experience and level
        self.level = 1
        self.experience = 0
        self.skill_points = 0
        
    def init_abilities(self):
        """Initialize abilities based on character class"""
        if self.character_class == CharacterClass.WARRIOR:
            self.abilities = {
                "1": WhirlwindAbility(),
                "2": ShieldBashAbility(),
                "3": ChargeAbility()
            }
        else:  # Mage
            self.abilities = {
                "1": TeleportAbility(),
                "2": FrostNovaAbility(),
                "3": MeteorAbility()
            }
        
        # Selected ability (1, 2, or 3)
        self.selected_ability = "1"
        
    def load_animations(self):
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sprites")
        
        # Define animations based on character class
        if self.character_class == CharacterClass.WARRIOR:
            self.animations = {
                "idle": Animation(os.path.join(base_path, "warrior_idle.png"), 64, 64, 4),
                "walk": Animation(os.path.join(base_path, "warrior_walk.png"), 64, 64, 6),
                "attack": Animation(os.path.join(base_path, "warrior_attack.png"), 64, 64, 4, loop=False),
                "hurt": Animation(os.path.join(base_path, "warrior_hurt.png"), 64, 64, 2, loop=False),
                "death": Animation(os.path.join(base_path, "warrior_death.png"), 64, 64, 5, loop=False)
            }
        else:  # Mage
            self.animations = {
                "idle": Animation(os.path.join(base_path, "mage_idle.png"), 64, 64, 4),
                "walk": Animation(os.path.join(base_path, "mage_glide.png"), 64, 64, 6),
                "attack": Animation(os.path.join(base_path, "mage_cast.png"), 64, 64, 5, loop=False),
                "hurt": Animation(os.path.join(base_path, "mage_hurt.png"), 64, 64, 2, loop=False),
                "death": Animation(os.path.join(base_path, "mage_death.png"), 64, 64, 6, loop=False)
            }
        
        self.current_animation = self.animations["idle"]
        
    def handle_event(self, event, scale_x=1.0, scale_y=1.0):
        """Handle player input events"""
        # Skip input handling if stunned
        if self.is_stunned:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.moving_left = True
                self.facing_right = False
                self.attack_direction = -1
                self.set_animation("walk")
            elif event.key == pygame.K_d:
                self.moving_right = True
                self.facing_right = True
                self.attack_direction = 1
                self.set_animation("walk")
            elif event.key == pygame.K_w:
                self.moving_up = True
                self.set_animation("walk")
            elif event.key == pygame.K_s:
                self.moving_down = True
                self.set_animation("walk")
            elif event.key == pygame.K_SPACE:
                self.attacking = True
                self.attack_animation_timer = self.attack_animation_frames
                self.set_animation("attack")
            elif event.key == pygame.K_TAB:
                self.show_stats = not self.show_stats
            elif event.key == pygame.K_i:
                self.show_inventory = not self.show_inventory
            elif event.key == pygame.K_c:
                self.switch_character_class()
            # Ability selection
            elif event.key == pygame.K_1:
                self.selected_ability = "1"
                print(f"Selected ability: {self.abilities[self.selected_ability].ability_type.value}")
            elif event.key == pygame.K_2:
                self.selected_ability = "2"
                print(f"Selected ability: {self.abilities[self.selected_ability].ability_type.value}")
            elif event.key == pygame.K_3:
                self.selected_ability = "3"
                print(f"Selected ability: {self.abilities[self.selected_ability].ability_type.value}")
            # Ability activation
            elif event.key == pygame.K_q:
                self.activate_ability()
                
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.moving_left = False
                if not any([self.moving_right, self.moving_up, self.moving_down]):
                    self.set_animation("idle")
            elif event.key == pygame.K_d:
                self.moving_right = False
                if not any([self.moving_left, self.moving_up, self.moving_down]):
                    self.set_animation("idle")
            elif event.key == pygame.K_w:
                self.moving_up = False
                if not any([self.moving_left, self.moving_right, self.moving_down]):
                    self.set_animation("idle")
            elif event.key == pygame.K_s:
                self.moving_down = False
                if not any([self.moving_left, self.moving_right, self.moving_up]):
                    self.set_animation("idle")
            elif event.key == pygame.K_SPACE:
                self.attacking = False
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Sử dụng tọa độ chuột thực tế, không điều chỉnh
                if self.show_stats:
                    # Kiểm tra xem chuột có nằm trong khu vực bảng chỉ số không
                    stats_panel = pygame.Rect(50, 50, 300, 400)  # x, y, width, height
                    scaled_stats_panel = pygame.Rect(
                        int(stats_panel.x * scale_x),
                        int(stats_panel.y * scale_y),
                        int(stats_panel.width * scale_x),
                        int(stats_panel.height * scale_y)
                    )
                    
                    if scaled_stats_panel.collidepoint(event.pos):
                        self.stats.handle_click(event.pos)
                        
                if self.show_inventory:
                    # Kiểm tra xem chuột có nằm trong khu vực túi đồ không
                    inventory_panel = pygame.Rect(400, 50, 350, 400)  # x, y, width, height
                    scaled_inventory_panel = pygame.Rect(
                        int(inventory_panel.x * scale_x),
                        int(inventory_panel.y * scale_y),
                        int(inventory_panel.width * scale_x),
                        int(inventory_panel.height * scale_y)
                    )
                    
                    if scaled_inventory_panel.collidepoint(event.pos):
                        self.inventory.handle_click(event.pos)
    
    def activate_ability(self):
        """Activate the selected ability"""
        ability = self.abilities.get(self.selected_ability)
        if ability:
            if ability.activate(self):
                print(f"Activated {ability.ability_type.value}!")
                return True
        return False
        
    def add_status_effect(self, effect_type, duration, strength=1.0):
        """Add a status effect to the player"""
        # Check if effect already exists
        for effect in self.status_effects:
            if effect.effect_type == effect_type:
                # Refresh duration if effect already exists
                effect.remaining = max(effect.remaining, duration)
                return
                
        # Add new effect
        effect = StatusEffect(effect_type, duration, strength)
        self.status_effects.append(effect)
        print(f"Applied {effect_type.value} effect!")
        
    def update_status_effects(self):
        """Update all status effects"""
        for effect in list(self.status_effects):
            # Apply effect
            effect.apply_effect(self)
            
            # Update duration
            if not effect.update():
                # Remove expired effect
                effect.remove_effect(self)
                self.status_effects.remove(effect)
                print(f"{effect.effect_type.value} effect expired")
    
    def set_animation(self, animation_name):
        if animation_name in self.animations and self.current_state != animation_name:
            self.current_state = animation_name
            self.current_animation = self.animations[animation_name]
            self.current_animation.reset()
    
    def switch_character_class(self):
        """Switch between Warrior and Mage"""
        if self.character_class == CharacterClass.WARRIOR:
            self.character_class = CharacterClass.MAGE
        else:
            self.character_class = CharacterClass.WARRIOR
            
        self.stats = Stats(self.character_class)
        self.load_animations()
        self.init_abilities()
        print(f"Switched to {self.character_class.value}")
    
    def update(self, dt=1/60, game_map=None):
        """Update player state"""
        # Update status effects
        self.update_status_effects()
        
        # Skip movement if stunned
        if not self.is_stunned:
            old_x, old_y = self.x, self.y
            
            # Apply speed multiplier from status effects
            actual_speed = self.speed * self.speed_multiplier
            
            # Movement
            if self.moving_left:
                self.x -= actual_speed
                self.facing_right = False
                self.attack_direction = -1
            if self.moving_right:
                self.x += actual_speed
                self.facing_right = True
                self.attack_direction = 1
            if self.moving_up:
                self.y -= actual_speed
            if self.moving_down:
                self.y += actual_speed
                
            # Check if new position is valid (if map is provided)
            if game_map:
                if not game_map.is_passable(self.x, self.y):
                    # Revert to old position if not passable
                    self.x, self.y = old_x, old_y
            
            # Keep player on screen
            self.x = max(0, min(800 - self.width, self.x))
            self.y = max(0, min(600 - self.height, self.y))
        
        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        # Attack animation timer
        if self.attack_animation_timer > 0:
            self.attack_animation_timer -= 1
            
        # Handle attack
        if self.attacking and self.attack_cooldown == 0 and not self.is_stunned:
            self.perform_attack()
            self.attack_cooldown = self.attack_cooldown_max
            self.attack_animation_timer = self.attack_animation_frames
            self.set_animation("attack")
            
        # Update current animation
        self.current_animation.update(dt)
        
        # If attack animation finished, return to idle or walk
        if self.current_state == "attack" and self.current_animation.finished:
            if any([self.moving_left, self.moving_right, self.moving_up, self.moving_down]):
                self.set_animation("walk")
            else:
                self.set_animation("idle")
                
        # Update abilities
        for ability in self.abilities.values():
            ability.update()
    
    def perform_attack(self):
        """Perform an attack based on character class"""
        if self.character_class == CharacterClass.WARRIOR:
            print(f"Warrior attacks for {self.stats.physical_damage} physical damage!")
        else:
            print(f"Mage casts a spell for {self.stats.magic_damage} magic damage!")
    
    def draw(self, screen, scale_x=1.0, scale_y=1.0):
        """Draw the player and UI elements"""
        # Calculate scaled position
        scaled_x = int(self.x * scale_x)
        scaled_y = int(self.y * scale_y)
        
        # Draw current animation frame
        self.current_animation.draw(screen, scaled_x, scaled_y, not self.facing_right)
        
        # Draw attack animation if attacking
        if self.attack_animation_timer > 0:
            self.draw_attack_animation(screen, scale_x, scale_y)
            
        # Draw active ability effects
        for ability in self.abilities.values():
            if ability.is_active:
                if hasattr(ability, 'draw'):
                    if ability.ability_type.name in ["WHIRLWIND", "FROST_NOVA"]:
                        ability.draw(screen, self.x, self.y, scale_x, scale_y)
                    elif ability.ability_type.name in ["SHIELD_BASH", "CHARGE"]:
                        ability.draw(screen, self.x, self.y, self.attack_direction, scale_x, scale_y)
        
        # Draw health bar
        health_width = int(100 * scale_x)
        health_height = int(10 * scale_y)
        health_x = scaled_x - int(20 * scale_x)
        health_y = scaled_y - int(20 * scale_y)
        
        # Background (empty health)
        pygame.draw.rect(screen, (100, 0, 0), (health_x, health_y, health_width, health_height))
        
        # Foreground (current health)
        health_percent = self.stats.current_health / self.stats.max_health
        current_health_width = int(health_width * health_percent)
        pygame.draw.rect(screen, (255, 0, 0), (health_x, health_y, current_health_width, health_height))
        
        # Draw character class indicator
        font = pygame.font.SysFont(None, 24)
        class_text = font.render(self.character_class.value, True, (255, 255, 255))
        screen.blit(class_text, (scaled_x, scaled_y - int(30 * scale_y)))
        
        # Draw status effects
        self.draw_status_effects(screen, scaled_x, scaled_y - int(50 * scale_y))
        
        # Draw ability cooldowns
        self.draw_ability_cooldowns(screen, scaled_x, scaled_y + int(70 * scale_y))
        
        # Draw stats panel if active
        if self.show_stats:
            self.stats.draw_stats_panel(screen, 50, 50)
            
        # Draw inventory if active
        if self.show_inventory:
            self.inventory.draw(screen, 400, 50)
            
    def draw_status_effects(self, screen, x, y):
        """Draw status effect icons"""
        icon_size = 20
        spacing = 5
        
        for i, effect in enumerate(self.status_effects):
            icon_x = x + (icon_size + spacing) * i
            pygame.draw.rect(screen, effect.get_icon_color(), (icon_x, y, icon_size, icon_size))
            
            # Draw remaining time indicator
            remaining_percent = effect.remaining / effect.duration
            indicator_height = int(icon_size * remaining_percent)
            pygame.draw.rect(screen, (255, 255, 255), 
                           (icon_x, y + icon_size - indicator_height, 3, indicator_height))
            
    def draw_ability_cooldowns(self, screen, x, y):
        """Draw ability cooldown indicators"""
        width = 30
        height = 30
        spacing = 10
        
        for i, (key, ability) in enumerate(self.abilities.items()):
            # Position
            ability_x = x + (width + spacing) * i
            
            # Background
            color = (50, 50, 50)
            if key == self.selected_ability:
                color = (100, 100, 100)  # Highlight selected ability
            pygame.draw.rect(screen, color, (ability_x, y, width, height))
            
            # Cooldown overlay
            cooldown_percent = ability.get_cooldown_percent()
            if cooldown_percent > 0:
                cooldown_height = int(height * cooldown_percent)
                pygame.draw.rect(screen, (100, 100, 100, 150), 
                               (ability_x, y, width, cooldown_height))
            
            # Key number
            font = pygame.font.SysFont(None, 20)
            key_text = font.render(key, True, (255, 255, 255))
            screen.blit(key_text, (ability_x + 5, y + 5))
            
    def draw_attack_animation(self, screen, scale_x, scale_y):
        """Draw the attack animation"""
        scaled_x = int(self.x * scale_x)
        scaled_y = int(self.y * scale_y)
        scaled_width = int(self.width * scale_x)
        scaled_height = int(self.height * scale_y)
        
        # Calculate attack area
        attack_width = int(self.attack_range * scale_x)
        attack_height = int(self.height * scale_y)
        
        # Position attack area based on direction
        if self.attack_direction > 0:  # Right
            attack_x = scaled_x + scaled_width
            attack_y = scaled_y
        else:  # Left
            attack_x = scaled_x - attack_width
            attack_y = scaled_y
        
        # Draw attack area with transparency based on animation timer
        alpha = int(200 * (self.attack_animation_timer / self.attack_animation_frames))
        
        # Create a surface for the attack area
        attack_surface = pygame.Surface((attack_width, attack_height), pygame.SRCALPHA)
        
        # Fill with color based on character class
        if self.character_class == CharacterClass.WARRIOR:
            attack_color = (255, 165, 0, alpha)  # Orange for warrior
        else:
            attack_color = (138, 43, 226, alpha)  # Purple for mage
            
        pygame.draw.rect(attack_surface, attack_color, (0, 0, attack_width, attack_height))
        
        # Draw attack pattern
        if self.character_class == CharacterClass.WARRIOR:
            # Draw slash lines for warrior
            for i in range(3):
                line_y = i * (attack_height // 3)
                line_width = 3
                pygame.draw.line(attack_surface, (255, 255, 255, alpha), 
                                (0, line_y), (attack_width, line_y + attack_height // 3), line_width)
        else:
            # Draw magic circles for mage
            circle_radius = min(attack_width, attack_height) // 4
            pygame.draw.circle(attack_surface, (255, 255, 255, alpha), 
                              (attack_width // 2, attack_height // 2), circle_radius)
            pygame.draw.circle(attack_surface, (100, 100, 255, alpha), 
                              (attack_width // 2, attack_height // 2), circle_radius // 2)
        
        # Blit the attack surface to the screen
        screen.blit(attack_surface, (attack_x, attack_y))
            
    def get_attack_rect(self):
        """Get attack rectangle for collision detection"""
        if self.attack_animation_timer > 0:
            if self.attack_direction > 0:  # Right
                # Tăng phạm vi tấn công để dễ va chạm hơn
                return pygame.Rect(self.x + self.width, self.y, self.attack_range * 1.5, self.height)
            else:  # Left
                # Tăng phạm vi tấn công để dễ va chạm hơn
                return pygame.Rect(self.x - self.attack_range * 1.5, self.y, self.attack_range * 1.5, self.height)
        return None
        
    def get_rect(self):
        """Get player rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def take_damage(self, amount):
        """Take damage and update health"""
        self.stats.current_health -= amount
        self.set_animation("hurt")
        
        if self.stats.current_health <= 0:
            self.stats.current_health = 0
            self.set_animation("death")
            print("Player defeated!")
        else:
            print(f"Player took {amount} damage! Health: {self.stats.current_health}/{self.stats.max_health}")
            
    def heal(self, amount):
        """Heal the player"""
        self.stats.current_health = min(self.stats.max_health, self.stats.current_health + amount)
        print(f"Player healed for {amount}! Health: {self.stats.current_health}/{self.stats.max_health}")
        
    def add_experience(self, amount):
        """Add experience and level up if needed"""
        self.experience += amount
        print(f"Gained {amount} experience! Total: {self.experience}")
        
        # Check for level up
        exp_needed = self.level * 100  # Simple formula: level * 100
        if self.experience >= exp_needed:
            self.level_up()
            
    def level_up(self):
        """Level up the player"""
        self.level += 1
        self.skill_points += 2
        
        # Increase stats
        self.stats.max_health += 20
        self.stats.current_health = self.stats.max_health
        
        print(f"Level up! Now level {self.level}. +2 skill points.")
        print(f"Max health increased to {self.stats.max_health}")
        
        # Reset experience for next level
        self.experience = 0
