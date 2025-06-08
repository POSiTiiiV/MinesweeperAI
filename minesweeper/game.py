"""
Minesweeper Game Implementation

This module contains the main game class and constants for the Minesweeper game.
It handles game initialization, rendering, user input, and game logic.
"""
import pygame
import os
import sys
from minesweeper.tile import Tile
from minesweeper.grid import Grid
from minesweeper.api import MinesweeperAPI


#----------------------------------------------------------------------
# Game configuration constants
#----------------------------------------------------------------------

import platform

# Platform detection - updated to handle command line arguments properly
IS_MOBILE = (platform.system() in ['Android', 'iOS'] or 
            '--mobile' in sys.argv or 
            any('--mobile' in arg for arg in sys.argv))

# Desktop PC proportions - smaller window size (unchanged)
DESKTOP_ROWS, DESKTOP_COLS = 16, 25
DESKTOP_N_BOMBS = 80
DESKTOP_BUFFER = 3
DESKTOP_STRIP_HEIGHT = 80
DESKTOP_SCREEN_WIDTH = 800
DESKTOP_SCREEN_HEIGHT = 600

# Mobile phone proportions - optimized for portrait mode
MOBILE_ROWS, MOBILE_COLS = 15, 10  # Portrait ratio, more rows than columns
MOBILE_N_BOMBS = 30                # Adjusted for smaller grid
MOBILE_BUFFER = 2                  # Tighter spacing for mobile
MOBILE_STRIP_HEIGHT = 100          # Fixed: Increased from 10 to 100 for proper spacing
MOBILE_SCREEN_WIDTH = 400          # Portrait width
MOBILE_SCREEN_HEIGHT = 650         # Changed to 650 as requested

# Set active configuration based on platform
if IS_MOBILE:
    ROWS, COLS = MOBILE_ROWS, MOBILE_COLS
    N_BOMBS = MOBILE_N_BOMBS
    BUFFER = MOBILE_BUFFER
    STRIP_HEIGHT = MOBILE_STRIP_HEIGHT
    SCREEN_WIDTH = MOBILE_SCREEN_WIDTH
    SCREEN_HEIGHT = MOBILE_SCREEN_HEIGHT
else:
    ROWS, COLS = DESKTOP_ROWS, DESKTOP_COLS
    N_BOMBS = DESKTOP_N_BOMBS
    BUFFER = DESKTOP_BUFFER
    STRIP_HEIGHT = DESKTOP_STRIP_HEIGHT
    SCREEN_WIDTH = DESKTOP_SCREEN_WIDTH
    SCREEN_HEIGHT = DESKTOP_SCREEN_HEIGHT


# Modern color scheme - Black tiles with cyan/purple accents
COLORS = {
    'background': (5, 18, 21),         # Keep your dark background
    'tile_hidden': (25, 25, 30),       # Dark gray/black tiles
    'tile_revealed': (15, 15, 20),     # Even darker for revealed tiles
    'tile_border': (45, 45, 55),       # Subtle dark border
    'accent_blue': (47, 181, 208),     # Keep your cyan accent
    'light_blue': (89, 196, 217),      # Keep your light cyan
    'text_primary': (234, 248, 250),   # Keep your light text
    'text_secondary': (171, 227, 237), # Keep your secondary text
    'danger': (255, 65, 55),           # Keep red for bombs
    'success': (45, 210, 85),          # Keep green for success
    'warning': (255, 210, 10),         # Keep yellow for warning
    'secondary_accent': (144, 47, 208), # Keep your purple
    'secondary_light': (166, 89, 217),  # Keep your light purple
    'accent_purple': (208, 47, 208),    # Keep your magenta
    'light_purple': (217, 89, 217),     # Keep your light magenta
}

