import pygame


class Tile:
    """
    Tile class for Minesweeper game.

    This class represents a single tile in the Minesweeper game grid.
    Each tile can be a bomb or a numbered tile indicating adjacent bombs.
    Tiles manage their own state (hidden, revealed, flagged) and handle
    relationships with neighboring tiles.
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
    
    def __init__(self, value, pos, matrix_pos, tile_size):
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
        self.neighbours = []          # List of all adjacent tiles
        self.hidden_neighbours = set() # Set of adjacent tiles that are still hidden
        self.flagged_neighbours = set() # Set of adjacent tiles that are flagged

    #----------------------------------------------------------------------
    # Property accessors
    #----------------------------------------------------------------------

    @property
    def is_numbered(self):
        """
        Check if this tile has a number (1-8).
        
        A numbered tile is a revealed non-bomb tile with a value greater than 0,
        indicating it has at least one bomb in an adjacent tile.
        
        Returns:
            bool: True if this tile has a visible number, False otherwise
        """
        return not self.is_hidden and not self.is_bomb and self.value > 0
    
    @property
    def is_satisfied(self):
        """
        Check if the number of flagged neighbors equals this tile's value.
        
        A tile is "satisfied" when the player has correctly flagged exactly
        as many neighbors as the tile's number indicates. This property is
        used for chord operations and solving algorithms.
        
        Returns:
            bool: True if the number of flagged neighbors equals this tile's value
        """
        return self.value == self.n_flagged_neighbours
    
    @property
    def is_satisfiable(self):
        """
        Check if all remaining hidden neighbors should be flagged to satisfy this tile.
        
        A tile is "satisfiable" when the number of hidden neighbors plus the
        number of flagged neighbors equals the tile's value. When this is true,
        all remaining hidden neighbors must be bombs.
        
        Returns:
            bool: True if all hidden neighbors should be flagged, False otherwise
        """
        return self.value == self.n_hidden_neighbours + self.n_flagged_neighbours
    
    @property
    def n_neighbours(self):
        """
        Get the total number of neighboring tiles.
        
        Returns:
            int: Number of tiles adjacent to this one (usually 8, but can be less at edges)
        """
        return len(self.neighbours)
    
    @property
    def n_hidden_neighbours(self):
        """
        Get the number of neighboring tiles that are still hidden.
        
        This property is useful for solving algorithms to determine which
        tiles need further inspection.
        
        Returns:
            int: Number of adjacent tiles that are still hidden
        """
        return len(self.hidden_neighbours)
    
    @property
    def n_flagged_neighbours(self):
        """
        Get the number of neighboring tiles that are flagged as bombs.
        
        This property is used for chord operations and solving algorithms
        to determine if a numbered tile's bomb requirement is satisfied.
        
        Returns:
            int: Number of adjacent tiles that are flagged
        """
        return len(self.flagged_neighbours)

    #----------------------------------------------------------------------
    # Visual rendering methods
    #----------------------------------------------------------------------
    
    def get_color(self):
        """
        Get the RGB color tuple for the tile's number based on its value.
        
        Colors follow the standard Minesweeper scheme:
        1: Blue, 2: Green, 3: Red, 4: Dark Blue, etc.
        
        Returns:
            tuple: RGB color values (0-255) for the number's color
        """
        tile_colors = {
            0: (192, 192, 192),    # Empty opened tile
            1: (0, 0, 255),        # Blue
            2: (0, 128, 0),        # Green
            3: (255, 0, 0),        # Red
            4: (0, 0, 128),        # Dark Blue
            5: (128, 0, 0),        # Dark Red
            6: (0, 128, 128),      # Cyan
            7: (0, 0, 0),          # Black
            8: (128, 128, 128)     # Gray
        }
        return tile_colors[self.value]

    def draw(self, game_window):
        """
        Render the tile on the game window with appropriate visuals based on its state.
        
        This method draws the tile with different appearances depending on whether it's:
        - Hidden: Shows the hidden tile image
        - Flagged: Shows the flag image
        - Revealed bomb: Shows the bomb image
        - Revealed number: Shows the revealed tile with number
        - Revealed empty: Shows the revealed tile without number
        
        Args:
            game_window (pygame.Surface): The pygame surface on which to draw the tile
        """
        # Determine which image to use
        if self.is_hidden:
            img = self.flagged_img if self.is_flagged else self.hidden_img
        elif self.is_bomb:
            img = self.bomb_img
        else:
            img = self.revealed_img
            
        # Scale and draw the base tile image
        scaled_img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
        game_window.blit(scaled_img, (self.pos_x, self.pos_y))
        
        # Add number text if it's already revealed and has a number
        if not self.is_hidden and self.is_numbered:
            text_surface = self.font.render(str(self.value), True, self.get_color())
            text_rect = text_surface.get_rect(center=(
                self.pos_x + self.tile_size // 2,
                self.pos_y + self.tile_size // 2
            ))
            game_window.blit(text_surface, text_rect)

    #----------------------------------------------------------------------
    # Game mechanics - primary interaction methods
    #----------------------------------------------------------------------

    def reveal(self, game_window, count_callback):
        """
        Reveal this tile and potentially connected tiles with cascade effect.
        
        This method:
        1. Reveals the current tile
        2. If it's a 0-value tile, recursively reveals all adjacent tiles
        3. Updates neighbor relationships through on_reveal()
        4. Counts revealed tiles through the callback function
        
        Args:
            game_window (pygame.Surface): The pygame surface to draw on
            count_callback (function): Function to call when a non-bomb tile is revealed,
                                      used to track total revealed tiles for win condition
            
        Returns:
            bool: True if a bomb was revealed (game over), False otherwise
        """
        if not self.is_hidden:
            return False   # Already revealed

        queue = [self]
        visited = set()
        bomb_revealed = False

        while queue:
            tile = queue.pop()
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
                    count_callback(tile)  # Pass the tile to the callback
                    
            tile.on_reveal(count_callback)
            tile.draw(game_window)

            if tile.value == 0:
                for neighbor in tile.neighbours:
                    if neighbor.is_hidden and neighbor not in visited:
                        queue.append(neighbor)
        
        return bomb_revealed

    def flag(self, game_window, flag_callback, neighbour_callback):
        """
        Toggle the flag state of this tile.
        
        This method:
        1. Toggles the is_flagged property
        2. Updates neighbor relationships through on_flag() or remove_flag()
        3. Redraws the tile to show the new state
        
        Args:
            game_window (pygame.Surface): The pygame surface to draw on
            flag_callback (function): Function to call to track flag changes 
                                     takes a Tile object and a boolean (was_flagged)
            neighbour_callback (function): Function to call for each neighbor
                                          that is affected by this change
        """
        was_flagged = self.is_flagged
    
        if self.is_flagged:
            self.is_flagged = False
            self.remove_flag(neighbour_callback)
        else:
            self.is_flagged = True
            self.on_flag(neighbour_callback)
            
        flag_callback(self, was_flagged)
            
        self.draw(game_window)

    def satisfy_tile(self, game_window):
        """
        Flag all remaining hidden neighbors to satisfy the tile's value.
        
        This method is used by solver algorithms when the number of hidden
        neighbors equals the remaining unflagged bombs adjacent to this tile.
        In this case, all hidden neighbors must be bombs and can be safely flagged.
        
        Note: This is primarily used by AI solvers rather than manual gameplay.
        
        Args:
            game_window (pygame.Surface): The pygame surface to draw on
        """
        for neighbour in list(self.hidden_neighbours):
            if not neighbour.is_flagged:
                neighbour.flag(game_window)
                self.hidden_neighbours.remove(neighbour)
                self.flagged_neighbours.add(neighbour)

    #----------------------------------------------------------------------
    # Neighbor relationship management methods
    #----------------------------------------------------------------------

    def on_reveal(self, neighbour_callback):
        """
        Update neighbor tiles when this tile is revealed.
        
        This method removes this tile from all neighbors' hidden_neighbours sets,
        maintaining accurate tracking of hidden/revealed relationships for
        solving algorithms and cascade reveals.
        
        Args:
            neighbour_callback (function): Function to call for each neighbor 
                                          that is affected by this change
        """
        for neighbour in self.neighbours:
            if self in neighbour.hidden_neighbours:
                neighbour.hidden_neighbours.remove(self)
                neighbour_callback(neighbour)

    def on_flag(self, neighbour_callback):
        """
        Update neighbor tiles when this tile is flagged.
        
        This method adds this tile to all neighbors' flagged_neighbours sets,
        maintaining accurate tracking of flagged tiles for chord operations
        and solving algorithms.

        Args:
            neighbour_callback (function): Function to call for each neighbor
                                          that is affected by this change
        """
        for neighbour in self.neighbours:
            if self not in neighbour.flagged_neighbours:
                neighbour.flagged_neighbours.add(self)
                neighbour_callback(neighbour)

    def remove_flag(self, neighbour_callback):
        """
        Update neighbor tiles when this tile's flag is removed.
        
        This method removes this tile from all neighbors' flagged_neighbours sets,
        maintaining accurate tracking of flagged tiles for chord operations
        and solving algorithms.

        Args:
            neighbour_callback (function): Function to call for each neighbor
                                          that is affected by this change
        """
        for neighbour in self.neighbours:
            if self in neighbour.flagged_neighbours:
                neighbour.flagged_neighbours.remove(self)
                neighbour_callback(neighbour)
