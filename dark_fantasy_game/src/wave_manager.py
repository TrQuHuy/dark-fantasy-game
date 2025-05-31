import pygame
import random
import math
from dark_fantasy_game.src.monster import Monster
from dark_fantasy_game.src.boss_monster import BossMonster
from dark_fantasy_game.src.monster_types import MonsterType, MonsterAbility, MonsterBehavior
from dark_fantasy_game.src.wave_functions import get_wave_config

class WaveManager:
    def __init__(self):
        self.current_wave = 0
        self.max_waves = 5
        self.wave_timer = 0
        self.wave_complete = False
        self.monsters_to_spawn = []
        # Tăng thời gian chờ giữa các lần spawn quái
        self.spawn_delay = 45  # frames between monster spawns
        self.spawn_timer = 0
        # Luôn bật chế độ vô hạn
        self.infinity_mode = True
        # Thêm biến để tự động spawn quái
        self.auto_spawn_timer = 0
        # Giảm thời gian spawn quái xuống để quái xuất hiện thường xuyên hơn
        self.auto_spawn_delay = 120  # Tự động spawn quái mỗi 2 giây (120 frames ở 60fps)
        
    def start_wave(self, wave_number):
        """Start a new wave"""
        self.current_wave = wave_number
        self.wave_timer = 0
        self.wave_complete = False
        self.monsters_to_spawn = []
        
        # Số lượng quái vật trong mỗi wave tăng theo cấp độ
        monsters_count = 10 + (wave_number - 1) * 2
        
        # Get wave configuration
        if self.infinity_mode and wave_number > self.max_waves:
            # Generate infinity wave with increasing difficulty
            self.generate_infinity_wave(wave_number, monsters_count)
        else:
            # Get normal wave configuration
            wave_config = get_wave_config(wave_number)
            
            # Create monster spawn list
            for monster_type, count in wave_config["monsters"].items():
                for _ in range(count):
                    self.monsters_to_spawn.append(monster_type)
                    
            # Shuffle monster spawn order
            random.shuffle(self.monsters_to_spawn)
            
            # Add boss at the end if this wave has one
            if wave_config["boss"]:
                self.monsters_to_spawn.append(wave_config["boss"])
        
    def generate_infinity_wave(self, wave_number, monsters_count):
        """Generate an infinity wave with increasing difficulty"""
        # Calculate difficulty multiplier based on wave number
        difficulty = (wave_number - self.max_waves) + 1
        
        # Base monster count increases with difficulty
        base_count = monsters_count
        
        # Monster distribution changes with difficulty
        if difficulty <= 3:
            # Early infinity waves: mostly goblins and skeletons
            self.monsters_to_spawn.extend([MonsterType.GOBLIN] * (base_count // 2))
            self.monsters_to_spawn.extend([MonsterType.SKELETON] * (base_count // 3))
            self.monsters_to_spawn.extend([MonsterType.ORC] * (difficulty))
        elif difficulty <= 6:
            # Mid infinity waves: more orcs and some demons
            self.monsters_to_spawn.extend([MonsterType.GOBLIN] * (base_count // 4))
            self.monsters_to_spawn.extend([MonsterType.SKELETON] * (base_count // 3))
            self.monsters_to_spawn.extend([MonsterType.ORC] * (base_count // 3))
            self.monsters_to_spawn.extend([MonsterType.DEMON] * (difficulty - 2))
        else:
            # Late infinity waves: all monster types with more powerful ones
            self.monsters_to_spawn.extend([MonsterType.GOBLIN] * (base_count // 5))
            self.monsters_to_spawn.extend([MonsterType.SKELETON] * (base_count // 4))
            self.monsters_to_spawn.extend([MonsterType.ORC] * (base_count // 3))
            self.monsters_to_spawn.extend([MonsterType.DEMON] * (difficulty - 1))
        
        # Add boss every 5 waves in infinity mode
        if difficulty % 5 == 0:
            if difficulty % 10 == 0:
                # Dragon boss every 10 waves
                self.monsters_to_spawn.append(MonsterType.DRAGON)
            else:
                # Demon boss every 5 waves
                self.monsters_to_spawn.append(MonsterType.DEMON)
        
        # Shuffle monster spawn order (but keep boss at the end)
        random.shuffle(self.monsters_to_spawn)
        
    def toggle_infinity_mode(self):
        """Toggle infinity wave mode"""
        self.infinity_mode = not self.infinity_mode
        # Luôn bật chế độ vô hạn
        self.infinity_mode = True
        return self.infinity_mode
        
    def update(self):
        """Update wave state and spawn monsters"""
        # Spawn từ danh sách quái vật
        if not self.wave_complete and len(self.monsters_to_spawn) > 0:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0
                return self.spawn_monster()
        
        # Tự động spawn quái vật mới nếu ở chế độ vô hạn
        if self.infinity_mode:
            self.auto_spawn_timer += 1
            if self.auto_spawn_timer >= self.auto_spawn_delay:
                self.auto_spawn_timer = 0
                return self.spawn_random_monster()
            
        return None
        
    def spawn_monster(self):
        """Spawn a monster from the queue"""
        if not self.monsters_to_spawn:
            self.wave_complete = True
            return None
            
        monster_type = self.monsters_to_spawn.pop(0)
        return self.create_monster(monster_type)
    
    def spawn_random_monster(self):
        """Spawn a random monster based on current wave difficulty"""
        # Xác định loại quái vật dựa trên mức độ khó
        difficulty = max(1, self.current_wave)
        
        # Danh sách các loại quái vật có thể spawn
        monster_types = [
            MonsterType.GOBLIN, 
            MonsterType.SKELETON, 
            MonsterType.ORC, 
            MonsterType.ZOMBIE,
            MonsterType.DEMON, 
            MonsterType.WRAITH,
            MonsterType.GOLEM,
            MonsterType.VAMPIRE
        ]
        
        # Boss monsters
        boss_types = [
            MonsterType.DRAGON,
            MonsterType.NECROMANCER,
            MonsterType.DEMON_LORD,
            MonsterType.LICH
        ]
        
        # Tỷ lệ spawn các loại quái vật thường
        if difficulty <= 3:
            weights = [40, 30, 20, 10, 0, 0, 0, 0]  # Tỷ lệ cho 8 loại quái thường
        elif difficulty <= 6:
            weights = [30, 25, 20, 15, 10, 0, 0, 0]
        elif difficulty <= 10:
            weights = [15, 20, 20, 15, 15, 10, 5, 0]
        else:
            weights = [10, 15, 15, 15, 15, 15, 10, 5]
            
        # Tỷ lệ spawn boss (tăng theo cấp độ)
        boss_chance = min(0.05 + (difficulty - 1) * 0.005, 0.15)  # Tối đa 15%
        
        # Quyết định xem có spawn boss không
        if random.random() < boss_chance:
            # Chọn loại boss dựa trên cấp độ
            if difficulty <= 10:
                boss_weights = [100, 0, 0, 0]  # Chỉ Dragon ở cấp độ thấp
            elif difficulty <= 20:
                boss_weights = [60, 40, 0, 0]  # Dragon và Necromancer
            elif difficulty <= 30:
                boss_weights = [40, 30, 30, 0]  # Thêm Demon Lord
            else:
                boss_weights = [25, 25, 25, 25]  # Tất cả các boss
                
            # Chọn boss dựa trên trọng số
            total = sum(boss_weights)
            r = random.randint(1, total)
            cumulative = 0
            
            for i, weight in enumerate(boss_weights):
                cumulative += weight
                if r <= cumulative:
                    return self.create_monster(boss_types[i])
        
        # Chọn loại quái vật thường dựa trên trọng số
        total = sum(weights)
        r = random.randint(1, total)
        cumulative = 0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return self.create_monster(monster_types[i])
                
        # Mặc định nếu có lỗi
        return self.create_monster(MonsterType.GOBLIN)
        
    def create_monster(self, monster_type):
        """Create a monster of specified type at a random edge position"""
        # Vị trí spawn sẽ được xác định sau trong game_state.spawn_monster_at_valid_location
        # Tạm thời đặt vị trí là (0, 0)
        x = 0
        y = 0
            
        # Xác định xem có phải boss không
        is_boss = monster_type in [
            MonsterType.DRAGON, 
            MonsterType.NECROMANCER, 
            MonsterType.DEMON_LORD, 
            MonsterType.LICH
        ]
        
        # Tạo boss hoặc quái thường
        if is_boss:
            monster = BossMonster(monster_type, x, y, self.current_wave)
        else:
            # Create monster with level based on current wave
            monster = Monster(monster_type, x, y, self.current_wave)
        
        return monster
        
    def is_wave_complete(self):
        """Check if the current wave is complete"""
        # Trong chế độ vô hạn, wave không bao giờ hoàn thành
        if self.infinity_mode:
            return False
        return self.wave_complete
