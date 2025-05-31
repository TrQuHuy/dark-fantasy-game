import math

class ExperienceSystem:
    def __init__(self):
        # Cấp độ và kinh nghiệm
        self.level = 1
        self.experience = 0
        self.skill_points = 0
        self.total_skill_points_spent = 0
        
        # Các hằng số cho công thức tính kinh nghiệm
        self.base_exp_required = 100  # Kinh nghiệm cơ bản cần để lên cấp 2
        self.exp_growth_factor = 1.5  # Hệ số tăng trưởng kinh nghiệm
        
        # Lịch sử kinh nghiệm nhận được
        self.exp_history = []
        
        # Các kỹ năng đã mở khóa theo cấp độ
        self.unlocked_skills = {
            1: ["Kiếm Khí", "Vòng Lửa"],  # Kỹ năng cơ bản (Warrior/Mage)
            3: ["Xoáy Kiếm", "Cầu Băng"],  # Kỹ năng cấp 2
            5: ["Phá Giáp", "Sấm Sét"],    # Kỹ năng cấp 3
            8: ["Lưỡi Kiếm Bão", "Thiên Thạch"],  # Kỹ năng cấp 4
            12: ["Thần Kiếm", "Thiên Hỏa"],  # Kỹ năng cấp 5
        }
        
        # Các thuộc tính có thể nâng cấp
        self.upgradable_stats = {
            "strength": 0,      # Tăng sát thương vật lý
            "intelligence": 0,  # Tăng sát thương phép thuật
            "vitality": 0,      # Tăng máu
            "agility": 0,       # Tăng tốc độ di chuyển
            "defense": 0,       # Tăng phòng thủ
            "critical": 0,      # Tăng tỷ lệ chí mạng
        }
        
        # Hệ số tăng chỉ số cho mỗi điểm
        self.stat_bonuses = {
            "strength": 2,       # +2 sát thương vật lý
            "intelligence": 2,   # +2 sát thương phép thuật
            "vitality": 10,      # +10 máu
            "agility": 0.1,      # +0.1 tốc độ
            "defense": 1,        # +1 phòng thủ
            "critical": 0.02,    # +2% tỷ lệ chí mạng
        }
        
    def get_exp_required(self, level=None):
        """Tính kinh nghiệm cần thiết để lên cấp tiếp theo"""
        if level is None:
            level = self.level
        return int(self.base_exp_required * (self.exp_growth_factor ** (level - 1)))
        
    def get_total_exp_required(self, target_level):
        """Tính tổng kinh nghiệm cần thiết để đạt cấp độ mục tiêu"""
        total = 0
        for level in range(1, target_level):
            total += self.get_exp_required(level)
        return total
        
    def add_experience(self, amount):
        """Thêm kinh nghiệm và xử lý việc lên cấp"""
        self.experience += amount
        self.exp_history.append({
            "amount": amount,
            "total": self.experience
        })
        
        # Kiểm tra lên cấp
        leveled_up = False
        levels_gained = 0
        
        while True:
            exp_required = self.get_exp_required()
            if self.experience >= exp_required:
                self.experience -= exp_required
                self.level += 1
                self.skill_points += 2  # Nhận 2 điểm kỹ năng mỗi khi lên cấp
                leveled_up = True
                levels_gained += 1
            else:
                break
                
        return {
            "leveled_up": leveled_up,
            "levels_gained": levels_gained,
            "new_level": self.level,
            "skill_points_gained": levels_gained * 2,
            "new_skills_unlocked": self.get_newly_unlocked_skills(self.level - levels_gained, self.level)
        }
        
    def get_newly_unlocked_skills(self, old_level, new_level):
        """Lấy danh sách kỹ năng mới được mở khóa"""
        newly_unlocked = []
        for level, skills in self.unlocked_skills.items():
            if old_level < level <= new_level:
                newly_unlocked.extend(skills)
        return newly_unlocked
        
    def get_all_unlocked_skills(self):
        """Lấy tất cả kỹ năng đã mở khóa ở cấp độ hiện tại"""
        unlocked = []
        for level, skills in self.unlocked_skills.items():
            if self.level >= level:
                unlocked.extend(skills)
        return unlocked
        
    def spend_skill_point(self, stat):
        """Sử dụng điểm kỹ năng để nâng cấp thuộc tính"""
        if stat not in self.upgradable_stats:
            return False
            
        if self.skill_points <= 0:
            return False
            
        self.upgradable_stats[stat] += 1
        self.skill_points -= 1
        self.total_skill_points_spent += 1
        return True
        
    def get_stat_bonus(self, stat):
        """Tính toán chỉ số bổ sung từ việc nâng cấp thuộc tính"""
        if stat not in self.upgradable_stats:
            return 0
            
        return self.upgradable_stats[stat] * self.stat_bonuses[stat]
        
    def get_exp_progress(self):
        """Tính phần trăm tiến trình kinh nghiệm hiện tại"""
        exp_required = self.get_exp_required()
        if exp_required == 0:
            return 100
        return (self.experience / exp_required) * 100
        
    def get_level_info(self):
        """Lấy thông tin cấp độ hiện tại"""
        return {
            "level": self.level,
            "experience": self.experience,
            "exp_required": self.get_exp_required(),
            "exp_progress": self.get_exp_progress(),
            "skill_points": self.skill_points,
            "total_skill_points_spent": self.total_skill_points_spent
        }
        
    def calculate_monster_exp(self, monster):
        """Tính kinh nghiệm nhận được từ việc tiêu diệt quái vật"""
        base_exp = monster.score_value
        
        # Điều chỉnh kinh nghiệm dựa trên cấp độ quái vật và người chơi
        level_diff = monster.level - self.level
        
        # Nếu quái vật cấp cao hơn, nhận nhiều kinh nghiệm hơn
        if level_diff > 0:
            exp_multiplier = 1 + (level_diff * 0.1)  # +10% mỗi cấp độ cao hơn
        # Nếu quái vật cấp thấp hơn, nhận ít kinh nghiệm hơn
        elif level_diff < 0:
            exp_multiplier = max(0.1, 1 + (level_diff * 0.1))  # -10% mỗi cấp độ thấp hơn, tối thiểu 10%
        else:
            exp_multiplier = 1
            
        # Boss cho nhiều kinh nghiệm hơn
        if monster.is_boss:
            exp_multiplier *= 3
            
        return int(base_exp * exp_multiplier)
        
    def draw_exp_bar(self, screen, x, y, width, height, scale_x=1.0, scale_y=1.0):
        """Vẽ thanh kinh nghiệm lên màn hình"""
        import pygame
        
        # Điều chỉnh vị trí và kích thước theo tỷ lệ
        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)
        scaled_width = int(width * scale_x)
        scaled_height = int(height * scale_y)
        
        # Vẽ nền thanh kinh nghiệm
        pygame.draw.rect(screen, (50, 50, 50), (scaled_x, scaled_y, scaled_width, scaled_height))
        
        # Tính toán phần trăm kinh nghiệm
        exp_percent = self.get_exp_progress() / 100
        exp_width = int(scaled_width * exp_percent)
        
        # Vẽ phần kinh nghiệm hiện tại
        pygame.draw.rect(screen, (100, 100, 255), (scaled_x, scaled_y, exp_width, scaled_height))
        
        # Vẽ viền
        pygame.draw.rect(screen, (200, 200, 200), (scaled_x, scaled_y, scaled_width, scaled_height), 1)
        
        # Vẽ text thông tin cấp độ và kinh nghiệm
        font = pygame.font.SysFont(None, int(24 * min(scale_x, scale_y)))
        level_text = font.render(f"Level {self.level}", True, (255, 255, 255))
        exp_text = font.render(f"EXP: {self.experience}/{self.get_exp_required()}", True, (255, 255, 255))
        
        # Vẽ text
        screen.blit(level_text, (scaled_x + 10, scaled_y + scaled_height // 2 - level_text.get_height() // 2))
        screen.blit(exp_text, (scaled_x + scaled_width - exp_text.get_width() - 10, 
                              scaled_y + scaled_height // 2 - exp_text.get_height() // 2))
        
    def draw_level_up_notification(self, screen, scale_x=1.0, scale_y=1.0):
        """Vẽ thông báo lên cấp"""
        import pygame
        
        # Kích thước màn hình
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Kích thước thông báo
        notification_width = int(400 * scale_x)
        notification_height = int(200 * scale_y)
        
        # Vị trí thông báo (giữa màn hình)
        notification_x = (screen_width - notification_width) // 2
        notification_y = (screen_height - notification_height) // 2
        
        # Vẽ nền thông báo với độ trong suốt
        notification_surface = pygame.Surface((notification_width, notification_height), pygame.SRCALPHA)
        notification_surface.fill((0, 0, 0, 200))
        
        # Vẽ viền
        pygame.draw.rect(notification_surface, (255, 215, 0), 
                        (0, 0, notification_width, notification_height), 3)
        
        # Vẽ text thông báo
        font_large = pygame.font.SysFont(None, int(48 * min(scale_x, scale_y)))
        font_medium = pygame.font.SysFont(None, int(36 * min(scale_x, scale_y)))
        font_small = pygame.font.SysFont(None, int(24 * min(scale_x, scale_y)))
        
        # Text tiêu đề
        level_up_text = font_large.render("LEVEL UP!", True, (255, 215, 0))
        level_text = font_medium.render(f"Level {self.level}", True, (255, 255, 255))
        points_text = font_small.render(f"Skill Points: {self.skill_points}", True, (255, 255, 255))
        continue_text = font_small.render("Press TAB to open Stats menu", True, (200, 200, 200))
        
        # Vẽ text lên surface
        notification_surface.blit(level_up_text, 
                                 ((notification_width - level_up_text.get_width()) // 2, 30))
        notification_surface.blit(level_text, 
                                 ((notification_width - level_text.get_width()) // 2, 80))
        notification_surface.blit(points_text, 
                                 ((notification_width - points_text.get_width()) // 2, 120))
        notification_surface.blit(continue_text, 
                                 ((notification_width - continue_text.get_width()) // 2, 160))
        
        # Vẽ hiệu ứng ánh sáng xung quanh thông báo
        glow_surface = pygame.Surface((notification_width + 40, notification_height + 40), pygame.SRCALPHA)
        for i in range(20, 0, -1):
            alpha = 10 - i // 2
            pygame.draw.rect(glow_surface, (255, 215, 0, alpha), 
                            (20 - i, 20 - i, notification_width + i * 2, notification_height + i * 2), 2)
        
        # Vẽ hiệu ứng ánh sáng lên màn hình
        screen.blit(glow_surface, (notification_x - 20, notification_y - 20))
        
        # Vẽ thông báo lên màn hình
        screen.blit(notification_surface, (notification_x, notification_y))
        
    def draw_stats_panel(self, screen, x, y, scale_x=1.0, scale_y=1.0):
        """Vẽ bảng chỉ số và nâng cấp"""
        import pygame
        
        # Điều chỉnh vị trí và kích thước theo tỷ lệ
        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)
        panel_width = int(350 * scale_x)
        panel_height = int(450 * scale_y)
        
        # Vẽ nền bảng với độ trong suốt
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 200))
        
        # Vẽ viền
        pygame.draw.rect(panel_surface, (200, 200, 200), 
                        (0, 0, panel_width, panel_height), 2)
        
        # Vẽ tiêu đề
        font_large = pygame.font.SysFont(None, int(36 * min(scale_x, scale_y)))
        font_medium = pygame.font.SysFont(None, int(24 * min(scale_x, scale_y)))
        font_small = pygame.font.SysFont(None, int(20 * min(scale_x, scale_y)))
        
        # Text tiêu đề
        title_text = font_large.render("Character Stats", True, (255, 255, 255))
        level_text = font_medium.render(f"Level: {self.level}", True, (255, 255, 255))
        exp_text = font_medium.render(f"EXP: {self.experience}/{self.get_exp_required()}", True, (255, 255, 255))
        points_text = font_medium.render(f"Skill Points: {self.skill_points}", True, (255, 215, 0))
        
        # Vẽ text tiêu đề
        panel_surface.blit(title_text, ((panel_width - title_text.get_width()) // 2, 10))
        panel_surface.blit(level_text, (20, 50))
        panel_surface.blit(exp_text, (20, 80))
        panel_surface.blit(points_text, (20, 110))
        
        # Vẽ đường kẻ phân cách
        pygame.draw.line(panel_surface, (200, 200, 200), (20, 140), (panel_width - 20, 140), 1)
        
        # Vẽ các thuộc tính có thể nâng cấp
        stat_y = 160
        stat_height = 40
        
        # Tên hiển thị cho các thuộc tính
        stat_names = {
            "strength": "Strength (STR)",
            "intelligence": "Intelligence (INT)",
            "vitality": "Vitality (VIT)",
            "agility": "Agility (AGI)",
            "defense": "Defense (DEF)",
            "critical": "Critical (CRIT)"
        }
        
        # Mô tả cho các thuộc tính
        stat_descriptions = {
            "strength": f"+{self.stat_bonuses['strength']} Physical Damage",
            "intelligence": f"+{self.stat_bonuses['intelligence']} Magic Damage",
            "vitality": f"+{self.stat_bonuses['vitality']} Max Health",
            "agility": f"+{self.stat_bonuses['agility']} Movement Speed",
            "defense": f"+{self.stat_bonuses['defense']} Defense",
            "critical": f"+{int(self.stat_bonuses['critical'] * 100)}% Critical Chance"
        }
        
        # Vẽ từng thuộc tính
        for stat, value in self.upgradable_stats.items():
            # Vẽ nền cho thuộc tính
            pygame.draw.rect(panel_surface, (50, 50, 50), 
                            (20, stat_y, panel_width - 40, stat_height))
            
            # Vẽ tên thuộc tính
            stat_name_text = font_medium.render(stat_names[stat], True, (255, 255, 255))
            panel_surface.blit(stat_name_text, (30, stat_y + 5))
            
            # Vẽ giá trị thuộc tính
            stat_value_text = font_medium.render(f"{value}", True, (255, 255, 255))
            panel_surface.blit(stat_value_text, (panel_width - 80, stat_y + 5))
            
            # Vẽ mô tả thuộc tính
            stat_desc_text = font_small.render(stat_descriptions[stat], True, (200, 200, 200))
            panel_surface.blit(stat_desc_text, (30, stat_y + 25))
            
            # Vẽ nút nâng cấp nếu còn điểm kỹ năng
            if self.skill_points > 0:
                button_rect = pygame.Rect(panel_width - 60, stat_y + 5, 30, 30)
                pygame.draw.rect(panel_surface, (0, 150, 0), button_rect)
                pygame.draw.rect(panel_surface, (255, 255, 255), button_rect, 1)
                
                # Vẽ dấu cộng
                plus_text = font_medium.render("+", True, (255, 255, 255))
                panel_surface.blit(plus_text, (button_rect.centerx - plus_text.get_width() // 2, 
                                             button_rect.centery - plus_text.get_height() // 2))
                
            stat_y += stat_height + 10
            
        # Vẽ đường kẻ phân cách
        pygame.draw.line(panel_surface, (200, 200, 200), 
                        (20, stat_y), (panel_width - 20, stat_y), 1)
        
        # Vẽ hướng dẫn
        guide_text = font_small.render("Click + to spend skill points", True, (200, 200, 200))
        panel_surface.blit(guide_text, ((panel_width - guide_text.get_width()) // 2, stat_y + 10))
        
        # Vẽ bảng lên màn hình
        screen.blit(panel_surface, (scaled_x, scaled_y))
        
        # Trả về các nút nâng cấp để xử lý sự kiện click
        buttons = {}
        stat_y = 160
        for stat in self.upgradable_stats:
            if self.skill_points > 0:
                button_rect = pygame.Rect(scaled_x + panel_width - 60, 
                                        scaled_y + stat_y + 5, 
                                        30, 30)
                buttons[stat] = button_rect
            stat_y += stat_height + 10
            
        return buttons
        
    def handle_stats_click(self, pos, buttons):
        """Xử lý sự kiện click vào bảng chỉ số"""
        for stat, button_rect in buttons.items():
            if button_rect.collidepoint(pos):
                return self.spend_skill_point(stat)
        return False
