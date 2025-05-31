import pygame
import math
import os
from dark_fantasy_game.src.stats import Stats, CharacterClass
from dark_fantasy_game.src.inventory import Inventory
from dark_fantasy_game.src.animation import Animation
from dark_fantasy_game.src.skill_bar import SkillBar
from dark_fantasy_game.src.experience_system import ExperienceSystem
from dark_fantasy_game.src.skill_tree import SkillTree

class Player:
    def __init__(self, x=400, y=300, character_class=CharacterClass.WARRIOR):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64
        self.speed = 7  # Tốc độ di chuyển cao
        self.character_class = character_class
        self.stats = Stats(character_class)
        self.inventory = Inventory()
        self.skill_bar = SkillBar(character_class)
        self.exp_system = ExperienceSystem()  # Thêm hệ thống kinh nghiệm
        self.skill_tree = SkillTree(character_class)  # Thêm skill tree
        
        # Movement
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False
        
        # Combat
        self.attacking = False
        self.attack_cooldown = 0
        self.attack_cooldown_max = 15  # Giảm thời gian hồi chiêu
        self.attack_direction = 1  # 1: right, -1: left
        self.attack_animation_frames = 15  # frames for attack animation
        self.attack_animation_timer = 0
        self.attack_range = 120  # Tăng phạm vi tấn công
        
        # Thêm hệ thống hồi máu
        self.health_regen_timer = 0
        self.health_regen_rate = 1  # Hồi 1 máu mỗi 60 frames (1 giây)
        self.health_regen_interval = 60
        
        # UI
        self.show_stats = False
        self.show_inventory = False
        self.show_level_up = False
        self.level_up_timer = 0
        self.level_up_duration = 180  # Hiển thị thông báo lên cấp trong 3 giây
        
        # Animation
        self.facing_right = True
        self.current_state = "idle"
        self.load_animations()
        
        # Nút nâng cấp chỉ số
        self.stat_buttons = {}
        
    def load_animations(self):
        try:
            base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sprites")
            
            # Define animations based on character class
            if self.character_class == CharacterClass.WARRIOR:
                # Sử dụng animation gốc thay vì stickman
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
        except Exception as e:
            print(f"Error loading animations: {e}")
            # Fallback to simple rectangle if animations fail to load
            self.animations = {}
            self.current_animation = None
        
    def handle_event(self, event, scale_x=1.0, scale_y=1.0):
        """Handle player input events"""
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
                # Ẩn thông báo lên cấp khi mở bảng chỉ số
                if self.show_stats:
                    self.show_level_up = False
            elif event.key == pygame.K_i:
                self.show_inventory = not self.show_inventory
            elif event.key == pygame.K_c:
                self.switch_character_class()
            elif event.key == pygame.K_k:
                print("K key pressed - toggling skill tree")  # Debug message
                self.skill_tree.toggle_skill_tree()
                return True
            # Xử lý phím tắt kỹ năng
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                if self.skill_bar.handle_key(event.key):
                    self.attacking = True
                    self.attack_animation_timer = self.attack_animation_frames
                    self.set_animation("attack")
                
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
                        # Xử lý click vào nút nâng cấp chỉ số
                        if self.exp_system.handle_stats_click(event.pos, self.stat_buttons):
                            # Cập nhật chỉ số người chơi dựa trên điểm đã phân bổ
                            self.apply_stat_bonuses()
                        
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
    
    def set_animation(self, animation_name):
        if animation_name in self.animations and self.current_state != animation_name:
            self.current_state = animation_name
            self.current_animation = self.animations[animation_name]
            if self.current_animation:
                self.current_animation.reset()
    
    def set_class(self, class_index):
        """Đặt lớp nhân vật dựa trên chỉ số"""
        if class_index == 0:
            self.character_class = CharacterClass.WARRIOR
        else:
            self.character_class = CharacterClass.MAGE
        # Cập nhật lại stats và các thuộc tính liên quan
        self.stats = Stats(self.character_class)
        self.skill_bar = SkillBar(self.character_class)
        self.skill_tree = SkillTree(self.character_class)
        
        # Thêm hệ thống hồi máu
        self.health_regen_timer = 0
        self.health_regen_rate = 1  # Hồi 1 máu mỗi 60 frames (1 giây)
        self.health_regen_interval = 60
        
        # Load animations
        self.load_animations()
    
    def switch_character_class(self):
        """Switch between Warrior and Mage"""
        if self.character_class == CharacterClass.WARRIOR:
            self.character_class = CharacterClass.MAGE
        else:
            self.character_class = CharacterClass.WARRIOR
            
        self.stats = Stats(self.character_class)
        self.load_animations()
        self.skill_bar.init_skills(self.character_class)
    
    def update(self, dt=1/60, game_map=None):
        """Update player state"""
        old_x, old_y = self.x, self.y
        
        # Movement
        if self.moving_left:
            self.x -= self.speed
            self.facing_right = False
            self.attack_direction = -1
        if self.moving_right:
            self.x += self.speed
            self.facing_right = True
            self.attack_direction = 1
        if self.moving_up:
            self.y -= self.speed
        if self.moving_down:
            self.y += self.speed
            
        # Check if new position is valid (if map is provided)
        if game_map:
            if not game_map.is_passable(self.x, self.y):
                # Revert to old position if not passable
                self.x, self.y = old_x, old_y
        
        # Không giới hạn người chơi trong màn hình, để camera theo dõi
        # Cho phép người chơi di chuyển tự do trong map vô hạn
        
        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        # Attack animation timer
        if self.attack_animation_timer > 0:
            self.attack_animation_timer -= 1
            
        # Handle attack
        if self.attacking and self.attack_cooldown == 0:
            self.perform_attack()
            self.attack_cooldown = self.attack_cooldown_max
            self.attack_animation_timer = self.attack_animation_frames
            self.set_animation("attack")
            
        # Hệ thống hồi máu tự động
        self.health_regen_timer += 1
        if self.health_regen_timer >= self.health_regen_interval:
            self.health_regen_timer = 0
            if self.stats.current_health < self.stats.max_health:
                self.stats.current_health = min(self.stats.max_health, self.stats.current_health + self.health_regen_rate)
            
        # Update current animation
        if self.current_animation:
            self.current_animation.update(dt)
        
        # Update skill bar
        self.skill_bar.update()
        
        # Cập nhật thông báo lên cấp
        if self.show_level_up:
            self.level_up_timer -= 1
            if self.level_up_timer <= 0:
                self.show_level_up = False
        
        # If attack animation finished, return to idle or walk
        if self.current_animation and self.current_state == "attack" and self.current_animation.finished:
            if any([self.moving_left, self.moving_right, self.moving_up, self.moving_down]):
                self.set_animation("walk")
            else:
                self.set_animation("idle")
                
    def apply_stat_bonuses(self):
        """Áp dụng các chỉ số bổ sung từ hệ thống kinh nghiệm"""
        # Tăng sát thương vật lý
        if self.character_class == CharacterClass.WARRIOR:
            self.stats.physical_damage += self.exp_system.get_stat_bonus("strength")
        
        # Tăng sát thương phép thuật
        if self.character_class == CharacterClass.MAGE:
            self.stats.magic_damage += self.exp_system.get_stat_bonus("intelligence")
        
        # Tăng máu tối đa
        vitality_bonus = self.exp_system.get_stat_bonus("vitality")
        self.stats.max_health += vitality_bonus
        self.stats.current_health += vitality_bonus  # Hồi máu khi tăng máu tối đa
        
        # Tăng tốc độ di chuyển
        self.speed += self.exp_system.get_stat_bonus("agility")
        
        # Tăng phòng thủ
        self.stats.physical_defense += self.exp_system.get_stat_bonus("defense")
        
        # Tăng tỷ lệ chí mạng (cần thêm logic xử lý chí mạng)
        # self.stats.critical_chance = self.exp_system.get_stat_bonus("critical")
        
    def gain_experience(self, amount):
        """Nhận kinh nghiệm và xử lý lên cấp"""
        result = self.exp_system.add_experience(amount)
        
        if result["leveled_up"]:
            # Hiển thị thông báo lên cấp
            self.show_level_up = True
            self.level_up_timer = self.level_up_duration
            
            # Áp dụng chỉ số mới
            self.apply_stat_bonuses()
            
            # Mở khóa kỹ năng mới nếu có
            if len(result["new_skills_unlocked"]) > 0:
                # Cập nhật kỹ năng mới cho skill bar
                pass
                
        return result
    
    def perform_attack(self):
        """Perform an attack based on character class"""
        pass
    
    def draw(self, screen, scale_x=1.0, scale_y=1.0):
        """Draw the player and UI elements"""
        try:
            # Calculate scaled position
            scaled_x = int(self.x * scale_x)
            scaled_y = int(self.y * scale_y)
            
            # Draw current animation frame or fallback to rectangle
            if self.current_animation:
                self.current_animation.draw(screen, scaled_x, scaled_y, not self.facing_right)
            else:
                # Fallback to simple rectangle if animation fails
                color = (0, 0, 255) if self.character_class == CharacterClass.MAGE else (255, 0, 0)
                pygame.draw.rect(screen, color, (scaled_x, scaled_y, 
                                               int(self.width * scale_x), 
                                               int(self.height * scale_y)))
            
            # Draw attack animation if attacking
            if self.attack_animation_timer > 0:
                self.draw_attack_animation(screen, scale_x, scale_y)
            
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
            
            # Hiển thị số máu
            font = pygame.font.SysFont(None, 20)
            health_text = font.render(f"{int(self.stats.current_health)}/{self.stats.max_health}", True, (255, 255, 255))
            screen.blit(health_text, (health_x + 5, health_y - 15))
            
            # Draw character class indicator
            class_text = font.render(self.character_class.value, True, (255, 255, 255))
            screen.blit(class_text, (scaled_x, scaled_y - int(30 * scale_y)))
            
            # Draw level indicator
            level_text = font.render(f"Lv.{self.exp_system.level}", True, (255, 215, 0))
            screen.blit(level_text, (scaled_x - int(30 * scale_x), scaled_y - int(30 * scale_y)))
            
            # Draw skill bar at bottom of screen
            skill_bar_x = int(20 * scale_x)
            skill_bar_y = screen.get_height() - int(70 * scale_y)
            self.skill_bar.draw(screen, skill_bar_x, skill_bar_y, scale_x, scale_y)
            
            # Draw experience bar at bottom of screen
            exp_bar_x = int(20 * scale_x)
            exp_bar_y = screen.get_height() - int(30 * scale_y)
            exp_bar_width = int(300 * scale_x)
            exp_bar_height = int(20 * scale_y)
            self.exp_system.draw_exp_bar(screen, exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height, scale_x, scale_y)
            
            # Draw level up notification if active
            if self.show_level_up:
                self.exp_system.draw_level_up_notification(screen, scale_x, scale_y)
            
            # Draw stats panel if active
            if self.show_stats:
                self.stat_buttons = self.exp_system.draw_stats_panel(screen, 50, 50, scale_x, scale_y)
                
            # Draw inventory if active
            if self.show_inventory:
                self.inventory.draw(screen, 400, 50)
        except Exception as e:
            print(f"Error drawing player: {e}")
            # Fallback to simple rectangle if drawing fails
            scaled_x = int(self.x * scale_x)
            scaled_y = int(self.y * scale_y)
            pygame.draw.rect(screen, (255, 0, 0), (scaled_x, scaled_y, 
                                                 int(self.width * scale_x), 
                                                 int(self.height * scale_y)))
            
    def draw_attack_animation(self, screen, scale_x, scale_y):
        """Draw the attack animation - AOE circular effect"""
        try:
            scaled_x = int(self.x * scale_x)
            scaled_y = int(self.y * scale_y)
            scaled_width = int(self.width * scale_x)
            scaled_height = int(self.height * scale_y)
            
            # Calculate center of player for AOE effect
            center_x = scaled_x + scaled_width // 2
            center_y = scaled_y + scaled_height // 2
            
            # Calculate AOE radius based on attack range
            aoe_radius = int(self.attack_range * scale_x)
            
            # Animation progress (0.0 to 1.0)
            progress = self.attack_animation_timer / self.attack_animation_frames
            
            # Current radius based on animation progress (grows outward)
            current_radius = int(aoe_radius * progress)
            
            # Alpha fades as the animation progresses
            alpha = int(200 * (1 - progress * 0.7))
            
            # Create a surface for the AOE effect
            aoe_surface = pygame.Surface((aoe_radius * 2, aoe_radius * 2), pygame.SRCALPHA)
            
            if self.character_class == CharacterClass.WARRIOR:
                # Kiếm sĩ: Hiệu ứng kiếm khí từ trong người chơi đẩy ra
                # Vẽ vòng tròn kiếm khí với màu xanh nhạt
                for i in range(3):
                    # Multiple rings with different sizes
                    ring_radius = current_radius - i * 10
                    if ring_radius > 0:
                        # Màu kiếm khí: xanh nhạt
                        pygame.draw.circle(aoe_surface, (100, 200, 255, alpha), 
                                          (aoe_radius, aoe_radius), ring_radius, 3)
                
                # Vẽ các tia kiếm khí phát ra
                for i in range(12):
                    angle = i * (360 / 12) + (progress * 30)  # Rotation effect
                    rad = math.radians(angle)
                    start_x = aoe_radius
                    start_y = aoe_radius
                    # Tia kiếm khí dài hơn khi animation tiến triển
                    length = current_radius * 0.8
                    end_x = start_x + int(math.cos(rad) * length)
                    end_y = start_y + int(math.sin(rad) * length)
                    # Vẽ tia kiếm khí
                    pygame.draw.line(aoe_surface, (150, 220, 255, alpha), 
                                    (start_x, start_y), (end_x, end_y), 3)
                    
                # Vẽ hiệu ứng sóng xung kích
                pygame.draw.circle(aoe_surface, (200, 230, 255, alpha // 2), 
                                  (aoe_radius, aoe_radius), current_radius, 5)
                                  
            else:  # Mage
                # Pháp sư: Vòng lửa màu đỏ
                # Vẽ vòng lửa chính
                pygame.draw.circle(aoe_surface, (255, 50, 20, alpha), 
                                  (aoe_radius, aoe_radius), current_radius, 4)
                
                # Vẽ các ngọn lửa nhỏ xung quanh vòng tròn
                for i in range(16):
                    angle = i * (360 / 16) + (progress * 20)  # Rotation effect
                    rad = math.radians(angle)
                    
                    # Vị trí của ngọn lửa trên vòng tròn
                    flame_x = aoe_radius + int(math.cos(rad) * current_radius)
                    flame_y = aoe_radius + int(math.sin(rad) * current_radius)
                    
                    # Kích thước ngọn lửa
                    flame_height = int(15 * scale_x * (0.5 + progress * 0.5))
                    
                    # Vẽ ngọn lửa (tam giác)
                    flame_points = [
                        (flame_x, flame_y),
                        (flame_x + int(math.cos(rad + 0.2) * flame_height), 
                         flame_y + int(math.sin(rad + 0.2) * flame_height)),
                        (flame_x + int(math.cos(rad - 0.2) * flame_height), 
                         flame_y + int(math.sin(rad - 0.2) * flame_height))
                    ]
                    pygame.draw.polygon(aoe_surface, (255, 100, 0, alpha), flame_points)
                    
                # Vẽ hiệu ứng ánh sáng ở giữa
                inner_radius = int(current_radius * 0.7)
                if inner_radius > 0:
                    pygame.draw.circle(aoe_surface, (255, 200, 100, alpha // 3), 
                                      (aoe_radius, aoe_radius), inner_radius)
            
            # Blit the AOE surface to the screen
            screen.blit(aoe_surface, (center_x - aoe_radius, center_y - aoe_radius))
        except Exception as e:
            print(f"Error drawing attack animation: {e}")
            
    def get_attack_rect(self):
        """Get attack rectangle for collision detection - now circular AOE"""
        if self.attack_animation_timer > 0:
            # Tạo hình tròn AOE xung quanh người chơi
            # Trả về hình chữ nhật bao quanh hình tròn để kiểm tra va chạm
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # Phạm vi tấn công là hình tròn với bán kính là attack_range
            return pygame.Rect(
                center_x - self.attack_range, 
                center_y - self.attack_range,
                self.attack_range * 2, 
                self.attack_range * 2
            )
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
        else:
            pass
            
    def heal(self, amount):
        """Heal the player"""
        self.stats.current_health = min(self.stats.max_health, self.stats.current_health + amount)