# Enhanced number colors using your cyan/teal and purple theme palette
NUMBER_COLORS = {
    1: (47, 181, 208),      # --primary-500 (main cyan)
    2: (45, 210, 85),       # Green (keep for contrast)
    3: (255, 65, 55),       # Red (keep for contrast)
    4: (144, 47, 208),      # --secondary-500 (purple)
    5: (255, 160, 10),      # Orange (keep for contrast)
    6: (208, 47, 208),      # --accent-500 (magenta)
    7: (130, 211, 227),     # --primary-700 (light cyan)
    8: (234, 248, 250)      # --text-950 (white)
}

# Modern design constants - adaptive for platform
if IS_MOBILE:
    TILE_BORDER_RADIUS = 6     # Larger for touch targets
    TILE_PADDING = 2           # More padding for mobile
    MIN_TILE_SIZE = 30         # Reduced from 35 to fit more tiles
    BUTTON_SIZE = 50           # Reduced from 60
    COUNTER_FONT_SIZE = 36     # Reduced from 50
    LABEL_FONT_SIZE = 18       # Reduced from 24
else:
    TILE_BORDER_RADIUS = 4     # Smaller for crisp pixels
    TILE_PADDING = 1           # Minimal padding
    MIN_TILE_SIZE = 20         # Smaller minimum for desktop
    BUTTON_SIZE = 50           # Standard button size
    COUNTER_FONT_SIZE = 40     # Standard text size
    LABEL_FONT_SIZE = 20       # Standard labels

# Asset directory
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# Grid layout calculations - platform adaptive with bounds checking
AVAILABLE_WIDTH = SCREEN_WIDTH - (BUFFER * 4)  # More margin for mobile
AVAILABLE_HEIGHT = SCREEN_HEIGHT - STRIP_HEIGHT - (BUFFER * 4)  # More margin

# Calculate tile size with better constraints
max_tile_width = AVAILABLE_WIDTH // COLS
max_tile_height = AVAILABLE_HEIGHT // ROWS
TILE_SIZE = min(max_tile_width, max_tile_height) - BUFFER

# Ensure tile size is appropriate for platform with stricter limits
if IS_MOBILE:
    TILE_SIZE = max(min(TILE_SIZE, 35), MIN_TILE_SIZE)  # Cap at 35px for mobile
else:
    TILE_SIZE = max(TILE_SIZE, MIN_TILE_SIZE)

ACTUAL_GRID_WIDTH = (TILE_SIZE * COLS) + (BUFFER * (COLS - 1))
ACTUAL_GRID_HEIGHT = (TILE_SIZE * ROWS) + (BUFFER * (ROWS - 1))

# Ensure grid fits within screen bounds
if ACTUAL_GRID_WIDTH > SCREEN_WIDTH - 20:
    TILE_SIZE = (SCREEN_WIDTH - 20 - (BUFFER * (COLS - 1))) // COLS
    ACTUAL_GRID_WIDTH = (TILE_SIZE * COLS) + (BUFFER * (COLS - 1))

if ACTUAL_GRID_HEIGHT > SCREEN_HEIGHT - STRIP_HEIGHT - 20:
    TILE_SIZE = (SCREEN_HEIGHT - STRIP_HEIGHT - 20 - (BUFFER * (ROWS - 1))) // ROWS
    ACTUAL_GRID_HEIGHT = (TILE_SIZE * ROWS) + (BUFFER * (ROWS - 1))

GRID_X_OFFSET = (SCREEN_WIDTH - ACTUAL_GRID_WIDTH) // 2
GRID_Y_OFFSET = STRIP_HEIGHT + (SCREEN_HEIGHT - STRIP_HEIGHT - ACTUAL_GRID_HEIGHT) // 2

