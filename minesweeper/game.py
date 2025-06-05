import pygame
import os
import time
from minesweeper.grid import Grid
from minesweeper.tile import Tile

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
ROWS, COLS = 8, 8
N_BOMBS = 10
BUFFER = 4  # margin/gap between tiles
STRIP_HEIGHT = 50  # Height of the top strip

# Fixed screen dimensions (regardless of grid size)
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600 + STRIP_HEIGHT

# Calculate tile size based on available space
# Available width = screen width - total buffer space between tiles
# Available height = screen height - strip - total buffer space between tiles
AVAILABLE_WIDTH = SCREEN_WIDTH - (BUFFER * (COLS + 1))
AVAILABLE_HEIGHT = SCREEN_HEIGHT - STRIP_HEIGHT - (BUFFER * (ROWS + 1))

# Tile size is the minimum of the available space divided by rows/cols
# to ensure tiles fit within both dimensions
TILE_SIZE = min(AVAILABLE_WIDTH // COLS, AVAILABLE_HEIGHT // ROWS)

# Recalculate actual width and height used by the grid
ACTUAL_GRID_WIDTH = (TILE_SIZE * COLS) + (BUFFER * (COLS + 1))
ACTUAL_GRID_HEIGHT = (TILE_SIZE * ROWS) + (BUFFER * (ROWS + 1))

# Center the grid horizontally if needed
GRID_X_OFFSET = (SCREEN_WIDTH - ACTUAL_GRID_WIDTH) // 2

class MinesweeperGame:
    def __init__(self):
        pygame.init()

        self.game_window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MinesweeperAI")

        # Add game status attribute
        self.game_status = "playing"  # Can be "playing", "won", or "lost"
        # Track bombs and flags
        self.bomb_count = N_BOMBS
        self.flagged_count = 0

        # Load images and font for all tiles
        Tile.load_assets(
            bomb_path=os.path.join(ASSETS_DIR, 'bomb.png'),
            hidden_path=os.path.join(ASSETS_DIR, 'hidden2.png'),
            revealed_path=os.path.join(ASSETS_DIR, 'revealed.png'),
            flagged_path=os.path.join(ASSETS_DIR, 'flag1.png'),
            font=pygame.font.Font('freesansbold.ttf', 32)
        )
        
        # Load emoji faces for restart button
        self.face_happy = pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, 'face_happy.png')), (40, 40))
        self.face_sad = pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, 'face_sad.png')), (40, 40))
        self.face_cool = pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, 'face_cool.png')), (40, 40))
        
        # Restart button rect
        self.restart_rect = pygame.Rect(SCREEN_WIDTH//2 - 20, STRIP_HEIGHT//2 - 20, 40, 40)
        
        # Create fonts for the counters
        self.counter_font = pygame.font.Font('freesansbold.ttf', 24)

    def run(self) -> None:
        # Fill the entire window with gray background first
        self.game_window.fill((192, 192, 192))
    
        # Create the grid and cache all_tiles
        self.grid, self.all_tiles = Grid.make_grid(
            self.game_window, 
            ROWS, 
            COLS, 
            TILE_SIZE, 
            N_BOMBS, 
            BUFFER,
            y_offset=STRIP_HEIGHT,
            x_offset=GRID_X_OFFSET
        )
        self.non_bomb_tiles_count = ROWS * COLS - N_BOMBS
        self.revealed_count = 0
        
        self.setup_new_game()
        return self.game_loop()
        
    def setup_new_game(self) -> None:
        # Setup a new game (for first game or after restart)
        self.grid.draw_grid()
        
        # Reset counters
        self.flagged_count = 0
        self.bomb_count = N_BOMBS
        
        # Start with no bombs placed - wait for first click
        self.bombs_placed = False
        
        # Draw the initial counter
        self.draw_counters()

    def game_loop(self) -> None:
        run = True
        
        # Draw the initial counters
        self.draw_counters()
        
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # Check if restart button was clicked
                    if self.restart_rect.collidepoint(mouse_x, mouse_y):
                        self.restart()
                        continue
                    
                    # Adjust mouse position to account for the top strip
                    adjusted_y = mouse_y - STRIP_HEIGHT
                    
                    # Only process mouse events on the grid if the game is still active
                    if self.game_status == "playing" and adjusted_y >= 0:
                        row, col = self.get_tile_at_pos(mouse_x, adjusted_y, TILE_SIZE, BUFFER, GRID_X_OFFSET)
                        if 0 <= row < ROWS and 0 <= col < COLS:
                            tile = self.grid.tiles[row][col]
                            
                            # Handle first click - place bombs
                            if not self.bombs_placed:
                                self.place_bombs_after_first_click(tile)
                                self.bombs_placed = True
                            
                            # Handle the click
                            self.handle_click(row, col, event.button, pygame.key.get_mods())
                            pygame.display.flip()  # Only flip once per frame
                            
                            # Redraw the counters
                            self.draw_counters()
                            
                            # Check for win
                            if self.revealed_count == self.non_bomb_tiles_count:
                                self.won()

        pygame.quit()
        return
        
    def restart(self) -> None:
        # Reset the game state without recursion
        self.grid, self.all_tiles = Grid.make_grid(
            self.game_window, 
            ROWS, 
            COLS, 
            TILE_SIZE, 
            N_BOMBS, 
            BUFFER,
            y_offset=STRIP_HEIGHT,
            x_offset=GRID_X_OFFSET
        )
        self.non_bomb_tiles_count = ROWS * COLS - N_BOMBS
        self.revealed_count = 0
        self.bombs_placed = False
        self.game_status = "playing"
        self.flagged_count = 0  
        self.bomb_count = N_BOMBS
        
        # Fill entire window with gray instead of just the game area with black
        # This prevents black strips from appearing
        self.game_window.fill((192, 192, 192))
        
        # Draw the grid (which will update the display)
        self.grid.draw_grid()
        
        # Draw the counters (which will update the strip area)
        self.draw_counters()

    def handle_click(self, row: int, col: int, button: int, mods=0) -> None:
        tile = self.grid.tiles[row][col]
        
        # Left click
        if button == 1:
            # Check for shift+click on revealed numbered tile
            if mods & pygame.KMOD_SHIFT and not tile.is_hidden and tile.is_numbered:
                # Only proceed if flagged neighbors equals tile value (safe to reveal)
                if tile.n_flagged_neighbours == tile.value:
                    # Reveal all non-flagged neighbors
                    bomb_revealed = False
                    for neighbor in tile.neighbours:
                        if not neighbor.is_flagged and neighbor.is_hidden:
                            # Track the previously revealed count
                            old_revealed_count = sum(1 for t in self.all_tiles if not t.is_hidden and not t.is_bomb)
                            
                            if neighbor.reveal(self.game_window):
                                bomb_revealed = True
                            
                            # Update revealed count based on newly revealed tiles
                            new_revealed_count = sum(1 for t in self.all_tiles if not t.is_hidden and not t.is_bomb)
                            self.revealed_count += (new_revealed_count - old_revealed_count)
                    
                    # Handle if a bomb was revealed
                    if bomb_revealed:
                        pygame.display.flip()
                        self.lost()
                        return
                else:
                    # If flagged neighbors don't equal tile value, do nothing special
                    pass
            # Regular left click
            else:
                # Track the previously revealed count
                old_revealed_count = sum(1 for t in self.all_tiles if not t.is_hidden and not t.is_bomb)
                
                bomb_revealed = tile.reveal(self.game_window)
                
                # Update revealed count based on newly revealed tiles
                new_revealed_count = sum(1 for t in self.all_tiles if not t.is_hidden and not t.is_bomb)
                self.revealed_count += (new_revealed_count - old_revealed_count)
                
                if bomb_revealed:
                    pygame.display.flip()
                    self.lost()
                    return
        # Right click
        elif button == 3:
            # Get the previous flag state before toggling
            was_flagged = tile.is_flagged
            
            # Flag the tile (this toggles the flag)
            tile.flag(self.game_window)
            
            # Update flag counter based on the change
            if was_flagged and not tile.is_flagged:
                self.flagged_count -= 1
            elif not was_flagged and tile.is_flagged:
                self.flagged_count += 1
                
            # Update the counter display
            self.draw_counters()

    def won(self) -> None:
        """
        Display win screen and mark all hidden tiles as flagged.
        Game will continue until manually restarted or closed.
        """
        print("Congratulations! You won!")
        
        # Set game status
        self.game_status = "won"
        
        # Mark all hidden tiles (which must be bombs) as flags
        for tile in self.all_tiles:
            if tile.is_hidden and not tile.is_flagged:
                tile.flag(self.game_window)
                self.flagged_count += 1
        
        # Update the counter display with cool face
        self.draw_counters()
        
        # Show a message on the screen
        font = pygame.font.Font('freesansbold.ttf', 64)
        win_text = font.render("YOU WIN!", True, (0, 255, 0))
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, STRIP_HEIGHT + SCREEN_HEIGHT//2))
        
        # Apply a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        
        # Draw overlay and text
        self.game_window.blit(overlay, (0, 0))
        self.game_window.blit(win_text, text_rect)
        pygame.display.flip()

    def lost(self) -> None:
        """
        Display loss screen and reveal all bombs.
        Game will continue until manually restarted or closed.
        """
        print("Game over! You hit a bomb.")
        
        # Set game status
        self.game_status = "lost"
        
        # Reveal all bombs
        for tile in self.all_tiles:
            if tile.is_bomb and tile.is_hidden:
                # Force reveal bombs without triggering cascade
                tile.is_hidden = False
                tile.draw(self.game_window)
        
        # Update the counter display with sad face
        self.draw_counters()
        
        # Show a message on the screen
        font = pygame.font.Font('freesansbold.ttf', 64)
        lose_text = font.render("GAME OVER", True, (255, 0, 0))
        text_rect = lose_text.get_rect(center=(SCREEN_WIDTH//2, STRIP_HEIGHT + SCREEN_HEIGHT//2))
        
        # Apply a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        
        # Draw overlay and text
        self.game_window.blit(overlay, (0, 0))
        self.game_window.blit(lose_text, text_rect)
        pygame.display.flip()

    def place_bombs_after_first_click(self, first_tile: Tile) -> list[Tile]:
        """
        Places bombs after the first click, ensuring that the first clicked tile
        and its neighbors don't have bombs.
        """
        # Place bombs AFTER first click, ensuring first_tile and neighbors are safe
        all_tiles = self.all_tiles
        safe_tiles = [first_tile] + first_tile.neighbours
        placeable_tiles = [tile for tile in all_tiles if tile not in safe_tiles]
        
        # Place bombs on the grid
        bomb_tiles = self.grid.place_bombs(placeable_tiles)
        
        # Set the numbers for all tiles
        self.grid.set_numbers(all_tiles, bomb_tiles)
        
        return bomb_tiles
    
    @staticmethod
    def get_tile_at_pos(mouse_x: int, mouse_y: int, tile_size: int, buffer: int, x_offset: int) -> tuple[int, int]:
        # Adjust mouse position by the offset
        adjusted_x = mouse_x - x_offset - buffer
    
        # Calculate tile coordinates
        col = adjusted_x // (tile_size + buffer)
        row = mouse_y // (tile_size + buffer)
    
        return row, col
    
    def draw_counters(self) -> None:
        """Draw the top strip with bomb counter, restart button, and flag counter."""
        # Create a gray background for the strip
        strip_bg = pygame.Surface((SCREEN_WIDTH, STRIP_HEIGHT))
        strip_bg.fill((192, 192, 192))  # Light gray like classic Minesweeper
        self.game_window.blit(strip_bg, (0, 0))
        
        # Draw border for the strip
        pygame.draw.rect(self.game_window, (128, 128, 128), (0, 0, SCREEN_WIDTH, STRIP_HEIGHT), 2)
        
        # Calculate remaining flags (bomb count - flagged count), it could go negative
        remaining_flags_count = self.bomb_count - self.flagged_count
        
        # Create bomb counter (left side)
        bomb_counter = self.counter_font.render(f"{remaining_flags_count:03d}", True, (255, 0, 0))
        bomb_rect = bomb_counter.get_rect(center=(80, STRIP_HEIGHT//2))
        
        # Create flag counter (right side)
        flag_counter = self.counter_font.render(f"{self.flagged_count:03d}", True, (0, 0, 255))
        flag_rect = flag_counter.get_rect(center=(SCREEN_WIDTH - 80, STRIP_HEIGHT//2))
        
        # Draw the counters
        self.game_window.blit(bomb_counter, bomb_rect)
        self.game_window.blit(flag_counter, flag_rect)
        
        # Draw restart button with appropriate face
        if self.game_status == "playing":
            self.game_window.blit(self.face_happy, self.restart_rect)
        elif self.game_status == "won":
            self.game_window.blit(self.face_cool, self.restart_rect)
        else:  # lost
            self.game_window.blit(self.face_sad, self.restart_rect)
    
        # Add a border around the button
        pygame.draw.rect(self.game_window, (128, 128, 128), self.restart_rect, 2)
        
        # Update only the strip region
        pygame.display.update([(0, 0, SCREEN_WIDTH, STRIP_HEIGHT)])

    def draw_restart_button(self) -> None:
        """Draw the restart button at the top center of the screen."""
        if self.game_status == "playing":
            # Draw the happy face
            self.game_window.blit(self.face_happy, self.restart_rect.topleft)
        elif self.game_status == "won":
            # Draw the cool face
            self.game_window.blit(self.face_cool, self.restart_rect.topleft)
        elif self.game_status == "lost":
            # Draw the sad face
            self.game_window.blit(self.face_sad, self.restart_rect.topleft)

        # Update the restart button area
        pygame.display.update(self.restart_rect)
