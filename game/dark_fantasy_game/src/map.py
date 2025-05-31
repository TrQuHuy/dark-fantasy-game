import pygame
import random
import os

class Tile:
    def __init__(self, tile_type, passable=True):
        self.tile_type = tile_type
        self.passable = passable
        
class Minimap:
    def __init__(self, game_map, size=150):
        self.game_map = game_map
        self.size = size
        self.visible = True
        self.zoomed = False
        self.zoom_factor = 1.0
        self.surface = pygame.Surface((size, size))
        self.position = (20, 20)  # Vị trí góc trên bên phải
        
    def toggle_visibility(self):
        self.visible = not self.visible
        
    def toggle_zoom(self):
        self.zoomed = not self.zoomed
        if self.zoomed:
            self.zoom_factor = 2.0
            self.size = 300
        else:
            self.zoom_factor = 1.0
            self.size = 150
        self.surface = pygame.Surface((self.size, self.size))
        
    def draw(self, screen, player_x, player_y):
        if not self.visible:
            return
            
        # Vẽ nền cho minimap
        self.surface.fill((0, 0, 0))
        
        # Tính tỷ lệ giữa kích thước minimap và kích thước thực của map
        map_width_pixels = self.game_map.width * self.game_map.tile_size
        map_height_pixels = self.game_map.height * self.game_map.tile_size
        
        scale_x = self.size / map_width_pixels
        scale_y = self.size / map_height_pixels
        
        # Vẽ các tile lên minimap với màu tương ứng
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                tile = self.game_map.tiles[y][x]
                
                # Xác định màu cho từng loại tile
                if tile.tile_type == 'grass':
                    color = (34, 139, 34)
                elif tile.tile_type == 'dirt':
                    color = (139, 69, 19)
                elif tile.tile_type == 'stone':
                    color = (169, 169, 169)
                elif tile.tile_type == 'water':
                    color = (65, 105, 225)
                elif tile.tile_type == 'tree':
                    color = (0, 100, 0)
                elif tile.tile_type == 'wall':
                    color = (105, 105, 105)
                else:
                    color = (255, 255, 255)
                
                # Tính toán vị trí và kích thước của tile trên minimap
                mini_x = int(x * self.game_map.tile_size * scale_x)
                mini_y = int(y * self.game_map.tile_size * scale_y)
                mini_width = max(1, int(self.game_map.tile_size * scale_x))
                mini_height = max(1, int(self.game_map.tile_size * scale_y))
                
                # Vẽ tile
                pygame.draw.rect(self.surface, color, (mini_x, mini_y, mini_width, mini_height))
        
        # Vẽ vị trí người chơi (điểm đỏ)
        player_mini_x = int((player_x / map_width_pixels) * self.size)
        player_mini_y = int((player_y / map_height_pixels) * self.size)
        pygame.draw.circle(self.surface, (255, 0, 0), (player_mini_x, player_mini_y), 3)
        
        # Vẽ viền cho minimap
        pygame.draw.rect(self.surface, (255, 255, 255), (0, 0, self.size, self.size), 2)
        
        # Hiển thị minimap lên màn hình
        screen.blit(self.surface, self.position)
        
