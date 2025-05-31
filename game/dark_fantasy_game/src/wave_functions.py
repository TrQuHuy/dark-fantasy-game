from dark_fantasy_game.src.monster import MonsterType

def get_wave_config(wave_number):
    """Get the configuration for a specific wave"""
    wave_configs = {
        1: {
            "monsters": {
                MonsterType.GOBLIN: 5,
                MonsterType.SKELETON: 2
            },
            "boss": None
        },
        2: {
            "monsters": {
                MonsterType.GOBLIN: 8,
                MonsterType.SKELETON: 5,
                MonsterType.ORC: 1
            },
            "boss": None
        },
        3: {
            "monsters": {
                MonsterType.GOBLIN: 6,
                MonsterType.SKELETON: 8,
                MonsterType.ORC: 3
            },
            "boss": MonsterType.DEMON
        },
        4: {
            "monsters": {
                MonsterType.SKELETON: 10,
                MonsterType.ORC: 6,
                MonsterType.DEMON: 2
            },
            "boss": None
        },
        5: {
            "monsters": {
                MonsterType.ORC: 8,
                MonsterType.DEMON: 5
            },
            "boss": MonsterType.DRAGON
        }
    }
    
    # Return default wave if wave number is not defined
    if wave_number not in wave_configs:
        return {
            "monsters": {
                MonsterType.GOBLIN: 5,
                MonsterType.SKELETON: 5
            },
            "boss": None
        }
        
    return wave_configs[wave_number]
