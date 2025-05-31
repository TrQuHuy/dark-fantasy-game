import pygame
import math

class DayNightCycle:
    def __init__(self):
        self.time = 0  # 0-1440 phút (24 giờ)
        self.day = 1
        self.cycle_speed = 0.5  # Tốc độ chu kỳ (phút/frame)
        self.day_length = 1440  # Độ dài một ngày (phút)
        
        # Thời điểm chuyển giao
        self.dawn_time = 360     # 6:00
        self.day_time = 480      # 8:00
        self.dusk_time = 1080    # 18:00
        self.night_time = 1200   # 20:00
        
    def update(self):
        """Cập nhật thời gian"""
        self.time += self.cycle_speed
        
        # Sang ngày mới
        if self.time >= self.day_length:
            self.time = 0
            self.day += 1
            print(f"Day {self.day} has begun!")
            
    def get_time_of_day(self):
        """Lấy thời điểm trong ngày"""
        if self.dawn_time <= self.time < self.day_time:
            return "dawn"
        elif self.day_time <= self.time < self.dusk_time:
            return "day"
        elif self.dusk_time <= self.time < self.night_time:
            return "dusk"
        else:
            return "night"
            
    def get_time_string(self):
        """Lấy chuỗi thời gian dạng HH:MM"""
        hours = int(self.time / 60)
        minutes = int(self.time % 60)
        return f"{hours:02d}:{minutes:02d}"
        
    def get_light_level(self):
        """Lấy mức độ ánh sáng (0-1)"""
        time_of_day = self.get_time_of_day()
        
        if time_of_day == "day":
            return 1.0
        elif time_of_day == "night":
            return 0.3
        elif time_of_day == "dawn":
            # Tăng dần từ 0.3 đến 1.0
            progress = (self.time - self.dawn_time) / (self.day_time - self.dawn_time)
            return 0.3 + (0.7 * progress)
        else:  # dusk
            # Giảm dần từ 1.0 đến 0.3
            progress = (self.time - self.dusk_time) / (self.night_time - self.dusk_time)
            return 1.0 - (0.7 * progress)
            
    def apply_lighting(self, screen):
        """Áp dụng hiệu ứng ánh sáng lên màn hình"""
        light_level = self.get_light_level()
        
        # Tạo lớp phủ với độ trong suốt phù hợp
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        
        # Màu phủ dựa trên thời gian
        time_of_day = self.get_time_of_day()
        if time_of_day == "dawn":
            overlay.fill((255, 200, 100))  # Cam nhạt
        elif time_of_day == "day":
            overlay.fill((255, 255, 255))  # Trắng
        elif time_of_day == "dusk":
            overlay.fill((200, 100, 50))   # Cam đỏ
        else:  # night
            overlay.fill((0, 0, 50))       # Xanh đậm
            
        # Điều chỉnh độ trong suốt
        alpha = int(255 * (1 - light_level))
        overlay.set_alpha(alpha)
        
        # Áp dụng lớp phủ
        screen.blit(overlay, (0, 0))
        
    def get_monster_spawn_modifier(self):
        """Lấy hệ số sinh quái dựa trên thời gian"""
        time_of_day = self.get_time_of_day()
        
        if time_of_day == "day":
            return 1.0
        elif time_of_day == "night":
            return 2.0  # Gấp đôi quái vào ban đêm
        else:  # dawn or dusk
            return 1.5
