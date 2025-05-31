import pygame
import math

class Skill:
    def __init__(self, name, icon_color, cooldown, key):
        self.name = name
        self.icon_color = icon_color
        self.cooldown_max = cooldown
        self.cooldown = 0
        self.key = key
        self.active = False
        self.key_text = key.upper()
        
    def use(self):
        if self.cooldown <= 0:
            self.cooldown = self.cooldown_max
            self.active = True
            return True
        return False
        
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
            
    def get_cooldown_percent(self):
        if self.cooldown_max == 0:
            return 0
        return self.cooldown / self.cooldown_max
        
    def is_ready(self):
        return self.cooldown <= 0

class SkillBar:
    def __init__(self, character_class):
        self.skills = []
        self.init_skills(character_class)
        self.selected_skill_index = 0
        
    def init_skills(self, character_class):
        self.skills = []
        
        if character_class.value == "Warrior":
            # Kỹ năng cho Warrior
            self.skills.append(Skill("Kiếm Khí", (100, 200, 255), 60, "1"))  # Kỹ năng AOE hiện tại
            self.skills.append(Skill("Xoáy Kiếm", (50, 150, 255), 120, "2"))  # Kỹ năng mới
            self.skills.append(Skill("Phá Giáp", (200, 200, 255), 180, "3"))  # Kỹ năng mới
        else:
            # Kỹ năng cho Mage
            self.skills.append(Skill("Vòng Lửa", (255, 50, 20), 60, "1"))  # Kỹ năng AOE hiện tại
            self.skills.append(Skill("Cầu Băng", (20, 150, 255), 120, "2"))  # Kỹ năng mới
            self.skills.append(Skill("Sấm Sét", (255, 255, 0), 180, "3"))  # Kỹ năng mới
            
    def update(self):
        for skill in self.skills:
            skill.update()
            
    def use_skill(self, index):
        if 0 <= index < len(self.skills):
            return self.skills[index].use()
        return False
        
    def get_active_skill(self):
        for i, skill in enumerate(self.skills):
            if skill.active:
                skill.active = False
                return i
        return -1
        
    def handle_key(self, key):
        if key == pygame.K_1 and len(self.skills) > 0:
            self.selected_skill_index = 0
            return self.use_skill(0)
        elif key == pygame.K_2 and len(self.skills) > 1:
            self.selected_skill_index = 1
            return self.use_skill(1)
        elif key == pygame.K_3 and len(self.skills) > 2:
            self.selected_skill_index = 2
            return self.use_skill(2)
        return False
        
    def draw(self, screen, x, y, scale_x=1.0, scale_y=1.0):
        skill_size = int(50 * min(scale_x, scale_y))
        spacing = int(10 * min(scale_x, scale_y))
        
        for i, skill in enumerate(self.skills):
            # Vị trí của kỹ năng
            skill_x = x + (skill_size + spacing) * i
            skill_y = y
            
            # Vẽ nền kỹ năng
            pygame.draw.rect(screen, (50, 50, 50), 
                            (skill_x, skill_y, skill_size, skill_size))
            
            # Vẽ biểu tượng kỹ năng
            icon_rect = pygame.Rect(skill_x + 2, skill_y + 2, skill_size - 4, skill_size - 4)
            pygame.draw.rect(screen, skill.icon_color, icon_rect)
            
            # Vẽ hiệu ứng cho kỹ năng được chọn
            if i == self.selected_skill_index:
                pygame.draw.rect(screen, (255, 255, 255), 
                                (skill_x, skill_y, skill_size, skill_size), 3)
            else:
                pygame.draw.rect(screen, (150, 150, 150), 
                                (skill_x, skill_y, skill_size, skill_size), 1)
            
            # Vẽ overlay cooldown
            if skill.cooldown > 0:
                cooldown_percent = skill.get_cooldown_percent()
                cooldown_height = int(skill_size * cooldown_percent)
                cooldown_rect = pygame.Rect(
                    skill_x, skill_y + (skill_size - cooldown_height),
                    skill_size, cooldown_height
                )
                
                # Màu overlay cooldown
                cooldown_color = (0, 0, 0, 150)
                cooldown_surface = pygame.Surface((skill_size, cooldown_height), pygame.SRCALPHA)
                cooldown_surface.fill(cooldown_color)
                screen.blit(cooldown_surface, (skill_x, skill_y + (skill_size - cooldown_height)))
                
                # Hiển thị thời gian cooldown còn lại
                font = pygame.font.SysFont(None, int(24 * min(scale_x, scale_y)))
                cooldown_text = font.render(str(math.ceil(skill.cooldown / 60)), True, (255, 255, 255))
                text_x = skill_x + (skill_size - cooldown_text.get_width()) // 2
                text_y = skill_y + (skill_size - cooldown_text.get_height()) // 2
                screen.blit(cooldown_text, (text_x, text_y))
            
            # Vẽ phím tắt
            key_font = pygame.font.SysFont(None, int(18 * min(scale_x, scale_y)))
            key_text = key_font.render(skill.key_text, True, (255, 255, 255))
            key_x = skill_x + skill_size - key_text.get_width() - 2
            key_y = skill_y + 2
            
            # Vẽ nền cho phím tắt
            key_bg_rect = pygame.Rect(
                key_x - 2, key_y - 2,
                key_text.get_width() + 4, key_text.get_height() + 4
            )
            pygame.draw.rect(screen, (0, 0, 0, 180), key_bg_rect)
            
            screen.blit(key_text, (key_x, key_y))
