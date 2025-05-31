import pygame
import random
import math

class Effect:
    def __init__(self, x, y, effect_type, duration=60):
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.duration = duration
        self.timer = duration
        self.scale = 1.0
        self.alpha = 255
        self.color = (255, 255, 255)
        self.particles = []
        
        # Khởi tạo hiệu ứng dựa trên loại
        if effect_type == "hit":
            self.color = (255, 0, 0)
            self.create_hit_particles()
        elif effect_type == "heal":
            self.color = (0, 255, 0)
            self.create_heal_particles()
        elif effect_type == "magic":
            self.color = (100, 100, 255)
            self.create_magic_particles()
        elif effect_type == "critical":
            self.color = (255, 255, 0)
            self.create_critical_particles()
        elif effect_type == "level_up":
            self.color = (255, 215, 0)
            self.create_level_up_particles()
            
    def create_hit_particles(self):
        """Tạo các hạt cho hiệu ứng đánh trúng"""
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            size = random.randint(2, 5)
            lifetime = random.randint(20, 40)
            self.particles.append({
                "x": 0,
                "y": 0,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": size,
                "lifetime": lifetime,
                "timer": lifetime,
                "color": (255, random.randint(0, 100), 0)
            })
            
    def create_heal_particles(self):
        """Tạo các hạt cho hiệu ứng hồi máu"""
        for _ in range(15):
            angle = random.uniform(-math.pi/2 - 0.5, -math.pi/2 + 0.5)  # Hướng lên trên
            speed = random.uniform(0.5, 2)
            size = random.randint(3, 6)
            lifetime = random.randint(30, 60)
            self.particles.append({
                "x": random.uniform(-10, 10),
                "y": random.uniform(0, 20),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": size,
                "lifetime": lifetime,
                "timer": lifetime,
                "color": (random.randint(0, 100), 255, random.randint(0, 100))
            })
            
    def create_magic_particles(self):
        """Tạo các hạt cho hiệu ứng phép thuật"""
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(5, 15)
            size = random.randint(2, 6)
            lifetime = random.randint(30, 50)
            self.particles.append({
                "x": math.cos(angle) * distance,
                "y": math.sin(angle) * distance,
                "vx": math.cos(angle) * 0.5,
                "vy": math.sin(angle) * 0.5,
                "size": size,
                "lifetime": lifetime,
                "timer": lifetime,
                "color": (random.randint(100, 200), 100, 255)
            })
            
    def create_critical_particles(self):
        """Tạo các hạt cho hiệu ứng chí mạng"""
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            size = random.randint(3, 7)
            lifetime = random.randint(30, 50)
            self.particles.append({
                "x": 0,
                "y": 0,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": size,
                "lifetime": lifetime,
                "timer": lifetime,
                "color": (255, 255, random.randint(0, 100))
            })
            
    def create_level_up_particles(self):
        """Tạo các hạt cho hiệu ứng lên cấp"""
        for i in range(30):
            angle = i * (2 * math.pi / 30)
            speed = random.uniform(1, 3)
            size = random.randint(4, 8)
            lifetime = random.randint(40, 70)
            self.particles.append({
                "x": 0,
                "y": 0,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": size,
                "lifetime": lifetime,
                "timer": lifetime,
                "color": (255, 215, random.randint(0, 255))
            })
            
    def update(self):
        """Cập nhật hiệu ứng"""
        self.timer -= 1
        
        # Cập nhật các thuộc tính dựa trên thời gian còn lại
        progress = self.timer / self.duration
        self.alpha = int(255 * progress)
        
        # Cập nhật các hạt
        for particle in list(self.particles):
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["timer"] -= 1
            
            # Xóa hạt hết thời gian
            if particle["timer"] <= 0:
                self.particles.remove(particle)
                
    def is_finished(self):
        """Kiểm tra xem hiệu ứng đã kết thúc chưa"""
        return self.timer <= 0
        
    def draw(self, screen, camera_x, camera_y, scale_x=1.0, scale_y=1.0):
        """Vẽ hiệu ứng lên màn hình"""
        # Tính toán vị trí trên màn hình
        screen_x = int((self.x - camera_x) * scale_x)
        screen_y = int((self.y - camera_y) * scale_y)
        
        # Vẽ các hạt
        for particle in self.particles:
            # Tính toán vị trí hạt trên màn hình
            particle_x = screen_x + int(particle["x"] * scale_x)
            particle_y = screen_y + int(particle["y"] * scale_y)
            
            # Tính kích thước hạt
            particle_size = int(particle["size"] * min(scale_x, scale_y))
            
            # Tính alpha dựa trên thời gian còn lại
            particle_alpha = int(255 * (particle["timer"] / particle["lifetime"]))
            
            # Tạo màu với alpha
            particle_color = (*particle["color"], particle_alpha)
            
            # Vẽ hạt
            particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, 
                              (particle_size, particle_size), particle_size)
            screen.blit(particle_surface, (particle_x - particle_size, particle_y - particle_size))

class EffectsManager:
    def __init__(self):
        self.effects = []
        
    def add_effect(self, x, y, effect_type, duration=60):
        """Thêm hiệu ứng mới"""
        self.effects.append(Effect(x, y, effect_type, duration))
        
    def update(self):
        """Cập nhật tất cả hiệu ứng"""
        for effect in list(self.effects):
            effect.update()
            
            # Xóa hiệu ứng đã kết thúc
            if effect.is_finished():
                self.effects.remove(effect)
                
    def draw(self, screen, camera_x, camera_y, scale_x=1.0, scale_y=1.0):
        """Vẽ tất cả hiệu ứng"""
        for effect in self.effects:
            effect.draw(screen, camera_x, camera_y, scale_x, scale_y)
