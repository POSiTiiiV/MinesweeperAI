import pygame
from typing import Callable


class Tile:
    """
    Tile class for Minesweeper game.

    This class represents a single tile in the Minesweeper game grid.
    Each tile can be a bomb or a numbered tile indicating adjacent bombs.
    Tiles manage their own state (hidden, revealed, flagged) and handle
    relationships with neighbouring tiles.
    """
    # Class variables for shared assets
    bomb_img = None
    hidden_img = None
    revealed_img = None
    flagged_img = None
    font = None

    #----------------------------------------------------------------------
    # Initialization and asset loading
    #----------------------------------------------------------------------

    @classmethod
    def load_assets(cls, bomb_path, hidden_path, revealed_path,
                     flagged_path, font):
        """
        Load all image assets and font for the tiles.
        This is a class method that loads shared assets once for all tile instances.
        
        Args:
            bomb_path (str): Path to the bomb image
            hidden_path (str): Path to the hidden tile image
            revealed_path (str): Path to the revealed tile image
            flagged_path (str): Path to the flagged tile image
            font (pygame.font.Font): Pygame font for rendering numbers
        """
        cls.bomb_img = pygame.image.load(bomb_path).convert()
        cls.hidden_img = pygame.image.load(hidden_path).convert()
        cls.revealed_img = pygame.image.load(revealed_path).convert()
        cls.flagged_img = pygame.image.load(flagged_path).convert()
        cls.font = font
    
    def __init__(self, value: int | None, pos: list[int, int], matrix_pos: list[int, int], tile_size: int):
        """
        Initialize a tile with its properties.
        
        Args:
            value (int or None): The number value of the tile (number of adjacent bombs),
                               or None for bomb tiles
            pos (tuple): Screen position (x, y) in pixels
            matrix_pos (tuple): Position (row, col) in the game grid
            tile_size (int): Size of the tile in pixels
        """
        self.value = value
        self.is_hidden = True
        self.is_flagged = False
        self.is_bomb = False
        self.pos_x, self.pos_y = pos
        self.row, self.col = matrix_pos
        self.tile_size = tile_size
        self.neighbours: list[Tile] = []          # List of all adjacent tiles
        self.hidden_neighbours: set[Tile] = set()  # Set of adjacent tiles that are still hidden
        self.flagged_neighbours: set[Tile] = set()  # Set of adjacent tiles that are flagged

    #----------------------------------------------------------------------
    # Property accessors
    #----------------------------------------------------------------------

    @property
    def is_numbered(self) -> bool:
        """
        Check if this tile has a number (1-8).
        
        A numbered tile is a revealed non-bomb tile with a value greater than 0,
        indicating it has at least one bomb in an adjacent tile.
        
        Returns:
            bool: True if this tile has a visible number, False otherwise
        """
        return not self.is_hidden and not self.is_bomb and self.value > 0
    
    @property
    def is_satisfied(self) -> bool:
        """
        Check if the number of flagged neighbours equals this tile's value.
        
        A tile is "satisfied" when the player has correctly flagged exactly
        as many neighbours as the tile's number indicates. This property is
        used for chord operations and solving algorithms.
        
        Returns:
            bool: True if the number of flagged neighbours equals this tile's value
        """
        return self.value == self.n_flagged_neighbours
    
    @property
    def is_satisfiable(self) -> bool:
        """
        Check if all remaining hidden neighbours should be flagged to satisfy this tile.
        
        A tile is "satisfiable" when the number of hidden neighbours plus the
        number of flagged neighbours equals the tile's value. When this is true,
        all remaining hidden neighbours must be bombs.
        
        Returns:
            bool: True if all hidden neighbours should be flagged, False otherwise
        """
        return self.value == self.n_hidden_neighbours + self.n_flagged_neighbours
    
    @property
    def n_neighbours(self) -> int:
        """
        Get the total number of neighbouring tiles.
        
        Returns:
            int: Number of tiles adjacent to this one (usually 8, but can be less at edges)
        """
        return len(self.neighbours)
    
    @property
    def n_hidden_neighbours(self) -> int:
        """
        Get the number of neighbouring tiles that are still hidden.
        
        This property is useful for solving algorithms to determine which
        tiles need further inspection.
        
        Returns:
            int: Number of adjacent tiles that are still hidden
        """
        return len(self.hidden_neighbours)
    
    @property
    def n_flagged_neighbours(self) -> int:
        """
        Get the number of neighbouring tiles that are flagged as bombs.
        
        This property is used for chord operations and solving algorithms
        to determine if a numbered tile's bomb requirement is satisfied.
        
        Returns:
            int: Number of adjacent tiles that are flagged
        """
        return len(self.flagged_neighbours)

    #----------------------------------------------------------------------
    # Visual rendering methods
    #----------------------------------------------------------------------
    
    def get_color(self) -> tuple[int, int, int]:
        """
        Get the RGB color tuple for the tile's number based on its value.
        Modern minimalist color scheme.
        
        Returns:
            tuple: RGB color values (0-255) for the number's color
        """
        from minesweeper.game import NUMBER_COLORS
        return NUMBER_COLORS.get(self.value, (255, 255, 255))

    def draw(self, game_window: pygame.Surface) -> None:
        """
        Render the tile with your custom cyan/teal and purple theme colors.
        
        Args:
            game_window (pygame.Surface): The pygame surface on which to draw the tile
        """
        from minesweeper.game import COLORS, TILE_BORDER_RADIUS
        
        # Create crisp tile rectangle
        tile_rect = pygame.Rect(
            self.pos_x, 
            self.pos_y, 
            self.tile_size, 
            self.tile_size
        )
        
        if self.is_hidden:
            if self.is_flagged:
                # Flagged tile - using your beautiful cyan accent
                pygame.draw.rect(game_window, COLORS['accent_blue'], tile_rect, border_radius=TILE_BORDER_RADIUS)
                pygame.draw.rect(game_window, COLORS['light_blue'], tile_rect, 2, border_radius=TILE_BORDER_RADIUS)
                
                # Draw crisp flag symbol
                center_x = self.pos_x + self.tile_size // 2
                center_y = self.pos_y + self.tile_size // 2
                flag_size = self.tile_size // 3
                
                # Flag pole
                pygame.draw.line(game_window, COLORS['text_primary'], 
                               (center_x - flag_size//3, center_y - flag_size//2),
                               (center_x - flag_size//3, center_y + flag_size//2), 3)
                
                # Flag triangle using purple accent
                flag_points = [
                    (center_x - flag_size//3, center_y - flag_size//2),
                    (center_x + flag_size//3, center_y - flag_size//4),
                    (center_x - flag_size//3, center_y)
                ]
                pygame.draw.polygon(game_window, COLORS['secondary_accent'], flag_points)
            else:
                # Hidden tile - using your teal background colors
                pygame.draw.rect(game_window, COLORS['tile_hidden'], tile_rect, border_radius=TILE_BORDER_RADIUS)
                pygame.draw.rect(game_window, COLORS['tile_border'], tile_rect, 1, border_radius=TILE_BORDER_RADIUS)
        else:
            if self.is_bomb:
                # Bomb tile - red with your theme background
                pygame.draw.rect(game_window, COLORS['danger'], tile_rect, border_radius=TILE_BORDER_RADIUS)
                
                # Draw enhanced bomb icon
                center_x = self.pos_x + self.tile_size // 2
                center_y = self.pos_y + self.tile_size // 2
                bomb_radius = max(self.tile_size // 5, 4)
                
                # Main bomb body using your dark background
                pygame.draw.circle(game_window, COLORS['background'], (center_x, center_y), bomb_radius)
                pygame.draw.circle(game_window, COLORS['text_primary'], (center_x, center_y), bomb_radius, 2)
                
                # Bomb spikes for detail
                spike_length = bomb_radius // 2
                for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                    import math
                    end_x = center_x + spike_length * math.cos(math.radians(angle))
                    end_y = center_y + spike_length * math.sin(math.radians(angle))
                    pygame.draw.line(game_window, COLORS['text_primary'], 
                                   (center_x, center_y), (int(end_x), int(end_y)), 1)
            else:
                # Revealed tile - using your theme colors
                pygame.draw.rect(game_window, COLORS['tile_revealed'], tile_rect, border_radius=TILE_BORDER_RADIUS)
                pygame.draw.rect(game_window, COLORS['tile_border'], tile_rect, 1, border_radius=TILE_BORDER_RADIUS)
                
                # Add crisp number rendering
                if self.is_numbered:
                    # Use optimized font rendering for clarity
                    font_size = max(self.tile_size // 2, 16)
                    number_font = pygame.font.Font(None, font_size)
                    
                    # Render with anti-aliasing for crisp text
                    text_surface = number_font.render(str(self.value), True, self.get_color())
                    text_rect = text_surface.get_rect(center=(
                        self.pos_x + self.tile_size // 2,
                        self.pos_y + self.tile_size // 2
                    ))
                    game_window.blit(text_surface, text_rect)

    #----------------------------------------------------------------------
    # Game mechanics - primary interaction methods
    #----------------------------------------------------------------------

    def reveal(self, game_window: pygame.Surface, 
               reveal_count_callback: Callable[['Tile'], None], 
               neighbour_update_callback: Callable[['Tile'], None]) -> bool:
        """
        Reveal this tile and potentially connected tiles with cascade effect.
        
        This method:
        1. Reveals the current tile
        2. If it's a 0-value tile, recursively reveals all adjacent tiles
        3. Updates neighbour relationships through on_reveal()
        4. Counts revealed tiles through the callback function
        
        Args:
            game_window (pygame.Surface): The pygame surface to draw on
            count_callback (Callable[['Tile'], None]): Function to call when a non-bomb tile is revealed,
                                                        used to track total revealed tiles for win condition
            neighbour_update_callback (Callable[['Tile'], None]): Function to call for each neighbour that is affected by this change
            
        Returns:
            bool: True if a bomb was revealed (game over), False otherwise
        """
        if not self.is_hidden:
            return False   # Already revealed

        queue = [self]
        visited = set()
        bomb_revealed = False

        while queue:
            tile = queue.pop(0)
            if tile in visited:
                continue
            if tile.is_bomb:
                bomb_revealed = True
            visited.add(tile)
            
            # Only count the tile as revealed if it wasn't hidden before
            if tile.is_hidden:
                tile.is_hidden = False
                # Call the callback to increment the counter
                if not tile.is_bomb:
                    reveal_count_callback(tile)  # Pass the tile to the callback
                    
            tile.on_reveal(neighbour_update_callback)
            tile.draw(game_window)

            if tile.value == 0:
                for neighbour in tile.neighbours:
                    if neighbour.is_hidden and neighbour not in visited:
                        queue.append(neighbour)
        
        return bomb_revealed
    
    @staticmethod
    def reveal_batch(tiles: list['Tile'], game_window: pygame.Surface, 
                reveal_count_callback: Callable[['Tile'], None], 
                neighbour_update_callback: Callable[['Tile'], None]) -> tuple[bool, tuple[int, int]]:
        """
        Reveal a batch of tiles efficiently using a single BFS queue.
        
        Args:
            tiles (list['Tile']): List of tiles to reveal
            game_window (pygame.Surface): The pygame surface to draw on
            reveal_count_callback (Callable[['Tile'], None]): Function to call when a tile is revealed
            neighbour_update_callback (Callable[['Tile'], None]): Function to call for affected neighbours
            
        Returns:
            tuple[bool, tuple[int, int]]: (bomb_revealed, bomb_position)
        """
        queue = list(tiles)
        visited = set()
        bomb_revealed = False
        bomb_position = None

        while queue:
            tile = queue.pop(0)
            if tile in visited or not tile.is_hidden:
                continue
                
            visited.add(tile)
            
            if tile.is_bomb:
                bomb_revealed = True
                bomb_position = (tile.row, tile.col)
                # Don't return immediately - continue revealing to show all bombs
            
            # Reveal the tile
            tile.is_hidden = False
            if not tile.is_bomb:
                reveal_count_callback(tile)
            
            tile.on_reveal(neighbour_update_callback)
            tile.draw(game_window)
            
            # Add neighbours to queue if this is an empty tile
            if tile.value == 0:
                for neighbour in tile.neighbours:
                    if neighbour.is_hidden and neighbour not in visited and not neighbour.is_flagged:
                        queue.append(neighbour)
        
        return bomb_revealed, bomb_position

    def flag(self, game_window: pygame.Surface, flag_callback: Callable[['Tile', bool], None], neighbour_update_callback: Callable[['Tile'], None]) -> None:
        """
        Toggle the flag state of this tile.
        
        This method:
        1. Toggles the is_flagged property
        2. Updates neighbour relationships through on_flag() or remove_flag()
        3. Redraws the tile to show the new state
        
        Args:
            game_window (pygame.Surface): The pygame surface to draw on
            flag_callback (Callable[['Tile', bool], None]): Function to call to track flag changes 
                                                            takes a Tile object and a boolean (was_flagged)
            neighbour_update_callback (Callable[['Tile'], None]): Function to call for each neighbour
                                                                  that is affected by this change
        """
        was_flagged = self.is_flagged
    
        if self.is_flagged:
            self.is_flagged = False
            self.remove_flag(neighbour_update_callback)
        else:
            self.is_flagged = True
            self.on_flag(neighbour_update_callback)
            
        flag_callback(self, was_flagged)
            
        self.draw(game_window)

    #----------------------------------------------------------------------
    # Neighbor relationship management methods
    #----------------------------------------------------------------------

    def on_reveal(self, neighbour_update_callback: Callable[['Tile'], None]) -> None:
        """
        Update neighbour tiles when this tile is revealed.
        
        This method removes this tile from all non zero neighbours' hidden_neighbours sets,
        maintaining accurate tracking of hidden/revealed relationships for
        solving algorithms and cascade reveals.
        
        Args:
            neighbour_update_callback (Callable[['Tile'], None]): Function to call for each neighbour that 
                                                                  is affected by this change
        """
        for neighbour in self.neighbours:
            if neighbour.value != 0 and self in neighbour.hidden_neighbours:
                neighbour.hidden_neighbours.remove(self)
                neighbour_update_callback(neighbour)

    def on_flag(self, neighbour_update_callback: Callable[['Tile'], None]) -> None:
        """
        Update neighbour tiles when this tile is flagged.
        
        This method adds this tile to all non zero neighbours' flagged_neighbours sets and remove it
        from all neighbours' hidden_neighbours set, maintaining accurate tracking of flagged 
        tiles for chord operations and solving algorithms.

        Args:
            neighbour_update_callback (Callable[['Tile'], None]): Function to call for each neighbour
                                                                  that is affected by this change
        """
        for neighbour in self.neighbours:
            updated = False
            if neighbour.value == 0:
                continue
            if self not in neighbour.flagged_neighbours:
                neighbour.flagged_neighbours.add(self)
                updated = True
            if self in neighbour.hidden_neighbours:
                neighbour.hidden_neighbours.remove(self)
                updated = True
            if updated:
                neighbour_update_callback(neighbour)

    def remove_flag(self, neighbour_update_callback: Callable[['Tile'], None]) -> None:
        """
        Update neighbour tiles when this tile's flag is removed.
        
        This method removes this tile from all non zero neighbours' flagged_neighbours sets and add it
        from all neighbours' hidden_neighbours set, maintaining accurate tracking of flagged 
        tiles for chord operations and solving algorithms.

        Args:
            neighbour_update_callback (Callable[['Tile'], None]): Function to call for each neighbour
                                                                  that is affected by this change
        """
        for neighbour in self.neighbours:
            updated = False
            if neighbour.value == 0:
                continue
            if self in neighbour.flagged_neighbours:
                neighbour.flagged_neighbours.remove(self)
                updated = True
            if self not in neighbour.flagged_neighbours:
                neighbour.flagged_neighbours.add(self)
                updated = True
            if updated:
                neighbour_update_callback(neighbour)
