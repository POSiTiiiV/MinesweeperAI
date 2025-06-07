import pygame
from random import shuffle
from minesweeper.tile import Tile


class Grid:
    """
    Grid class for Minesweeper game.

    This class manages the grid of tiles for a Minesweeper game, handling the creation,
    initialization, bomb placement, and rendering of the game board.
    The Grid class contains methods for:
    - Creating and initializing the grid
    - Connecting neighbouring tiles
    - Placing bombs randomly
    - Setting numeric values for tiles based on adjacent bombs
    - Drawing the grid to the game window
    The grid system uses a 2D array of Tile objects, with each tile representing
    a cell in the Minesweeper board that can contain a bomb, a number, or be empty.
    """
    def __init__(self, rows: int, cols: int, tile_size: int, tiles: list[list[Tile]],
                 game_window: pygame.Surface, n_bombs: int, buffer: int, y_offset: int = 0):
        """
        Initialize a Grid object representing the Minesweeper game grid.

        Args:
            rows (int): Number of rows in the grid.
            cols (int): Number of columns in the grid.
            tile_size (int): Size of each tile in pixels.
            tiles (list[list[Tile]]): 2D list containing Tile objects for the grid.
            game_window (pygame.Surface): Pygame surface to render the grid on.
            n_bombs (int): Number of bombs in the grid.
            buffer (int): Padding/margin between tiles in pixels.
            y_offset (int, optional): Vertical offset for rendering the grid, used for placing
                                     the grid below UI elements like the top strip. Defaults to 0.
        """
        self.game_window = game_window
        self.tiles = tiles
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size
        self.n_bombs = n_bombs
        self.buffer = buffer
        self.y_offset = y_offset

    #----------------------------------------------------------------------
    # Grid creation and initialization methods
    #----------------------------------------------------------------------

    @classmethod
    def make_grid(cls, game_window: pygame.Surface, rows: int, cols: int, tile_size: int, 
                  n_bombs: int, buffer: int, y_offset=0, x_offset=0) -> tuple['Grid', list[Tile]]:
        """
        Factory method to create a new grid instance with initialized tiles.
        This handles the grid creation, tile positioning, and neighbour connections.
        
        Args:
            game_window (pygame.Surface): Pygame surface where the grid will be drawn
            rows (int): Number of rows in the grid
            cols (int): Number of columns in the grid
            tile_size (int): Size of each tile in pixels
            n_bombs (int): Number of bombs to place on the grid
            buffer (int): Space between tiles in pixels for visual separation
            y_offset (int, optional): Vertical offset from the top of the window,
                                     used for placing the grid below UI elements. Defaults to 0.
            x_offset (int, optional): Horizontal offset from the left of the window,
                                     used for centering the grid. Defaults to 0.
            
        Returns:
            tuple: (Grid object, list of all tiles) - The initialized grid and a flat list of all tiles
        """
        # Create a grid of tiles
        tiles = [[None for _ in range(cols)] for _ in range(rows)]
        all_tiles = []
        
        for r in range(rows):
            for c in range(cols):
                # Add buffer space between tiles and account for offsets
                pos_x = (c * (tile_size + buffer)) + buffer + x_offset
                pos_y = (r * (tile_size + buffer)) + buffer + y_offset
                
                # Create tile with calculated position
                tile = Tile(None, (pos_x, pos_y), (r, c), tile_size)
                tiles[r][c] = tile
                all_tiles.append(tile)
        
        grid_obj = cls(rows, cols, tile_size, tiles, game_window, n_bombs, buffer, y_offset)
        grid_obj.connect_neighbours()
        
        return grid_obj, all_tiles

    def connect_neighbours(self) -> None:
        """
        Connect each tile with its neighbouring tiles.
        
        This method:
        1. Defines all 8 possible directions (N, NE, E, SE, S, SW, W, NW)
        2. For each tile, finds valid neighbours in those directions
        3. Adds references to neighbouring tiles in each tile's neighbours list
        4. Initializes the hidden_neighbours set for tracking unrevealed neighbours
        
        This establishes the connections needed for revealing adjacent tiles
        and calculating tile values based on neighbouring bombs.
        """
        directions = [
            (-1, -1), # north-west
            (-1, 0),  # north
            (-1, 1),  # north-east
            (0, 1),   # east
            (1, 1),   # south-east
            (1, 0),   # south
            (1, -1),  # south-west
            (0, -1)   # west
        ]
        for i in range(self.rows):
            for j in range(self.cols):
                for d_i, d_j in directions:
                    ni, nj = i + d_i, j + d_j
                    if 0 <= ni < self.rows and 0 <= nj < self.cols:
                        self.tiles[i][j].neighbours.append(self.tiles[ni][nj])
                        self.tiles[i][j].hidden_neighbours.add(self.tiles[ni][nj])

    #----------------------------------------------------------------------
    # Game mechanics methods
    #----------------------------------------------------------------------

    def place_bombs(self, all_tiles: list) -> list:
        """
        Randomly place bombs on the grid.
        
        Args:
            all_tiles (list): A flat list of all tiles in the grid
            
        Returns:
            list: List of tiles that have bombs placed on them
            
        This method:
        1. Shuffles the list of tiles to randomize bomb placement
        2. Takes the first n_bombs tiles and marks them as bombs
        3. Returns the list of bomb tiles for further processing
        """
        shuffle(all_tiles)
        bomb_tiles = all_tiles[:self.n_bombs]
        for tile in bomb_tiles:
            tile.is_bomb = True
        
        return bomb_tiles
    
    def set_numbers(self, all_tiles: list, bomb_tiles: list) -> None:
        """
        Set the numeric values for all non-bomb tiles based on adjacent bombs.
        
        Args:
            all_tiles (list): A flat list of all tiles in the grid
            bomb_tiles (list): List of tiles with bombs
            
        This method:
        1. Sets all non-bomb tiles to have value 0 initially
        2. For each bomb, increments the value of all its non-bomb neighbours
        3. Ensures bomb tiles have a value of None
        
        After this method runs, each non-bomb tile will have a value equal to
        the number of adjacent bomb tiles (0-8).
        """
        # First, set all non-bomb tiles to 0
        for tile in all_tiles:
            if tile not in bomb_tiles:
                tile.value = 0
        
        # Then increment neighbours of bomb tiles
        for bomb in bomb_tiles:
            bomb.value = None  # Ensure bombs have None value
            for neighbour in bomb.neighbours:
                if neighbour not in bomb_tiles:
                    neighbour.value += 1

    #----------------------------------------------------------------------
    # Rendering methods
    #----------------------------------------------------------------------

    def draw_grid(self) -> None:
        """
        Draw the grid with modern flat design and minimal spacing.
        """
        from minesweeper.game import COLORS
        
        # Fill background with modern dark color
        pygame.draw.rect(
            self.game_window,
            COLORS['background'],
            (0, self.y_offset, self.game_window.get_width(), 
             self.game_window.get_height() - self.y_offset)
        )
        
        # Draw all tiles with minimal spacing
        for row in self.tiles:
            for tile in row:
                tile.draw(self.game_window)
        
        # Update the display
        pygame.display.update([(0, self.y_offset, 
                             self.game_window.get_width(), 
                             self.game_window.get_height() - self.y_offset)])

    #----------------------------------------------------------------------
    # Debug methods
    #----------------------------------------------------------------------

    def print_grid(self) -> None:
        """
        Print a text representation of the grid to the console.
        
        This is a debugging method that prints the value of each tile
        in a grid format, making it easier to visualize the grid state
        during development and testing.
        """
        for i in range(self.rows):
            for j in range(self.cols):
                print(self.tiles[i][j].value, end=' ')
            print('\n')
        print('\n')
