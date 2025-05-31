import pygame
import random
import math
from dark_fantasy_game.src.player import Player, CharacterClass
from dark_fantasy_game.src.monster import Monster, MonsterType
from dark_fantasy_game.src.wave_manager import WaveManager
from dark_fantasy_game.src.map import Map
from dark_fantasy_game.src.mini_map import MiniMap
from dark_fantasy_game.src.effects_manager import EffectsManager
from dark_fantasy_game.src.quest_system import QuestSystem, QuestObjectiveType
from dark_fantasy_game.src.save_system import SaveSystem

# Game states
class State:
    MAIN_MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    VICTORY = 4

class Item:
    def __init__(self, item_type, x, y):
        self.item_type = item_type
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.pickup_radius = 50
        self.animation_offset = 0
        self.animation_direction = 1
        
        # Thiết lập thuộc tính dựa trên loại vật phẩm
        if item_type == "health":
            self.color = (255, 0, 0)  # Đỏ
            self.heal_amount = 20
        elif item_type == "damage":
            self.color = (255, 165, 0)  # Cam
            self.damage_boost = 5
        elif item_type == "defense":
            self.color = (0, 0, 255)  # Xanh dương
            self.defense_boost = 5
        elif item_type == "speed":
            self.color = (0, 255, 0)  # Xanh lá
            self.speed_boost = 1
            
    def update(self):
        # Hiệu ứng nhấp nhô cho vật phẩm
        self.animation_offset += 0.2 * self.animation_direction
        if abs(self.animation_offset) > 5:
            self.animation_direction *= -1
            
    def draw(self, screen, camera_x, camera_y, scale_x=1.0, scale_y=1.0):
        # Tính toán vị trí vẽ trên màn hình
        screen_x = int((self.x - camera_x) * scale_x)
        screen_y = int((self.y - camera_y + self.animation_offset) * scale_y)
        
        # Vẽ vật phẩm
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, 
                                             int(self.width * scale_x), 
                                             int(self.height * scale_y)))
        
        # Vẽ viền
        pygame.draw.rect(screen, (255, 255, 255), (screen_x, screen_y, 
                                                  int(self.width * scale_x), 
                                                  int(self.height * scale_y)), 2)
        
        # Vẽ hiệu ứng ánh sáng
        glow_surface = pygame.Surface((int(self.width * 2 * scale_x), 
                                      int(self.height * 2 * scale_y)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color, 100), 
                          (int(self.width * scale_x), int(self.height * scale_y)), 
                          int(self.width * scale_x))
        screen.blit(glow_surface, (screen_x - int(self.width * scale_x / 2), 
                                  screen_y - int(self.height * scale_y / 2)))

