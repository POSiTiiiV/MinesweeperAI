"""
Minesweeper Game Implementation

This module contains the main game class and constants for the Minesweeper game.
It handles game initialization, rendering, user input, and game logic.
"""
import pygame
import os
import time
from minesweeper.tile import Tile
from minesweeper.grid import Grid
from minesweeper.api import MinesweeperAPI

#----------------------------------------------------------------------
# Game configuration constants
#----------------------------------------------------------------------

ROWS, COLS = 8, 8
N_BOMBS = 10
BUFFER = 4  # margin/gap between tiles
STRIP_HEIGHT = 50  # Height of the top strip
SCREEN_WIDTH = 600  # Fixed screen width
SCREEN_HEIGHT = 600 + STRIP_HEIGHT  # Screen height with strip

# Asset directory
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# Grid layout calculations
AVAILABLE_WIDTH = SCREEN_WIDTH - (BUFFER * (COLS + 1))
AVAILABLE_HEIGHT = SCREEN_HEIGHT - STRIP_HEIGHT - (BUFFER * (ROWS + 1))
TILE_SIZE = min(AVAILABLE_WIDTH // COLS, AVAILABLE_HEIGHT // ROWS)
ACTUAL_GRID_WIDTH = (TILE_SIZE * COLS) + (BUFFER * (COLS + 1))
ACTUAL_GRID_HEIGHT = (TILE_SIZE * ROWS) + (BUFFER * (ROWS + 1))
GRID_X_OFFSET = (SCREEN_WIDTH - ACTUAL_GRID_WIDTH) // 2

class MinesweeperGame:
    """
    Main game class for Minesweeper.
    
    This class manages the game state, handles user input, and controls
    the rendering of the game. It integrates with the Grid and Tile classes
    to implement the core Minesweeper gameplay.
    """
    
    def __init__(self):
        """
        Initialize the game, setting up the window, assets, and initial game state.
        
        This creates the game window, loads all required assets, and prepares
        the game for the first run.
        """
        pygame.init()

        self.game_window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MinesweeperAI")

        # Game state variables
        self.game_status = "playing"  # Can be "playing", "won", or "lost"
        self.bomb_count = N_BOMBS
        self.flagged_count = 0
        self.grid = None
        self.all_tiles = None
        self.non_bomb_tiles_count = 0
        self.revealed_count = 0
        self.bombs_placed = False

        # Load tile assets
        self._load_assets()
        
        # Create API instance
        self.api = MinesweeperAPI(self)
    
    #----------------------------------------------------------------------
    # Initialization methods
    #----------------------------------------------------------------------
    
    def _load_assets(self):
        """
        Load all game assets including tile images, fonts and emoji faces.
        
        This is a private helper method called during initialization.
        """
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
    
    def setup_new_game(self) -> None:
        """
        Set up a new game with fresh state.
        
        This resets the game state for a new game, whether it's the
        first game or after a restart.
        """
        # Setup a new game (for first game or after restart)
        self.grid.draw_grid()
        
        # Reset counters
        self.flagged_count = 0
        self.bomb_count = N_BOMBS
        
        # Start with no bombs placed - wait for first click
        self.bombs_placed = False
        
        # Draw the initial counter
        self.draw_counters()
    
    #----------------------------------------------------------------------
    # Main game flow methods
    #----------------------------------------------------------------------
    
    def run(self) -> None:
        """
        Start and run the main game.
        
        This method initializes the grid, sets up a new game,
        and enters the main game loop.
        
        Returns:
            None
        """
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
    
    def game_loop(self) -> None:
        """
        Run the main game loop, handling events and updates.
        
        This processes all user inputs, updates game state,
        and handles rendering until the game is closed.
        """
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
                        self.api.restart_game()
                        continue
                    
                    # Adjust mouse position to account for the top strip
                    adjusted_y = mouse_y - STRIP_HEIGHT
                    
                    # Only process mouse events on the grid if adjusted_y is positive
                    if adjusted_y >= 0:
                        row, col = self.get_tile_at_pos(mouse_x, adjusted_y, TILE_SIZE, BUFFER, GRID_X_OFFSET)
                        
                        if 0 <= row < ROWS and 0 <= col < COLS:
                            # Handle clicks through the API
                            if event.button == 1:  # Left click
                                mods = pygame.key.get_mods()
                                if mods & pygame.KMOD_SHIFT:
                                    # Chord (shift+click)
                                    self.api.chord_tile(row, col)
                                else:
                                    # Regular reveal
                                    self.api.reveal_tile(row, col)
                            elif event.button == 3:  # Right click
                                self.api.flag_tile(row, col)
                                
                        # Update the display
                        pygame.display.flip()
                        
                        # Redraw the counters
                        self.draw_counters()

        pygame.quit()
        return
    
    def restart(self) -> None:
        """
        Restart the game to a fresh state.
        
        This creates a new grid, resets all game variables,
        and prepares for a new game.
        """
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
    
    #----------------------------------------------------------------------
    # Game mechanics methods
    #----------------------------------------------------------------------
    
    def place_bombs_after_first_click(self, first_tile: Tile) -> list[Tile]:
        """
        Place bombs on the grid after the first click.
        
        This ensures that the first clicked tile and its neighbors
        don't have bombs, providing a fair start to the player.
        
        Args:
            first_tile (Tile): The first tile clicked by the player
            
        Returns:
            list[Tile]: List of tiles containing bombs
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
    
    #----------------------------------------------------------------------
    # Game state transition methods
    #----------------------------------------------------------------------
    
    def won(self) -> None:
        """
        Handle the game-won state.
        
        Updates the game status, flags all remaining bombs,
        and displays a win message overlay.
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
        Handle the game-lost state.
        
        Updates the game status, reveals all bombs,
        and displays a game over message overlay.
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
    
    #----------------------------------------------------------------------
    # UI rendering methods
    #----------------------------------------------------------------------
    
    def draw_counters(self) -> None:
        """
        Draw the top strip with bomb counter, restart button, and flag counter.
        
        This updates the UI elements in the top strip of the game window.
        """
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
        """
        Draw the restart button with the appropriate face.
        
        The face changes based on game status (happy, cool, or sad).
        """
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
    
    #----------------------------------------------------------------------
    # Utility methods
    #----------------------------------------------------------------------
    
    @staticmethod
    def get_tile_at_pos(mouse_x: int, mouse_y: int, tile_size: int, buffer: int, x_offset: int) -> tuple[int, int]:
        """
        Convert mouse coordinates to grid coordinates.
        
        Args:
            mouse_x (int): Mouse x-coordinate
            mouse_y (int): Mouse y-coordinate (already adjusted for strip height)
            tile_size (int): Size of each tile in pixels
            buffer (int): Space between tiles in pixels
            x_offset (int): Horizontal offset of the grid
            
        Returns:
            tuple[int, int]: (row, col) coordinates in the grid
        """
        # Adjust mouse position by the offset
        adjusted_x = mouse_x - x_offset - buffer
    
        # Calculate tile coordinates
        col = adjusted_x // (tile_size + buffer)
        row = mouse_y // (tile_size + buffer)
    
        return row, col
