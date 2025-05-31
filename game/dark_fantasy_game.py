import sys
import os
import pygame

# Add the dark_fantasy_game directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dark_fantasy_game'))

# Import game components with error handling
try:
    # Try to import the main game components
    from dark_fantasy_game.src.main import Game
except ImportError as e:
    print(f"Error importing game components: {e}")
    
    # Fallback implementation if imports fail
    class Game:
        def __init__(self):
            pygame.init()
            self.screen = pygame.display.set_mode((800, 600))
            pygame.display.set_caption("Dark Fantasy Game - Error Recovery Mode")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont(None, 36)
            self.running = True
            
        def run(self):
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.running = False
                
                self.screen.fill((0, 0, 0))
                error_text = self.font.render("Error loading game components", True, (255, 0, 0))
                self.screen.blit(error_text, (200, 250))
                
                instructions = self.font.render("Please check installation and try again", True, (255, 255, 255))
                self.screen.blit(instructions, (150, 300))
                
                pygame.display.flip()
                self.clock.tick(30)

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        
        # Emergency error display
        try:
            pygame.init()
            screen = pygame.display.set_mode((800, 600))
            pygame.display.set_caption("Dark Fantasy Game - Error")
            font = pygame.font.SysFont(None, 36)
            
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        running = False
                
                screen.fill((0, 0, 0))
                error_text = font.render(f"Fatal error: {str(e)}", True, (255, 0, 0))
                screen.blit(error_text, (100, 250))
                
                instructions = font.render("Press ESC to exit", True, (255, 255, 255))
                screen.blit(instructions, (300, 300))
                
                pygame.display.flip()
                pygame.time.delay(30)
        except:
            pass
    finally:
        pygame.quit()
        sys.exit()
