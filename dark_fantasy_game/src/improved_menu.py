import pygame
from scripts.button import Button

class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.bg_image = pygame.image.load("assets/background/menu.png")
        self.bg_image = pygame.transform.scale(self.bg_image, (screen_width, screen_height))

        self.title_font = pygame.font.Font("assets/fonts/joystix.ttf", 60)
        self.button_font = pygame.font.Font("assets/fonts/joystix.ttf", 20)

        self.button_color = (0, 0, 0)
        self.hover_color = (255, 255, 255)

        self.selected_class = "warrior"

        self.animations = {
            "title_offset": 0,
            "title_direction": 1
        }

        self.init_buttons()

    def init_buttons(self):
        """Khởi tạo các nút trong màn hình chính"""
        button_width = 200
        button_height = 50
        center_x = self.screen_width // 2

        # Điều chỉnh lại vị trí Y để không bị chồng lên tiêu đề
        self.buttons = {
            "warrior": Button(center_x - button_width - 20, 300, button_width, button_height,
                              "Warrior", self.button_font, self.button_color, self.hover_color),
            "mage": Button(center_x + 20, 300, button_width, button_height,
                           "Mage", self.button_font, self.button_color, self.hover_color),
            "start": Button(center_x - button_width // 2, 380, button_width, button_height,
                            "Start Game", self.button_font, self.button_color, self.hover_color),
            "load": Button(center_x - button_width // 2, 450, button_width, button_height,
                           "Load Game", self.button_font, self.button_color, self.hover_color),
            "quit": Button(center_x - button_width // 2, 520, button_width, button_height,
                           "Quit", self.button_font, self.button_color, self.hover_color)
        }

    def update_animation(self):
        self.animations["title_offset"] += self.animations["title_direction"]
        if abs(self.animations["title_offset"]) > 5:
            self.animations["title_direction"] *= -1

    def draw(self, screen):
        screen.blit(self.bg_image, (0, 0))
        self.draw_title(screen, 0, 0)

        for key, button in self.buttons.items():
            button.draw(screen)

    def draw_title(self, screen, offset_x, offset_y):
        """Vẽ tiêu đề game với hiệu ứng đổ bóng"""
        title_text = "Dark Fantasy Stickman"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        shadow_surface = self.title_font.render(title_text, True, (0, 0, 0))

        # Tính vị trí chính giữa và offset chuyển động
        title_x = (self.screen_width - title_surface.get_width()) // 2 + offset_x
        title_y = 40 + self.animations["title_offset"] + offset_y  # Hạ xuống thấp hơn để tránh đè nút

        # Vẽ bóng đổ (hiệu ứng đổ bóng)
        screen.blit(shadow_surface, (title_x + 4, title_y + 4))

        # Vẽ tiêu đề chính
        screen.blit(title_surface, (title_x, title_y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for key, button in self.buttons.items():
                if button.is_hovered():
                    if key in ["warrior", "mage"]:
                        self.selected_class = key
                    return key
        return None
