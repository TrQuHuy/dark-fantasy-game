import pygame
import math

class Button:
    def __init__(self, x, y, width, height, text, color1=(60, 60, 100), color2=(90, 90, 130)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color1 = color1  # Màu gradient bắt đầu
        self.color2 = color2  # Màu gradient kết thúc
        self.is_hover = False
        self.border_radius = 10
        self.hover_glow_size = 15  # Size of the glow effect when hovering
        
    def draw(self, screen, font, scale_x=1.0, scale_y=1.0, offset_x=0, offset_y=0):
        # Tính toán kích thước và vị trí theo tỷ lệ
        scaled_rect = pygame.Rect(
            int(self.rect.x * scale_x) + offset_x,
            int(self.rect.y * scale_y) + offset_y,
            int(self.rect.width * scale_x),
            int(self.rect.height * scale_y)
        )
        
        # Tăng độ sáng nếu đang hover
        color1 = self.color1
        color2 = self.color2
        if self.is_hover:
            color1 = tuple(min(255, c + 40) for c in self.color1)
            color2 = tuple(min(255, c + 40) for c in self.color2)
            
            # Thêm hiệu ứng phát sáng khi hover
            glow_size = self.hover_glow_size
            glow_surface = pygame.Surface((scaled_rect.width + glow_size*2, scaled_rect.height + glow_size*2), pygame.SRCALPHA)
            for r in range(glow_size, 0, -2):
                alpha = 10 - r // 2  # Fade out the glow
                pygame.draw.rect(glow_surface, (*color2, alpha), 
                                (glow_size - r, glow_size - r, 
                                 scaled_rect.width + r*2, scaled_rect.height + r*2), 
                                border_radius=self.border_radius)
            screen.blit(glow_surface, (scaled_rect.x - glow_size, scaled_rect.y - glow_size))
        
        # Vẽ nút với bo góc
        button_surface = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
        
        # Vẽ gradient
        for i in range(scaled_rect.height):
            progress = i / scaled_rect.height
            color = (
                int(color1[0] + (color2[0] - color1[0]) * progress),
                int(color1[1] + (color2[1] - color1[1]) * progress),
                int(color1[2] + (color2[2] - color1[2]) * progress)
            )
            pygame.draw.line(button_surface, color, 
                            (0, i), (scaled_rect.width, i))
        
        # Vẽ nút với bo góc
        screen.blit(button_surface, (scaled_rect.x, scaled_rect.y))
        
        # Draw a thicker border when hovering
        border_width = 2 if self.is_hover else 1
        pygame.draw.rect(screen, (200, 200, 200), scaled_rect, border_width, border_radius=self.border_radius)
        
        # Button text với đổ bóng
        button_text = font.render(self.text, True, (255, 255, 255))
        text_x = scaled_rect.centerx - button_text.get_width() // 2
        text_y = scaled_rect.centery - button_text.get_height() // 2
        
        # Đổ bóng
        shadow = font.render(self.text, True, (0, 0, 0))
        shadow_x = text_x + 2
        shadow_y = text_y + 2
        screen.blit(shadow, (shadow_x, shadow_y))
        
        # Text chính
        screen.blit(button_text, (text_x, text_y))
        
    def check_hover(self, mouse_pos, scale_x=1.0, scale_y=1.0, offset_x=0, offset_y=0):
        scaled_rect = pygame.Rect(
            int(self.rect.x * scale_x) + offset_x,
            int(self.rect.y * scale_y) + offset_y,
            int(self.rect.width * scale_x),
            int(self.rect.height * scale_y)
        )
        self.is_hover = scaled_rect.collidepoint(mouse_pos)
        return self.is_hover

class HealthBar:
    def __init__(self, x, y, width, height, max_value):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.current_value = max_value
        self.border_radius = 5
        
    def update(self, current_value):
        self.current_value = max(0, min(current_value, self.max_value))
        
    def draw(self, screen, scale_x=1.0, scale_y=1.0, offset_x=0, offset_y=0):
        # Tính toán kích thước và vị trí theo tỷ lệ
        scaled_rect = pygame.Rect(
            int(self.rect.x * scale_x) + offset_x,
            int(self.rect.y * scale_y) + offset_y,
            int(self.rect.width * scale_x),
            int(self.rect.height * scale_y)
        )
        
        # Tính tỷ lệ giá trị hiện tại
        value_percent = self.current_value / self.max_value
        
        # Vẽ nền thanh
        pygame.draw.rect(screen, (50, 0, 0), scaled_rect, border_radius=self.border_radius)
        
        # Vẽ phần giá trị hiện tại
        if value_percent > 0:
            # Tính màu dựa trên phần trăm (từ đỏ đến xanh lá)
            r = int(255 * (1 - value_percent))
            g = int(255 * value_percent)
            b = 0
            
            value_rect = pygame.Rect(
                scaled_rect.x,
                scaled_rect.y,
                int(scaled_rect.width * value_percent),
                scaled_rect.height
            )
            pygame.draw.rect(screen, (r, g, b), value_rect, border_radius=self.border_radius)
        
        # Vẽ viền
        pygame.draw.rect(screen, (200, 200, 200), scaled_rect, 1, border_radius=self.border_radius)

class SkillButton:
    def __init__(self, x, y, size, key, icon_color=(100, 100, 255), cooldown=0):
        self.rect = pygame.Rect(x, y, size, size)
        self.key = key
        self.icon_color = icon_color
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.is_hover = False
        self.tooltip = ""
        
    def update(self, dt=1/60):
        if self.current_cooldown > 0:
            self.current_cooldown -= dt
            
    def draw(self, screen, font, scale_x=1.0, scale_y=1.0, offset_x=0, offset_y=0):
        # Tính toán kích thước và vị trí theo tỷ lệ
        scaled_rect = pygame.Rect(
            int(self.rect.x * scale_x) + offset_x,
            int(self.rect.y * scale_y) + offset_y,
            int(self.rect.width * scale_x),
            int(self.rect.height * scale_y)
        )
        
        # Vẽ nền nút
        bg_color = (40, 40, 60)
        if self.is_hover:
            bg_color = (60, 60, 80)
        pygame.draw.rect(screen, bg_color, scaled_rect, border_radius=5)
        
        # Vẽ icon kỹ năng (đơn giản hóa)
        icon_rect = pygame.Rect(
            scaled_rect.x + scaled_rect.width * 0.2,
            scaled_rect.y + scaled_rect.height * 0.2,
            scaled_rect.width * 0.6,
            scaled_rect.height * 0.6
        )
        pygame.draw.rect(screen, self.icon_color, icon_rect, border_radius=3)
        
        # Vẽ phần cooldown (che phủ một phần nút)
        if self.current_cooldown > 0:
            cooldown_percent = self.current_cooldown / self.cooldown
            cooldown_height = int(scaled_rect.height * cooldown_percent)
            cooldown_rect = pygame.Rect(
                scaled_rect.x,
                scaled_rect.y + scaled_rect.height - cooldown_height,
                scaled_rect.width,
                cooldown_height
            )
            cooldown_surface = pygame.Surface((cooldown_rect.width, cooldown_rect.height), pygame.SRCALPHA)
            cooldown_surface.fill((0, 0, 0, 150))
            screen.blit(cooldown_surface, (cooldown_rect.x, cooldown_rect.y))
        
        # Vẽ phím tắt
        key_text = font.render(self.key, True, (255, 255, 255))
        screen.blit(key_text, (scaled_rect.x + 5, scaled_rect.y + 5))
        
        # Vẽ viền
        border_color = (100, 100, 150) if self.is_hover else (80, 80, 120)
        pygame.draw.rect(screen, border_color, scaled_rect, 2, border_radius=5)
        
        # Vẽ tooltip nếu đang hover
        if self.is_hover and self.tooltip:
            self.draw_tooltip(screen, font, scaled_rect)
            
    def draw_tooltip(self, screen, font, button_rect):
        tooltip_text = font.render(self.tooltip, True, (255, 255, 255))
        tooltip_width = tooltip_text.get_width() + 20
        tooltip_height = tooltip_text.get_height() + 10
        
        # Vị trí tooltip (phía trên nút)
        tooltip_rect = pygame.Rect(
            button_rect.x - (tooltip_width - button_rect.width) // 2,
            button_rect.y - tooltip_height - 5,
            tooltip_width,
            tooltip_height
        )
        
        # Đảm bảo tooltip không vượt ra ngoài màn hình
        if tooltip_rect.x < 10:
            tooltip_rect.x = 10
        if tooltip_rect.right > screen.get_width() - 10:
            tooltip_rect.right = screen.get_width() - 10
            
        # Vẽ nền tooltip
        tooltip_bg = pygame.Surface((tooltip_rect.width, tooltip_rect.height), pygame.SRCALPHA)
        tooltip_bg.fill((20, 20, 40, 220))
        screen.blit(tooltip_bg, (tooltip_rect.x, tooltip_rect.y))
        
        # Vẽ viền
        pygame.draw.rect(screen, (150, 150, 200), tooltip_rect, 1, border_radius=5)
        
        # Vẽ text
        screen.blit(tooltip_text, (tooltip_rect.x + 10, tooltip_rect.y + 5))
        
    def check_hover(self, mouse_pos, scale_x=1.0, scale_y=1.0, offset_x=0, offset_y=0):
        scaled_rect = pygame.Rect(
            int(self.rect.x * scale_x) + offset_x,
            int(self.rect.y * scale_y) + offset_y,
            int(self.rect.width * scale_x),
            int(self.rect.height * scale_y)
        )
        self.is_hover = scaled_rect.collidepoint(mouse_pos)
        return self.is_hover

class MiniMapImproved:
    def __init__(self, game_map, x, y, size=150):
        self.game_map = game_map
        self.rect = pygame.Rect(x, y, size, size)
        self.border_radius = 10
        self.alpha = 180  # Độ trong suốt
        
    def draw(self, screen, player, monsters, items, camera_x, camera_y, scale_x=1.0, scale_y=1.0):
        # Tính toán kích thước và vị trí theo tỷ lệ
        scaled_rect = pygame.Rect(
            int(self.rect.x * scale_x),
            int(self.rect.y * scale_y),
            int(self.rect.width * scale_x),
            int(self.rect.height * scale_y)
        )
        
        # Tạo surface cho mini-map với hỗ trợ alpha
        minimap_surface = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
        
        # Vẽ nền bán trong suốt
        pygame.draw.rect(minimap_surface, (20, 20, 40, self.alpha), 
                        (0, 0, scaled_rect.width, scaled_rect.height), 
                        border_radius=self.border_radius)
        
        # Tính tỷ lệ thu nhỏ cho mini-map
        map_width = self.game_map.width * self.game_map.tile_size
        map_height = self.game_map.height * self.game_map.tile_size
        scale_factor = min(scaled_rect.width / map_width, scaled_rect.height / map_height) * 0.8
        
        # Vẽ các vật phẩm trên mini-map
        for item in items:
            item_x = int(item.x * scale_factor) + scaled_rect.width // 2 - int(player.x * scale_factor)
            item_y = int(item.y * scale_factor) + scaled_rect.height // 2 - int(player.y * scale_factor)
            
            # Chỉ vẽ nếu nằm trong mini-map
            if 0 <= item_x < scaled_rect.width and 0 <= item_y < scaled_rect.height:
                pygame.draw.circle(minimap_surface, item.color, (item_x, item_y), 3)
        
        # Vẽ các quái vật trên mini-map
        for monster in monsters:
            monster_x = int(monster.x * scale_factor) + scaled_rect.width // 2 - int(player.x * scale_factor)
            monster_y = int(monster.y * scale_factor) + scaled_rect.height // 2 - int(player.y * scale_factor)
            
            # Chỉ vẽ nếu nằm trong mini-map
            if 0 <= monster_x < scaled_rect.width and 0 <= monster_y < scaled_rect.height:
                # Màu khác nhau cho boss và quái thường
                color = (255, 0, 0) if monster.is_boss else (200, 0, 0)
                size = 5 if monster.is_boss else 3
                pygame.draw.circle(minimap_surface, color, (monster_x, monster_y), size)
        
        # Vẽ người chơi ở giữa mini-map
        pygame.draw.circle(minimap_surface, (0, 255, 0), 
                          (scaled_rect.width // 2, scaled_rect.height // 2), 5)
        
        # Vẽ viền
        pygame.draw.rect(minimap_surface, (150, 150, 200, 255), 
                        (0, 0, scaled_rect.width, scaled_rect.height), 
                        2, border_radius=self.border_radius)
        
        # Hiển thị mini-map lên màn hình
        screen.blit(minimap_surface, (scaled_rect.x, scaled_rect.y))