# Font size calculations - platform adaptive
TILE_FONT_SIZE = max(TILE_SIZE // 2, 16 if IS_MOBILE else 14)

class MinesweeperGame:
    """
    Main game class for Minesweeper.
    
    This class manages the game state, handles user input, and controls
    the rendering of the game. It integrates with the Grid and Tile classes
    to implement the core Minesweeper gameplay.
    """
    
    def __init__(self):
        """
        Initialize the game with modern dark theme.
        """
        pygame.init()

        self.game_window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MinesweeperAI - Modern")
        
        # Set window background to dark
        self.game_window.fill(COLORS['background'])

        # Game state variables
        self.game_status = "playing"
        self.bomb_count = N_BOMBS
        self.flagged_count = 0
        self.grid = None
        self.all_tiles = None
        self.non_bomb_tiles_count = 0
        self.revealed_count = 0
        self.bombs_placed = False

        # Load modern assets
        self._load_assets()
        
        # Create API instance
        self.api = None

    def _load_assets(self):
        """
        Load assets with platform-adaptive sizing.
        """
        # Create modern tile font
        Tile.load_assets(
            bomb_path=os.path.join(ASSETS_DIR, 'bomb.png'),
            hidden_path=os.path.join(ASSETS_DIR, 'hidden2.png'),
            revealed_path=os.path.join(ASSETS_DIR, 'revealed.png'),
            flagged_path=os.path.join(ASSETS_DIR, 'flag1.png'),
            font=pygame.font.Font(None, max(TILE_FONT_SIZE, 16))
        )
        
        # Platform-adaptive restart button
        button_size = BUTTON_SIZE
        self.restart_rect = pygame.Rect(
            SCREEN_WIDTH//2 - button_size//2, 
            STRIP_HEIGHT//2 - button_size//2, 
            button_size, 
            button_size
        )
        
        # Platform-adaptive fonts
        self.counter_font = pygame.font.Font(None, COUNTER_FONT_SIZE)
        self.title_font = pygame.font.Font(None, LABEL_FONT_SIZE)

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
    
    def setup(self) -> None:
        """
        Set up the game with properly sized grid.
        """
        # Fill with dark background
        self.game_window.fill(COLORS['background'])

        # Create the grid with proper positioning
        self.grid, self.all_tiles = Grid.make_grid(
            self.game_window, 
            ROWS, 
            COLS, 
            TILE_SIZE, 
            N_BOMBS, 
            BUFFER,
            y_offset=GRID_Y_OFFSET,  # Use calculated Y offset
            x_offset=GRID_X_OFFSET
        )
        self.non_bomb_tiles_count = ROWS * COLS - N_BOMBS
        self.revealed_count = 0
        
        if self.api is None:
            self.api = MinesweeperAPI(self)

        self.setup_new_game()
        pygame.display.flip()
    
    def run(self) -> None:
        """
        Start and run the main game.
        
        This method initializes the grid, sets up a new game,
        and enters the main game loop.
        """
        self.setup()
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
                    
                    # Adjust mouse position to account for the grid offset
                    adjusted_x = mouse_x - GRID_X_OFFSET
                    adjusted_y = mouse_y - GRID_Y_OFFSET
                    
                    # Only process mouse events on the grid if coordinates are positive
                    if adjusted_x >= 0 and adjusted_y >= 0:
                        row, col = self.get_tile_at_pos(adjusted_x, adjusted_y, TILE_SIZE, BUFFER)
                        
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
        
        This ensures that the first clicked tile and its neighbours
        don't have bombs, providing a fair start to the player.
        
        Args:
            first_tile (Tile): The first tile clicked by the player
            
        Returns:
            list[Tile]: List of tiles containing bombs
        """
        # Place bombs AFTER first click, ensuring first_tile and neighbours are safe
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
        Handle the game-won state with modern overlay.
        """
        print("Congratulations! You won!")
        
        self.game_status = "won"
        
        # Mark all hidden tiles as flags
        for tile in self.all_tiles:
            if tile.is_hidden and not tile.is_flagged:
                self.api.flag_tile(tile.row, tile.col)
        
        self.draw_counters()
        
        # Modern win overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Modern win text
        win_font = pygame.font.Font(None, 72)
        win_text = win_font.render("VICTORY", True, COLORS['success'])
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, STRIP_HEIGHT + SCREEN_HEIGHT//2 - 20))
        
        sub_text = self.counter_font.render("Click restart to play again", True, COLORS['text_secondary'])
        sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH//2, STRIP_HEIGHT + SCREEN_HEIGHT//2 + 30))
        
        self.game_window.blit(overlay, (0, 0))
        self.game_window.blit(win_text, win_rect)
        self.game_window.blit(sub_text, sub_rect)
        pygame.display.flip()

    def lost(self) -> None:
        """
        Handle the game-lost state with modern overlay.
        """
        print("Game over! You hit a bomb.")
        
        self.game_status = "lost"
        
        # Reveal all bombs
        for tile in self.all_tiles:
            if tile.is_bomb and tile.is_hidden:
                tile.is_hidden = False
                tile.draw(self.game_window)
        
        self.draw_counters()
        
        # Modern loss overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)  
        overlay.fill((0, 0, 0, 180))
        
        # Modern loss text
        lose_font = pygame.font.Font(None, 72)
        lose_text = lose_font.render("GAME OVER", True, COLORS['danger'])
        lose_rect = lose_text.get_rect(center=(SCREEN_WIDTH//2, STRIP_HEIGHT + SCREEN_HEIGHT//2 - 20))
        
        sub_text = self.counter_font.render("Click restart to try again", True, COLORS['text_secondary'])
        sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH//2, STRIP_HEIGHT + SCREEN_HEIGHT//2 + 30))
        
        self.game_window.blit(overlay, (0, 0))
        self.game_window.blit(lose_text, lose_rect)
        self.game_window.blit(sub_text, sub_rect)
        pygame.display.flip()
    
    #----------------------------------------------------------------------
    # UI rendering methods
    #----------------------------------------------------------------------
    
    def draw_counters(self) -> None:
        """
        Draw counters with platform-adaptive sizing.
        """
        # Modern dark strip
        strip_bg = pygame.Surface((SCREEN_WIDTH, STRIP_HEIGHT))
        strip_bg.fill(COLORS['background'])
        self.game_window.blit(strip_bg, (0, 0))
        
        # Calculate remaining mines
        remaining_mines = self.bomb_count - self.flagged_count
        
        # Platform-adaptive fonts
        counter_font = pygame.font.Font(None, COUNTER_FONT_SIZE)
        label_font = pygame.font.Font(None, LABEL_FONT_SIZE)
        
        # Modern mine counter (left side)
        mine_text = f"{remaining_mines:03d}"
        mine_surface = counter_font.render(mine_text, True, COLORS['text_primary'])
        mine_label = label_font.render("MINES", True, COLORS['text_secondary'])
        
        # Platform-adaptive positioning
        x_margin = 100 if IS_MOBILE else 80
        y_offset = 8 if IS_MOBILE else 5
        label_offset = -25 if IS_MOBILE else -15
        
        mine_rect = mine_surface.get_rect(center=(x_margin, STRIP_HEIGHT//2 + y_offset))
        mine_label_rect = mine_label.get_rect(center=(x_margin, STRIP_HEIGHT//2 + label_offset))
        
        # Modern flag counter (right side)
        flag_text = f"{self.flagged_count:03d}"
        flag_surface = counter_font.render(flag_text, True, COLORS['text_primary'])
        flag_label = label_font.render("FLAGS", True, COLORS['text_secondary'])
        
        flag_rect = flag_surface.get_rect(center=(SCREEN_WIDTH - x_margin, STRIP_HEIGHT//2 + y_offset))
        flag_label_rect = flag_label.get_rect(center=(SCREEN_WIDTH - x_margin, STRIP_HEIGHT//2 + label_offset))
        
        # Draw the counters
        self.game_window.blit(mine_label, mine_label_rect)
        self.game_window.blit(mine_surface, mine_rect)
        self.game_window.blit(flag_label, flag_label_rect)
        self.game_window.blit(flag_surface, flag_rect)
        
        # Modern restart button
        self.draw_modern_restart_button()
        
        # Update strip
        pygame.display.update([(0, 0, SCREEN_WIDTH, STRIP_HEIGHT)])

    def draw_modern_restart_button(self) -> None:
        """
        Draw restart button with platform-adaptive sizing.
        """
        # Platform-adaptive button radius
        button_radius = 30 if IS_MOBILE else 20
        center = (self.restart_rect.centerx, self.restart_rect.centery)
        
        if self.game_status == "playing":
            pygame.draw.circle(self.game_window, COLORS['tile_hidden'], center, button_radius)
            pygame.draw.circle(self.game_window, COLORS['accent_blue'], center, button_radius, 2)
            
            # Restart symbol (larger for mobile)
            arc_size = 16 if IS_MOBILE else 10
            line_width = 4 if IS_MOBILE else 3
            
            pygame.draw.arc(self.game_window, COLORS['text_primary'], 
                           (center[0]-arc_size, center[1]-arc_size, arc_size*2, arc_size*2), 0.5, 5.5, line_width)
            
            # Arrow tip (larger for mobile)
            arrow_size = 8 if IS_MOBILE else 5
            pygame.draw.polygon(self.game_window, COLORS['text_primary'], [
                (center[0]+arc_size-2, center[1]-arc_size+2),
                (center[0]+arc_size+arrow_size-2, center[1]-arrow_size),
                (center[0]+arrow_size, center[1]-arrow_size)
            ])
        elif self.game_status == "won":
            pygame.draw.circle(self.game_window, COLORS['success'], center, button_radius)
            pygame.draw.circle(self.game_window, COLORS['light_blue'], center, button_radius, 2)
            
            # Checkmark (larger for mobile)
            check_size = 8 if IS_MOBILE else 6
            line_width = 4 if IS_MOBILE else 3
            check_points = [
                (center[0]-check_size, center[1]),
                (center[0]-2, center[1]+check_size//2),
                (center[0]+check_size, center[1]-check_size//2)
            ]
            pygame.draw.lines(self.game_window, COLORS['text_primary'], False, check_points, line_width)
        else:  # lost
            pygame.draw.circle(self.game_window, COLORS['danger'], center, button_radius)
            pygame.draw.circle(self.game_window, COLORS['secondary_light'], center, button_radius, 2)
            
            # X symbol (larger for mobile)
            x_size = 8 if IS_MOBILE else 6
            line_width = 4 if IS_MOBILE else 3
            pygame.draw.line(self.game_window, COLORS['text_primary'], 
                           (center[0]-x_size, center[1]-x_size), (center[0]+x_size, center[1]+x_size), line_width)
            pygame.draw.line(self.game_window, COLORS['text_primary'], 
                           (center[0]+x_size, center[1]-x_size), (center[0]-x_size, center[1]+x_size), line_width)

    #----------------------------------------------------------------------
    # Utility methods
    #----------------------------------------------------------------------
    
    @staticmethod
    def get_tile_at_pos(mouse_x: int, mouse_y: int, tile_size: int, buffer: int) -> tuple[int, int]:
        """
        Convert mouse coordinates to grid coordinates.
        
        Args:
            mouse_x (int): Mouse x-coordinate (already adjusted for grid offset)
            mouse_y (int): Mouse y-coordinate (already adjusted for grid offset)
            tile_size (int): Size of each tile in pixels
            buffer (int): Space between tiles in pixels
            
        Returns:
            tuple[int, int]: (row, col) coordinates in the grid
        """
        # Calculate tile coordinates with buffer consideration
        col = mouse_x // (tile_size + buffer)
        row = mouse_y // (tile_size + buffer)
    
        return row, col
