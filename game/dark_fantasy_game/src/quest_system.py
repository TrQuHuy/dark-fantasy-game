import pygame
import json
import os
from enum import Enum

class QuestType(Enum):
    MAIN = "Main Quest"
    SIDE = "Side Quest"
    ACHIEVEMENT = "Achievement"

class QuestStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"

class QuestObjectiveType(Enum):
    KILL_MONSTERS = "Kill Monsters"
    COLLECT_ITEMS = "Collect Items"
    REACH_LOCATION = "Reach Location"
    TALK_TO_NPC = "Talk to NPC"
    SURVIVE_TIME = "Survive Time"
    REACH_LEVEL = "Reach Level"
    DEFEAT_BOSS = "Defeat Boss"

class QuestObjective:
    def __init__(self, objective_type, target, required_amount=1, current_amount=0, description=""):
        self.objective_type = objective_type
        self.target = target  # Monster type, item type, location, NPC name, etc.
        self.required_amount = required_amount
        self.current_amount = current_amount
        self.description = description
        self.completed = False
        
    def update(self, event_type, event_target, amount=1):
        """Update objective progress based on game events"""
        if self.completed:
            return False
            
        if event_type == self.objective_type and event_target == self.target:
            self.current_amount += amount
            if self.current_amount >= self.required_amount:
                self.current_amount = self.required_amount
                self.completed = True
                return True
        return False
        
    def get_progress_percentage(self):
        """Get progress as a percentage"""
        if self.required_amount == 0:
            return 100
        return (self.current_amount / self.required_amount) * 100
        
    def to_dict(self):
        """Convert to dictionary for saving"""
        return {
            "objective_type": self.objective_type.value,
            "target": self.target,
            "required_amount": self.required_amount,
            "current_amount": self.current_amount,
            "description": self.description,
            "completed": self.completed
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary when loading"""
        objective = cls(
            QuestObjectiveType(data["objective_type"]),
            data["target"],
            data["required_amount"],
            data["current_amount"],
            data["description"]
        )
        objective.completed = data["completed"]
        return objective

class Quest:
    def __init__(self, quest_id, title, description, quest_type, level_requirement=1):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.quest_type = quest_type
        self.level_requirement = level_requirement
        self.objectives = []
        self.status = QuestStatus.NOT_STARTED
        self.rewards = {
            "experience": 0,
            "gold": 0,
            "items": []
        }
        self.next_quest_id = None  # For quest chains
        self.is_hidden = False  # Some quests are hidden until certain conditions are met
        
    def add_objective(self, objective):
        """Add an objective to the quest"""
        self.objectives.append(objective)
        
    def set_rewards(self, experience=0, gold=0, items=None):
        """Set quest rewards"""
        self.rewards["experience"] = experience
        self.rewards["gold"] = gold
        if items:
            self.rewards["items"] = items
            
    def start(self):
        """Start the quest"""
        if self.status == QuestStatus.NOT_STARTED:
            self.status = QuestStatus.IN_PROGRESS
            return True
        return False
        
    def update(self, event_type, event_target, amount=1):
        """Update quest progress based on game events"""
        if self.status != QuestStatus.IN_PROGRESS:
            return False
            
        updated = False
        for objective in self.objectives:
            if objective.update(event_type, event_target, amount):
                updated = True
                
        # Check if all objectives are completed
        if all(objective.completed for objective in self.objectives):
            self.status = QuestStatus.COMPLETED
            updated = True
            
        return updated
        
    def get_progress_percentage(self):
        """Get overall quest progress as a percentage"""
        if not self.objectives:
            return 0
            
        total_progress = sum(obj.get_progress_percentage() for obj in self.objectives)
        return total_progress / len(self.objectives)
        
    def is_available(self, player_level):
        """Check if quest is available based on player level"""
        return player_level >= self.level_requirement and not self.is_hidden
        
    def to_dict(self):
        """Convert to dictionary for saving"""
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "description": self.description,
            "quest_type": self.quest_type.value,
            "level_requirement": self.level_requirement,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "status": self.status.value,
            "rewards": self.rewards,
            "next_quest_id": self.next_quest_id,
            "is_hidden": self.is_hidden
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary when loading"""
        quest = cls(
            data["quest_id"],
            data["title"],
            data["description"],
            QuestType(data["quest_type"]),
            data["level_requirement"]
        )
        quest.objectives = [QuestObjective.from_dict(obj_data) for obj_data in data["objectives"]]
        quest.status = QuestStatus(data["status"])
        quest.rewards = data["rewards"]
        quest.next_quest_id = data["next_quest_id"]
        quest.is_hidden = data["is_hidden"]
        return quest

class QuestSystem:
    def __init__(self):
        self.quests = {}
        self.active_quests = []  # List of quest_ids that are currently active
        self.completed_quests = []  # List of quest_ids that have been completed
        self.failed_quests = []  # List of quest_ids that have been failed
        self.quest_log_visible = False
        self.selected_quest_index = 0
        self.quest_notification_timer = 0
        self.quest_notification_text = ""
        self.quest_notification_duration = 180  # 3 seconds at 60 FPS
        
        # UI elements
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        
        # Load predefined quests
        self.load_predefined_quests()
        
    def load_predefined_quests(self):
        """Load predefined quests from a JSON file or create default quests"""
        quest_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "quests.json")
        
        if os.path.exists(quest_file):
            try:
                with open(quest_file, 'r') as f:
                    quests_data = json.load(f)
                    
                for quest_data in quests_data:
                    quest = Quest.from_dict(quest_data)
                    self.quests[quest.quest_id] = quest
            except Exception as e:
                print(f"Error loading quests: {e}")
                self.create_default_quests()
        else:
            self.create_default_quests()
            
    def create_default_quests(self):
        """Create default quests if no quest file is found"""
        # Main quest line
        main_quest1 = Quest("main_1", "The Dark Beginning", 
                          "Survive the first wave of monsters and discover the source of darkness.", 
                          QuestType.MAIN, 1)
        main_quest1.add_objective(QuestObjective(
            QuestObjectiveType.KILL_MONSTERS, "any", 10, 0, 
            "Defeat 10 monsters of any type"
        ))
        main_quest1.set_rewards(experience=100, gold=50)
        main_quest1.next_quest_id = "main_2"
        self.quests["main_1"] = main_quest1
        
        main_quest2 = Quest("main_2", "The Growing Darkness", 
                          "The darkness is spreading. Defeat more powerful enemies to gain strength.", 
                          QuestType.MAIN, 3)
        main_quest2.add_objective(QuestObjective(
            QuestObjectiveType.KILL_MONSTERS, "demon", 5, 0, 
            "Defeat 5 demons"
        ))
        main_quest2.add_objective(QuestObjective(
            QuestObjectiveType.REACH_LEVEL, "player", 5, 0, 
            "Reach level 5"
        ))
        main_quest2.set_rewards(experience=300, gold=100)
        main_quest2.next_quest_id = "main_3"
        self.quests["main_2"] = main_quest2
        
        main_quest3 = Quest("main_3", "The Final Confrontation", 
                          "Face the source of darkness and save the realm.", 
                          QuestType.MAIN, 8)
        main_quest3.add_objective(QuestObjective(
            QuestObjectiveType.DEFEAT_BOSS, "dragon", 1, 0, 
            "Defeat the Dragon Boss"
        ))
        main_quest3.set_rewards(experience=1000, gold=500)
        self.quests["main_3"] = main_quest3
        
        # Side quests
        side_quest1 = Quest("side_1", "Monster Hunter", 
                          "Prove your worth as a monster hunter.", 
                          QuestType.SIDE, 2)
        side_quest1.add_objective(QuestObjective(
            QuestObjectiveType.KILL_MONSTERS, "goblin", 15, 0, 
            "Defeat 15 goblins"
        ))
        side_quest1.add_objective(QuestObjective(
            QuestObjectiveType.KILL_MONSTERS, "skeleton", 10, 0, 
            "Defeat 10 skeletons"
        ))
        side_quest1.set_rewards(experience=200, gold=75)
        self.quests["side_1"] = side_quest1
        
        side_quest2 = Quest("side_2", "Survival Expert", 
                          "Survive against overwhelming odds.", 
                          QuestType.SIDE, 5)
        side_quest2.add_objective(QuestObjective(
            QuestObjectiveType.SURVIVE_TIME, "wave", 300, 0, 
            "Survive for 5 minutes in a single wave"
        ))
        side_quest2.set_rewards(experience=350, gold=150)
        self.quests["side_2"] = side_quest2
        
        # Achievements
        achievement1 = Quest("achievement_1", "First Blood", 
                           "Defeat your first monster.", 
                           QuestType.ACHIEVEMENT, 1)
        achievement1.add_objective(QuestObjective(
            QuestObjectiveType.KILL_MONSTERS, "any", 1, 0, 
            "Defeat 1 monster"
        ))
        achievement1.set_rewards(experience=50)
        self.quests["achievement_1"] = achievement1
        
        achievement2 = Quest("achievement_2", "Leveling Up", 
                           "Reach level 10.", 
                           QuestType.ACHIEVEMENT, 1)
        achievement2.add_objective(QuestObjective(
            QuestObjectiveType.REACH_LEVEL, "player", 10, 0, 
            "Reach level 10"
        ))
        achievement2.set_rewards(experience=500)
        self.quests["achievement_2"] = achievement2
        
        achievement3 = Quest("achievement_3", "Boss Slayer", 
                           "Defeat your first boss.", 
                           QuestType.ACHIEVEMENT, 1)
        achievement3.add_objective(QuestObjective(
            QuestObjectiveType.DEFEAT_BOSS, "any", 1, 0, 
            "Defeat any boss"
        ))
        achievement3.set_rewards(experience=300, gold=100)
        self.quests["achievement_3"] = achievement3
        
    def update_fonts(self, scale_x=1.0, scale_y=1.0):
        """Update font sizes based on screen scale"""
        font_large_size = int(32 * min(scale_x, scale_y))
        font_medium_size = int(24 * min(scale_x, scale_y))
        font_small_size = int(18 * min(scale_x, scale_y))
        
        self.font_large = pygame.font.SysFont(None, font_large_size)
        self.font_medium = pygame.font.SysFont(None, font_medium_size)
        self.font_small = pygame.font.SysFont(None, font_small_size)
        
    def start_quest(self, quest_id):
        """Start a quest by ID"""
        if quest_id in self.quests and quest_id not in self.active_quests:
            quest = self.quests[quest_id]
            if quest.start():
                self.active_quests.append(quest_id)
                self.show_notification(f"New Quest: {quest.title}")
                return True
        return False
        
    def update(self, event_type, event_target, amount=1, player_level=1):
        """Update all active quests based on game events"""
        updated_quests = []
        
        # Update active quests
        for quest_id in list(self.active_quests):
            quest = self.quests[quest_id]
            if quest.update(event_type, event_target, amount):
                updated_quests.append(quest)
                
                # If quest completed, handle rewards and next quest
                if quest.status == QuestStatus.COMPLETED:
                    self.active_quests.remove(quest_id)
                    self.completed_quests.append(quest_id)
                    self.show_notification(f"Quest Completed: {quest.title}")
                    
                    # Start next quest in chain if available
                    if quest.next_quest_id and quest.next_quest_id in self.quests:
                        next_quest = self.quests[quest.next_quest_id]
                        if next_quest.is_available(player_level):
                            self.start_quest(quest.next_quest_id)
                            
        # Check for new available quests based on player level
        for quest_id, quest in self.quests.items():
            if (quest_id not in self.active_quests and 
                quest_id not in self.completed_quests and
                quest_id not in self.failed_quests and
                quest.status == QuestStatus.NOT_STARTED and
                quest.is_available(player_level)):
                
                # Auto-start achievements
                if quest.quest_type == QuestType.ACHIEVEMENT:
                    self.start_quest(quest_id)
                    
        # Update notification timer
        if self.quest_notification_timer > 0:
            self.quest_notification_timer -= 1
            
        return updated_quests
        
    def show_notification(self, text):
        """Show a quest notification"""
        self.quest_notification_text = text
        self.quest_notification_timer = self.quest_notification_duration
        
    def get_quest_rewards(self, quest_id):
        """Get rewards for a completed quest"""
        if quest_id in self.completed_quests and quest_id in self.quests:
            return self.quests[quest_id].rewards
        return None
        
    def toggle_quest_log(self):
        """Toggle quest log visibility"""
        self.quest_log_visible = not self.quest_log_visible
        if self.quest_log_visible:
            self.selected_quest_index = 0
            
    def select_next_quest(self):
        """Select next quest in the log"""
        if self.active_quests:
            self.selected_quest_index = (self.selected_quest_index + 1) % len(self.active_quests)
            
    def select_previous_quest(self):
        """Select previous quest in the log"""
        if self.active_quests:
            self.selected_quest_index = (self.selected_quest_index - 1) % len(self.active_quests)
            
    def get_active_quests_count(self):
        """Get number of active quests"""
        return len(self.active_quests)
        
    def get_completed_quests_count(self):
        """Get number of completed quests"""
        return len(self.completed_quests)
        
    def get_total_quests_count(self):
        """Get total number of quests"""
        return len(self.quests)
        
    def draw_quest_notification(self, screen, scale_x=1.0, scale_y=1.0):
        """Draw quest notification if active"""
        if self.quest_notification_timer <= 0:
            return
            
        if not self.font_medium:
            self.update_fonts(scale_x, scale_y)
            
        # Calculate notification position and size
        notification_width = int(400 * scale_x)
        notification_height = int(60 * scale_y)
        notification_x = (screen.get_width() - notification_width) // 2
        notification_y = int(50 * scale_y)
        
        # Calculate alpha based on remaining time
        alpha = min(255, int(255 * (self.quest_notification_timer / self.quest_notification_duration)))
        
        # Create notification surface with transparency
        notification_surface = pygame.Surface((notification_width, notification_height), pygame.SRCALPHA)
        notification_surface.fill((0, 0, 0, min(200, alpha)))
        
        # Draw border
        pygame.draw.rect(notification_surface, (255, 215, 0, alpha), 
                        (0, 0, notification_width, notification_height), 2)
        
        # Draw text
        text_surface = self.font_medium.render(self.quest_notification_text, True, (255, 255, 255))
        text_x = (notification_width - text_surface.get_width()) // 2
        text_y = (notification_height - text_surface.get_height()) // 2
        notification_surface.blit(text_surface, (text_x, text_y))
        
        # Draw notification
        screen.blit(notification_surface, (notification_x, notification_y))
        
    def draw_quest_log(self, screen, scale_x=1.0, scale_y=1.0):
        """Draw the quest log if visible"""
        if not self.quest_log_visible:
            return
            
        if not self.font_large:
            self.update_fonts(scale_x, scale_y)
            
        # Calculate quest log position and size
        log_width = int(600 * scale_x)
        log_height = int(500 * scale_y)
        log_x = (screen.get_width() - log_width) // 2
        log_y = (screen.get_height() - log_height) // 2
        
        # Create quest log surface with transparency
        log_surface = pygame.Surface((log_width, log_height), pygame.SRCALPHA)
        log_surface.fill((0, 0, 0, 200))
        
        # Draw border
        pygame.draw.rect(log_surface, (200, 200, 200), 
                        (0, 0, log_width, log_height), 2)
        
        # Draw title
        title_text = self.font_large.render("Quest Log", True, (255, 215, 0))
        title_x = (log_width - title_text.get_width()) // 2
        log_surface.blit(title_text, (title_x, 10))
        
        # Draw quest categories
        category_y = 60
        categories = [
            (QuestType.MAIN, "Main Quests", (255, 100, 100)),
            (QuestType.SIDE, "Side Quests", (100, 255, 100)),
            (QuestType.ACHIEVEMENT, "Achievements", (100, 100, 255))
        ]
        
        for category_type, category_name, category_color in categories:
            # Draw category header
            category_text = self.font_medium.render(category_name, True, category_color)
            log_surface.blit(category_text, (20, category_y))
            
            # Draw underline
            pygame.draw.line(log_surface, category_color, 
                            (20, category_y + category_text.get_height() + 2),
                            (log_width - 20, category_y + category_text.get_height() + 2), 1)
            
            category_y += 40
            
            # Draw quests in this category
            quests_drawn = 0
            for i, quest_id in enumerate(self.active_quests):
                quest = self.quests[quest_id]
                if quest.quest_type == category_type:
                    # Highlight selected quest
                    if i == self.selected_quest_index:
                        pygame.draw.rect(log_surface, (50, 50, 50), 
                                        (10, category_y - 5, log_width - 20, 60))
                    
                    # Draw quest title
                    quest_title = self.font_medium.render(quest.title, True, (255, 255, 255))
                    log_surface.blit(quest_title, (30, category_y))
                    
                    # Draw progress bar
                    progress = quest.get_progress_percentage()
                    bar_width = int(200 * scale_x)
                    bar_height = int(10 * scale_y)
                    bar_x = 30
                    bar_y = category_y + 25
                    
                    # Draw background
                    pygame.draw.rect(log_surface, (50, 50, 50), 
                                    (bar_x, bar_y, bar_width, bar_height))
                    
                    # Draw progress
                    progress_width = int(bar_width * progress / 100)
                    pygame.draw.rect(log_surface, category_color, 
                                    (bar_x, bar_y, progress_width, bar_height))
                    
                    # Draw border
                    pygame.draw.rect(log_surface, (200, 200, 200), 
                                    (bar_x, bar_y, bar_width, bar_height), 1)
                    
                    # Draw progress text
                    progress_text = self.font_small.render(f"{int(progress)}%", True, (255, 255, 255))
                    log_surface.blit(progress_text, 
                                    (bar_x + bar_width + 10, bar_y))
                    
                    category_y += 70
                    quests_drawn += 1
            
            # If no quests in category, show message
            if quests_drawn == 0:
                no_quests_text = self.font_small.render("No active quests", True, (150, 150, 150))
                log_surface.blit(no_quests_text, (40, category_y))
                category_y += 30
                
            category_y += 20
            
        # Draw selected quest details if any quest is selected
        if self.active_quests and 0 <= self.selected_quest_index < len(self.active_quests):
            selected_quest = self.quests[self.active_quests[self.selected_quest_index]]
            
            # Draw separator
            pygame.draw.line(log_surface, (200, 200, 200), 
                            (20, category_y), (log_width - 20, category_y), 1)
            
            category_y += 20
            
            # Draw quest description
            desc_text = self.font_small.render(selected_quest.description, True, (200, 200, 200))
            log_surface.blit(desc_text, (20, category_y))
            
            category_y += 30
            
            # Draw objectives
            objectives_text = self.font_medium.render("Objectives:", True, (255, 255, 255))
            log_surface.blit(objectives_text, (20, category_y))
            
            category_y += 30
            
            for objective in selected_quest.objectives:
                # Draw objective description
                obj_text = self.font_small.render(objective.description, True, 
                                                (255, 255, 255) if not objective.completed else (100, 255, 100))
                log_surface.blit(obj_text, (40, category_y))
                
                # Draw progress
                progress_text = self.font_small.render(
                    f"{objective.current_amount}/{objective.required_amount}", 
                    True, (200, 200, 200))
                log_surface.blit(progress_text, (log_width - 80, category_y))
                
                category_y += 25
                
            # Draw rewards
            category_y += 10
            rewards_text = self.font_medium.render("Rewards:", True, (255, 215, 0))
            log_surface.blit(rewards_text, (20, category_y))
            
            category_y += 30
            
            # Experience
            if selected_quest.rewards["experience"] > 0:
                exp_text = self.font_small.render(
                    f"Experience: {selected_quest.rewards['experience']}", 
                    True, (200, 200, 255))
                log_surface.blit(exp_text, (40, category_y))
                category_y += 25
                
            # Gold
            if selected_quest.rewards["gold"] > 0:
                gold_text = self.font_small.render(
                    f"Gold: {selected_quest.rewards['gold']}", 
                    True, (255, 215, 0))
                log_surface.blit(gold_text, (40, category_y))
                category_y += 25
                
            # Items
            if selected_quest.rewards["items"]:
                for item in selected_quest.rewards["items"]:
                    item_text = self.font_small.render(
                        f"Item: {item}", 
                        True, (100, 255, 100))
                    log_surface.blit(item_text, (40, category_y))
                    category_y += 25
        
        # Draw instructions
        instructions_text = self.font_small.render(
            "Press J to close, Up/Down to navigate", 
            True, (150, 150, 150))
        instructions_x = (log_width - instructions_text.get_width()) // 2
        instructions_y = log_height - 30
        log_surface.blit(instructions_text, (instructions_x, instructions_y))
        
        # Draw quest log
        screen.blit(log_surface, (log_x, log_y))
        
    def to_dict(self):
        """Convert quest system state to dictionary for saving"""
        return {
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests,
            "failed_quests": self.failed_quests,
            "quests": {quest_id: quest.to_dict() for quest_id, quest in self.quests.items()}
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create quest system from saved data"""
        quest_system = cls()
        
        # Load quests
        quest_system.quests = {}
        for quest_id, quest_data in data["quests"].items():
            quest_system.quests[quest_id] = Quest.from_dict(quest_data)
            
        # Load quest lists
        quest_system.active_quests = data["active_quests"]
        quest_system.completed_quests = data["completed_quests"]
        quest_system.failed_quests = data["failed_quests"]
        
        return quest_system
