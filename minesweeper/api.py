import pygame
from minesweeper.tile import Tile
from minesweeper.grid import Grid
from minesweeper.game import MinesweeperGame

class MinesweeperAPI:
    def __init__(self, game: MinesweeperGame):
        self.game = game
        self.grid = game.grid
        self.game_window = game.game_window

    def get_board_state(self) -> list[list[dict]]:
        """
        Return a representation of the visible board for the solver.
        Each tile is represented as a dictionary with its current state.
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

    def reveal_tile(self, row: int, col: int) -> bool:
        """
        Reveal a tile at the given coordinates.
        Returns True if a bomb was revealed else False
        """
        return self.grid.tiles[row][col].reveal(self.game_window)

    def flag_tile(self, row: int, col: int) -> None:
        """
        Flag or unflag a tile at the given coordinates.
        """
        self.grid.tiles[row][col].flag(self.game_window)

    def get_game_status(self) -> str:
        """
        Returns the current status of the game.
        Can be "playing", "won", or "lost".
        """
        return self.game.game_status
    
    def restart_game(self) -> None:
        self.game.restart()
    
    def get_bombs_count(self) -> int:
        """Get the total number of bombs in the game."""
        return self.game.bomb_count
    
    def get_flags_count(self) -> int:
        """Get the current number of flagged tiles."""
        return self.game.flagged_count
    
    def get_remaining_bombs_count(self) -> int:
        """Get the remianing number of bombs in the game."""
        return self.game.bomb_count - self.game.flagged_count
    
    def _is_valid_position(self, row: int, col: int) -> bool:
        """Check if the given position is valid on the grid."""
        return 0 <= row < self.grid.rows and 0 <= col < self.grid.cols