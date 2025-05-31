import pygame
import random
import math
import os
from enum import Enum
from dark_fantasy_game.src.animation import Animation
from dark_fantasy_game.src.monster_types import MonsterType, MonsterAbility, MonsterBehavior, MonsterStats

class Monster:
    def __init__(self, monster_type, x, y, level=1):
        self.monster_type = monster_type
        self.x = x
        self.y = y
        self.level = level
        
        # Xác định xem có phải boss không
        self.is_boss = monster_type in [
            MonsterType.DRAGON, 
            MonsterType.NECROMANCER, 
            MonsterType.DEMON_LORD, 
            MonsterType.LICH
        ]
        
        # Khởi tạo chỉ số từ MonsterStats
        self.stats = MonsterStats(monster_type, level, self.is_boss)
        
        # Lấy các thuộc tính từ stats
        self.max_health = self.stats.max_health
        self.health = self.stats.health
        self.damage = self.stats.damage
        self.speed = self.stats.speed
        self.attack_range = self.stats.attack_range
        self.attack_cooldown_max = self.stats.attack_cooldown
        self.score_value = self.stats.score_value
        self.width = self.stats.width
        self.height = self.stats.height
        self.color = self.stats.color
        self.abilities = self.stats.abilities
        self.behavior = self.stats.behavior
        
        # Hướng di chuyển
        self.direction_timer = 0
        self.direction_change_time = 120  # frames
        self.direction_x = 0
        self.direction_y = 0
        self.change_direction()
        
        # Trạng thái animation
        self.current_state = "walk"
        self.facing_right = True
        self.load_animations()
        
        # Cooldown tấn công
        self.attack_cooldown = 0
        self.is_attacking = False
        self.show_attack_range = False  # Chỉ hiển thị phạm vi tấn công khi debug
        
        # Cooldown khả năng đặc biệt
        self.ability_cooldown = 0
        self.ability_cooldown_max = 300  # 5 giây
        
        # Các biến cho khả năng đặc biệt
        self.is_invisible = False
        self.invisibility_timer = 0
        self.invisibility_duration = 180  # 3 giây
        self.teleport_cooldown = 0
        self.teleport_distance = 200
        self.summon_cooldown = 0
        self.heal_amount = int(self.max_health * 0.1)  # Hồi 10% máu tối đa
        self.poison_damage = 2
        self.poison_duration = 180  # 3 giây
        self.fire_damage = 3
        self.ice_slow_factor = 0.5
        self.ice_duration = 120  # 2 giây
        
        # Các biến cho hành vi
        self.patrol_points = []
        self.current_patrol_point = 0
        self.was_attacked = False
        self.target_x = 0
        self.target_y = 0
        self.swarm_bonus = 0
        self.berserker_threshold = 0.3  # Kích hoạt berserker khi máu dưới 30%
        self.berserker_active = False
        
        # Hiệu ứng
        self.effects = []
        
    def load_animations(self):
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sprites")
        
        # Sử dụng sprite cụ thể dựa trên loại quái vật
        if self.monster_type == MonsterType.GOBLIN:
            prefix = "goblin"
        elif self.monster_type == MonsterType.SKELETON:
            prefix = "skeleton"
        elif self.monster_type == MonsterType.ZOMBIE:
            prefix = "zombie"
        elif self.monster_type == MonsterType.ORC:
            prefix = "orc"
        elif self.monster_type == MonsterType.DEMON:
            prefix = "demon"
        elif self.monster_type == MonsterType.WRAITH:
            prefix = "wraith"
        elif self.monster_type == MonsterType.DRAGON:
            prefix = "dragon"
        else:
            # Mặc định cho các loại quái khác
            prefix = "skeleton"
        
        try:
            self.animations = {
                "idle": Animation(os.path.join(base_path, f"{prefix}_idle.png"), 64, 64, 4),
                "walk": Animation(os.path.join(base_path, f"{prefix}_walk.png"), 64, 64, 6),
                "attack": Animation(os.path.join(base_path, f"{prefix}_attack.png"), 64, 64, 4, loop=False),
                "hurt": Animation(os.path.join(base_path, f"{prefix}_hurt.png"), 64, 64, 2, loop=False),
                "death": Animation(os.path.join(base_path, f"{prefix}_death.png"), 64, 64, 5, loop=False)
            }
        except:
            # Fallback nếu không tìm thấy sprite
            self.animations = {
                "idle": Animation(os.path.join(base_path, "skeleton_idle.png"), 64, 64, 4),
                "walk": Animation(os.path.join(base_path, "skeleton_walk.png"), 64, 64, 6),
                "attack": Animation(os.path.join(base_path, "skeleton_attack.png"), 64, 64, 4, loop=False),
                "hurt": Animation(os.path.join(base_path, "skeleton_hurt.png"), 64, 64, 2, loop=False),
                "death": Animation(os.path.join(base_path, "skeleton_death.png"), 64, 64, 5, loop=False)
            }
        
        self.current_animation = self.animations["walk"]
        
    def set_animation(self, animation_name):
        if animation_name in self.animations and self.current_state != animation_name:
            self.current_state = animation_name
            self.current_animation = self.animations[animation_name]
            self.current_animation.reset()
            
    def update(self, player, game_map=None, monsters=None):
        """Cập nhật vị trí và hành vi của quái vật"""
        if self.health <= 0:
            return
            
        old_x, old_y = self.x, self.y
        
        # Cập nhật cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if self.ability_cooldown > 0:
            self.ability_cooldown -= 1
            
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1
            
        if self.summon_cooldown > 0:
            self.summon_cooldown -= 1
            
        # Cập nhật hiệu ứng tàng hình
        if self.is_invisible:
            self.invisibility_timer -= 1
            if self.invisibility_timer <= 0:
                self.is_invisible = False
                
        # Kiểm tra chế độ berserker
        if self.behavior == MonsterBehavior.BERSERKER and self.health < self.max_health * self.berserker_threshold:
            if not self.berserker_active:
                self.berserker_active = True
                self.damage = int(self.damage * 1.5)
                self.speed = self.speed * 1.3
                
        # Xử lý hành vi dựa trên loại
        if self.behavior == MonsterBehavior.AGGRESSIVE or self.is_boss:
            self.chase_player(player)
        elif self.behavior == MonsterBehavior.DEFENSIVE:
            if self.was_attacked:
                self.chase_player(player)
            else:
                self.wander()
        elif self.behavior == MonsterBehavior.RANGED:
            # Giữ khoảng cách với người chơi
            self.keep_distance(player)
        elif self.behavior == MonsterBehavior.PATROL:
            self.patrol()
        elif self.behavior == MonsterBehavior.AMBUSH:
            # Nếu người chơi đến gần và quái vật đang tàng hình, tấn công
            if self.is_player_in_range(player) and self.is_invisible:
                self.is_invisible = False
                self.chase_player(player)
            # Nếu không ở gần người chơi, tàng hình và đứng yên
            elif not self.is_player_in_range(player):
                if not self.is_invisible and self.ability_cooldown <= 0:
                    self.use_ability(MonsterAbility.INVISIBLE)
                # Đứng yên khi tàng hình
                if self.is_invisible:
                    pass
                else:
                    self.wander()
            else:
                self.chase_player(player)
        elif self.behavior == MonsterBehavior.SWARM:
            # Tính toán số lượng quái vật gần đó
            if monsters:
                nearby_monsters = 0
                for monster in monsters:
                    if monster != self:
                        dx = monster.x - self.x
                        dy = monster.y - self.y
                        distance = math.sqrt(dx * dx + dy * dy)
                        if distance < 150:  # Trong phạm vi 150 đơn vị
                            nearby_monsters += 1
                
                # Tăng sức mạnh dựa trên số lượng quái vật gần đó
                self.swarm_bonus = nearby_monsters * 0.1  # Mỗi quái vật tăng 10% sức mạnh
            
            self.chase_player(player)
        else:
            self.wander()
            
        # Sử dụng khả năng đặc biệt nếu có thể
        if self.ability_cooldown <= 0 and len(self.abilities) > 0:
            # Chọn ngẫu nhiên một khả năng
            ability = random.choice(self.abilities)
            self.use_ability(ability, player, monsters)
            
        # Kiểm tra va chạm với bản đồ
        if game_map:
            if not game_map.is_passable(self.x, self.y):
                # Quay lại vị trí cũ nếu không thể đi qua
                self.x, self.y = old_x, old_y
                # Đổi hướng
                self.change_direction()
        
        # Cập nhật hướng nhìn
        if self.direction_x > 0:
            self.facing_right = True
        elif self.direction_x < 0:
            self.facing_right = False
            
        # Kiểm tra nếu người chơi trong tầm tấn công
        if self.is_player_in_range(player):
            if self.attack_cooldown <= 0:
                self.is_attacking = True
                self.set_animation("attack")
                self.attack_cooldown = self.attack_cooldown_max
        else:
            self.is_attacking = False
            
        # Cập nhật animation
        self.current_animation.update(1/60)
        
        # Nếu animation tấn công kết thúc, quay lại trạng thái đi
        if self.current_state == "attack" and self.current_animation.finished:
            self.set_animation("walk")
            
    def wander(self):
        """Di chuyển ngẫu nhiên"""
        self.direction_timer += 1
        if self.direction_timer >= self.direction_change_time:
            self.direction_timer = 0
            self.change_direction()
            
        # Di chuyển theo hướng hiện tại
        self.x += self.direction_x * self.speed
        self.y += self.direction_y * self.speed
        
    def patrol(self):
        """Đi tuần tra theo các điểm định sẵn"""
        if len(self.patrol_points) == 0:
            self.wander()
            return
            
        # Lấy điểm tuần tra hiện tại
        target_x, target_y = self.patrol_points[self.current_patrol_point]
        
        # Tính khoảng cách đến điểm tuần tra
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Nếu đã đến điểm tuần tra, chuyển sang điểm tiếp theo
        if distance < 10:
            self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
        else:
            # Di chuyển đến điểm tuần tra
            if distance > 0:
                self.direction_x = dx / distance
                self.direction_y = dy / distance
                
                self.x += self.direction_x * self.speed
                self.y += self.direction_y * self.speed
                
    def keep_distance(self, player):
        """Giữ khoảng cách với người chơi (cho quái vật tấn công từ xa)"""
        # Tính khoảng cách đến người chơi
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        ideal_distance = self.attack_range * 0.8  # Giữ khoảng cách bằng 80% tầm tấn công
        
        if distance < ideal_distance - 20:
            # Quá gần, di chuyển ra xa
            if distance > 0:
                self.direction_x = -dx / distance
                self.direction_y = -dy / distance
                
                self.x += self.direction_x * self.speed
                self.y += self.direction_y * self.speed
        elif distance > ideal_distance + 20:
            # Quá xa, di chuyển lại gần
            if distance > 0:
                self.direction_x = dx / distance
                self.direction_y = dy / distance
                
                self.x += self.direction_x * self.speed
                self.y += self.direction_y * self.speed
        else:
            # Giữ nguyên vị trí, đã ở khoảng cách lý tưởng
            self.direction_x = 0
            self.direction_y = 0
            
    def chase_player(self, player):
        """Đuổi theo người chơi"""
        # Tính hướng đến người chơi
        dx = player.x - self.x
        dy = player.y - self.y
        
        # Chuẩn hóa hướng
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            self.direction_x = dx / distance
            self.direction_y = dy / distance
            
            # Di chuyển về phía người chơi
            self.x += self.direction_x * self.speed
            self.y += self.direction_y * self.speed
        else:
            self.change_direction()
            
    def change_direction(self):
        """Đổi sang hướng ngẫu nhiên"""
        angle = random.uniform(0, 2 * math.pi)
        self.direction_x = math.cos(angle)
        self.direction_y = math.sin(angle)
        
    def is_player_in_range(self, player):
        """Kiểm tra xem người chơi có trong tầm tấn công không"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= self.attack_range
        
    def use_ability(self, ability, player=None, monsters=None):
        """Sử dụng khả năng đặc biệt"""
        if ability == MonsterAbility.HEAL:
            # Hồi máu
            self.health = min(self.max_health, self.health + self.heal_amount)
            # Hiệu ứng hồi máu
            self.effects.append({
                "type": "heal",
                "timer": 60
            })
        elif ability == MonsterAbility.TELEPORT and player and self.teleport_cooldown <= 0:
            # Dịch chuyển đến gần người chơi
            angle = random.uniform(0, 2 * math.pi)
            teleport_distance = random.uniform(100, self.teleport_distance)
            self.x = player.x + math.cos(angle) * teleport_distance
            self.y = player.y + math.sin(angle) * teleport_distance
            self.teleport_cooldown = 180  # 3 giây
            # Hiệu ứng dịch chuyển
            self.effects.append({
                "type": "teleport",
                "timer": 30
            })
        elif ability == MonsterAbility.SUMMON and monsters is not None and self.summon_cooldown <= 0:
            # Triệu hồi quái vật nhỏ
            # Chỉ triệu hồi nếu có ít hơn 10 quái vật
            if len(monsters) < 10:
                # Tạo 1-3 quái vật nhỏ xung quanh
                num_summons = random.randint(1, 3)
                for _ in range(num_summons):
                    angle = random.uniform(0, 2 * math.pi)
                    summon_distance = random.uniform(50, 100)
                    summon_x = self.x + math.cos(angle) * summon_distance
                    summon_y = self.y + math.sin(angle) * summon_distance
                    
                    # Chọn loại quái vật nhỏ để triệu hồi
                    summon_type = random.choice([MonsterType.GOBLIN, MonsterType.SKELETON])
                    
                    # Thêm quái vật mới vào danh sách
                    # Lưu ý: Cần xử lý thêm ở GameState để thêm quái vật vào game
                    return {
                        "type": "summon",
                        "monster_type": summon_type,
                        "x": summon_x,
                        "y": summon_y,
                        "level": max(1, self.level - 1)
                    }
                    
                self.summon_cooldown = 300  # 5 giây
            
        elif ability == MonsterAbility.INVISIBLE:
            # Tàng hình
            self.is_invisible = True
            self.invisibility_timer = self.invisibility_duration
            # Hiệu ứng tàng hình
            self.effects.append({
                "type": "invisible",
                "timer": 30
            })
            
        # Đặt cooldown cho khả năng
        self.ability_cooldown = self.ability_cooldown_max
        
        return None  # Không có quái vật mới được triệu hồi
        
    def take_damage(self, amount):
        """Nhận sát thương và cập nhật máu"""
        # Đánh dấu là đã bị tấn công (cho hành vi phòng thủ)
        self.was_attacked = True
        
        # Nếu đang tàng hình, hủy tàng hình
        if self.is_invisible:
            self.is_invisible = False
            
        # Giảm máu
        self.health -= amount
        self.set_animation("hurt")
        
        # Đảm bảo máu không âm
        if self.health < 0:
            self.health = 0
            
        if self.health <= 0:
            self.set_animation("death")
            
    def draw(self, screen, scale_x=1.0, scale_y=1.0):
        """Vẽ quái vật"""
        if self.health <= 0:
            return
            
        # Nếu đang tàng hình, vẽ với độ trong suốt
        alpha = 100 if self.is_invisible else 255
        
        # Tính toán vị trí đã điều chỉnh tỷ lệ
        scaled_x = int(self.x * scale_x)
        scaled_y = int(self.y * scale_y)
        
        # Vẽ phạm vi tấn công nếu được bật và quái vật đang tấn công
        if self.show_attack_range and self.is_attacking:
            # Tạo surface cho phạm vi tấn công với độ trong suốt
            range_surface = pygame.Surface((self.attack_range * 2 * scale_x, self.attack_range * 2 * scale_y), pygame.SRCALPHA)
            
            # Vẽ hình tròn với độ trong suốt
            pygame.draw.circle(range_surface, (255, 0, 0, 80), 
                              (self.attack_range * scale_x, self.attack_range * scale_y), 
                              self.attack_range * scale_x)
            
            # Vẽ surface phạm vi tấn công căn giữa trên quái vật
            range_x = scaled_x + int(self.width * scale_x / 2) - int(self.attack_range * scale_x)
            range_y = scaled_y + int(self.height * scale_y / 2) - int(self.attack_range * scale_y)
            screen.blit(range_surface, (range_x, range_y))
        
        # Vẽ khung animation hiện tại với độ trong suốt
        if alpha < 255:
            # Tạo surface tạm với hỗ trợ alpha
            temp_surface = pygame.Surface((int(self.width * scale_x), int(self.height * scale_y)), pygame.SRCALPHA)
            
            # Vẽ animation lên surface tạm
            self.current_animation.draw(temp_surface, 0, 0, not self.facing_right)
            
            # Điều chỉnh alpha
            temp_surface.set_alpha(alpha)
            
            # Vẽ surface tạm lên màn hình
            screen.blit(temp_surface, (scaled_x, scaled_y))
        else:
            # Vẽ animation trực tiếp nếu không cần alpha
            self.current_animation.draw(screen, scaled_x, scaled_y, not self.facing_right)
        
        # Vẽ thanh máu
        health_width = int(self.width * scale_x)
        health_height = int(5 * scale_y)
        health_x = scaled_x
        health_y = scaled_y - int(10 * scale_y)
        
        # Nền (máu trống)
        pygame.draw.rect(screen, (100, 0, 0), (health_x, health_y, health_width, health_height))
        
        # Phần trước (máu hiện tại)
        health_percent = self.health / self.max_health
        current_health_width = int(health_width * health_percent)
        
        # Màu thanh máu thay đổi theo % máu
        if health_percent > 0.6:
            health_color = (0, 255, 0)  # Xanh lá
        elif health_percent > 0.3:
            health_color = (255, 255, 0)  # Vàng
        else:
            health_color = (255, 0, 0)  # Đỏ
            
        pygame.draw.rect(screen, health_color, (health_x, health_y, current_health_width, health_height))
        
        # Vẽ loại quái vật cho boss
        if self.is_boss:
            font = pygame.font.SysFont(None, 20)
            type_text = font.render(f"BOSS: {self.monster_type.value}", True, (255, 255, 255))
            screen.blit(type_text, (scaled_x, scaled_y - int(25 * scale_y)))
            
        # Vẽ hiệu ứng
        for effect in list(self.effects):
            if effect["type"] == "heal":
                # Hiệu ứng hồi máu (các hạt xanh lá bay lên)
                particles = 5
                for i in range(particles):
                    particle_x = scaled_x + random.randint(0, int(self.width * scale_x))
                    particle_y = scaled_y + random.randint(0, int(self.height * scale_y)) - effect["timer"] * 0.5
                    particle_size = int(3 * scale_x)
                    pygame.draw.circle(screen, (0, 255, 0), (particle_x, particle_y), particle_size)
            elif effect["type"] == "teleport":
                # Hiệu ứng dịch chuyển (các hạt xanh dương xoay quanh)
                particles = 12
                for i in range(particles):
                    angle = 2 * math.pi * i / particles + effect["timer"] * 0.1
                    radius = int(20 * scale_x) * (1 - effect["timer"] / 30)
                    particle_x = scaled_x + int(self.width * scale_x / 2) + int(math.cos(angle) * radius)
                    particle_y = scaled_y + int(self.height * scale_y / 2) + int(math.sin(angle) * radius)
                    particle_size = int(4 * scale_x)
                    pygame.draw.circle(screen, (0, 100, 255), (particle_x, particle_y), particle_size)
            elif effect["type"] == "invisible":
                # Hiệu ứng tàng hình (các hạt trắng mờ dần)
                particles = 8
                for i in range(particles):
                    angle = 2 * math.pi * i / particles
                    radius = int(15 * scale_x)
                    particle_x = scaled_x + int(self.width * scale_x / 2) + int(math.cos(angle) * radius)
                    particle_y = scaled_y + int(self.height * scale_y / 2) + int(math.sin(angle) * radius)
                    particle_size = int(3 * scale_x) * (effect["timer"] / 30)
                    particle_color = (255, 255, 255, int(200 * effect["timer"] / 30))
                    
                    # Tạo surface cho hạt với alpha
                    particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surface, particle_color, (particle_size, particle_size), particle_size)
                    screen.blit(particle_surface, (particle_x - particle_size, particle_y - particle_size))
                    
            # Giảm thời gian hiệu ứng
            effect["timer"] -= 1
            if effect["timer"] <= 0:
                self.effects.remove(effect)
            
    def get_rect(self):
        """Lấy hình chữ nhật của quái vật để kiểm tra va chạm"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
