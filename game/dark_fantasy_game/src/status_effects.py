import pygame
import math
from enum import Enum

class StatusEffectType(Enum):
    POISON = "Poison"
    STUN = "Stun"
    SLOW = "Slow"
    BURN = "Burn"
    FREEZE = "Freeze"

class StatusEffect:
    def __init__(self, effect_type, duration, strength=1.0):
        self.effect_type = effect_type
        self.duration = duration  # Thời gian hiệu lực (frames)
        self.remaining = duration
        self.strength = strength  # Cường độ hiệu ứng (1.0 = 100%)
        
    def update(self):
        """Cập nhật thời gian còn lại của hiệu ứng"""
        if self.remaining > 0:
            self.remaining -= 1
            return True
        return False
        
    def is_active(self):
        """Kiểm tra hiệu ứng còn hoạt động không"""
        return self.remaining > 0
        
    def get_icon_color(self):
        """Lấy màu biểu tượng của hiệu ứng"""
        if self.effect_type == StatusEffectType.POISON:
            return (0, 255, 0)  # Xanh lá
        elif self.effect_type == StatusEffectType.STUN:
            return (255, 255, 0)  # Vàng
        elif self.effect_type == StatusEffectType.SLOW:
            return (0, 0, 255)  # Xanh dương
        elif self.effect_type == StatusEffectType.BURN:
            return (255, 0, 0)  # Đỏ
        elif self.effect_type == StatusEffectType.FREEZE:
            return (0, 255, 255)  # Xanh lam
        return (255, 255, 255)  # Trắng
        
    def apply_effect(self, entity):
        """Áp dụng hiệu ứng lên thực thể (người chơi hoặc quái)"""
        if self.effect_type == StatusEffectType.POISON:
            # Gây sát thương theo thời gian
            damage = max(1, int(entity.stats.max_health * 0.01 * self.strength))
            entity.take_damage(damage)
            
        elif self.effect_type == StatusEffectType.STUN:
            # Làm choáng, không thể di chuyển hoặc tấn công
            entity.is_stunned = True
            
        elif self.effect_type == StatusEffectType.SLOW:
            # Giảm tốc độ di chuyển
            entity.speed_multiplier = max(0.2, 1.0 - (0.5 * self.strength))
            
        elif self.effect_type == StatusEffectType.BURN:
            # Gây sát thương lửa theo thời gian
            damage = max(1, int(entity.stats.max_health * 0.015 * self.strength))
            entity.take_damage(damage)
            
        elif self.effect_type == StatusEffectType.FREEZE:
            # Giảm tốc độ tấn công
            entity.attack_speed_multiplier = max(0.3, 1.0 - (0.4 * self.strength))
            
    def remove_effect(self, entity):
        """Xóa hiệu ứng khỏi thực thể"""
        if self.effect_type == StatusEffectType.STUN:
            entity.is_stunned = False
            
        elif self.effect_type == StatusEffectType.SLOW:
            entity.speed_multiplier = 1.0
            
        elif self.effect_type == StatusEffectType.FREEZE:
            entity.attack_speed_multiplier = 1.0
            
    def draw_icon(self, screen, x, y, size=16):
        """Vẽ biểu tượng hiệu ứng"""
        color = self.get_icon_color()
        
        # Vẽ biểu tượng dựa trên loại hiệu ứng
        if self.effect_type == StatusEffectType.POISON:
            # Vẽ biểu tượng độc
            pygame.draw.circle(screen, color, (x + size//2, y + size//2), size//2)
            pygame.draw.circle(screen, (0, 0, 0), (x + size//2, y + size//2), size//4)
            
        elif self.effect_type == StatusEffectType.STUN:
            # Vẽ biểu tượng choáng
            pygame.draw.circle(screen, color, (x + size//2, y + size//2), size//2)
            pygame.draw.line(screen, (0, 0, 0), (x + size//4, y + size//4), 
                            (x + 3*size//4, y + 3*size//4), 2)
            pygame.draw.line(screen, (0, 0, 0), (x + 3*size//4, y + size//4), 
                            (x + size//4, y + 3*size//4), 2)
            
        elif self.effect_type == StatusEffectType.SLOW:
            # Vẽ biểu tượng làm chậm
            pygame.draw.circle(screen, color, (x + size//2, y + size//2), size//2)
            pygame.draw.polygon(screen, (0, 0, 0), [
                (x + size//4, y + size//4),
                (x + 3*size//4, y + size//2),
                (x + size//4, y + 3*size//4)
            ])
            
        elif self.effect_type == StatusEffectType.BURN:
            # Vẽ biểu tượng cháy
            pygame.draw.circle(screen, color, (x + size//2, y + size//2), size//2)
            for i in range(3):
                pygame.draw.line(screen, (255, 255, 0), 
                                (x + size//2, y + size//4), 
                                (x + size//2 + (i-1)*size//4, y + size//8), 2)
            
        elif self.effect_type == StatusEffectType.FREEZE:
            # Vẽ biểu tượng đóng băng
            pygame.draw.circle(screen, color, (x + size//2, y + size//2), size//2)
            pygame.draw.line(screen, (255, 255, 255), 
                            (x + size//4, y + size//2), 
                            (x + 3*size//4, y + size//2), 2)
            pygame.draw.line(screen, (255, 255, 255), 
                            (x + size//2, y + size//4), 
                            (x + size//2, y + 3*size//4), 2)
        
        # Vẽ thời gian còn lại
        remaining_percent = self.remaining / self.duration
        pygame.draw.arc(screen, (255, 255, 255), 
                       (x, y, size, size), 
                       0, remaining_percent * 2 * math.pi, 2)
