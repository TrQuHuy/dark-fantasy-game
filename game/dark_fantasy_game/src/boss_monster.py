import pygame
import random
import math
import os
from dark_fantasy_game.src.monster import Monster
from dark_fantasy_game.src.monster_types import MonsterType, MonsterAbility, MonsterBehavior

class BossMonster(Monster):
    def __init__(self, monster_type, x, y, level=1):
        super().__init__(monster_type, x, y, level)
        
        # Đảm bảo là boss
        self.is_boss = True
        
        # Tăng kích thước
        self.width = int(self.width * 1.5)
        self.height = int(self.height * 1.5)
        
        # Các giai đoạn của boss
        self.max_phases = 3
        self.current_phase = 1
        self.phase_health_thresholds = [0.7, 0.4, 0.1]  # 70%, 40%, 10% máu
        
        # Các đòn tấn công đặc biệt
        self.special_attacks = []
        self.setup_special_attacks()
        
        # Cooldown tấn công đặc biệt
        self.special_attack_cooldown = 0
        self.special_attack_cooldown_max = 300  # 5 giây
        
        # Hiệu ứng
        self.phase_transition_effect = False
        self.phase_transition_timer = 0
        self.phase_transition_duration = 120  # 2 giây
        
        # Các minion (quái vật nhỏ) được triệu hồi
        self.minions = []
        self.max_minions = 5
        
        # Các điểm yếu (chỉ cho một số boss)
        self.weak_points = []
        self.setup_weak_points()
        
        # Các mẫu tấn công
        self.attack_patterns = []
        self.current_pattern = 0
        self.setup_attack_patterns()
        
    def setup_special_attacks(self):
        """Thiết lập các đòn tấn công đặc biệt dựa trên loại boss"""
        if self.monster_type == MonsterType.DRAGON:
            self.special_attacks = [
                {"name": "Fire Breath", "damage": self.damage * 2, "range": self.attack_range * 1.5, "cooldown": 180},
                {"name": "Tail Swipe", "damage": self.damage * 1.5, "range": self.attack_range * 0.8, "cooldown": 120},
                {"name": "Wing Gust", "damage": self.damage, "range": self.attack_range * 2, "cooldown": 240}
            ]
        elif self.monster_type == MonsterType.NECROMANCER:
            self.special_attacks = [
                {"name": "Death Ray", "damage": self.damage * 1.8, "range": self.attack_range * 2, "cooldown": 200},
                {"name": "Summon Undead", "damage": 0, "range": 0, "cooldown": 300},
                {"name": "Life Drain", "damage": self.damage, "range": self.attack_range * 1.2, "cooldown": 150}
            ]
        elif self.monster_type == MonsterType.DEMON_LORD:
            self.special_attacks = [
                {"name": "Hellfire", "damage": self.damage * 2.5, "range": self.attack_range * 1.2, "cooldown": 210},
                {"name": "Shadow Strike", "damage": self.damage * 1.7, "range": self.attack_range, "cooldown": 120},
                {"name": "Demonic Roar", "damage": self.damage * 1.2, "range": self.attack_range * 1.8, "cooldown": 180}
            ]
        elif self.monster_type == MonsterType.LICH:
            self.special_attacks = [
                {"name": "Frost Nova", "damage": self.damage * 1.5, "range": self.attack_range * 1.5, "cooldown": 180},
                {"name": "Soul Harvest", "damage": self.damage * 2, "range": self.attack_range, "cooldown": 240},
                {"name": "Arcane Missiles", "damage": self.damage * 1.3, "range": self.attack_range * 2, "cooldown": 150}
            ]
            
    def setup_weak_points(self):
        """Thiết lập các điểm yếu (chỉ cho một số boss)"""
        if self.monster_type == MonsterType.DRAGON:
            # Điểm yếu ở bụng
            self.weak_points = [
                {"x": self.width * 0.5, "y": self.height * 0.6, "radius": 15, "active": True, "damage_multiplier": 2.0}
            ]
        elif self.monster_type == MonsterType.NECROMANCER:
            # Điểm yếu là cuốn sách phép
            self.weak_points = [
                {"x": self.width * 0.3, "y": self.height * 0.5, "radius": 10, "active": True, "damage_multiplier": 1.8}
            ]
            
    def setup_attack_patterns(self):
        """Thiết lập các mẫu tấn công dựa trên loại boss"""
        if self.monster_type == MonsterType.DRAGON:
            self.attack_patterns = [
                {"name": "Circle", "duration": 300, "speed_multiplier": 1.2},
                {"name": "Charge", "duration": 120, "speed_multiplier": 2.0},
                {"name": "Retreat", "duration": 180, "speed_multiplier": 0.8}
            ]
        elif self.monster_type == MonsterType.NECROMANCER:
            self.attack_patterns = [
                {"name": "Summon Phase", "duration": 240, "speed_multiplier": 0.5},
                {"name": "Attack Phase", "duration": 180, "speed_multiplier": 1.0},
                {"name": "Teleport Phase", "duration": 120, "speed_multiplier": 1.5}
            ]
            
    def update(self, player, game_map=None, monsters=None):
        """Cập nhật trạng thái của boss"""
        if self.health <= 0:
            return
            
        # Kiểm tra chuyển giai đoạn
        health_percent = self.health / self.max_health
        for i, threshold in enumerate(self.phase_health_thresholds):
            if health_percent <= threshold and self.current_phase == i + 1:
                self.transition_to_next_phase()
                break
                
        # Xử lý hiệu ứng chuyển giai đoạn
        if self.phase_transition_effect:
            self.phase_transition_timer -= 1
            if self.phase_transition_timer <= 0:
                self.phase_transition_effect = False
                # Tăng sức mạnh khi chuyển giai đoạn
                self.damage = int(self.damage * 1.2)
                self.speed = self.speed * 1.1
                # Thêm khả năng mới nếu cần
                if self.current_phase == 2:
                    if MonsterAbility.TELEPORT not in self.abilities:
                        self.abilities.append(MonsterAbility.TELEPORT)
                elif self.current_phase == 3:
                    if MonsterAbility.SUMMON not in self.abilities:
                        self.abilities.append(MonsterAbility.SUMMON)
            return  # Không di chuyển trong khi chuyển giai đoạn
            
        # Cập nhật cooldown tấn công đặc biệt
        if self.special_attack_cooldown > 0:
            self.special_attack_cooldown -= 1
            
        # Sử dụng tấn công đặc biệt nếu có thể
        if self.special_attack_cooldown <= 0 and len(self.special_attacks) > 0:
            # Ưu tiên tấn công đặc biệt dựa trên giai đoạn hiện tại
            attack_index = min(self.current_phase - 1, len(self.special_attacks) - 1)
            special_attack = self.special_attacks[attack_index]
            
            # Kiểm tra xem người chơi có trong tầm không
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= special_attack["range"]:
                # Thực hiện tấn công đặc biệt
                self.perform_special_attack(special_attack, player)
                self.special_attack_cooldown = special_attack["cooldown"]
                return  # Không di chuyển trong khi thực hiện tấn công đặc biệt
                
        # Cập nhật mẫu tấn công
        if len(self.attack_patterns) > 0:
            current_pattern = self.attack_patterns[self.current_pattern]
            
            # Áp dụng hệ số tốc độ từ mẫu tấn công
            original_speed = self.speed / current_pattern["speed_multiplier"]
            self.speed = original_speed * current_pattern["speed_multiplier"]
            
            # Chuyển sang mẫu tấn công tiếp theo sau một khoảng thời gian
            if random.random() < 0.005:  # 0.5% cơ hội mỗi frame
                self.current_pattern = (self.current_pattern + 1) % len(self.attack_patterns)
                
        # Gọi phương thức update của lớp cha
        super().update(player, game_map, monsters)
        
    def transition_to_next_phase(self):
        """Chuyển sang giai đoạn tiếp theo"""
        self.current_phase += 1
        if self.current_phase > self.max_phases:
            self.current_phase = self.max_phases
            
        # Kích hoạt hiệu ứng chuyển giai đoạn
        self.phase_transition_effect = True
        self.phase_transition_timer = self.phase_transition_duration
        
        # Hồi một lượng máu nhỏ khi chuyển giai đoạn
        heal_amount = int(self.max_health * 0.1)  # Hồi 10% máu tối đa
        self.health = min(self.max_health, self.health + heal_amount)
        
        # Thêm hiệu ứng
        self.effects.append({
            "type": "phase_transition",
            "timer": self.phase_transition_duration
        })
        
    def perform_special_attack(self, attack, player):
        """Thực hiện tấn công đặc biệt"""
        # Đặt animation tấn công
        self.set_animation("attack")
        
        # Thêm hiệu ứng tấn công đặc biệt
        self.effects.append({
            "type": "special_attack",
            "name": attack["name"],
            "timer": 60,
            "range": attack["range"]
        })
        
        # Xử lý logic tấn công đặc biệt
        if attack["name"] == "Summon Undead" or attack["name"] == "Summon Phase":
            # Triệu hồi quái vật nhỏ
            return self.use_ability(MonsterAbility.SUMMON, player)
        elif attack["name"] == "Life Drain":
            # Hút máu từ người chơi
            heal_amount = int(attack["damage"] * 0.5)
            self.health = min(self.max_health, self.health + heal_amount)
            # Thêm hiệu ứng hồi máu
            self.effects.append({
                "type": "heal",
                "timer": 60
            })
        elif attack["name"] == "Teleport Phase":
            # Dịch chuyển
            return self.use_ability(MonsterAbility.TELEPORT, player)
            
        return None
        
    def draw(self, screen, scale_x=1.0, scale_y=1.0):
        """Vẽ boss với các hiệu ứng đặc biệt"""
        if self.health <= 0:
            return
            
        # Vẽ hiệu ứng chuyển giai đoạn
        if self.phase_transition_effect:
            # Tính toán vị trí đã điều chỉnh tỷ lệ
            scaled_x = int(self.x * scale_x)
            scaled_y = int(self.y * scale_y)
            scaled_width = int(self.width * scale_x)
            scaled_height = int(self.height * scale_y)
            
            # Vẽ hiệu ứng ánh sáng xung quanh boss
            for radius in range(int(self.width * scale_x * 2), 0, -10):
                alpha = int(100 * (radius / (self.width * scale_x * 2)))
                color = (255, 200, 0, alpha)  # Màu vàng
                
                # Tạo surface cho hiệu ứng với alpha
                effect_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(effect_surface, color, (radius, radius), radius)
                
                # Vẽ hiệu ứng lên màn hình
                effect_x = scaled_x + scaled_width // 2 - radius
                effect_y = scaled_y + scaled_height // 2 - radius
                screen.blit(effect_surface, (effect_x, effect_y))
                
            # Vẽ boss với hiệu ứng nhấp nháy
            if self.phase_transition_timer % 10 < 5:
                super().draw(screen, scale_x, scale_y)
        else:
            # Vẽ boss bình thường
            super().draw(screen, scale_x, scale_y)
            
            # Vẽ các hiệu ứng tấn công đặc biệt
            for effect in list(self.effects):
                if effect["type"] == "special_attack":
                    # Tính toán vị trí đã điều chỉnh tỷ lệ
                    scaled_x = int(self.x * scale_x)
                    scaled_y = int(self.y * scale_y)
                    scaled_width = int(self.width * scale_x)
                    scaled_height = int(self.height * scale_y)
                    
                    # Vẽ hiệu ứng dựa trên tên tấn công
                    if "Fire" in effect["name"] or "Hellfire" in effect["name"]:
                        # Hiệu ứng lửa
                        for i in range(20):
                            angle = random.uniform(0, 2 * math.pi)
                            distance = random.uniform(0, effect["range"] * scale_x)
                            particle_x = scaled_x + scaled_width // 2 + int(math.cos(angle) * distance)
                            particle_y = scaled_y + scaled_height // 2 + int(math.sin(angle) * distance)
                            particle_size = int(5 * scale_x)
                            
                            # Màu lửa ngẫu nhiên
                            r = random.randint(200, 255)
                            g = random.randint(50, 150)
                            b = 0
                            
                            pygame.draw.circle(screen, (r, g, b), (particle_x, particle_y), particle_size)
                    elif "Frost" in effect["name"] or "Ice" in effect["name"]:
                        # Hiệu ứng băng
                        for i in range(15):
                            angle = random.uniform(0, 2 * math.pi)
                            distance = random.uniform(0, effect["range"] * scale_x)
                            particle_x = scaled_x + scaled_width // 2 + int(math.cos(angle) * distance)
                            particle_y = scaled_y + scaled_height // 2 + int(math.sin(angle) * distance)
                            particle_size = int(4 * scale_x)
                            
                            # Màu băng
                            pygame.draw.circle(screen, (150, 200, 255), (particle_x, particle_y), particle_size)
                    elif "Lightning" in effect["name"] or "Arcane" in effect["name"]:
                        # Hiệu ứng sét/phép thuật
                        for i in range(5):
                            start_x = scaled_x + scaled_width // 2
                            start_y = scaled_y + scaled_height // 2
                            angle = random.uniform(0, 2 * math.pi)
                            end_x = start_x + int(math.cos(angle) * effect["range"] * scale_x)
                            end_y = start_y + int(math.sin(angle) * effect["range"] * scale_y)
                            
                            # Vẽ tia sét với nhiều đoạn
                            points = [(start_x, start_y)]
                            segments = 10
                            for j in range(1, segments):
                                segment_x = start_x + (end_x - start_x) * j / segments
                                segment_y = start_y + (end_y - start_y) * j / segments
                                # Thêm độ lệch ngẫu nhiên
                                segment_x += random.randint(-10, 10)
                                segment_y += random.randint(-10, 10)
                                points.append((segment_x, segment_y))
                            points.append((end_x, end_y))
                            
                            # Vẽ tia sét
                            pygame.draw.lines(screen, (100, 100, 255), False, points, 2)
                            
                    # Giảm thời gian hiệu ứng
                    effect["timer"] -= 1
                    if effect["timer"] <= 0:
                        self.effects.remove(effect)
                        
            # Vẽ chỉ số giai đoạn
            font = pygame.font.SysFont(None, 24)
            phase_text = font.render(f"Phase {self.current_phase}/{self.max_phases}", True, (255, 200, 0))
            
            # Tính toán vị trí đã điều chỉnh tỷ lệ
            scaled_x = int(self.x * scale_x)
            scaled_y = int(self.y * scale_y)
            
            # Vẽ text giai đoạn
            screen.blit(phase_text, (scaled_x, scaled_y - int(40 * scale_y)))
