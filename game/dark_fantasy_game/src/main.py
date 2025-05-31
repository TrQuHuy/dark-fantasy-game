import pygame
import sys
import os
from dark_fantasy_game.src.game_state import GameState

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
        try:
            # Khởi tạo màn hình với chế độ cố định (không thể thay đổi kích thước)
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Dark Fantasy Stickman")
            
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
        except Exception as e:
            print(f"Error initializing game: {e}")
            self.running = False
        
    def handle_events(self):
        try:
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
                            if hasattr(self.game_state, 'state') and hasattr(self.game_state, 'PLAYING'):
                                if self.game_state.state == 1:  # PLAYING
                                    event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
                                    self.game_state.handle_event(event, self.scale_factor_x, self.scale_factor_y)
                                else:
                                    self.running = False
                    elif event.key == pygame.K_f:  # Phím F để chuyển đổi chế độ toàn màn hình
                        self.toggle_fullscreen()
                        
                # Chuyển sự kiện đến game state với tỷ lệ tương ứng
                if not self.game_state.handle_event(event, self.scale_factor_x, self.scale_factor_y):
                    self.running = False
        except Exception as e:
            print(f"Error handling events: {e}")

    def toggle_fullscreen(self):
        try:
            # Chuyển đổi giữa chế độ cửa sổ và toàn màn hình
            if self.is_fullscreen:
                # Chuyển từ toàn màn hình về cửa sổ
                self.screen = pygame.display.set_mode(self.last_windowed_size)
                self.resize(self.last_windowed_size[0], self.last_windowed_size[1])
                self.is_fullscreen = False
            else:
                # Lưu kích thước cửa sổ hiện tại
                self.last_windowed_size = (self.screen.get_width(), self.screen.get_height())
                
                # Chuyển từ cửa sổ sang toàn màn hình
                info = pygame.display.Info()
                self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                self.resize(info.current_w, info.current_h)
                self.is_fullscreen = True
        except Exception as e:
            print(f"Error toggling fullscreen: {e}")

    def resize(self, width, height):
        try:
            # Đảm bảo kích thước tối thiểu
            width = max(width, 640)
            height = max(height, 480)
            
            # Cập nhật tỷ lệ
            self.scale_factor_x = width / self.original_width
            self.scale_factor_y = height / self.original_height
            
            # Cập nhật tỷ lệ cho game state
            if hasattr(self.game_state, 'update_scale'):
                self.game_state.update_scale(self.scale_factor_x, self.scale_factor_y)
        except Exception as e:
            print(f"Error resizing: {e}")

    def update(self):
        try:
            # Xử lý đầu vào liên tục (phím được giữ)
            if hasattr(self.game_state, 'handle_continuous_input'):
                self.game_state.handle_continuous_input(self.scale_factor_x, self.scale_factor_y)
            
            # Cập nhật trạng thái game
            if hasattr(self.game_state, 'update'):
                self.game_state.update()
        except Exception as e:
            print(f"Error updating game: {e}")

    def draw(self):
        try:
            self.screen.fill(BLACK)
            if hasattr(self.game_state, 'draw'):
                self.game_state.draw(self.screen, self.scale_factor_x, self.scale_factor_y)
            pygame.display.flip()
        except Exception as e:
            print(f"Error drawing: {e}")
            # Vẽ thông báo lỗi
            self.screen.fill((0, 0, 0))
            error_font = pygame.font.SysFont(None, 36)
            error_text = error_font.render(f"Rendering error: {str(e)}", True, (255, 0, 0))
            self.screen.blit(error_text, (50, 50))
            pygame.display.flip()

    def run(self):
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
        except Exception as e:
            print(f"Critical error in game loop: {e}")
            # Hiển thị thông báo lỗi và tiếp tục
            self.screen.fill((0, 0, 0))
            error_font = pygame.font.SysFont(None, 36)
            error_text = error_font.render(f"Critical error: {str(e)}", True, (255, 0, 0))
            self.screen.blit(error_text, (50, 50))
            
            # Hiển thị hướng dẫn khởi động lại
            restart_text = error_font.render("Press ESC to exit", True, (255, 255, 255))
            self.screen.blit(restart_text, (50, 100))
            
            pygame.display.flip()
            
            # Đợi người dùng thoát
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        waiting = False
                        self.running = False
                self.clock.tick(10)

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        pygame.quit()
        sys.exit()
