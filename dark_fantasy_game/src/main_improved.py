import pygame
import sys
from dark_fantasy_game.src.game_state import GameState
from dark_fantasy_game.src.improved_menu import ImprovedMenu
from dark_fantasy_game.src.game_ui import GameUI

# Initialize Pygame
pygame.init()
pygame.display.set_caption("Dark Fantasy Stickman")

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Game:
    def __init__(self):
        # Khởi tạo màn hình với chế độ cố định (không thể thay đổi kích thước)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption("Dark Fantasy Stickman")
        
        # Khởi tạo menu cải tiến
        self.improved_menu = ImprovedMenu(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Khởi tạo UI game cải tiến
        self.game_ui = GameUI(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Tạo cửa sổ tùy chỉnh chỉ có nút đóng (X)
        self.create_custom_window()
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = GameState()
        
        # Lưu kích thước ban đầu để tính toán tỷ lệ
        self.original_width = WINDOW_WIDTH
        self.original_height = WINDOW_HEIGHT
        self.scale_factor_x = 1.0
        self.scale_factor_y = 1.0
        
        # Trạng thái toàn màn hình
        self.is_fullscreen = False
        self.last_windowed_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Tự động điều chỉnh kích thước màn hình theo độ phân giải màn hình
        self.auto_adjust_screen_size()
        
        # Khởi tạo menu cải tiến
        self.improved_menu = ImprovedMenu(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Khởi tạo UI game cải tiến
        self.game_ui = GameUI(WINDOW_WIDTH, WINDOW_HEIGHT)
        
    def create_custom_window(self):
        # Kích thước và vị trí của nút đóng
        self.close_button_rect = pygame.Rect(WINDOW_WIDTH - 30, 5, 25, 25)
        self.close_button_color = (200, 0, 0)  # Màu đỏ
        self.close_button_hover_color = (255, 0, 0)  # Màu đỏ sáng khi di chuột qua
        self.is_close_button_hover = False
        
        # Tạo thanh tiêu đề
        self.title_bar_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 35)
        self.title_bar_color = (50, 50, 50)  # Màu xám đậm
        
        # Biến để theo dõi việc kéo cửa sổ
        self.dragging = False
        self.drag_offset = (0, 0)
        
    def auto_adjust_screen_size(self):
        """Tự động điều chỉnh kích thước màn hình dựa trên độ phân giải màn hình"""
        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h
        
        # Tính toán kích thước tối ưu (80% kích thước màn hình)
        optimal_width = int(screen_width * 0.8)
        optimal_height = int(screen_height * 0.8)
        
        # Đảm bảo tỷ lệ khung hình 4:3
        aspect_ratio = 4/3
        
        if optimal_width / optimal_height > aspect_ratio:  # Nếu quá rộng
            optimal_width = int(optimal_height * aspect_ratio)
        elif optimal_width / optimal_height < aspect_ratio:  # Nếu quá cao
            optimal_height = int(optimal_width / aspect_ratio)
            
        # Cập nhật kích thước màn hình
        self.resize(optimal_width, optimal_height)
        self.last_windowed_size = (optimal_width, optimal_height)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.is_fullscreen:
                        # Thoát khỏi chế độ toàn màn hình khi nhấn ESC
                        self.toggle_fullscreen()
                    else:
                        # Chuyển sang trạng thái tạm dừng nếu đang chơi
                        if self.game_state.state == 1:  # PLAYING
                            event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
                            self.game_state.handle_event(event, self.scale_factor_x, self.scale_factor_y)
                        else:
                            self.running = False
                elif event.key == pygame.K_g and self.game_state.state == 1:  # PLAYING
                    # Bật/tắt lưới khi nhấn G
                    self.game_ui.toggle_grid()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Kiểm tra xem người dùng có nhấp vào nút đóng (X) không
                if self.close_button_rect.collidepoint(event.pos):
                    self.running = False
                # Kiểm tra xem người dùng có nhấp vào thanh tiêu đề để kéo cửa sổ không
                elif self.title_bar_rect.collidepoint(event.pos):
                    self.dragging = True
                    mouse_x, mouse_y = event.pos
                    self.drag_offset = (mouse_x, mouse_y)
                    
                # Điều chỉnh vị trí chuột dựa trên offset khi vẽ game
                screen_width = self.screen.get_width()
                screen_height = self.screen.get_height()
                game_width = int(self.original_width * self.scale_factor_x)
                game_height = int(self.original_height * self.scale_factor_y)
                offset_x = (screen_width - game_width) // 2
                offset_y = (screen_height - game_height) // 2 + 35  # Thêm chiều cao của thanh tiêu đề
                
                # Xử lý sự kiện cho menu cải tiến nếu đang ở màn hình menu
                if self.game_state.state == 0:  # MAIN_MENU
                    button_clicked = self.improved_menu.handle_event(
                        event, self.scale_factor_x, self.scale_factor_y, offset_x, offset_y
                    )
                    
                    if button_clicked:
                        if button_clicked == "start":
                            self.game_state.state = 1  # PLAYING
                            self.game_state.start_game()
                        elif button_clicked == "warrior":
                            self.game_state.player.set_class(0)  # CharacterClass.WARRIOR
                        elif button_clicked == "mage":
                            self.game_state.player.set_class(1)  # CharacterClass.MAGE
                        elif button_clicked == "load":
                            self.game_state.save_system.toggle_load_menu()
                        elif button_clicked == "quit":
                            self.running = False
                
                # Chỉ chuyển sự kiện đến game state nếu nhấp vào khu vực game và không phải menu chính
                elif event.pos[1] > self.title_bar_rect.height and self.game_state.state != 0:
                    # Tạo sự kiện mới với vị trí chuột đã điều chỉnh
                    adjusted_event = pygame.event.Event(
                        pygame.MOUSEBUTTONDOWN,
                        {
                            'pos': (event.pos[0] - offset_x, event.pos[1] - offset_y),
                            'button': event.button
                        }
                    )
                    self.game_state.handle_event(adjusted_event, self.scale_factor_x, self.scale_factor_y)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                # Kiểm tra xem chuột có đang di chuyển qua nút đóng không
                self.is_close_button_hover = self.close_button_rect.collidepoint(event.pos)
                
                # Kéo cửa sổ nếu đang trong trạng thái kéo
                if self.dragging:
                    mouse_x, mouse_y = event.pos
                    # Tính toán vị trí mới của cửa sổ
                    # Lưu ý: Pygame không hỗ trợ trực tiếp việc di chuyển cửa sổ
                    # Đây chỉ là mã giả để minh họa
                    # Trong thực tế, bạn cần sử dụng thư viện khác như PyQt hoặc Tkinter
                    pass
            else:
                # Chuyển các sự kiện khác đến game state
                self.game_state.handle_event(event, self.scale_factor_x, self.scale_factor_y)

    def toggle_fullscreen(self):
        # Chuyển đổi giữa chế độ cửa sổ và toàn màn hình
        if self.is_fullscreen:
            # Chuyển từ toàn màn hình về cửa sổ
            self.screen = pygame.display.set_mode(self.last_windowed_size, pygame.NOFRAME)
            self.resize(self.last_windowed_size[0], self.last_windowed_size[1])
            self.is_fullscreen = False
        else:
            # Lưu kích thước cửa sổ hiện tại
            self.last_windowed_size = (self.screen.get_width(), self.screen.get_height())
            
            # Chuyển từ cửa sổ sang toàn màn hình
            info = pygame.display.Info()
            
            # Tính toán tỷ lệ khung hình tối ưu cho toàn màn hình
            screen_width = info.current_w
            screen_height = info.current_h
            
            # Giữ tỷ lệ khung hình 4:3 hoặc 16:9 khi chuyển sang toàn màn hình
            aspect_ratio = self.original_width / self.original_height
            
            if screen_width / screen_height > aspect_ratio:
                # Màn hình quá rộng, giới hạn chiều rộng
                game_height = screen_height
                game_width = int(game_height * aspect_ratio)
            else:
                # Màn hình quá cao, giới hạn chiều cao
                game_width = screen_width
                game_height = int(game_width / aspect_ratio)
            
            self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
            
            # Cập nhật vị trí của thanh tiêu đề và nút đóng
            self.title_bar_rect.width = screen_width
            self.close_button_rect.x = screen_width - 30
            
            # Tính toán tỷ lệ mới dựa trên kích thước game thực tế
            self.scale_factor_x = game_width / self.original_width
            self.scale_factor_y = (game_height - self.title_bar_rect.height) / self.original_height
            
            # Đảm bảo tỷ lệ không bị méo
            min_scale = min(self.scale_factor_x, self.scale_factor_y)
            self.scale_factor_x = min_scale
            self.scale_factor_y = min_scale
            
            # Cập nhật tỷ lệ cho game state
            self.game_state.update_scale(self.scale_factor_x, self.scale_factor_y)
            
            # Cập nhật tỷ lệ cho menu cải tiến
            self.improved_menu.update_scale(self.scale_factor_x, self.scale_factor_y)
            
            # Cập nhật tỷ lệ cho UI game
            self.game_ui.update_scale(self.scale_factor_x, self.scale_factor_y)
            
            self.is_fullscreen = True

    def resize(self, width, height):
        # Đảm bảo kích thước tối thiểu
        width = max(width, 640)
        height = max(height, 480)
        
        # Cập nhật kích thước màn hình nếu không ở chế độ toàn màn hình
        if not self.is_fullscreen:
            # Sử dụng cửa sổ không viền
            self.screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
            
        # Cập nhật vị trí của thanh tiêu đề và nút đóng
        self.title_bar_rect.width = width
        self.close_button_rect.x = width - 30
            
        # Cập nhật tỷ lệ
        self.scale_factor_x = width / self.original_width
        self.scale_factor_y = (height - self.title_bar_rect.height) / self.original_height
        
        # Đảm bảo tỷ lệ không bị méo (sử dụng tỷ lệ nhỏ hơn để giữ nguyên tỷ lệ khung hình)
        min_scale = min(self.scale_factor_x, self.scale_factor_y)
        self.scale_factor_x = min_scale
        self.scale_factor_y = min_scale
        
        # Cập nhật tỷ lệ cho game state
        self.game_state.update_scale(self.scale_factor_x, self.scale_factor_y)
        
        # Cập nhật tỷ lệ cho menu cải tiến
        self.improved_menu.update_scale(self.scale_factor_x, self.scale_factor_y)
        
        # Cập nhật tỷ lệ cho UI game
        self.game_ui.update_scale(self.scale_factor_x, self.scale_factor_y)

    def update(self):
        # Cập nhật menu cải tiến nếu đang ở màn hình menu
        if self.game_state.state == 0:  # MAIN_MENU
            self.improved_menu.update()
        
        # Xử lý đầu vào liên tục (phím được giữ)
        self.game_state.handle_continuous_input(self.scale_factor_x, self.scale_factor_y)
        
        # Cập nhật trạng thái game
        self.game_state.update()
        
        # Cập nhật UI game nếu đang chơi
        if self.game_state.state == 1:  # PLAYING
            self.game_ui.update(self.game_state.player)

    def draw(self):
        self.screen.fill(BLACK)
        
        # Vẽ thanh tiêu đề
        pygame.draw.rect(self.screen, self.title_bar_color, self.title_bar_rect)
        
        # Vẽ nút đóng (X)
        button_color = self.close_button_hover_color if self.is_close_button_hover else self.close_button_color
        pygame.draw.rect(self.screen, button_color, self.close_button_rect)
        
        # Vẽ dấu X trên nút đóng
        x_color = (255, 255, 255)  # Màu trắng
        x_start1 = (self.close_button_rect.left + 5, self.close_button_rect.top + 5)
        x_end1 = (self.close_button_rect.right - 5, self.close_button_rect.bottom - 5)
        x_start2 = (self.close_button_rect.left + 5, self.close_button_rect.bottom - 5)
        x_end2 = (self.close_button_rect.right - 5, self.close_button_rect.top + 5)
        pygame.draw.line(self.screen, x_color, x_start1, x_end1, 2)
        pygame.draw.line(self.screen, x_color, x_start2, x_end2, 2)
        
        # Vẽ tiêu đề
        font = pygame.font.SysFont(None, 24)
        title_text = font.render("Dark Fantasy Stickman", True, (255, 255, 255))
        self.screen.blit(title_text, (10, 10))
        
        # Tính toán kích thước và vị trí của khu vực vẽ để giữ tỷ lệ khung hình
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height() - self.title_bar_rect.height
        
        # Tính toán kích thước game với tỷ lệ đúng
        game_width = int(self.original_width * self.scale_factor_x)
        game_height = int(self.original_height * self.scale_factor_y)
        
        # Tính toán vị trí để căn giữa game trên màn hình
        offset_x = (screen_width - game_width) // 2
        offset_y = self.title_bar_rect.height + (screen_height - game_height) // 2
        
        # Vẽ viền đen xung quanh nếu cần
        if offset_x > 0 or (offset_y - self.title_bar_rect.height) > 0:
            pygame.draw.rect(self.screen, BLACK, (0, self.title_bar_rect.height, screen_width, screen_height))
            
            # Vẽ đường viền để đánh dấu khu vực game
            border_color = (50, 50, 50)
            pygame.draw.rect(self.screen, border_color, 
                           (offset_x - 2, offset_y - 2, game_width + 4, game_height + 4), 2)
        
        # Vẽ menu cải tiến nếu đang ở màn hình menu
        if self.game_state.state == 0:  # MAIN_MENU
            self.improved_menu.draw(self.screen, self.scale_factor_x, self.scale_factor_y, 
                                   self.game_state.player.character_class, offset_x, offset_y)
        else:
            # Vẽ game trực tiếp lên màn hình với offset
            self.game_state.draw(self.screen, self.scale_factor_x, self.scale_factor_y, offset_x, offset_y)
            
            # Vẽ UI game cải tiến nếu đang chơi
            if self.game_state.state == 1:  # PLAYING
                self.game_ui.draw(self.screen, self.game_state.player, self.game_state.monsters, 
                                 self.game_state.game_map, self.scale_factor_x, self.scale_factor_y)
        
        pygame.display.flip()

    def run(self):
        # Đặt FPS cao hơn để game mượt hơn
        target_fps = 120
        
        # Bật chế độ vô hạn ngay từ đầu
        self.game_state.infinity_mode = True
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(target_fps)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
