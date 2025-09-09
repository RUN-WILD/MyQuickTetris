import pygame
from board import Board

# Button class for UI elements
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont('Arial', 30)
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# game play logic - where we manage the game state
class Tetris:

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((720, 920))
        self._clock = pygame.time.Clock()
        self._running = True
        self._paused = False
        self._game_over = False
        self._base_speed = 40  # Base speed (higher is slower)
        self._speed = self._base_speed
        self._level = 1
        self._start_time = pygame.time.get_ticks()
        self._pause_start = 0
        self._pause_duration = 0
        self._elapsed_time = 0
        self._board = Board(self._screen)
        pygame.font.init()
        self._score_font = pygame.font.SysFont('Arial', 30)
        self._large_font = pygame.font.SysFont('Arial', 72, bold=True)
        
        # Create buttons
        button_width, button_height = 150, 50
        self.pause_button = Button(
            500, 220, 
            button_width, button_height, 
            'Pause', 
            (200, 200, 200), 
            (180, 180, 180)
        )
        self.exit_button = Button(
            500, 290, 
            button_width, button_height, 
            'Exit', 
            (255, 100, 100), 
            (220, 80, 80)
        )
        self.restart_button = Button(
            500, 360,
            button_width, button_height,
            'Restart',
            (144, 238, 144),  # Light green
            (124, 218, 124)
        )
        
        self.run()
# listening to the key strokes and updating the board
    def run(self):
        counter = 0
        last_time = pygame.time.get_ticks()
        self._pause_start = 0
        self._pause_duration = 0
        
        while self._running:
            current_time = pygame.time.get_ticks()
            dt = current_time - last_time
            last_time = current_time
            
            mouse_pos = pygame.mouse.get_pos()
            
            # Check button hovers
            self.pause_button.check_hover(mouse_pos)
            self.exit_button.check_hover(mouse_pos)
            self.restart_button.check_hover(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    
                # Handle button clicks
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.pause_button.is_clicked(mouse_pos, event) and not self._game_over:
                        self._paused = not self._paused
                        if self._paused:
                            self._pause_start = pygame.time.get_ticks()
                        else:
                            # When unpausing, adjust the start time to account for pause duration
                            self._pause_duration = pygame.time.get_ticks() - self._pause_start
                            self._start_time += self._pause_duration
                            self._pause_duration = 0
                        self.pause_button.text = 'Resume' if self._paused else 'Pause'
                    elif self.exit_button.is_clicked(mouse_pos, event):
                        self._running = False
                    elif self.restart_button.is_clicked(mouse_pos, event) and self._game_over:
                        self.__init__()  # Reset the game
                        return
                
                # Handle keyboard events only when not paused and not game over
                if not self._paused and not self._game_over and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Pause with P key
                        self._paused = True
                        self._pause_start = pygame.time.get_ticks()
                        self.pause_button.text = 'Resume'
                    if event.key == pygame.K_UP:
                        self._board.on_key_up()
                    if event.key == pygame.K_DOWN:
                        self._board.on_key_down()
                    if event.key == pygame.K_LEFT:
                        self._board.on_key_left()
                    if event.key == pygame.K_RIGHT:
                        self._board.on_key_right()
                    self._screen.fill("lightblue")
                    self._board.update(False)
                    self._board.draw()
            
            # Update game state if not paused and not game over
            if not self._paused and not self._game_over:
                # Calculate elapsed time (in seconds) since game start, minus pause durations
                current_time = pygame.time.get_ticks()
                self._elapsed_time = (current_time - self._start_time) / 1000
                
                # Increase level every minute (60 seconds)
                new_level = int(self._elapsed_time // 60) + 1
                if new_level > self._level:
                    self._level = new_level
                    # Increase speed (decrease the delay between drops)
                    self._speed = max(5, self._base_speed - (self._level - 1) * 5)
                
                # Update game
                if counter % self._speed == 0:
                    # Check for game over (if piece is already at the top)
                    if hasattr(self._board, '_current_tile') and self._board._current_tile:
                        if any(y < 0 for _, y in self._board._current_tile.get_coordinates()):
                            self._game_over = True
                    
                    if not self._game_over:
                        self._board.update()
                    counter = 1
                else:
                    counter += 1
            
            # Clear screen and draw everything
            self._screen.fill("lightblue")
            self._board.draw()
            
            # Draw UI elements
            # Score
            score_surface = self._score_font.render(f'Score: {self._board.score}', True, "black")
            self._screen.blit(score_surface, (500, 100))
            
            # Level
            level_surface = self._score_font.render(f'Level: {self._level}', True, "black")
            self._screen.blit(level_surface, (500, 150))
            
            # Timer (formatted as MM:SS)
            minutes = int(self._elapsed_time) // 60
            seconds = int(self._elapsed_time) % 60
            time_surface = self._score_font.render(f'Time: {minutes:02d}:{seconds:02d}', True, "black")
            self._screen.blit(time_surface, (500, 50))
            
            # Draw buttons
            self.pause_button.draw(self._screen)
            self.exit_button.draw(self._screen)
            self.restart_button.draw(self._screen)
            
            # Show pause message if game is paused
            if self._paused:
                pause_font = pygame.font.SysFont('Arial', 72, bold=True)
                pause_surface = pause_font.render('PAUSED', True, (0, 0, 0))
                pause_rect = pause_surface.get_rect(center=(360, 460))
                self._screen.blit(pause_surface, pause_rect)
            
            # Check for game over
            if self._board.game_over:
                self._game_over = True
                game_over_font = pygame.font.SysFont('Arial', 72, bold=True)
                game_over_surface = game_over_font.render('GAME OVER', True, (0, 0, 0))
                game_over_rect = game_over_surface.get_rect(center=(360, 460))
                self._screen.blit(game_over_surface, game_over_rect)
            
            # Update display
            pygame.display.flip()
            counter += 1
            self._clock.tick(100)
        pygame.quit()
