import pygame
import math
import random
from enum import Enum

class AbilityType(Enum):
    # Warrior abilities
    WHIRLWIND = "Whirlwind"
    SHIELD_BASH = "Shield Bash"
    CHARGE = "Charge"
    
    # Mage abilities
    TELEPORT = "Teleport"
    FROST_NOVA = "Frost Nova"
    METEOR = "Meteor Shower"

class Ability:
    def __init__(self, ability_type, cooldown, mana_cost=0):
        self.ability_type = ability_type
        self.cooldown = cooldown  # Thời gian hồi chiêu (frames)
        self.current_cooldown = 0
        self.mana_cost = mana_cost
        self.is_active = False
        self.duration = 0  # Thời gian kéo dài của kỹ năng (frames)
        self.current_duration = 0
        
    def activate(self, player):
        """Kích hoạt kỹ năng nếu không trong thời gian hồi chiêu"""
        if self.current_cooldown <= 0:
            self.is_active = True
            self.current_cooldown = self.cooldown
            self.current_duration = self.duration
            return True
        return False
        
    def update(self):
        """Cập nhật trạng thái kỹ năng"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
            
        if self.is_active:
            if self.current_duration > 0:
                self.current_duration -= 1
            else:
                self.is_active = False
                
    def get_cooldown_percent(self):
        """Trả về phần trăm thời gian hồi chiêu còn lại"""
        return self.current_cooldown / self.cooldown if self.cooldown > 0 else 0

class WhirlwindAbility(Ability):
    def __init__(self):
        super().__init__(AbilityType.WHIRLWIND, cooldown=300, mana_cost=20)
        self.duration = 60  # 1 giây ở 60fps
        self.damage_multiplier = 0.5  # Sát thương mỗi tick
        self.radius = 100  # Bán kính tấn công
        
    def get_affected_area(self, player_x, player_y):
        """Trả về khu vực ảnh hưởng của kỹ năng"""
        return pygame.Rect(
            player_x - self.radius,
            player_y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        
    def draw(self, screen, player_x, player_y, scale_x=1.0, scale_y=1.0):
        """Vẽ hiệu ứng kỹ năng"""
        if self.is_active:
            # Tạo surface cho hiệu ứng xoáy
            radius = int(self.radius * scale_x)
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            
            # Vẽ hiệu ứng xoáy với độ trong suốt
            alpha = int(200 * (self.current_duration / self.duration))
            color = (255, 165, 0, alpha)  # Màu cam với độ trong suốt
            
            # Vẽ nhiều vòng tròn với bán kính khác nhau
            for i in range(5):
                circle_radius = int(radius * (0.4 + i * 0.12))
                thickness = 3
                pygame.draw.circle(surface, color, (radius, radius), circle_radius, thickness)
            
            # Vẽ các đường chéo
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = radius + int(radius * 0.3 * math.cos(rad))
                y1 = radius + int(radius * 0.3 * math.sin(rad))
                x2 = radius + int(radius * 0.9 * math.cos(rad))
                y2 = radius + int(radius * 0.9 * math.sin(rad))
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)
            
            # Hiển thị hiệu ứng
            screen_x = int(player_x * scale_x) - radius
            screen_y = int(player_y * scale_y) - radius
            screen.blit(surface, (screen_x, screen_y))

class ShieldBashAbility(Ability):
    def __init__(self):
        super().__init__(AbilityType.SHIELD_BASH, cooldown=180, mana_cost=15)
        self.duration = 10  # Rất ngắn, chỉ là đòn đánh
        self.damage_multiplier = 1.5
        self.stun_duration = 120  # 2 giây choáng
        self.range = 60  # Tầm đánh
        
    def get_affected_area(self, player_x, player_y, direction):
        """Trả về khu vực ảnh hưởng của kỹ năng dựa trên hướng"""
        if direction > 0:  # Phải
            return pygame.Rect(player_x, player_y - 20, self.range, 40)
        else:  # Trái
            return pygame.Rect(player_x - self.range, player_y - 20, self.range, 40)
            
    def draw(self, screen, player_x, player_y, direction, scale_x=1.0, scale_y=1.0):
        """Vẽ hiệu ứng kỹ năng"""
        if self.is_active:
            # Tính toán vị trí hiệu ứng
            width = int(self.range * scale_x)
            height = int(40 * scale_y)
            
            if direction > 0:  # Phải
                x = int(player_x * scale_x)
                y = int((player_y - 20) * scale_y)
            else:  # Trái
                x = int((player_x - self.range) * scale_x)
                y = int((player_y - 20) * scale_y)
            
            # Tạo surface cho hiệu ứng
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Vẽ hiệu ứng shield bash
            alpha = int(200 * (self.current_duration / self.duration))
            color = (200, 200, 200, alpha)  # Màu bạc với độ trong suốt
            
            # Vẽ hình bán nguyệt
            if direction > 0:
                pygame.draw.arc(surface, color, (0, 0, width * 2, height), 3*math.pi/2, 5*math.pi/2, 5)
            else:
                pygame.draw.arc(surface, color, (-width, 0, width * 2, height), math.pi/2, 3*math.pi/2, 5)
            
            # Hiển thị hiệu ứng
            screen.blit(surface, (x, y))

class ChargeAbility(Ability):
    def __init__(self):
        super().__init__(AbilityType.CHARGE, cooldown=240, mana_cost=10)
        self.duration = 20  # Thời gian lướt
        self.speed_boost = 3  # Hệ số tăng tốc
        self.damage = 30  # Sát thương khi va chạm
        
    def draw(self, screen, player_x, player_y, direction, scale_x=1.0, scale_y=1.0):
        """Vẽ hiệu ứng kỹ năng"""
        if self.is_active:
            # Tính toán vị trí hiệu ứng
            width = int(30 * scale_x)
            height = int(30 * scale_y)
            
            x = int(player_x * scale_x) - width // 2
            y = int(player_y * scale_y) - height // 2
            
            # Tạo surface cho hiệu ứng
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Vẽ hiệu ứng lướt
            alpha = int(150 * (self.current_duration / self.duration))
            color = (255, 255, 255, alpha)  # Màu trắng với độ trong suốt
            
            # Vẽ các vệt chuyển động
            for i in range(3):
                offset = i * 10
                if direction > 0:  # Phải
                    pygame.draw.line(surface, color, (offset, 0), (offset, height), 2)
                else:  # Trái
                    pygame.draw.line(surface, color, (width - offset, 0), (width - offset, height), 2)
            
            # Hiển thị hiệu ứng
            screen.blit(surface, (x, y))

class TeleportAbility(Ability):
    def __init__(self):
        super().__init__(AbilityType.TELEPORT, cooldown=300, mana_cost=30)
        self.duration = 5  # Rất ngắn, chỉ là hiệu ứng
        self.max_distance = 200  # Khoảng cách tối đa có thể dịch chuyển
        
    def activate(self, player, target_x, target_y, game_map=None):
        """Kích hoạt kỹ năng dịch chuyển đến vị trí mục tiêu"""
        if self.current_cooldown <= 0:
            # Tính khoảng cách
            dx = target_x - player.x
            dy = target_y - player.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Giới hạn khoảng cách
            if distance > self.max_distance:
                ratio = self.max_distance / distance
                dx *= ratio
                dy *= ratio
                
            # Vị trí mới
            new_x = player.x + dx
            new_y = player.y + dy
            
            # Kiểm tra vị trí mới có hợp lệ không
            if game_map and game_map.is_passable(new_x, new_y):
                player.x = new_x
                player.y = new_y
                self.is_active = True
                self.current_cooldown = self.cooldown
                self.current_duration = self.duration
                return True
                
        return False
        
    def draw(self, screen, player_x, player_y, scale_x=1.0, scale_y=1.0):
        """Vẽ hiệu ứng kỹ năng"""
        if self.is_active:
            # Tính toán vị trí hiệu ứng
            radius = int(50 * scale_x)
            
            x = int(player_x * scale_x)
            y = int(player_y * scale_y)
            
            # Tạo surface cho hiệu ứng
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            
            # Vẽ hiệu ứng dịch chuyển
            alpha = int(200 * (self.current_duration / self.duration))
            color = (0, 255, 255, alpha)  # Màu xanh lam với độ trong suốt
            
            # Vẽ các vòng tròn mở rộng
            for i in range(3):
                circle_radius = int(radius * (0.3 + i * 0.2))
                pygame.draw.circle(surface, color, (radius, radius), circle_radius, 2)
            
            # Hiển thị hiệu ứng
            screen.blit(surface, (x - radius, y - radius))

class FrostNovaAbility(Ability):
    def __init__(self):
        super().__init__(AbilityType.FROST_NOVA, cooldown=240, mana_cost=25)
        self.duration = 30  # 0.5 giây ở 60fps
        self.damage = 20
        self.radius = 120
        self.slow_duration = 180  # 3 giây làm chậm
        self.slow_strength = 0.5  # Giảm 50% tốc độ
        
    def get_affected_area(self, player_x, player_y):
        """Trả về khu vực ảnh hưởng của kỹ năng"""
        return pygame.Rect(
            player_x - self.radius,
            player_y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        
    def draw(self, screen, player_x, player_y, scale_x=1.0, scale_y=1.0):
        """Vẽ hiệu ứng kỹ năng"""
        if self.is_active:
            # Tạo surface cho hiệu ứng
            radius = int(self.radius * scale_x)
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            
            # Vẽ hiệu ứng băng với độ trong suốt
            alpha = int(150 * (self.current_duration / self.duration))
            color = (0, 191, 255, alpha)  # Màu xanh da trời với độ trong suốt
            
            # Vẽ vòng tròn băng mở rộng
            progress = 1 - (self.current_duration / self.duration)
            current_radius = int(radius * progress)
            pygame.draw.circle(surface, color, (radius, radius), current_radius, 0)
            
            # Vẽ các mảnh băng
            for i in range(8):
                angle = i * (math.pi / 4)
                length = current_radius * 0.2
                x1 = radius + int(current_radius * math.cos(angle))
                y1 = radius + int(current_radius * math.sin(angle))
                x2 = radius + int((current_radius + length) * math.cos(angle))
                y2 = radius + int((current_radius + length) * math.sin(angle))
                pygame.draw.line(surface, (255, 255, 255, alpha), (x1, y1), (x2, y2), 3)
            
            # Hiển thị hiệu ứng
            screen_x = int(player_x * scale_x) - radius
            screen_y = int(player_y * scale_y) - radius
            screen.blit(surface, (screen_x, screen_y))

class MeteorAbility(Ability):
    def __init__(self):
        super().__init__(AbilityType.METEOR, cooldown=600, mana_cost=50)
        self.duration = 90  # 1.5 giây ở 60fps
        self.damage = 100
        self.radius = 150
        self.burn_duration = 180  # 3 giây cháy
        self.burn_strength = 0.5  # Sức mạnh hiệu ứng cháy
        self.target_x = 0
        self.target_y = 0
        
    def activate(self, player, target_x, target_y):
        """Kích hoạt kỹ năng với vị trí mục tiêu"""
        if self.current_cooldown <= 0:
            self.target_x = target_x
            self.target_y = target_y
            self.is_active = True
            self.current_cooldown = self.cooldown
            self.current_duration = self.duration
            return True
        return False
        
    def get_affected_area(self):
        """Trả về khu vực ảnh hưởng của kỹ năng"""
        return pygame.Rect(
            self.target_x - self.radius,
            self.target_y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        
    def draw(self, screen, camera_x, camera_y, scale_x=1.0, scale_y=1.0):
        """Vẽ hiệu ứng kỹ năng"""
        if self.is_active:
            # Tính toán vị trí hiệu ứng
            radius = int(self.radius * scale_x)
            
            # Vị trí trên màn hình
            screen_x = int((self.target_x - camera_x) * scale_x)
            screen_y = int((self.target_y - camera_y) * scale_y)
            
            # Tạo surface cho hiệu ứng
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            
            # Vẽ hiệu ứng thiên thạch
            progress = 1 - (self.current_duration / self.duration)
            
            if progress < 0.7:  # Thiên thạch đang rơi
                # Vẽ bóng trên mặt đất
                shadow_radius = int(radius * 0.5 * (progress / 0.7))
                pygame.draw.circle(surface, (0, 0, 0, 100), (radius, radius), shadow_radius)
                
                # Vẽ thiên thạch trên không trung
                meteor_y = int(radius * 2 * (1 - progress / 0.7))
                meteor_size = int(radius * 0.3)
                pygame.draw.circle(surface, (255, 0, 0), (radius, meteor_y), meteor_size)
                
                # Vẽ đuôi lửa
                for i in range(5):
                    tail_y = meteor_y + (i+1) * 10
                    tail_size = meteor_size * (1 - (i+1) * 0.15)
                    if tail_size > 0:
                        pygame.draw.circle(surface, (255, 165, 0), (radius, tail_y), int(tail_size))
                
            else:  # Vụ nổ
                explosion_progress = (progress - 0.7) / 0.3
                explosion_radius = int(radius * explosion_progress)
                
                # Vẽ vụ nổ
                pygame.draw.circle(surface, (255, 0, 0, 200), (radius, radius), explosion_radius)
                pygame.draw.circle(surface, (255, 165, 0, 150), (radius, radius), int(explosion_radius * 0.8))
                pygame.draw.circle(surface, (255, 255, 0, 100), (radius, radius), int(explosion_radius * 0.6))
                
                # Vẽ các mảnh vỡ
                for i in range(12):
                    angle = i * (math.pi / 6)
                    length = explosion_radius * 0.3
                    x1 = radius + int(explosion_radius * math.cos(angle))
                    y1 = radius + int(explosion_radius * math.sin(angle))
                    x2 = radius + int((explosion_radius + length) * math.cos(angle))
                    y2 = radius + int((explosion_radius + length) * math.sin(angle))
                    pygame.draw.line(surface, (255, 0, 0, 200), (x1, y1), (x2, y2), 3)
            
            # Hiển thị hiệu ứng
            screen.blit(surface, (screen_x - radius, screen_y - radius))