class GameState:
    def __init__(self):
        self.state = State.MAIN_MENU
        self.player = Player(400, 300, CharacterClass.WARRIOR)
        self.monsters = []
        self.wave_manager = WaveManager()
        self.score = 0
        self.level = 1
        self.infinity_mode = True  # Luôn bật chế độ vô hạn
        
        # Tạo map vô hạn với kích thước lớn hơn
        self.game_map = Map(200, 200)  # Map 200x200 tiles để tạo cảm giác vô hạn
        
        # Camera position
        self.camera_x = 0
        self.camera_y = 0
        
        # UI elements
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.buttons = {}
        
        # Screen dimensions
        self.screen_width = 800
        self.screen_height = 600
        
        # Hiệu ứng đặc biệt
        self.critical_hits = []  # Danh sách hiệu ứng chí mạng
        
        # Danh sách vật phẩm trên bản đồ
        self.items = []
        
        # Tỷ lệ rơi vật phẩm từ quái vật
        self.item_drop_chance = 0.3  # 30% cơ hội rơi vật phẩm
        
        # Số lượng quái vật cần tiêu diệt để hoàn thành wave
        self.monsters_per_wave = 10
        self.monsters_killed_in_wave = 0
        
        # Initialize main menu buttons
        self.init_main_menu()
        
        # Thêm mini-map
        self.mini_map = MiniMap(self.game_map)
        
        # Thêm quản lý hiệu ứng
        self.effects_manager = EffectsManager()
        
        # Thêm hệ thống nhiệm vụ
        self.quest_system = QuestSystem()
        
        # Thêm hệ thống lưu game
        self.save_system = SaveSystem()
        
    def init_main_menu(self):
        """Initialize main menu buttons with correct layout"""
        # Tạo các nút với kích thước phù hợp và khoảng cách đủ
        button_width = 200
        button_height = 50
        center_x = 400
        
        # Điều chỉnh vị trí các nút để không bị chồng lấn
        self.buttons = {
    "start": pygame.Rect(center_x - button_width//2, 200, button_width, button_height),
    "warrior": pygame.Rect(center_x - button_width - 20, 300, button_width, button_height),
    "mage": pygame.Rect(center_x + 20, 300, button_width, button_height),
    "quit": pygame.Rect(center_x - button_width//2, 400, button_width, button_height)
        }
        
        # Giữ lại hiệu ứng hoạt ảnh nhưng giảm bớt
        self.menu_animations = {
            "title_offset": 0,
            "title_direction": 1,
            "button_hover": None,
            "particles": []
        }
        
        # Giảm số lượng hạt nền để tránh quá tải
        for _ in range(30):
            self.menu_animations["particles"].append({
                "x": random.randint(0, 800),
                "y": random.randint(0, 600),
                "size": random.randint(1, 2),
                "speed": random.uniform(0.1, 0.5),
                "color": (random.randint(50, 150), random.randint(50, 100), random.randint(100, 200))
            })
        
    def spawn_item(self, x, y):
        """Spawn a random item at the given position"""
        item_types = ["health", "damage", "defense", "speed"]
        item_type = random.choice(item_types)
        self.items.append(Item(item_type, x, y))
        
    def handle_event(self, event, scale_x=1.0, scale_y=1.0):
        """Handle game events"""
        # Xử lý sự kiện cho hệ thống lưu game
        try:
            if self.save_system.handle_event(event, self):
                return True
        except AttributeError:
            # Xử lý trường hợp save_system chưa được khởi tạo
            pass
            
        if self.state == State.PLAYING:
            # Xử lý phím tắt cho hệ thống nhiệm vụ và lưu game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j:
                    try:
                        self.quest_system.toggle_quest_log()
                    except AttributeError:
                        # Xử lý trường hợp quest_system chưa được khởi tạo
                        pass
                    return True
                elif event.key == pygame.K_F5:
                    try:
                        self.save_system.toggle_save_menu()
                    except AttributeError:
                        # Xử lý trường hợp save_system chưa được khởi tạo
                        pass
                    return True
                elif event.key == pygame.K_F9:
                    try:
                        self.save_system.toggle_load_menu()
                    except AttributeError:
                        # Xử lý trường hợp save_system chưa được khởi tạo
                        pass
                    return True
                    
            # Pass events to player when playing
            self.player.handle_event(event, scale_x, scale_y)
            
            # Handle pause
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = State.PAUSED
                
        elif self.state == State.MAIN_MENU:
            # Handle main menu clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Sử dụng tọa độ chuột thực tế, không chia cho tỷ lệ
                    pos = event.pos
                    
                    # In ra vị trí chuột để debug
                    print(f"Mouse click at: {pos}")
                    
                    # Kiểm tra va chạm với các nút đã được điều chỉnh tỷ lệ
                    for name, rect in self.buttons.items():
                        scaled_rect = pygame.Rect(
                            int(rect.x * scale_x),
                            int(rect.y * scale_y),
                            int(rect.width * scale_x),
                            int(rect.height * scale_y)
                        )
                        
                        # In ra thông tin nút để debug
                        print(f"Button {name}: {scaled_rect}")
                        
                        if scaled_rect.collidepoint(pos):
                            print(f"Button {name} clicked!")
                            if name == "start":
                                self.state = State.PLAYING
                                self.start_game()
                            elif name == "warrior":
                                self.player = Player(400, 300, CharacterClass.WARRIOR)
                            elif name == "mage":
                                self.player = Player(400, 300, CharacterClass.MAGE)
                            elif name == "quit":
                                confirm = true  # Signal to quit
                                if confirm:
                                    return false
                        
        elif self.state == State.PAUSED:
            # Handle unpausing
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = State.PLAYING
                
        elif self.state in [State.GAME_OVER, State.VICTORY]:
            # Handle restart from game over or victory
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.state = State.MAIN_MENU
                self.init_main_menu()
                
        return True
        
    def handle_continuous_input(self, scale_x=1.0, scale_y=1.0):
        """Handle continuous input (keys held down)"""
        if self.state == State.PLAYING:
            # Player movement is handled in player.update()
            pass
            
    def start_game(self):
        """Start a new game"""
        self.monsters = []
        self.items = []  # Xóa tất cả vật phẩm
        self.score = 0
        self.level = 1
        self.monsters_killed_in_wave = 0
        self.wave_manager.start_wave(self.level)
        
        # Đặt người chơi vào giữa bản đồ
        map_center_x = self.game_map.width * self.game_map.tile_size / 2
        map_center_y = self.game_map.height * self.game_map.tile_size / 2
        self.player.x = map_center_x
        self.player.y = map_center_y
        
        # Bắt đầu nhiệm vụ đầu tiên
        self.quest_system.start_quest("main_1")
        self.quest_system.start_quest("achievement_1")
        
    def update(self):
        """Update game state"""
        if self.state == State.PLAYING:
            # Update player with delta time for animations
            self.player.update(1/60, self.game_map)
            
            # Update camera to follow player
            self.update_camera()
            
            # Update effects manager
            try:
                self.effects_manager.update()
            except AttributeError:
                # Xử lý trường hợp effects_manager chưa được khởi tạo
                pass
            
            # Update quest system
            try:
                self.quest_system.update(QuestObjectiveType.SURVIVE_TIME, "wave", 1, self.player.exp_system.level)
            except (AttributeError, NameError):
                # Xử lý trường hợp quest_system hoặc QuestObjectiveType chưa được khởi tạo
                pass
            
            # Update items
            for item in list(self.items):
                try:
                    item.update()
                    
                    # Check if player collects item
                    player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                    item_rect = pygame.Rect(item.x, item.y, item.width, item.height)
                    
                    # Tăng phạm vi nhặt vật phẩm
                    item_pickup_rect = pygame.Rect(
                        item.x - item.pickup_radius/2, 
                        item.y - item.pickup_radius/2,
                        item.width + item.pickup_radius,
                        item.height + item.pickup_radius
                    )
                    
                    if item_pickup_rect.colliderect(player_rect):
                        # Apply item effect
                        if item.item_type == "health":
                            self.player.heal(item.heal_amount)
                            try:
                                self.effects_manager.add_effect(self.player.x, self.player.y, "heal", 45)
                            except AttributeError:
                                pass
                        elif item.item_type == "damage":
                            if self.player.character_class == CharacterClass.WARRIOR:
                                self.player.stats.physical_damage += item.damage_boost
                            else:
                                self.player.stats.magic_damage += item.damage_boost
                        elif item.item_type == "defense":
                            self.player.stats.physical_defense += item.defense_boost
                        elif item.item_type == "speed":
                            self.player.speed += item.speed_boost
                            
                        # Remove item
                        self.items.remove(item)
                        
                        # Show pickup message
                        self.show_critical_hit(item.x, item.y, f"+{item.item_type.upper()}")
                        
                        # Update quest for item collection
                        try:
                            self.quest_system.update(QuestObjectiveType.COLLECT_ITEMS, item.item_type, 1, self.player.exp_system.level)
                        except (AttributeError, NameError):
                            pass
                except (AttributeError, TypeError):
                    # Xử lý trường hợp item không có các thuộc tính cần thiết
                    if item in self.items:
                        self.items.remove(item)
            
            # Update monsters
            for monster in list(self.monsters):
                monster.update(self.player, self.game_map)
                
                # Check for collisions with player attack
                attack_rect = self.player.get_attack_rect()
                if attack_rect and self.player.attack_animation_timer > 0:
                    # Tạo một bản sao của attack_rect để không ảnh hưởng đến rect gốc
                    real_attack_rect = pygame.Rect(
                        attack_rect.x, 
                        attack_rect.y,
                        attack_rect.width,
                        attack_rect.height
                    )
                    
                    # Tạo một bản sao của monster rect để kiểm tra va chạm
                    monster_rect = pygame.Rect(
                        monster.x,
                        monster.y,
                        monster.width,
                        monster.height
                    )
                    
                    # Kiểm tra va chạm - sử dụng khoảng cách cho AOE tròn thay vì va chạm hình chữ nhật
                    monster_center_x = monster.x + monster.width / 2
                    monster_center_y = monster.y + monster.height / 2
                    
                    player_center_x = self.player.x + self.player.width / 2
                    player_center_y = self.player.y + self.player.height / 2
                    
                    # Tính khoảng cách giữa trung tâm quái vật và người chơi
                    distance = math.sqrt((monster_center_x - player_center_x)**2 + 
                                        (monster_center_y - player_center_y)**2)
                    
                    # Nếu quái vật nằm trong phạm vi tấn công AOE
                    if distance <= self.player.attack_range:
                        # Player hit monster with attack
                        damage = self.player.stats.physical_damage if self.player.character_class == CharacterClass.WARRIOR else self.player.stats.magic_damage
                        
                        # Thêm hiệu ứng chí mạng (20% cơ hội)
                        if random.random() < 0.2:
                            damage = int(damage * 1.5)  # Sát thương chí mạng
                            # Hiển thị hiệu ứng chí mạng
                            self.show_critical_hit(monster.x, monster.y)
                            
                        monster.take_damage(damage)
                        
                        if monster.health <= 0:
                            # Tăng số quái vật đã tiêu diệt trong wave
                            self.monsters_killed_in_wave += 1
                            
                            # Nhận kinh nghiệm khi tiêu diệt quái vật
                            exp_gained = self.player.exp_system.calculate_monster_exp(monster)
                            level_up_result = self.player.gain_experience(exp_gained)
                            
                            # Hiển thị lượng kinh nghiệm nhận được
                            self.show_critical_hit(monster.x, monster.y - 30, f"+{exp_gained} EXP", (100, 100, 255))
                            
                            # Cập nhật nhiệm vụ
                            monster_type = monster.monster_type.value.lower()
                            self.quest_system.update(QuestObjectiveType.KILL_MONSTERS, monster_type, 1, self.player.exp_system.level)
                            self.quest_system.update(QuestObjectiveType.KILL_MONSTERS, "any", 1, self.player.exp_system.level)
                            
                            # Cập nhật nhiệm vụ đánh boss
                            if monster.is_boss:
                                self.quest_system.update(QuestObjectiveType.DEFEAT_BOSS, monster_type, 1, self.player.exp_system.level)
                                self.quest_system.update(QuestObjectiveType.DEFEAT_BOSS, "any", 1, self.player.exp_system.level)
                            
                            # Rơi vật phẩm khi quái vật chết (30% cơ hội)
                            if random.random() < self.item_drop_chance:
                                self.spawn_item(monster.x, monster.y)
                                
                            self.monsters.remove(monster)
                            self.score += monster.score_value
                            
                            # Hồi máu khi giết quái (5% máu tối đa)
                            heal_amount = int(self.player.stats.max_health * 0.05)
                            self.player.stats.current_health = min(self.player.stats.max_health, 
                                                                self.player.stats.current_health + heal_amount)
                
                # Check if monster is attacking player
                if monster.is_attacking and monster.is_player_in_range(self.player):
                    # Monster hit player
                    # Tính toán sát thương dựa trên phòng thủ của người chơi
                    damage = max(1, monster.damage - (self.player.stats.physical_defense // 5))
                    self.player.take_damage(damage)
                    
                    if self.player.stats.current_health <= 0:
                        self.state = State.GAME_OVER
            
            # Luôn ở chế độ vô hạn, không bao giờ kết thúc wave
            self.infinity_mode = True
            
            # Check if wave is complete (đã tiêu diệt đủ số quái vật)
            if self.monsters_killed_in_wave >= self.monsters_per_wave:
                self.level += 1
                self.monsters_killed_in_wave = 0
                self.wave_manager.start_wave(self.level)
                
                # Hiển thị thông báo lên cấp wave
                self.show_critical_hit(self.player.x, self.player.y - 50, f"WAVE {self.level}!", (255, 215, 0))
                
                # Tăng số lượng quái vật cần tiêu diệt theo cấp độ wave
                self.monsters_per_wave = 10 + (self.level - 1) * 2
                    
            # Spawn monsters if needed
            new_monster = self.wave_manager.update()
            if new_monster:
                # Spawn monster at a valid location on the map
                self.spawn_monster_at_valid_location(new_monster)
                
    def spawn_monster_at_valid_location(self, monster):
        """Spawn monster at a valid location around the player"""
        max_attempts = 50
        attempts = 0
        
        # Tạo quái vật xung quanh người chơi với khoảng cách từ 300-600 đơn vị
        spawn_distance = random.randint(300, 600)
        
        while attempts < max_attempts:
            # Tạo góc ngẫu nhiên
            angle = random.uniform(0, 2 * math.pi)
            
            # Tính toán vị trí spawn dựa trên vị trí người chơi
            monster.x = self.player.x + spawn_distance * math.cos(angle)
            monster.y = self.player.y + spawn_distance * math.sin(angle)
                
            # Check if location is valid
            if self.game_map.is_passable(monster.x, monster.y):
                self.monsters.append(monster)
                return
                
            attempts += 1
            
        # If no valid location found, just add the monster anyway
        self.monsters.append(monster)
        
    def update_camera(self):
        """Update camera position to follow player"""
        # Center camera on player
        target_x = self.player.x - self.screen_width / 2
        target_y = self.player.y - self.screen_height / 2
        
        # Smooth camera movement
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        # Không giới hạn camera trong map, cho phép di chuyển tự do trong map vô hạn
                
    def update_scale(self, scale_x, scale_y):
        """Update scale factors for UI elements"""
        # Update screen dimensions
        self.screen_width = int(800 * scale_x)
        self.screen_height = int(600 * scale_y)
        
        # Cập nhật kích thước font chữ theo tỷ lệ
        font_size = int(36 * min(scale_x, scale_y))
        small_font_size = int(24 * min(scale_x, scale_y))
        
        # Đảm bảo font không quá nhỏ hoặc quá lớn
        font_size = max(18, min(font_size, 72))
        small_font_size = max(12, min(small_font_size, 48))
        
        # Tạo lại font với kích thước mới
        self.font = pygame.font.SysFont(None, font_size)
        self.small_font = pygame.font.SysFont(None, small_font_size)
                
    def show_critical_hit(self, x, y, text="CRITICAL!", color=(255, 0, 0)):
        """Hiển thị hiệu ứng chí mạng hoặc thông báo"""
        self.critical_hits.append({
            "x": x,
            "y": y,
            "timer": 60,  # Hiển thị trong 60 frames (1 giây)
            "text": text,
            "color": color
        })
        
        # Thêm hiệu ứng hạt
        if text == "CRITICAL!":
            self.effects_manager.add_effect(x, y, "critical", 60)
        elif "WAVE" in text:
            self.effects_manager.add_effect(x, y, "level_up", 90)
        else:
            self.effects_manager.add_effect(x, y, "hit", 45)
                
    def draw(self, screen, scale_x=1.0, scale_y=1.0, offset_x=0, offset_y=0):
        """Draw the current game state"""
        if self.state == State.MAIN_MENU:
            self.draw_main_menu(screen, scale_x, scale_y, offset_x, offset_y)
        elif self.state == State.PLAYING:
            self.draw_game(screen, scale_x, scale_y, offset_x, offset_y)
        elif self.state == State.PAUSED:
            self.draw_game(screen, scale_x, scale_y, offset_x, offset_y)
            self.draw_pause_screen(screen, scale_x, scale_y, offset_x, offset_y)
        elif self.state == State.GAME_OVER:
            self.draw_game_over(screen, scale_x, scale_y, offset_x, offset_y)
        elif self.state == State.VICTORY:
            self.draw_victory(screen, scale_x, scale_y, offset_x, offset_y)
            
    def draw_main_menu(self, screen, scale_x, scale_y, offset_x=0, offset_y=0):
        """Draw the main menu with fixed layout"""
        # Vẽ nền menu chính với gradient đơn giản
        for y in range(self.screen_height):
            # Tạo gradient từ đen đến xanh đậm
            color_value = int(30 * (y / self.screen_height))
            blue_value = int(40 * (y / self.screen_height))
            pygame.draw.line(screen, (color_value, color_value, blue_value), 
                            (0, y), (self.screen_width, y))
        
        # Cập nhật và vẽ các hạt nền (giảm bớt hiệu ứng)
        for particle in self.menu_animations["particles"]:
            # Di chuyển hạt lên trên
            particle["y"] -= particle["speed"]
            # Nếu hạt ra khỏi màn hình, đặt lại vị trí
            if particle["y"] < 0:
                particle["y"] = self.screen_height
                particle["x"] = random.randint(0, self.screen_width)
            
            # Vẽ hạt với hiệu ứng mờ
            particle_surface = pygame.Surface((particle["size"] * 2, particle["size"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*particle["color"], 100), 
                              (particle["size"], particle["size"]), particle["size"])
            screen.blit(particle_surface, 
                       (int(particle["x"] * scale_x), int(particle["y"] * scale_y)))
        
        # Vẽ hiệu ứng ánh sáng đơn giản
        light_radius = int(150 * min(scale_x, scale_y))
        light_surface = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
        for r in range(light_radius, 0, -10):
            alpha = 5
            pygame.draw.circle(light_surface, (100, 100, 150, alpha), 
                              (light_radius, light_radius), r)
        screen.blit(light_surface, 
                   (self.screen_width // 2 - light_radius, 
                    int(150 * scale_y) - light_radius))
        
        # Cập nhật hiệu ứng chuyển động cho tiêu đề (giảm biên độ)
        self.menu_animations["title_offset"] += 0.1 * self.menu_animations["title_direction"]
        if abs(self.menu_animations["title_offset"]) > 3:
            self.menu_animations["title_direction"] *= -1
        
        # Title với hiệu ứng đổ bóng đơn giản
        title_font = pygame.font.SysFont(None, int(72 * min(scale_x, scale_y)))
        # Đổ bóng
        shadow_text = title_font.render("Dark Fantasy Stickman", True, (0, 0, 0))
        shadow_x = (self.screen_width - shadow_text.get_width()) // 2 + int(3 * scale_x) + offset_x
        shadow_y = int(100 * scale_y) + int(3 * scale_y) + offset_y + self.menu_animations["title_offset"]
        screen.blit(shadow_text, (shadow_x, shadow_y))
        
        # Text chính
        title_text = title_font.render("Dark Fantasy Stickman", True, (255, 215, 0))
        title_x = (self.screen_width - title_text.get_width()) // 2 + offset_x
        title_y = int(100 * scale_y) + offset_y + self.menu_animations["title_offset"]
        screen.blit(title_text, (title_x, title_y))
        
        # Kiểm tra vị trí chuột để hiệu ứng hover
        mouse_pos = pygame.mouse.get_pos()
        hover_button = None
        
        # Draw buttons with improved style
        for name, rect in self.buttons.items():
            scaled_rect = pygame.Rect(
                int(rect.x * scale_x) + offset_x,
                int(rect.y * scale_y) + offset_y,
                int(rect.width * scale_x),
                int(rect.height * scale_y)
            )
            
            # Kiểm tra hover
            is_hover = scaled_rect.collidepoint(mouse_pos)
            if is_hover:
                hover_button = name
                self.menu_animations["button_hover"] = name
            
            # Button background with gradient and hover effect
            if name == "warrior" and self.player.character_class == CharacterClass.WARRIOR:
                color1 = (80, 80, 180)
                color2 = (130, 130, 235)
            elif name == "mage" and self.player.character_class == CharacterClass.MAGE:
                color1 = (80, 80, 180)
                color2 = (130, 130, 235)
            elif name == "start":
                color1 = (0, 80, 0)
                color2 = (0, 130, 0)
            elif name == "load":
                color1 = (80, 40, 130)
                color2 = (130, 80, 180)
            elif name == "quit":
                color1 = (130, 0, 0)
                color2 = (180, 0, 0)
            else:
                color1 = (60, 60, 100)
                color2 = (90, 90, 130)
            
            # Tăng độ sáng nếu đang hover
            if is_hover:
                color1 = tuple(min(255, c + 40) for c in color1)
                color2 = tuple(min(255, c + 40) for c in color2)
            
            # Vẽ nút với gradient đơn giản
            for i in range(scaled_rect.height):
                progress = i / scaled_rect.height
                color = (
                    int(color1[0] + (color2[0] - color1[0]) * progress),
                    int(color1[1] + (color2[1] - color1[1]) * progress),
                    int(color1[2] + (color2[2] - color1[2]) * progress)
                )
                pygame.draw.line(screen, color, 
                                (scaled_rect.left, scaled_rect.top + i),
                                (scaled_rect.right, scaled_rect.top + i))
            
            # Vẽ viền nút
            pygame.draw.rect(screen, (200, 200, 200), scaled_rect, 1)
            
            # Button text with shadow
            button_font = pygame.font.SysFont(None, int(32 * min(scale_x, scale_y)))
            # Shadow
            shadow = button_font.render(name.capitalize(), True, (0, 0, 0))
            shadow_x = scaled_rect.centerx - shadow.get_width() // 2 + int(2 * scale_x)
            shadow_y = scaled_rect.centery - shadow.get_height() // 2 + int(2 * scale_y)
            screen.blit(shadow, (shadow_x, shadow_y))
            # Text
            button_text = button_font.render(name.capitalize(), True, (255, 255, 255))
            text_x = scaled_rect.centerx - button_text.get_width() // 2
            text_y = scaled_rect.centery - button_text.get_height() // 2
            screen.blit(button_text, (text_x, text_y))
        
        # Vẽ thông tin nhân vật ở vị trí không chồng lấn với các nút
        if self.player.character_class == CharacterClass.WARRIOR:
            char_info = [
                "WARRIOR",
                "High physical damage",
                "Strong defense",
                "Melee combat specialist"
            ]
            char_color = (255, 165, 0)
        else:
            char_info = [
                "MAGE",
                "High magic damage",
                "Ranged attacks",
                "Spell casting specialist"
            ]
            char_color = (138, 43, 226)
            
        # Vẽ khung thông tin ở vị trí không chồng lấn với các nút
        info_rect = pygame.Rect(
                int(50 * scale_x) + offset_x,
                int(470 * scale_y) + offset_y,  # Đổi từ 120 -> 60
                int(320 * scale_x),
                int(120 * scale_y)
        )
        # Vẽ nền bán trong suốt
        info_bg = pygame.Surface((info_rect.width, info_rect.height))
        info_bg.set_alpha(150)
        info_bg.fill((20, 20, 40))
        screen.blit(info_bg, (info_rect.x, info_rect.y))
        # Vẽ viền
        pygame.draw.rect(screen, char_color, info_rect, 2)
        
        # Vẽ thông tin nhân vật
        y_pos = info_rect.y + int(15 * scale_y)
        for i, line in enumerate(char_info):
            if i == 0:
                # Tiêu đề lớn hơn
                text = self.font.render(line, True, char_color)
                screen.blit(text, (info_rect.x + int(20 * scale_x), y_pos))
                y_pos += int(30 * scale_y)
            else:
                # Thêm bullet point đơn giản
                pygame.draw.circle(screen, char_color, 
                                  (info_rect.x + int(20 * scale_x), y_pos + int(6 * scale_y)), 
                                  int(3 * min(scale_x, scale_y)))
                text = self.small_font.render(line, True, (200, 200, 200))
                screen.blit(text, (info_rect.x + int(30 * scale_x), y_pos))
                y_pos += int(25 * scale_y)
            
        # Instructions với khung đơn giản và rộng hơn - di chuyển sang bên phải
        instructions = [
            "Use WASD to move, SPACE to attack",
            "Press TAB for stats, I for inventory",
            "Press J for quest log, F5 to save"
        ]
        
        # Vẽ khung hướng dẫn ở vị trí không chồng lấn
        inst_rect = pygame.Rect(
            int(430 * scale_x) + offset_x,  # Di chuyển sang phải để không chồng lấn với nút mage
            int(470 * scale_y) + offset_y,  # Di chuyển lên trên để không chồng lấn với các nút
            int(320 * scale_x),  # Giữ chiều rộng đủ lớn
            int(120 * scale_y)
        )
        # Vẽ nền bán trong suốt
        inst_bg = pygame.Surface((inst_rect.width, inst_rect.height))
        inst_bg.set_alpha(150)
        inst_bg.fill((20, 20, 40))
        screen.blit(inst_bg, (inst_rect.x, inst_rect.y))
        # Vẽ viền
        pygame.draw.rect(screen, (200, 200, 200), inst_rect, 2)
        
        # Tiêu đề hướng dẫn
        inst_title = self.font.render("INSTRUCTIONS", True, (255, 255, 255))
        screen.blit(inst_title, (inst_rect.x + int(20 * scale_x), inst_rect.y + int(15 * scale_y)))
        
        # Vẽ đường kẻ phân cách
        pygame.draw.line(screen, (100, 100, 150), 
                        (inst_rect.x + int(20 * scale_x), inst_rect.y + int(50 * scale_y)),
                        (inst_rect.right - int(20 * scale_x), inst_rect.y + int(50 * scale_y)),
                        1)
        
        # Vẽ hướng dẫn
        y_pos = inst_rect.y + int(60 * scale_y)
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, (200, 200, 200))
            screen.blit(inst_text, (inst_rect.x + int(20 * scale_x), y_pos))
            y_pos += int(20 * scale_y)
            
        # Vẽ phiên bản game
        version_text = self.small_font.render("v1.2.0", True, (150, 150, 150))
        screen.blit(version_text, (int(10 * scale_x) + offset_x, 
                                  self.screen_height - int(30 * scale_y) + offset_y))
            
    # Đã xóa phương thức trùng lặp show_critical_hit ở đây
        
    def draw_game(self, screen, scale_x, scale_y, offset_x=0, offset_y=0):
        """Draw the main gameplay screen"""
        # Draw map
        self.game_map.draw(screen, self.camera_x, self.camera_y, scale_x, scale_y)
        
        # Vẽ hiệu ứng ánh sáng xung quanh người chơi
        light_radius = int(200 * min(scale_x, scale_y))
        light_surface = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
        
        # Tạo gradient ánh sáng
        for r in range(light_radius, 0, -1):
            alpha = 5 if r > light_radius * 0.8 else 10
            pygame.draw.circle(light_surface, (255, 255, 200, alpha), 
                              (light_radius, light_radius), r)
                              
        # Vị trí ánh sáng trên màn hình
        light_x = int(self.player.x - self.camera_x) * scale_x - light_radius
        light_y = int(self.player.y - self.camera_y) * scale_y - light_radius
        screen.blit(light_surface, (light_x, light_y))
        
        # Draw items with improved effects
        for item in self.items:
            item.draw(screen, self.camera_x, self.camera_y, scale_x, scale_y)
            
            # Vẽ thêm hiệu ứng lấp lánh cho vật phẩm
            item_x = int((item.x - self.camera_x) * scale_x)
            item_y = int((item.y - self.camera_y + item.animation_offset) * scale_y)
            
            # Tạo hiệu ứng lấp lánh
            sparkle_size = int(5 * min(scale_x, scale_y))
            sparkle_offset = int(20 * min(scale_x, scale_y))
            
            # Vẽ các tia sáng nhỏ xung quanh vật phẩm
            for i in range(4):
                angle = i * math.pi / 2 + (pygame.time.get_ticks() % 1000) / 1000 * math.pi
                sparkle_x = item_x + int(math.cos(angle) * sparkle_offset)
                sparkle_y = item_y + int(math.sin(angle) * sparkle_offset)
                pygame.draw.circle(screen, (255, 255, 255), (sparkle_x, sparkle_y), sparkle_size)
        
        # Draw monsters with improved effects
        for monster in self.monsters:
            # Adjust position for camera
            monster_x = monster.x
            monster_y = monster.y
            monster.x = monster_x - self.camera_x
            monster.y = monster_y - self.camera_y
            monster.draw(screen, scale_x, scale_y)
            monster.x, monster.y = monster_x, monster_y
            
            # Vẽ thanh máu cho quái vật
            monster_screen_x = int((monster_x - self.camera_x) * scale_x)
            monster_screen_y = int((monster_y - self.camera_y) * scale_y) - int(15 * scale_y)
            monster_health_width = int(40 * scale_x)
            monster_health_height = int(5 * scale_y)
            
            # Tính tỷ lệ máu
            monster_health_percent = monster.health / monster.max_health
            
            # Vẽ nền thanh máu
            pygame.draw.rect(screen, (50, 0, 0), 
                            (monster_screen_x - monster_health_width//2, 
                             monster_screen_y, 
                             monster_health_width, 
                             monster_health_height))
                             
            # Vẽ phần máu hiện tại
            pygame.draw.rect(screen, (255, 0, 0), 
                            (monster_screen_x - monster_health_width//2, 
                             monster_screen_y, 
                             int(monster_health_width * monster_health_percent), 
                             monster_health_height))
            
        # Draw player (adjusted for camera) with improved effects
        player_x = self.player.x
        player_y = self.player.y
        self.player.x -= self.camera_x
        self.player.y -= self.camera_y
        self.player.draw(screen, scale_x, scale_y)
        self.player.x, self.player.y = player_x, player_y
        
        # Draw effects
        self.effects_manager.draw(screen, self.camera_x, self.camera_y, scale_x, scale_y)
        
        # Draw critical hit effects with improved animation
        for hit in list(self.critical_hits):
            # Adjust position for camera
            hit_x = int((hit["x"] - self.camera_x) * scale_x)
            hit_y = int((hit["y"] - self.camera_y) * scale_y)
            
            # Tính toán hiệu ứng phóng to và thu nhỏ
            scale_effect = 1.0
            if hit["timer"] > 45:
                # Phóng to nhanh
                scale_effect = 0.5 + (60 - hit["timer"]) / 30
            elif hit["timer"] < 15:
                # Thu nhỏ dần
                scale_effect = hit["timer"] / 15
                
            # Tính alpha dựa trên thời gian
            alpha = min(255, hit["timer"] * 4)
            
            # Vẽ hiệu ứng phát sáng xung quanh text
            glow_size = int(30 * scale_effect * min(scale_x, scale_y))
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            glow_color = hit.get("color", (255, 0, 0))
            for r in range(glow_size, 0, -2):
                alpha_glow = min(100, r * 3)
                pygame.draw.circle(glow_surface, (*glow_color, alpha_glow // 5), 
                                  (glow_size, glow_size), r)
            screen.blit(glow_surface, (hit_x - glow_size, hit_y - glow_size - 30))
            
            # Vẽ text với hiệu ứng
            crit_font = pygame.font.SysFont(None, int(36 * scale_effect * min(scale_x, scale_y)))
            text_surface = crit_font.render(hit["text"], True, hit.get("color", (255, 0, 0)))
            text_surface.set_alpha(alpha)
            
            # Vẽ đổ bóng cho text
            shadow_surface = crit_font.render(hit["text"], True, (0, 0, 0))
            shadow_surface.set_alpha(alpha // 2)
            screen.blit(shadow_surface, (hit_x - text_surface.get_width()//2 + 2, hit_y - 30 + 2))
            
            # Vẽ text chính
            screen.blit(text_surface, (hit_x - text_surface.get_width()//2, hit_y - 30))
            
            # Update timer
            hit["timer"] -= 1
            hit["y"] -= 0.8  # Move text upward faster
            
            # Remove expired effects
            if hit["timer"] <= 0:
                self.critical_hits.remove(hit)
        
        # Draw mini-map
        self.mini_map.draw(screen, self.player, self.monsters, self.items, 
                          self.camera_x, self.camera_y, scale_x, scale_y)
        
        # Draw quest notification
        self.quest_system.draw_quest_notification(screen, scale_x, scale_y)
        
        # Draw quest log if visible
        self.quest_system.draw_quest_log(screen, scale_x, scale_y)
        
        # Draw save/load menu if visible
        self.save_system.draw_save_load_menu(screen, scale_x, scale_y)
        
        # Draw HUD
        self.draw_hud(screen, scale_x, scale_y)
        
    def draw_hud(self, screen, scale_x, scale_y):
        """Draw the heads-up display"""
        # Vẽ thanh nền cho HUD
        hud_bg = pygame.Surface((self.screen_width, int(50 * scale_y)))
        hud_bg.set_alpha(180)
        hud_bg.fill((20, 20, 30))
        screen.blit(hud_bg, (0, 0))
        
        # Vẽ thanh nền cho thông tin bên phải
        right_hud_bg = pygame.Surface((int(200 * scale_x), int(180 * scale_y)))
        right_hud_bg.set_alpha(180)
        right_hud_bg.fill((20, 20, 30))
        screen.blit(right_hud_bg, (self.screen_width - int(200 * scale_x), 0))
        
        # Score với biểu tượng
        score_icon = pygame.Surface((int(20 * scale_x), int(20 * scale_y)))
        score_icon.fill((255, 215, 0))
        screen.blit(score_icon, (int(20 * scale_x), int(15 * scale_y)))
        score_text = self.font.render(f"{self.score}", True, (255, 255, 255))
        screen.blit(score_text, (int(50 * scale_x), int(15 * scale_y)))
        
        # Level/Wave với biểu tượng
        wave_icon = pygame.Surface((int(20 * scale_x), int(20 * scale_y)))
        wave_icon.fill((255, 100, 100))
        screen.blit(wave_icon, (int(150 * scale_x), int(15 * scale_y)))
        level_text = self.font.render(f"Wave {self.level}", True, (255, 215, 0))
        screen.blit(level_text, (int(180 * scale_x), int(15 * scale_y)))
        
        # Wave progress bar
        progress_percent = self.monsters_killed_in_wave / self.monsters_per_wave
        progress_width = int(150 * scale_x)
        progress_height = int(10 * scale_y)
        progress_x = int(300 * scale_x)
        progress_y = int(20 * scale_y)
        
        # Vẽ nền thanh tiến trình
        pygame.draw.rect(screen, (50, 50, 50), (progress_x, progress_y, progress_width, progress_height))
        # Vẽ phần đã hoàn thành
        pygame.draw.rect(screen, (255, 165, 0), 
                        (progress_x, progress_y, int(progress_width * progress_percent), progress_height))
        # Vẽ viền
        pygame.draw.rect(screen, (200, 200, 200), (progress_x, progress_y, progress_width, progress_height), 1)
        
        # Text hiển thị tiến trình
        progress_text = self.small_font.render(f"{self.monsters_killed_in_wave}/{self.monsters_per_wave}", True, (255, 255, 255))
        screen.blit(progress_text, (progress_x + progress_width/2 - progress_text.get_width()/2, 
                                   progress_y + progress_height + int(5 * scale_y)))
        
        # Health bar
        health_percent = self.player.stats.current_health / self.player.stats.max_health
        health_width = int(180 * scale_x)
        health_height = int(20 * scale_y)
        health_x = self.screen_width - health_width - int(10 * scale_x)
        health_y = int(20 * scale_y)
        
        # Vẽ nền thanh máu
        pygame.draw.rect(screen, (50, 0, 0), (health_x, health_y, health_width, health_height))
        # Vẽ phần máu hiện tại với gradient
        health_color = (255, int(health_percent * 100), int(health_percent * 100))
        pygame.draw.rect(screen, health_color, 
                        (health_x, health_y, int(health_width * health_percent), health_height))
        # Vẽ viền
        pygame.draw.rect(screen, (200, 200, 200), (health_x, health_y, health_width, health_height), 1)
        
        # Text hiển thị máu
        health_text = self.small_font.render(f"HP: {int(self.player.stats.current_health)}/{self.player.stats.max_health}", 
                                           True, (255, 255, 255))
        screen.blit(health_text, (health_x + health_width/2 - health_text.get_width()/2, 
                                 health_y + health_height/2 - health_text.get_height()/2))
        
        # Character class với icon
        class_y = int(60 * scale_y)
        class_icon_color = (138, 43, 226) if self.player.character_class == CharacterClass.MAGE else (255, 165, 0)
        pygame.draw.circle(screen, class_icon_color, 
                          (self.screen_width - int(180 * scale_x), class_y + int(10 * scale_y)), 
                          int(10 * scale_y))
        class_text = self.font.render(f"{self.player.character_class.value}", True, (255, 255, 255))
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
        
        defense_text = self.font.render(f"DEF: {self.player.stats.physical_defense}", True, (0, 200, 255))
        screen.blit(defense_text, (self.screen_width - int(160 * scale_x), defense_y))
        
        # Hiển thị sát thương với icon
        damage_y = int(140 * scale_y)
        # Vẽ icon kiếm hoặc phép thuật
        if self.player.character_class == CharacterClass.WARRIOR:
            # Icon kiếm
            sword_points = [
                (self.screen_width - int(180 * scale_x), damage_y),
                (self.screen_width - int(170 * scale_x), damage_y - int(15 * scale_y)),
                (self.screen_width - int(160 * scale_x), damage_y)
            ]
            pygame.draw.polygon(screen, (255, 165, 0), sword_points)
            pygame.draw.polygon(screen, (255, 255, 255), sword_points, 1)
            damage_text = self.font.render(f"ATK: {self.player.stats.physical_damage}", True, (255, 165, 0))
        else:
            # Icon phép thuật
            pygame.draw.circle(screen, (138, 43, 226), 
                              (self.screen_width - int(170 * scale_x), damage_y - int(5 * scale_y)), 
                              int(8 * scale_y))
            pygame.draw.circle(screen, (255, 255, 255), 
                              (self.screen_width - int(170 * scale_x), damage_y - int(5 * scale_y)), 
                              int(8 * scale_y), 1)
            damage_text = self.font.render(f"MAG: {self.player.stats.magic_damage}", True, (138, 43, 226))
            
        screen.blit(damage_text, (self.screen_width - int(160 * scale_x), damage_y))
        
        # Hiển thị số nhiệm vụ đang hoạt động
        quest_count = self.quest_system.get_active_quests_count()
        if quest_count > 0:
            quest_text = self.small_font.render(f"Active Quests: {quest_count} (Press J)", True, (255, 215, 0))
            screen.blit(quest_text, (int(20 * scale_x), int(40 * scale_y)))
        
    def draw_pause_screen(self, screen, scale_x, scale_y, offset_x=0, offset_y=0):
        """Draw the pause screen overlay with simplified visuals"""
        # Semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Vẽ khung menu tạm dừng
        menu_width = int(350 * scale_x)
        menu_height = int(250 * scale_y)
        menu_x = (self.screen_width - menu_width) // 2
        menu_y = (self.screen_height - menu_height) // 2
        
        # Vẽ nền menu
        menu_bg = pygame.Surface((menu_width, menu_height))
        menu_bg.set_alpha(200)
        menu_bg.fill((20, 20, 40))
        screen.blit(menu_bg, (menu_x, menu_y))
        
        # Vẽ viền menu
        pygame.draw.rect(screen, (100, 100, 200), 
                       (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Pause text
        pause_font = pygame.font.SysFont(None, int(48 * min(scale_x, scale_y)))
        pause_text = pause_font.render("PAUSED", True, (255, 255, 255))
        pause_x = menu_x + (menu_width - pause_text.get_width()) // 2
        pause_y = menu_y + int(30 * scale_y)
        screen.blit(pause_text, (pause_x, pause_y))
        
        # Vẽ đường kẻ phân cách
        pygame.draw.line(screen, (100, 100, 200), 
                        (menu_x + int(30 * scale_x), menu_y + int(70 * scale_y)),
                        (menu_x + menu_width - int(30 * scale_x), menu_y + int(70 * scale_y)),
                        1)
        
        # Tạo các nút menu tạm dừng
        pause_buttons = [
            {"text": "Resume Game", "key": "ESC", "y_offset": 100},
            {"text": "View Stats", "key": "TAB", "y_offset": 140},
            {"text": "Inventory", "key": "I", "y_offset": 180},
            {"text": "Save Game", "key": "F5", "y_offset": 220}
        ]
        
        # Vẽ các nút menu
        for button in pause_buttons:
            button_y = menu_y + int(button["y_offset"] * scale_y)
            
            # Vẽ text nút
            button_font = pygame.font.SysFont(None, int(28 * min(scale_x, scale_y)))
            button_text = button_font.render(button["text"], True, (200, 200, 200))
            screen.blit(button_text, (menu_x + int(30 * scale_x), button_y))
            
            # Vẽ phím tắt
            key_font = pygame.font.SysFont(None, int(24 * min(scale_x, scale_y)))
            key_text = key_font.render(f"[{button['key']}]", True, (150, 150, 200))
            screen.blit(key_text, (menu_x + menu_width - key_text.get_width() - int(30 * scale_x), button_y))
            
    def draw_game_over(self, screen, scale_x, scale_y, offset_x=0, offset_y=0):
        """Draw the game over screen"""
        # Vẽ màn chơi bên dưới với hiệu ứng mờ
        self.draw_game(screen, scale_x, scale_y)
        
        # Semi-transparent overlay with gradient
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        for y in range(screen.get_height()):
            # Tạo gradient từ đen đến đỏ đậm
            red_value = int(40 * (y / screen.get_height()))
            pygame.draw.line(overlay, (red_value, 0, 0), 
                            (0, y), (screen.get_width(), y))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Hiệu ứng máu chảy từ trên xuống
        for i in range(10):
            blood_x = random.randint(0, self.screen_width)
            blood_height = random.randint(50, 200)
            blood_width = random.randint(5, 20)
            blood_alpha = random.randint(100, 200)
            blood_surface = pygame.Surface((blood_width, blood_height))
            blood_surface.fill((150, 0, 0))
            blood_surface.set_alpha(blood_alpha)
            screen.blit(blood_surface, (blood_x, 0))
        
        # Game over text với hiệu ứng rung
        game_over_font = pygame.font.SysFont(None, int(72 * min(scale_x, scale_y)))
        shake_x = random.randint(-3, 3)
        shake_y = random.randint(-3, 3)
        
        # Đổ bóng cho text
        shadow_text = game_over_font.render("GAME OVER", True, (0, 0, 0))
        shadow_x = (self.screen_width - shadow_text.get_width()) // 2 + int(6 * scale_x) + shake_x
        shadow_y = (self.screen_height - shadow_text.get_height()) // 2 - int(50 * scale_y) + int(6 * scale_y) + shake_y
        screen.blit(shadow_text, (shadow_x, shadow_y))
        
        # Text chính
        game_over_text = game_over_font.render("GAME OVER", True, (200, 0, 0))
        game_over_x = (self.screen_width - game_over_text.get_width()) // 2 + shake_x
        game_over_y = (self.screen_height - game_over_text.get_height()) // 2 - int(50 * scale_y) + shake_y
        screen.blit(game_over_text, (game_over_x, game_over_y))
        
        # Vẽ khung thông tin
        info_rect = pygame.Rect(
            self.screen_width // 2 - int(200 * scale_x),
            game_over_y + int(100 * scale_y),
            int(400 * scale_x),
            int(200 * scale_y)
        )
        
        # Vẽ nền bán trong suốt
        info_bg = pygame.Surface((info_rect.width, info_rect.height))
        info_bg.set_alpha(150)
        info_bg.fill((50, 0, 0))
        screen.blit(info_bg, (info_rect.x, info_rect.y))
        
        # Vẽ viền với hiệu ứng 3D
        pygame.draw.rect(screen, (100, 0, 0), info_rect, 2)
        pygame.draw.line(screen, (150, 0, 0), 
                        (info_rect.left, info_rect.top),
                        (info_rect.right, info_rect.top), 2)
        pygame.draw.line(screen, (150, 0, 0), 
                        (info_rect.left, info_rect.top),
                        (info_rect.left, info_rect.bottom), 2)
        
        # Score với icon
        score_y = info_rect.y + int(30 * scale_y)
        score_icon = pygame.Surface((int(20 * scale_x), int(20 * scale_y)))
        score_icon.fill((255, 215, 0))
        screen.blit(score_icon, (info_rect.x + int(30 * scale_x), score_y))
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (info_rect.x + int(60 * scale_x), score_y))
        
        # Wave reached với icon
        wave_y = score_y + int(50 * scale_y)
        wave_icon = pygame.Surface((int(20 * scale_x), int(20 * scale_y)))
        wave_icon.fill((255, 100, 100))
        screen.blit(wave_icon, (info_rect.x + int(30 * scale_x), wave_y))
        wave_text = self.font.render(f"Infinity Wave Reached: {self.level}", True, (255, 215, 0))
        screen.blit(wave_text, (info_rect.x + int(60 * scale_x), wave_y))
        
        # Thêm thông tin về quái vật đã tiêu diệt
        monsters_y = wave_y + int(50 * scale_y)
        monsters_text = self.font.render(f"Monsters Killed: {self.monsters_killed_in_wave}", True, (200, 200, 200))
        screen.blit(monsters_text, (info_rect.x + int(60 * scale_x), monsters_y))
        
        # Restart instructions với hiệu ứng nhấp nháy
        if pygame.time.get_ticks() % 1000 < 500:
            restart_color = (255, 255, 255)
        else:
            restart_color = (200, 0, 0)
            
        restart_text = self.font.render("Press R to return to main menu", True, restart_color)
        restart_x = (self.screen_width - restart_text.get_width()) // 2
        restart_y = info_rect.bottom + int(30 * scale_y)
        screen.blit(restart_text, (restart_x, restart_y))
        
    def draw_victory(self, screen, scale_x, scale_y, offset_x=0, offset_y=0):
        """Draw the victory screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Victory text
        victory_font = pygame.font.SysFont(None, int(72 * min(scale_x, scale_y)))
        victory_text = victory_font.render("VICTORY!", True, (0, 255, 0))
        victory_x = (self.screen_width - victory_text.get_width()) // 2
        victory_y = (self.screen_height - victory_text.get_height()) // 2 - int(50 * scale_y)
        screen.blit(victory_text, (victory_x, victory_y))
        
        # Score
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        score_x = (self.screen_width - score_text.get_width()) // 2
        score_y = victory_y + int(100 * scale_y)
        screen.blit(score_text, (score_x, score_y))
        
        # Try infinity mode message
        if not self.infinity_mode:
            infinity_text = self.font.render("Try Infinity Mode for endless challenges!", True, (255, 215, 0))
            infinity_x = (self.screen_width - infinity_text.get_width()) // 2
            infinity_y = score_y + int(50 * scale_y)
            screen.blit(infinity_text, (infinity_x, infinity_y))
        
        # Restart instructions
        restart_text = self.font.render("Press R to return to main menu", True, (200, 200, 200))
        restart_x = (self.screen_width - restart_text.get_width()) // 2
        restart_y = score_y + int(100 * scale_y)
        screen.blit(restart_text, (restart_x, restart_y))
