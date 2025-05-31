import os
import json
import datetime
import pygame
from enum import Enum

class SaveSlot:
    def __init__(self, slot_id, save_name="", player_level=1, timestamp=None, screenshot=None):
        self.slot_id = slot_id
        self.save_name = save_name if save_name else f"Save {slot_id}"
        self.player_level = player_level
        self.timestamp = timestamp if timestamp else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.screenshot = screenshot
        
    def to_dict(self):
        """Convert to dictionary for saving metadata"""
        return {
            "slot_id": self.slot_id,
            "save_name": self.save_name,
            "player_level": self.player_level,
            "timestamp": self.timestamp
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary when loading metadata"""
        return cls(
            data["slot_id"],
            data["save_name"],
            data["player_level"],
            data["timestamp"]
        )

class SaveSystem:
    def __init__(self):
        self.save_slots = {}
        self.max_slots = 5
        self.current_slot = None
        self.save_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")
        self.show_save_menu = False
        self.show_load_menu = False
        self.selected_slot_index = 0
        self.rename_mode = False
        self.new_save_name = ""
        
        # UI elements
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        
        # Create save directory if it doesn't exist
        os.makedirs(self.save_directory, exist_ok=True)
        
        # Load save slot metadata
        self.load_save_slots_metadata()
        
    def update_fonts(self, scale_x=1.0, scale_y=1.0):
        """Update font sizes based on screen scale"""
        font_large_size = int(36 * min(scale_x, scale_y))
        font_medium_size = int(24 * min(scale_x, scale_y))
        font_small_size = int(18 * min(scale_x, scale_y))
        
        self.font_large = pygame.font.SysFont(None, font_large_size)
        self.font_medium = pygame.font.SysFont(None, font_medium_size)
        self.font_small = pygame.font.SysFont(None, font_small_size)
        
    def load_save_slots_metadata(self):
        """Load metadata for all save slots"""
        metadata_file = os.path.join(self.save_directory, "save_slots.json")
        
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    
                for slot_data in metadata:
                    slot = SaveSlot.from_dict(slot_data)
                    
                    # Load screenshot if available
                    screenshot_path = os.path.join(self.save_directory, f"slot_{slot.slot_id}_screenshot.png")
                    if os.path.exists(screenshot_path):
                        try:
                            slot.screenshot = pygame.image.load(screenshot_path)
                        except:
                            slot.screenshot = None
                            
                    self.save_slots[slot.slot_id] = slot
            except Exception as e:
                print(f"Error loading save slots metadata: {e}")
                self.initialize_empty_slots()
        else:
            self.initialize_empty_slots()
            
    def initialize_empty_slots(self):
        """Initialize empty save slots"""
        self.save_slots = {}
        for i in range(1, self.max_slots + 1):
            self.save_slots[i] = SaveSlot(i)
            
    def save_slots_metadata(self):
        """Save metadata for all save slots"""
        metadata_file = os.path.join(self.save_directory, "save_slots.json")
        
        try:
            metadata = [slot.to_dict() for slot in self.save_slots.values()]
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving slots metadata: {e}")
            
    def save_game(self, slot_id, game_state, take_screenshot=True):
        """Save game to specified slot"""
        if slot_id < 1 or slot_id > self.max_slots:
            return False
            
        save_file = os.path.join(self.save_directory, f"slot_{slot_id}.json")
        screenshot_file = os.path.join(self.save_directory, f"slot_{slot_id}_screenshot.png")
        
        try:
            # Create save data
            save_data = {
                "player": {
                    "x": game_state.player.x,
                    "y": game_state.player.y,
                    "character_class": game_state.player.character_class.value,
                    "stats": {
                        "max_health": game_state.player.stats.max_health,
                        "current_health": game_state.player.stats.current_health,
                        "physical_damage": game_state.player.stats.physical_damage,
                        "magic_damage": game_state.player.stats.magic_damage,
                        "physical_defense": game_state.player.stats.physical_defense
                    },
                    "experience_system": game_state.player.exp_system.to_dict(),
                    "inventory": game_state.player.inventory.to_dict()
                },
                "game_state": {
                    "score": game_state.score,
                    "level": game_state.level,
                    "monsters_killed_in_wave": game_state.monsters_killed_in_wave
                },
                "quest_system": game_state.quest_system.to_dict() if hasattr(game_state, "quest_system") else None
            }
            
            # Save game data
            with open(save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
                
            # Update save slot metadata
            self.save_slots[slot_id].player_level = game_state.player.exp_system.level
            self.save_slots[slot_id].timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Take screenshot if requested
            if take_screenshot and game_state.state == 1:  # Only if in playing state
                # Get a copy of the screen
                screen = pygame.display.get_surface()
                screenshot = pygame.Surface((screen.get_width(), screen.get_height()))
                screenshot.blit(screen, (0, 0))
                
                # Resize screenshot to thumbnail
                thumbnail_size = (200, 150)
                thumbnail = pygame.transform.scale(screenshot, thumbnail_size)
                
                # Save thumbnail
                pygame.image.save(thumbnail, screenshot_file)
                
                # Update slot screenshot
                self.save_slots[slot_id].screenshot = thumbnail
                
            # Save updated metadata
            self.save_slots_metadata()
            
            self.current_slot = slot_id
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
            
    def load_game(self, slot_id, game_state):
        """Load game from specified slot"""
        if slot_id < 1 or slot_id > self.max_slots:
            return False
            
        save_file = os.path.join(self.save_directory, f"slot_{slot_id}.json")
        
        if not os.path.exists(save_file):
            return False
            
        try:
            # Load save data
            with open(save_file, 'r') as f:
                save_data = json.load(f)
                
            # Load player data
            player_data = save_data["player"]
            game_state.player.x = player_data["x"]
            game_state.player.y = player_data["y"]
            
            # Load character class
            from dark_fantasy_game.src.stats import CharacterClass
            game_state.player.character_class = CharacterClass(player_data["character_class"])
            
            # Load stats
            stats_data = player_data["stats"]
            game_state.player.stats.max_health = stats_data["max_health"]
            game_state.player.stats.current_health = stats_data["current_health"]
            game_state.player.stats.physical_damage = stats_data["physical_damage"]
            game_state.player.stats.magic_damage = stats_data["magic_damage"]
            game_state.player.stats.physical_defense = stats_data["physical_defense"]
            
            # Load experience system
            if "experience_system" in player_data:
                from dark_fantasy_game.src.experience_system import ExperienceSystem
                exp_system = ExperienceSystem()
                exp_system.level = player_data["experience_system"]["level"]
                exp_system.experience = player_data["experience_system"]["experience"]
                exp_system.skill_points = player_data["experience_system"]["skill_points"]
                exp_system.upgradable_stats = player_data["experience_system"]["upgradable_stats"]
                game_state.player.exp_system = exp_system
                
            # Load inventory
            if "inventory" in player_data:
                game_state.player.inventory.from_dict(player_data["inventory"])
                
            # Load game state data
            game_state_data = save_data["game_state"]
            game_state.score = game_state_data["score"]
            game_state.level = game_state_data["level"]
            game_state.monsters_killed_in_wave = game_state_data["monsters_killed_in_wave"]
            
            # Load quest system if available
            if "quest_system" in save_data and save_data["quest_system"]:
                from dark_fantasy_game.src.quest_system import QuestSystem
                game_state.quest_system = QuestSystem.from_dict(save_data["quest_system"])
                
            # Update current slot
            self.current_slot = slot_id
            
            # Set game state to playing
            game_state.state = 1  # PLAYING
            
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
            
    def delete_save(self, slot_id):
        """Delete save from specified slot"""
        if slot_id < 1 or slot_id > self.max_slots:
            return False
            
        save_file = os.path.join(self.save_directory, f"slot_{slot_id}.json")
        screenshot_file = os.path.join(self.save_directory, f"slot_{slot_id}_screenshot.png")
        
        try:
            # Delete save file if it exists
            if os.path.exists(save_file):
                os.remove(save_file)
                
            # Delete screenshot if it exists
            if os.path.exists(screenshot_file):
                os.remove(screenshot_file)
                
            # Reset slot metadata
            self.save_slots[slot_id] = SaveSlot(slot_id)
            
            # Save updated metadata
            self.save_slots_metadata()
            
            # Reset current slot if it was deleted
            if self.current_slot == slot_id:
                self.current_slot = None
                
            return True
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False
            
    def rename_save(self, slot_id, new_name):
        """Rename save slot"""
        if slot_id < 1 or slot_id > self.max_slots:
            return False
            
        try:
            self.save_slots[slot_id].save_name = new_name
            self.save_slots_metadata()
            return True
        except Exception as e:
            print(f"Error renaming save: {e}")
            return False
            
    def toggle_save_menu(self):
        """Toggle save menu visibility"""
        self.show_save_menu = not self.show_save_menu
        if self.show_save_menu:
            self.show_load_menu = False
            self.selected_slot_index = 0
            self.rename_mode = False
            self.new_save_name = ""
            
    def toggle_load_menu(self):
        """Toggle load menu visibility"""
        self.show_load_menu = not self.show_load_menu
        if self.show_load_menu:
            self.show_save_menu = False
            self.selected_slot_index = 0
            self.rename_mode = False
            
    def select_next_slot(self):
        """Select next save slot"""
        self.selected_slot_index = (self.selected_slot_index + 1) % self.max_slots
        
    def select_previous_slot(self):
        """Select previous save slot"""
        self.selected_slot_index = (self.selected_slot_index - 1) % self.max_slots
        
    def get_selected_slot_id(self):
        """Get ID of currently selected slot"""
        return self.selected_slot_index + 1
        
    def handle_event(self, event, game_state):
        """Handle input events for save/load menus"""
        if not (self.show_save_menu or self.show_load_menu):
            return False
            
        if event.type == pygame.KEYDOWN:
            if self.rename_mode:
                # Handle text input for rename mode
                if event.key == pygame.K_RETURN:
                    # Confirm rename
                    if self.new_save_name:
                        self.rename_save(self.get_selected_slot_id(), self.new_save_name)
                    self.rename_mode = False
                    self.new_save_name = ""
                elif event.key == pygame.K_ESCAPE:
                    # Cancel rename
                    self.rename_mode = False
                    self.new_save_name = ""
                elif event.key == pygame.K_BACKSPACE:
                    # Delete last character
                    self.new_save_name = self.new_save_name[:-1]
                else:
                    # Add character if it's printable
                    if event.unicode.isprintable() and len(self.new_save_name) < 20:
                        self.new_save_name += event.unicode
            else:
                # Handle menu navigation
                if event.key == pygame.K_UP:
                    self.select_previous_slot()
                elif event.key == pygame.K_DOWN:
                    self.select_next_slot()
                elif event.key == pygame.K_ESCAPE:
                    # Close menu
                    self.show_save_menu = False
                    self.show_load_menu = False
                elif event.key == pygame.K_RETURN:
                    # Perform action on selected slot
                    slot_id = self.get_selected_slot_id()
                    if self.show_save_menu:
                        self.save_game(slot_id, game_state)
                        self.show_save_menu = False
                    elif self.show_load_menu:
                        save_file = os.path.join(self.save_directory, f"slot_{slot_id}.json")
                        if os.path.exists(save_file):
                            self.load_game(slot_id, game_state)
                            self.show_load_menu = False
                elif event.key == pygame.K_DELETE:
                    # Delete selected save
                    slot_id = self.get_selected_slot_id()
                    self.delete_save(slot_id)
                elif event.key == pygame.K_r:
                    # Rename selected save
                    slot_id = self.get_selected_slot_id()
                    self.rename_mode = True
                    self.new_save_name = self.save_slots[slot_id].save_name
                    
        return True
        
    def draw_save_load_menu(self, screen, scale_x=1.0, scale_y=1.0):
        """Draw save or load menu if visible"""
        if not (self.show_save_menu or self.show_load_menu):
            return
            
        if not self.font_large:
            self.update_fonts(scale_x, scale_y)
            
        # Calculate menu position and size
        menu_width = int(500 * scale_x)
        menu_height = int(400 * scale_y)
        menu_x = (screen.get_width() - menu_width) // 2
        menu_y = (screen.get_height() - menu_height) // 2
        
        # Create menu surface with transparency
        menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_surface.fill((0, 0, 0, 230))
        
        # Draw border
        pygame.draw.rect(menu_surface, (200, 200, 200), 
                        (0, 0, menu_width, menu_height), 2)
        
        # Draw title
        title_text = self.font_large.render(
            "Save Game" if self.show_save_menu else "Load Game", 
            True, (255, 255, 255))
        title_x = (menu_width - title_text.get_width()) // 2
        menu_surface.blit(title_text, (title_x, 10))
        
        # Draw separator
        pygame.draw.line(menu_surface, (200, 200, 200), 
                        (20, 50), (menu_width - 20, 50), 1)
        
        # Draw save slots
        slot_y = 70
        slot_height = 60
        
        for i in range(1, self.max_slots + 1):
            slot = self.save_slots[i]
            
            # Highlight selected slot
            if i - 1 == self.selected_slot_index:
                pygame.draw.rect(menu_surface, (50, 50, 80), 
                                (10, slot_y - 5, menu_width - 20, slot_height + 10))
                pygame.draw.rect(menu_surface, (100, 100, 150), 
                                (10, slot_y - 5, menu_width - 20, slot_height + 10), 1)
            
            # Draw slot number
            slot_num_text = self.font_medium.render(f"Slot {i}:", True, (200, 200, 200))
            menu_surface.blit(slot_num_text, (20, slot_y))
            
            # Draw save name
            if self.rename_mode and i - 1 == self.selected_slot_index:
                # Draw text input field
                pygame.draw.rect(menu_surface, (30, 30, 30), 
                                (120, slot_y, 250, 30))
                pygame.draw.rect(menu_surface, (100, 100, 100), 
                                (120, slot_y, 250, 30), 1)
                
                name_text = self.font_medium.render(self.new_save_name, True, (255, 255, 255))
                menu_surface.blit(name_text, (125, slot_y + 5))
                
                # Draw blinking cursor
                if pygame.time.get_ticks() % 1000 < 500:
                    cursor_x = 125 + name_text.get_width()
                    pygame.draw.line(menu_surface, (255, 255, 255), 
                                    (cursor_x, slot_y + 5), 
                                    (cursor_x, slot_y + 25), 1)
            else:
                name_text = self.font_medium.render(slot.save_name, True, (255, 255, 255))
                menu_surface.blit(name_text, (120, slot_y))
            
            # Draw save info
            save_file = os.path.join(self.save_directory, f"slot_{i}.json")
            if os.path.exists(save_file):
                # Draw level and timestamp
                level_text = self.font_small.render(f"Level: {slot.player_level}", True, (200, 200, 200))
                menu_surface.blit(level_text, (120, slot_y + 30))
                
                time_text = self.font_small.render(slot.timestamp, True, (150, 150, 150))
                menu_surface.blit(time_text, (250, slot_y + 30))
                
                # Draw screenshot thumbnail if available
                if slot.screenshot:
                    thumbnail_size = (80, 60)
                    thumbnail_x = menu_width - thumbnail_size[0] - 20
                    thumbnail_y = slot_y
                    
                    # Draw border
                    pygame.draw.rect(menu_surface, (100, 100, 100), 
                                    (thumbnail_x - 2, thumbnail_y - 2, 
                                     thumbnail_size[0] + 4, thumbnail_size[1] + 4))
                    
                    # Draw thumbnail
                    menu_surface.blit(pygame.transform.scale(slot.screenshot, thumbnail_size), 
                                     (thumbnail_x, thumbnail_y))
            else:
                # Draw empty slot text
                empty_text = self.font_small.render("Empty Slot", True, (150, 150, 150))
                menu_surface.blit(empty_text, (120, slot_y + 30))
            
            slot_y += slot_height + 10
            
        # Draw instructions
        instructions = []
        if self.rename_mode:
            instructions = [
                "Enter: Confirm rename",
                "Esc: Cancel rename"
            ]
        else:
            if self.show_save_menu:
                instructions = [
                    "Enter: Save to selected slot",
                    "R: Rename slot",
                    "Delete: Clear slot",
                    "Esc: Cancel"
                ]
            else:  # Load menu
                instructions = [
                    "Enter: Load selected save",
                    "Delete: Delete save",
                    "Esc: Cancel"
                ]
                
        # Draw instructions
        instruction_y = menu_height - 30 * len(instructions) - 10
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, (200, 200, 200))
            inst_x = (menu_width - inst_text.get_width()) // 2
            menu_surface.blit(inst_text, (inst_x, instruction_y))
            instruction_y += 25
            
        # Draw menu
        screen.blit(menu_surface, (menu_x, menu_y))
        
    def to_dict(self):
        """Convert save system state to dictionary"""
        return {
            "current_slot": self.current_slot,
            "save_slots": [slot.to_dict() for slot in self.save_slots.values()]
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create save system from saved data"""
        save_system = cls()
        save_system.current_slot = data["current_slot"]
        
        # Load save slots
        save_system.save_slots = {}
        for slot_data in data["save_slots"]:
            slot = SaveSlot.from_dict(slot_data)
            save_system.save_slots[slot.slot_id] = slot
            
        return save_system
