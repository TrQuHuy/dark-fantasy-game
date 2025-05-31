from enum import Enum

class MonsterType(Enum):
    # Cơ bản
    GOBLIN = "Goblin"
    SKELETON = "Skeleton"
    ORC = "Orc"
    ZOMBIE = "Zombie"
    
    # Trung cấp
    DEMON = "Demon"
    WRAITH = "Wraith"
    GOLEM = "Golem"
    VAMPIRE = "Vampire"
    
    # Boss
    DRAGON = "Dragon"
    NECROMANCER = "Necromancer"
    DEMON_LORD = "Demon Lord"
    LICH = "Lich"

class MonsterAbility(Enum):
    NONE = "None"
    HEAL = "Heal"  # Hồi máu
    TELEPORT = "Teleport"  # Dịch chuyển
    SUMMON = "Summon"  # Triệu hồi quái nhỏ
    INVISIBLE = "Invisible"  # Tàng hình
    POISON = "Poison"  # Độc
    FIRE = "Fire"  # Lửa
    ICE = "Ice"  # Băng
    LIGHTNING = "Lightning"  # Sét

class MonsterBehavior(Enum):
    AGGRESSIVE = "Aggressive"  # Luôn tấn công người chơi
    DEFENSIVE = "Defensive"  # Chỉ tấn công khi bị tấn công
    RANGED = "Ranged"  # Tấn công từ xa
    PATROL = "Patrol"  # Đi tuần tra theo đường định sẵn
    AMBUSH = "Ambush"  # Phục kích, tàng hình cho đến khi người chơi đến gần
    SWARM = "Swarm"  # Tấn công theo nhóm, mạnh hơn khi ở gần quái khác
    BERSERKER = "Berserker"  # Tấn công mạnh hơn khi máu thấp

