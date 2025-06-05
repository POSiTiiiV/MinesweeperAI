import pygame
from minesweeper.tile import Tile
from minesweeper.grid import Grid
from minesweeper.game import MinesweeperGame

class MinesweeperAPI:
    """
    API for interacting with the Minesweeper game.
    
    This class provides a clean interface for game interactions,
    making it suitable for both human players (via UI) and
    AI solvers (via method calls).
    """
    
    def __init__(self, game: MinesweeperGame):
        """
        Initialize the API with a reference to the game instance.
        
        Args:
            game (MinesweeperGame): The game instance to control
        """
        self.game = game
        self.grid = game.grid
        self.game_window = game.game_window
        
        # Tracking lists for different types of affected tiles
        self.newly_revealed_tiles = []   # Tiles revealed in current operation
        self.newly_flagged_tiles = []    # Tiles flagged in current operation
        self.newly_unflagged_tiles = []  # Tiles unflagged in current operation
        self.neighbour_updated_tiles = [] # Tiles whose neighbors changed status

    # Game state methods
    
    def get_game_status(self) -> str:
        """
        Get the current status of the game.
        
        Returns:
            str: Game status - "playing", "won", or "lost"
        """
        return self.game.game_status
    
    def get_bombs_count(self) -> int:
        """
        Get the total number of bombs in the game.
        
        Returns:
            int: Total number of bombs
        """
        return self.game.bomb_count
    
    def get_flags_count(self) -> int:
        """
        Get the current number of flagged tiles.
        
        Returns:
            int: Number of tiles currently flagged
        """
        return self.game.flagged_count
    
    def get_remaining_bombs_count(self) -> int:
        """
        Get the remaining number of bombs to be flagged.
        
        This is calculated as: total bombs - flagged tiles.
        Note that this may not represent actual unflagged bombs
        if the player has incorrectly flagged some tiles.
        
        Returns:
            int: Remaining bombs to flag (can be negative if over-flagged)
        """
        return self.game.bomb_count - self.game.flagged_count
    
    def get_board_state(self) -> list[list[dict[str, any]]]:
        """
        Get a representation of the visible board for solving algorithms.
        
        Returns a 2D array of dictionaries, each containing:
        - row, col: Position coordinates
        - is_hidden: Whether the tile is hidden
        - is_flagged: Whether the tile is flagged
        - value: The tile's value (if revealed, otherwise None)
        - is_bomb: Whether the tile is a bomb (if revealed, otherwise None)
        
        Returns:
            list[list[dict[str, any]]]: The current visible board state
        """
        board_state = []
        for row in range(self.grid.rows):
            row_data = []
            for col in range(self.grid.cols):
                tile = self.grid.tiles[row][col]
                tile_data = {
                    'row': row,
                    'col': col,
                    'is_hidden': tile.is_hidden,
                    'is_flagged': tile.is_flagged,
                    'value': tile.value if not tile.is_hidden else None,
                    'is_bomb': tile.is_bomb if not tile.is_hidden else None
                }
                row_data.append(tile_data)
            board_state.append(row_data)
        return board_state
    
    # Game action methods
    
    def reveal_tile(self, row: int, col: int) -> dict[str, any]:
        """
        Reveal a tile at the given coordinates.
        
        This simulates a left-click on a tile, which will:
        - Reveal the tile if it's hidden and not flagged
        - Trigger cascade reveals for empty tiles
        - End the game if a bomb is revealed
        - Check for win condition
        
        Args:
            row (int): Row coordinate of the tile
            col (int): Column coordinate of the tile
            
        Returns:
            dict[str, any]: Feedback with keys:
                - result: "invalid_position", "game_not_active", "already_revealed",
                         "flagged", "bomb", "win", or "revealed"
                - game_status: Current game status
                - tile_value: The revealed tile's value (for "revealed" result)
                - newly_revealed: Number of tiles revealed (for "revealed" result)
                - affected_tiles: Dict with lists of affected tile coordinates
        """
        # Reset tracking lists
        self.newly_revealed_tiles = []
        self.neighbour_updated_tiles = []
        
        if not self._is_valid_position(row, col):
            return {
                "result": "invalid_position",
                "game_status": self.game.game_status
            }
            
        tile = self.grid.tiles[row][col]
        
        # If the game isn't in playing state, return immediately
        if self.game.game_status != "playing":
            return {
                "result": "game_not_active",
                "game_status": self.game.game_status
            }
            
        # If this is the first click, handle bomb placement
        if not self.game.bombs_placed:
            self.game.place_bombs_after_first_click(tile)
            self.game.bombs_placed = True
        
        # If tile is already revealed, return that info
        if not tile.is_hidden:
            return {
                "result": "already_revealed",
                "tile_value": tile.value,
                "game_status": self.game.game_status
            }
            
        # If tile is flagged, don't reveal it
        if tile.is_flagged:
            return {
                "result": "flagged",
                "game_status": self.game.game_status
            }
    
        # Track the number of newly revealed tiles
        before_count = self.game.revealed_count
        
        # Reveal the tile with callbacks to track affected tiles
        bomb_revealed = tile.reveal(
            self.game_window, 
            count_callback=self._increment_revealed_count
        )
        
        # Calculate newly revealed tiles count
        newly_revealed = self.game.revealed_count - before_count
        
        # Handle bomb revealed
        if bomb_revealed:
            pygame.display.flip()
            self.game.lost()
            return {
                "result": "bomb",
                "game_status": "lost",
                "bomb_position": (row, col),
                "affected_tiles": {
                    "revealed": self.newly_revealed_tiles.copy(),
                    "neighbors_updated": self.neighbour_updated_tiles.copy()
                }
            }
            
        # Check for win
        if self.game.revealed_count == self.game.non_bomb_tiles_count:
            self.game.won()
            return {
                "result": "win",
                "tile_value": tile.value,
                "newly_revealed": newly_revealed,
                "affected_tiles": {
                    "revealed": self.newly_revealed_tiles.copy(),
                    "neighbors_updated": self.neighbour_updated_tiles.copy()
                },
                "game_status": "won"
            }
            
        # Normal reveal
        return {
            "result": "revealed",
            "tile_value": tile.value,
            "newly_revealed": newly_revealed,
            "affected_tiles": {
                "revealed": self.newly_revealed_tiles.copy(),
                "neighbors_updated": self.neighbour_updated_tiles.copy()
            },
            "game_status": self.game.game_status
        }

    def chord_tile(self, row: int, col: int) -> dict[str, any]:
        """
        Perform a chord action (shift+click) on a numbered tile.
        
        If the number of flagged neighbors equals the tile's number,
        reveals all non-flagged neighbors. This is a common shortcut
        in Minesweeper that speeds up gameplay.
        
        Args:
            row (int): Row coordinate of the tile
            col (int): Column coordinate of the tile
            
        Returns:
            dict[str, any]: Feedback with keys:
                - result: "invalid_position", "game_not_active", "not_chordable",
                         "not_satisfied", "bomb", "win", or "chorded"
                - game_status: Current game status
                - newly_revealed: Number of tiles revealed (for "chorded" result)
                - affected_tiles: Dict with lists of affected tile coordinates
        """
        # Reset tracking lists
        self.newly_revealed_tiles = []
        self.neighbour_updated_tiles = []
        
        if not self._is_valid_position(row, col):
            return {
                "result": "invalid_position",
                "game_status": self.game.game_status
            }
            
        tile = self.grid.tiles[row][col]
        
        # If the game isn't in playing state, return immediately
        if self.game.game_status != "playing":
            return {
                "result": "game_not_active",
                "game_status": self.game.game_status
            }
            
        # Can only chord on revealed numbered tiles
        if tile.is_hidden or not tile.is_numbered:
            return {
                "result": "not_chordable",
                "game_status": self.game.game_status
            }
            
        # Only proceed if flagged neighbors equals tile value
        if not tile.is_satisfied:
            return {
                "result": "not_satisfied",
                "game_status": self.game.game_status
            }
    
        # Track before count
        before_count = self.game.revealed_count
        
        # Reveal all non-flagged neighbors
        bomb_revealed = False
        bomb_position = None
        
        for neighbor in tile.neighbours:
            if not neighbor.is_flagged and neighbor.is_hidden:
                if neighbor.reveal(
                    self.game_window,
                    count_callback=self._increment_revealed_count
                ):
                    bomb_revealed = True
                    bomb_position = (neighbor.row, neighbor.col)
                    break
        
        # Calculate newly revealed tiles
        newly_revealed = self.game.revealed_count - before_count
        revealed_tiles = self.newly_revealed_tiles.copy()
        
        # Handle if a bomb was revealed
        if bomb_revealed:
            pygame.display.flip()
            self.game.lost()
            return {
                "result": "bomb",
                "game_status": "lost",
                "bomb_position": bomb_position,
                "affected_tiles": {
                    "revealed": self.newly_revealed_tiles.copy(),
                    "neighbors_updated": self.neighbour_updated_tiles.copy()
                }
            }
            
        # Check for win
        if self.game.revealed_count == self.game.non_bomb_tiles_count:
            self.game.won()
            return {
                "result": "win",
                "newly_revealed": newly_revealed,
                "affected_tiles": {
                    "revealed": self.newly_revealed_tiles.copy(),
                    "neighbors_updated": self.neighbour_updated_tiles.copy()
                },
                "game_status": "won"
            }
            
        # Normal chord
        return {
            "result": "chorded",
            "newly_revealed": newly_revealed,
            "affected_tiles": {
                "revealed": self.newly_revealed_tiles.copy(),
                "neighbors_updated": self.neighbour_updated_tiles.copy()
            },
            "game_status": self.game.game_status
        }

    def flag_tile(self, row: int, col: int) -> dict[str, any]:
        """
        Flag or unflag a tile at the given coordinates.
        
        This simulates a right-click on a tile, which will:
        - Toggle the flag status of a hidden tile
        - Update the flag counter
        - Update the UI
        
        Args:
            row (int): Row coordinate of the tile
            col (int): Column coordinate of the tile
            
        Returns:
            dict[str, any]: Feedback with keys:
                - result: "invalid_position", "game_not_active", "already_revealed",
                         "flagged", or "unflagged"
                - game_status: Current game status
                - flagged_count: Updated count of flagged tiles
                - remaining_bombs: Updated count of remaining bombs
                - affected_tiles: Dict with lists of affected tile coordinates
        """
        # Reset tracking lists
        self.newly_flagged_tiles = []
        self.newly_unflagged_tiles = []
        self.neighbour_updated_tiles = []
        
        if not self._is_valid_position(row, col):
            return {
                "result": "invalid_position",
                "game_status": self.game.game_status
            }
            
        tile = self.grid.tiles[row][col]
        
        # If the game isn't in playing state, return immediately
        if self.game.game_status != "playing":
            return {
                "result": "game_not_active",
                "game_status": self.game.game_status
            }
            
        # Can't flag revealed tiles
        if not tile.is_hidden:
            return {
                "result": "already_revealed",
                "game_status": self.game.game_status
            }
            
        # Get the previous flag state before toggling
        was_flagged = tile.is_flagged
        
        # Flag the tile (this toggles the flag) with callbacks to track changes
        tile.flag(
            self.game_window,
            flag_callback=self._track_flag_change,
            neighbour_callback=self._track_neighbour_update
        )
        
        # Update flag counter based on the change
        if was_flagged and not tile.is_flagged:
            self.game.flagged_count -= 1
            result = "unflagged"
        elif not was_flagged and tile.is_flagged:
            self.game.flagged_count += 1
            result = "flagged"
            
        # Update the counter display
        self.game.draw_counters()
        
        return {
            "result": result,
            "flagged_count": self.game.flagged_count,
            "remaining_bombs": self.game.bomb_count - self.game.flagged_count,
            "affected_tiles": {
                "flagged": self.newly_flagged_tiles.copy(),
                "unflagged": self.newly_unflagged_tiles.copy(),
                "neighbors_updated": self.neighbour_updated_tiles.copy()
            },
            "game_status": self.game.game_status
        }

    def restart_game(self) -> dict[str, any]:
        """
        Restart the game to a new fresh state.
        
        This will:
        - Clear the grid and generate a new game
        - Reset all game state variables
        - Update the UI
        
        Returns:
            dict[str, any]: Feedback with keys:
                - result: "restarted"
                - game_status: "playing"
        """
        # Reset all tracking arrays
        self.newly_revealed_tiles = []
        self.newly_flagged_tiles = []
        self.newly_unflagged_tiles = []
        self.neighbour_updated_tiles = []
        
        self.game.restart()
        self.grid = self.game.grid  # Update grid reference
        
        return {
            "result": "restarted",
            "game_status": "playing"
        }
    
    # Helper methods
    
    def _increment_revealed_count(self, tile: Tile) -> None:
        """
        Callback to increment the revealed count by 1 and track revealed tile.
        
        Args:
            tile (Tile): The tile being revealed. If provided,
            its position will be tracked for AI/solver use.
        """
        self.game.revealed_count += 1
        self.newly_revealed_tiles.append((tile.row, tile.col))

    def _track_flag_change(self, tile: Tile, was_flagged: bool) -> None:
        """
        Track a tile's flag status change.
        
        Args:
            tile (Tile): The tile whose flag status changed
            was_flagged (bool): Whether the tile was flagged before the change
        """
        if was_flagged:
            self.newly_unflagged_tiles.append((tile.row, tile.col))
        else:
            self.newly_flagged_tiles.append((tile.row, tile.col))

    def _track_neighbour_update(self, tile: Tile) -> None:
        """
        Track a tile whose neighbors changed status.
        
        Args:
            tile (Tile): The tile whose neighbors were updated
        """
        if hasattr(tile, 'row') and hasattr(tile, 'col'):
            pos = (tile.row, tile.col)
            if pos not in self.neighbour_updated_tiles:
                self.neighbour_updated_tiles.append(pos)
    
    def _is_valid_position(self, row: int, col: int) -> bool:
        """
        Check if the given position is valid on the grid.
        
        Args:
            row (int): Row coordinate to check
            col (int): Column coordinate to check
            
        Returns:
            bool: True if the position is within the grid boundaries, False otherwise
        """
        return 0 <= row < self.grid.rows and 0 <= col < self.grid.cols