class Map:
    def __init__(self, width, height):
        # Tăng kích thước map lên rất lớn để tạo cảm giác vô hạn
        self.width = width * 4
        self.height = height * 4
        self.tile_size = 32
        self.tiles = []
        self.objects = []
        self.load_tiles()
        self.generate_map()
        self.minimap = Minimap(self)
        
    def load_tiles(self):
        # Tạo các tile đơn giản
        self.tile_images = {
            'grass': pygame.Surface((self.tile_size, self.tile_size)),
            'dirt': pygame.Surface((self.tile_size, self.tile_size)),
            'stone': pygame.Surface((self.tile_size, self.tile_size)),
            'water': pygame.Surface((self.tile_size, self.tile_size)),
            'tree': pygame.Surface((self.tile_size, self.tile_size)),
            'wall': pygame.Surface((self.tile_size, self.tile_size))
        }
        
        # Tô màu cho các tile
        self.tile_images['grass'].fill((34, 139, 34))  # Xanh lá đậm
        self.tile_images['dirt'].fill((139, 69, 19))   # Nâu
        self.tile_images['stone'].fill((169, 169, 169)) # Xám
        self.tile_images['water'].fill((65, 105, 225))  # Xanh dương
        self.tile_images['tree'].fill((0, 100, 0))     # Xanh lá đậm hơn
        self.tile_images['wall'].fill((105, 105, 105))  # Xám đậm
        
    def generate_map(self):
        # Tạo map trống với cỏ
        self.tiles = [[Tile('grass', True) for _ in range(self.width)] for _ in range(self.height)]
        
        # Thêm các vùng đất
        self.generate_regions('dirt', 40, 15)
        
        # Thêm các vùng đá
        self.generate_regions('stone', 30, 10)
        
        # Thêm các vùng nước
        self.generate_regions('water', 20, 8, False)  # Nước không thể đi qua
        
        # Thêm cây (không thể đi qua)
        self.add_obstacles('tree', 200, False)
        
        # Không thêm tường bao quanh map để tạo cảm giác vô hạn
        
    def generate_regions(self, tile_type, num_regions, max_size, passable=True):
        for _ in range(num_regions):
            # Chọn điểm bắt đầu ngẫu nhiên
            x = random.randint(1, self.width - max_size - 1)
            y = random.randint(1, self.height - max_size - 1)
            
            # Kích thước ngẫu nhiên
            size_x = random.randint(3, max_size)
            size_y = random.randint(3, max_size)
            
            # Tạo vùng
            for i in range(size_y):
                for j in range(size_x):
                    if 0 <= y + i < self.height and 0 <= x + j < self.width:
                        # Tạo viền không đều
                        if random.random() < 0.8:
                            self.tiles[y + i][x + j] = Tile(tile_type, passable)
    
    def add_obstacles(self, tile_type, count, passable=False):
        placed = 0
        while placed < count:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            
            # Chỉ đặt trên cỏ hoặc đất
            if self.tiles[y][x].tile_type in ['grass', 'dirt'] and self.tiles[y][x].passable:
                self.tiles[y][x] = Tile(tile_type, passable)
                placed += 1
    
    def is_passable(self, x, y):
        # Kiểm tra xem vị trí có thể đi qua không
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        
        # Xử lý trường hợp ra ngoài biên map - tạo cảm giác vô hạn bằng cách wrap around
        tile_x = tile_x % self.width
        tile_y = tile_y % self.height
        
        return self.tiles[tile_y][tile_x].passable
    
    def draw(self, screen, camera_x=0, camera_y=0, scale_x=1.0, scale_y=1.0):
        # Vẽ map với camera offset
        visible_width = int(screen.get_width() / (self.tile_size * scale_x)) + 2
        visible_height = int(screen.get_height() / (self.tile_size * scale_y)) + 2
        
        # Tính toán vị trí tile bắt đầu hiển thị
        start_x = int(camera_x // self.tile_size)
        start_y = int(camera_y // self.tile_size)
        
        # Vẽ các tile trong vùng nhìn thấy
        for y_offset in range(-1, visible_height + 1):
            for x_offset in range(-1, visible_width + 1):
                # Tính toán vị trí tile trong map (với wrap around)
                tile_x = (start_x + x_offset) % self.width
                tile_y = (start_y + y_offset) % self.height
                
                # Tính toán vị trí vẽ trên màn hình
                screen_x = int(((start_x + x_offset) * self.tile_size - camera_x) * scale_x)
                screen_y = int(((start_y + y_offset) * self.tile_size - camera_y) * scale_y)
                
                # Tính toán kích thước tile sau khi scale
                scaled_size_x = int(self.tile_size * scale_x)
                scaled_size_y = int(self.tile_size * scale_y)
                
                # Vẽ tile
                tile_type = self.tiles[tile_y][tile_x].tile_type
                scaled_tile = pygame.transform.scale(self.tile_images[tile_type], (scaled_size_x, scaled_size_y))
                screen.blit(scaled_tile, (screen_x, screen_y))