class MonsterStats:
    def __init__(self, monster_type, level=1, is_boss=False):
        self.monster_type = monster_type
        self.level = level
        self.is_boss = is_boss
        
        # Thiết lập chỉ số cơ bản dựa trên loại quái
        self.setup_base_stats()
        
        # Áp dụng hệ số cấp độ
        self.apply_level_scaling()
        
        # Áp dụng hệ số boss nếu cần
        if is_boss:
            self.apply_boss_scaling()
            
    def setup_base_stats(self):
        """Thiết lập chỉ số cơ bản dựa trên loại quái"""
        # Chỉ số mặc định
        self.max_health = 50
        self.damage = 5
        self.speed = 1.5
        self.attack_range = 50
        self.attack_cooldown = 90
        self.score_value = 10
        self.width = 64
        self.height = 64
        self.abilities = []
        self.behavior = MonsterBehavior.AGGRESSIVE
        
        # Điều chỉnh theo loại quái
        if self.monster_type == MonsterType.GOBLIN:
            self.max_health = 40
            self.damage = 3
            self.speed = 2.0
            self.attack_range = 40
            self.attack_cooldown = 60
            self.score_value = 10
            self.color = (0, 150, 0)  # Green
            self.behavior = MonsterBehavior.SWARM
            
        elif self.monster_type == MonsterType.SKELETON:
            self.max_health = 50
            self.damage = 5
            self.speed = 1.6
            self.attack_range = 50
            self.attack_cooldown = 75
            self.score_value = 15
            self.color = (200, 200, 200)  # Light gray
            
        elif self.monster_type == MonsterType.ORC:
            self.max_health = 70
            self.damage = 7
            self.speed = 1.4
            self.attack_range = 60
            self.attack_cooldown = 90
            self.score_value = 25
            self.color = (150, 75, 0)  # Brown
            self.behavior = MonsterBehavior.AGGRESSIVE
            
        elif self.monster_type == MonsterType.ZOMBIE:
            self.max_health = 60
            self.damage = 4
            self.speed = 1.0
            self.attack_range = 45
            self.attack_cooldown = 100
            self.score_value = 15
            self.color = (100, 150, 100)  # Greenish
            self.abilities = [MonsterAbility.HEAL]
            self.behavior = MonsterBehavior.AGGRESSIVE
            
        elif self.monster_type == MonsterType.DEMON:
            self.max_health = 120
            self.damage = 10
            self.speed = 1.8
            self.attack_range = 70
            self.attack_cooldown = 80
            self.score_value = 40
            self.color = (200, 0, 0)  # Red
            self.abilities = [MonsterAbility.FIRE]
            self.behavior = MonsterBehavior.AGGRESSIVE
            
        elif self.monster_type == MonsterType.WRAITH:
            self.max_health = 80
            self.damage = 8
            self.speed = 2.2
            self.attack_range = 60
            self.attack_cooldown = 70
            self.score_value = 35
            self.color = (100, 100, 150)  # Bluish
            self.abilities = [MonsterAbility.INVISIBLE, MonsterAbility.TELEPORT]
            self.behavior = MonsterBehavior.AMBUSH
            
        elif self.monster_type == MonsterType.GOLEM:
            self.max_health = 200
            self.damage = 12
            self.speed = 1.0
            self.attack_range = 80
            self.attack_cooldown = 120
            self.score_value = 50
            self.color = (150, 150, 100)  # Sandy
            self.behavior = MonsterBehavior.DEFENSIVE
            
        elif self.monster_type == MonsterType.VAMPIRE:
            self.max_health = 150
            self.damage = 9
            self.speed = 1.9
            self.attack_range = 65
            self.attack_cooldown = 75
            self.score_value = 45
            self.color = (150, 0, 100)  # Purple-red
            self.abilities = [MonsterAbility.HEAL]
            self.behavior = MonsterBehavior.AGGRESSIVE
            
        # Boss monsters
        elif self.monster_type == MonsterType.DRAGON:
            self.max_health = 500
            self.damage = 20
            self.speed = 1.5
            self.attack_range = 120
            self.attack_cooldown = 100
            self.score_value = 200
            self.color = (150, 0, 150)  # Purple
            self.abilities = [MonsterAbility.FIRE]
            self.behavior = MonsterBehavior.AGGRESSIVE
            self.width = 96
            self.height = 96
            
        elif self.monster_type == MonsterType.NECROMANCER:
            self.max_health = 400
            self.damage = 15
            self.speed = 1.3
            self.attack_range = 150
            self.attack_cooldown = 120
            self.score_value = 180
            self.color = (50, 50, 100)  # Dark blue
            self.abilities = [MonsterAbility.SUMMON]
            self.behavior = MonsterBehavior.RANGED
            self.width = 80
            self.height = 80
            
        elif self.monster_type == MonsterType.DEMON_LORD:
            self.max_health = 600
            self.damage = 25
            self.speed = 1.7
            self.attack_range = 100
            self.attack_cooldown = 90
            self.score_value = 250
            self.color = (250, 50, 50)  # Bright red
            self.abilities = [MonsterAbility.FIRE, MonsterAbility.TELEPORT]
            self.behavior = MonsterBehavior.AGGRESSIVE
            self.width = 96
            self.height = 96
            
        elif self.monster_type == MonsterType.LICH:
            self.max_health = 450
            self.damage = 18
            self.speed = 1.4
            self.attack_range = 180
            self.attack_cooldown = 110
            self.score_value = 220
            self.color = (0, 200, 200)  # Cyan
            self.abilities = [MonsterAbility.ICE, MonsterAbility.SUMMON]
            self.behavior = MonsterBehavior.RANGED
            self.width = 80
            self.height = 80
            
        # Khởi tạo máu hiện tại
        self.health = self.max_health
            
    def apply_level_scaling(self):
        """Áp dụng hệ số cấp độ cho chỉ số"""
        level_factor = 1 + (self.level - 1) * 0.2  # Mỗi cấp tăng 20%
        
        self.max_health = int(self.max_health * level_factor)
        self.damage = int(self.damage * level_factor)
        self.score_value = int(self.score_value * level_factor)
        self.health = self.max_health
        
    def apply_boss_scaling(self):
        """Áp dụng hệ số boss cho chỉ số"""
        self.max_health *= 2
        self.damage *= 1.5
        self.score_value *= 3
        self.health = self.max_health
        self.width *= 1.5
        self.height *= 1.5
