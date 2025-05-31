import pygame
import math
from dark_fantasy_game.src.ui_components import HealthBar, SkillButton, MiniMapImproved

class GameUI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Font chữ
        self.font = pygame.font.SysFont("Arial", 36)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.tiny_font = pygame.font.SysFont("Arial", 18)
        
        # Thanh máu người chơi
        self.player_health_bar = HealthBar(
            self.screen_width - 190, 20, 180, 20, 100  # max_value sẽ được cập nhật sau
        )
        
        # Các nút kỹ năng
        self.skill_buttons = [
            SkillButton(10, self.screen_height - 60, 50, "1", (255, 100, 100), 5),
            SkillButton(70, self.screen_height - 60, 50, "2", (100, 100, 255), 8),
            SkillButton(130, self.screen_height - 60, 50, "3", (100, 255, 100), 12)
        ]
        
        # Thiết lập tooltip cho các nút kỹ năng
        self.skill_buttons[0].tooltip = "Basic Attack: Deal damage to enemies"
        self.skill_buttons[1].tooltip = "Area Attack: Hit multiple enemies"
        self.skill_buttons[2].tooltip = "Special Move: Powerful attack with cooldown"
        
        # Hiệu ứng đặc biệt
        self.effects = []
        
        # Cài đặt hiển thị
        self.show_grid = True  # Mặc định hiển thị lưới
        
    def update_scale(self, scale_x, scale_y):
        """Cập nhật tỷ lệ cho UI khi kích thước màn hình thay đổi"""
        self.screen_width = int(800 * scale_x)
        self.screen_height = int(600 * scale_y)
        
        # Cập nhật font chữ theo tỷ lệ
        font_size = int(36 * min(scale_x, scale_y))
        small_font_size = int(24 * min(scale_x, scale_y))
        tiny_font_size = int(18 * min(scale_x, scale_y))
        
        # Đảm bảo font không quá nhỏ hoặc quá lớn
        font_size = max(18, min(font_size, 72))
        small_font_size = max(12, min(small_font_size, 48))
        tiny_font_size = max(10, min(tiny_font_size, 36))
        
        # Tạo lại font với kích thước mới
        self.font = pygame.font.SysFont("Arial", font_size)
        self.small_font = pygame.font.SysFont("Arial", small_font_size)
        self.tiny_font = pygame.font.SysFont("Arial", tiny_font_size)
        
        # Cập nhật vị trí thanh máu
        self.player_health_bar.rect.x = self.screen_width - 190
        
        # Cập nhật vị trí các nút kỹ năng
        for i, button in enumerate(self.skill_buttons):
            button.rect.y = self.screen_height - 60
            button.rect.x = 10 + i * 60
    
    def update(self, player, dt=1/60):
        """Cập nhật trạng thái UI"""
        # Cập nhật thanh máu người chơi
        self.player_health_bar.max_value = player.stats.max_health
        self.player_health_bar.update(player.stats.current_health)
        
        # Cập nhật các nút kỹ năng
        for button in self.skill_buttons:
            button.update(dt)
            
        # Cập nhật hiệu ứng
        for effect in list(self.effects):
            effect["timer"] -= dt
            if effect["timer"] <= 0:
                self.effects.remove(effect)
    
    def draw(self, screen, player, monsters, game_map, scale_x=1.0, scale_y=1.0):
        """Vẽ giao diện game"""
        # Vẽ lưới nếu được bật
        if self.show_grid:
            self.draw_grid(screen, game_map, scale_x, scale_y)
        
        # Vẽ thanh máu người chơi
        self.player_health_bar.draw(screen, scale_x, scale_y)
        
        # Vẽ text hiển thị máu
        health_text = self.small_font.render(f"HP: {int(player.stats.current_health)}/{player.stats.max_health}", 
                                           True, (255, 255, 255))
        health_x = self.screen_width - 190 + 90 * scale_x - health_text.get_width() / 2
        health_y = 20 * scale_y + 10 * scale_y - health_text.get_height() / 2
        screen.blit(health_text, (health_x, health_y))
        
        # Vẽ các nút kỹ năng
        for button in self.skill_buttons:
            button.draw(screen, self.tiny_font, scale_x, scale_y)
        
        # Vẽ thông tin người chơi
        self.draw_player_info(screen, player, scale_x, scale_y)
        
        # Vẽ thông tin quái vật
        self.draw_monster_info(screen, monsters, scale_x, scale_y)
        
        # Vẽ hiệu ứng
        self.draw_effects(screen, scale_x, scale_y)
    
    def draw_grid(self, screen, game_map, scale_x, scale_y):
        """Vẽ lưới nền đẹp hơn"""
        # Tính toán kích thước và vị trí lưới
        grid_size = game_map.tile_size
        grid_color = (30, 30, 50, 50)  # Màu lưới mờ hơn
        
        # Tạo surface bán trong suốt cho lưới
        grid_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Vẽ các đường dọc
        for x in range(0, self.screen_width, int(grid_size * scale_x)):
            pygame.draw.line(grid_surface, grid_color, (x, 0), (x, self.screen_height), 1)
        
        # Vẽ các đường ngang
        for y in range(0, self.screen_height, int(grid_size * scale_y)):
            pygame.draw.line(grid_surface, grid_color, (0, y), (self.screen_width, y), 1)
        
        # Hiển thị lưới lên màn hình
        screen.blit(grid_surface, (0, 0))
    
    def draw_player_info(self, screen, player, scale_x, scale_y):
        """Vẽ thông tin người chơi"""
        # Vẽ thanh nền cho thông tin bên phải
        right_hud_bg = pygame.Surface((int(200 * scale_x), int(180 * scale_y)), pygame.SRCALPHA)
        right_hud_bg.fill((20, 20, 30, 180))
        screen.blit(right_hud_bg, (self.screen_width - int(200 * scale_x), 0))
        
        # Vẽ viền cho khung thông tin
        pygame.draw.rect(screen, (100, 100, 150), 
                        (self.screen_width - int(200 * scale_x), 0, 
                         int(200 * scale_x), int(180 * scale_y)), 
                        1, border_radius=5)
        
        # Character class với icon
        class_y = int(60 * scale_y)
        class_icon_color = (138, 43, 226) if player.character_class.value == "Mage" else (255, 165, 0)
        pygame.draw.circle(screen, class_icon_color, 
                          (self.screen_width - int(180 * scale_x), class_y + int(10 * scale_y)), 
                          int(10 * scale_y))
        class_text = self.font.render(f"{player.character_class.value}", True, (255, 255, 255))
        screen.blit(class_text, (self.screen_width - int(160 * scale_x), class_y))
        
        # Hiển thị phòng thủ với icon hình khiên
        defense_y = int(100 * scale_y)
        # Vẽ icon khiên
        shield_points = [
            (self.screen_width - int(180 * scale_x), defense_y),
            (self.screen_width - int(170 * scale_x), defense_y - int(10 * scale_y)),
            (self.screen_width - int(160 * scale_x), defense_y)
        ]
        pygame.draw.polygon(screen, (0, 200, 255), shield_points)
        pygame.draw.polygon(screen, (255, 255, 255), shield_points, 1)
        
        defense_text = self.font.render(f"DEF: {player.stats.physical_defense}", True, (0, 200, 255))
        screen.blit(defense_text, (self.screen_width - int(160 * scale_x), defense_y))
        
        # Hiển thị sát thương với icon
        damage_y = int(140 * scale_y)
        # Vẽ icon kiếm hoặc phép thuật
        if player.character_class.value == "Warrior":
            # Icon kiếm
            sword_points = [
                (self.screen_width - int(180 * scale_x), damage_y),
                (self.screen_width - int(170 * scale_x), damage_y - int(15 * scale_y)),
                (self.screen_width - int(160 * scale_x), damage_y)
            ]
            pygame.draw.polygon(screen, (255, 165, 0), sword_points)
            pygame.draw.polygon(screen, (255, 255, 255), sword_points, 1)
            
            damage_text = self.font.render(f"ATK: {player.stats.physical_damage}", True, (255, 165, 0))
        else:
            # Icon phép thuật
            magic_radius = int(8 * scale_y)
            pygame.draw.circle(screen, (138, 43, 226), 
                              (self.screen_width - int(170 * scale_x), damage_y), 
                              magic_radius)
            pygame.draw.circle(screen, (255, 255, 255), 
                              (self.screen_width - int(170 * scale_x), damage_y), 
                              magic_radius, 1)
            
            damage_text = self.font.render(f"MAG: {player.stats.magic_damage}", True, (138, 43, 226))
            
        screen.blit(damage_text, (self.screen_width - int(160 * scale_x), damage_y))
    
    def draw_monster_info(self, screen, monsters, scale_x, scale_y):
        """Vẽ thông tin quái vật gần nhất"""
        # Tìm quái vật gần nhất (nếu có)
        if not monsters:
            return
            
        # Vẽ thanh máu cho quái vật
        for monster in monsters:
            # Vẽ tên và cấp độ quái vật phía trên thanh máu
            monster_name = f"{monster.monster_type.value} Lv.{monster.level}"
            if monster.is_boss:
                monster_name = f"BOSS: {monster_name}"
                
            name_text = self.tiny_font.render(monster_name, True, (255, 255, 255))
            name_x = int((monster.x - monster.width/2) * scale_x)
            name_y = int((monster.y - monster.height - 25) * scale_y)
            
            # Vẽ nền cho tên
            name_bg = pygame.Surface((name_text.get_width() + 10, name_text.get_height() + 6), pygame.SRCALPHA)
            name_bg.fill((0, 0, 0, 150))
            screen.blit(name_bg, (name_x - 5, name_y - 3))
            screen.blit(name_text, (name_x, name_y))
            
            # Vẽ thanh máu đẹp hơn
            health_width = int(50 * scale_x)
            health_height = int(6 * scale_y)
            health_x = int((monster.x - health_width/2) * scale_x)
            health_y = int((monster.y - monster.height - 10) * scale_y)
            
            # Nền thanh máu
            pygame.draw.rect(screen, (50, 0, 0), 
                            (health_x, health_y, health_width, health_height),
                            border_radius=3)
            
            # Phần máu hiện tại
            health_percent = monster.health / monster.max_health
            if health_percent > 0:
                # Màu thanh máu thay đổi theo % máu
                if health_percent > 0.6:
                    health_color = (255, 0, 0)  # Đỏ
                elif health_percent > 0.3:
                    health_color = (255, 165, 0)  # Cam
                else:
                    health_color = (255, 50, 50)  # Đỏ nhạt
                    
                pygame.draw.rect(screen, health_color, 
                                (health_x, health_y, 
                                 int(health_width * health_percent), health_height),
                                border_radius=3)
            
            # Viền thanh máu
            pygame.draw.rect(screen, (200, 200, 200), 
                            (health_x, health_y, health_width, health_height), 
                            1, border_radius=3)
    
    def draw_effects(self, screen, scale_x, scale_y):
        """Vẽ các hiệu ứng đặc biệt"""
        for effect in self.effects:
            if effect["type"] == "damage":
                # Hiệu ứng sát thương
                alpha = int(255 * (effect["timer"] / effect["max_timer"]))
                text = self.small_font.render(effect["text"], True, effect["color"])
                text.set_alpha(alpha)
                screen.blit(text, (effect["x"] * scale_x, (effect["y"] - effect["offset"]) * scale_y))
            elif effect["type"] == "heal":
                # Hiệu ứng hồi máu
                alpha = int(255 * (effect["timer"] / effect["max_timer"]))
                text = self.small_font.render(effect["text"], True, (0, 255, 0))
                text.set_alpha(alpha)
                screen.blit(text, (effect["x"] * scale_x, (effect["y"] - effect["offset"]) * scale_y))
    
    def add_effect(self, x, y, text, effect_type="damage", color=(255, 0, 0), duration=1.0):
        """Thêm hiệu ứng mới"""
        self.effects.append({
            "x": x,
            "y": y,
            "text": text,
            "type": effect_type,
            "color": color,
            "timer": duration,
            "max_timer": duration,
            "offset": 0
        })
        
    def toggle_grid(self):
        """Bật/tắt hiển thị lưới"""
        self.show_grid = not self.show_grid
