import pygame

class MiniMap:
    def __init__(self, game_map, width=150, height=150):
        self.game_map = game_map
        self.width = width
        self.height = height
        self.border_color = (200, 200, 200)
        self.background_color = (20, 20, 30, 180)  # Với alpha
        self.player_color = (0, 255, 0)
        self.monster_color = (255, 0, 0)
        self.item_color = (255, 255, 0)
        
        # Tỷ lệ thu nhỏ
        self.scale_x = self.width / (self.game_map.width * self.game_map.tile_size)
        self.scale_y = self.height / (self.game_map.height * self.game_map.tile_size)
        
    def update_scale(self):
        """Cập nhật tỷ lệ thu nhỏ khi kích thước bản đồ thay đổi"""
        self.scale_x = self.width / (self.game_map.width * self.game_map.tile_size)
        self.scale_y = self.height / (self.game_map.height * self.game_map.tile_size)
        
    def draw(self, screen, player, monsters, items, camera_x, camera_y, scale_x=1.0, scale_y=1.0):
        """Vẽ mini-map lên màn hình"""
        # Điều chỉnh kích thước mini-map theo tỷ lệ màn hình
        scaled_width = int(self.width * min(scale_x, scale_y))
        scaled_height = int(self.height * min(scale_x, scale_y))
        
        # Vị trí mini-map (góc phải dưới)
        map_x = screen.get_width() - scaled_width - int(20 * min(scale_x, scale_y))
        map_y = screen.get_height() - scaled_height - int(20 * min(scale_x, scale_y))
        
        # Tạo surface cho mini-map với hỗ trợ alpha
        mini_map_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        mini_map_surface.fill(self.background_color)
        
        # Vẽ viền
        pygame.draw.rect(mini_map_surface, self.border_color, 
                        (0, 0, scaled_width, scaled_height), 2)
        
        # Vẽ vùng hiển thị camera
        view_x = int((camera_x * self.scale_x) * min(scale_x, scale_y))
        view_y = int((camera_y * self.scale_y) * min(scale_x, scale_y))
        view_width = int((screen.get_width() / scale_x) * self.scale_x * min(scale_x, scale_y))
        view_height = int((screen.get_height() / scale_y) * self.scale_y * min(scale_x, scale_y))
        
        # Đảm bảo vùng hiển thị không vượt quá kích thước mini-map
        view_width = min(view_width, scaled_width)
        view_height = min(view_height, scaled_height)
        
        # Vẽ khung hiển thị camera
        pygame.draw.rect(mini_map_surface, (255, 255, 255, 100), 
                        (view_x, view_y, view_width, view_height), 1)
        
        # Vẽ người chơi
        player_x = int(player.x * self.scale_x * min(scale_x, scale_y))
        player_y = int(player.y * self.scale_y * min(scale_x, scale_y))
        player_size = int(4 * min(scale_x, scale_y))
        
        # Vẽ người chơi với hiệu ứng nhấp nháy
        pulse = (pygame.time.get_ticks() % 1000) / 1000.0
        pulse_size = int(player_size * (1 + 0.5 * pulse))
        
        pygame.draw.circle(mini_map_surface, (0, 255, 0, 150), 
                          (player_x, player_y), pulse_size)
        pygame.draw.circle(mini_map_surface, (255, 255, 255), 
                          (player_x, player_y), player_size)
        
        # Vẽ quái vật
        for monster in monsters:
            monster_x = int(monster.x * self.scale_x * min(scale_x, scale_y))
            monster_y = int(monster.y * self.scale_y * min(scale_x, scale_y))
            monster_size = int(3 * min(scale_x, scale_y))
            
            pygame.draw.circle(mini_map_surface, self.monster_color, 
                              (monster_x, monster_y), monster_size)
        
        # Vẽ vật phẩm
        for item in items:
            item_x = int(item.x * self.scale_x * min(scale_x, scale_y))
            item_y = int(item.y * self.scale_y * min(scale_x, scale_y))
            item_size = int(2 * min(scale_x, scale_y))
            
            # Vẽ vật phẩm với màu tương ứng
            pygame.draw.circle(mini_map_surface, item.color, 
                              (item_x, item_y), item_size)
        
        # Vẽ mini-map lên màn hình
        screen.blit(mini_map_surface, (map_x, map_y))
        
        # Vẽ nhãn "Mini-Map"
        font = pygame.font.SysFont(None, int(20 * min(scale_x, scale_y)))
        label = font.render("Mini-Map", True, (255, 255, 255))
        screen.blit(label, (map_x + (scaled_width - label.get_width()) // 2, 
                           map_y - label.get_height() - 5))
