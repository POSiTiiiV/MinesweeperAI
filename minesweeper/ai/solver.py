import sys
import pygame
import time
from heapdict import heapdict
from random import randrange
from typing import Literal
from minesweeper.tile import Tile
from minesweeper.api import MinesweeperAPI

class MinesweeperSolver:
    """
    AI solver for Minesweeper that implements various solving strategies.
    
    This class provides methods to solve a Minesweeper game using logical deduction
    and probabilistic reasoning. It communicates with the game via an API interface.
    """
    
    def __init__(self, game_api: MinesweeperAPI):
        """
        Initialize the Minesweeper solver.
        
        Args:
            game_api (MinesweeperAPI): Interface to interact with the Minesweeper game
        """
        self.game_api = game_api
        self.grid = game_api.grid
        self.active_tiles: heapdict[Tile, Literal[1, 2, 3]] = heapdict()
    
    def start(self):
        """
        Start the solver algorithm.
        
        This method initiates the solving process by opening random tiles, then
        systematically processing tiles based on their priority until the game
        is complete or no more logical moves can be made.
        """
        tiles_to_update = self.open_random_tiles()
        self.update_active_tiles(tiles_to_update)
        
        # Process events and update display regularly
        self.process_events()
        
        while self.active_tiles:
            # Process pygame events to keep UI responsive
            self.process_events()
            
            # Pop next tile to process
            tile, priority = self.pop_active_tile()

            if priority == 2:  # top priority was normal, i.e., no tile that can be satisfied => we should open random tiles
                tiles_to_update = self.open_random_tiles()
                self.update_active_tiles(tiles_to_update)
            
            if tile.is_satisfied:
                game_feedback = self.game_api.chord_tile(tile.row, tile.col)
                if game_feedback["game_status"] != "playing":
                    self.wait_for_exit()
                    return
                self.refresh_grid()
                tiles_to_update: set[tuple[int, int]] = set().union(
                    game_feedback["affected_tiles"]["revealed"],
                    game_feedback["affected_tiles"]["neighbours_updated"]
                )
                self.update_active_tiles(tiles_to_update)
            else:
                tiles_to_update = self.try_satisfy_tile(tile)
                self.update_active_tiles(tiles_to_update)
            
            # pygame.time.delay(100)
        
        print("Active tiles empty - game likely completed or stuck")
        
        # Also wait at the end in case the game is won but not detected earlier
        game_status = self.game_api.get_game_status()
        if game_status != "playing":
            self.wait_for_exit()

    def refresh_grid(self) -> None:
        """
        Update the local grid representation from the game API.
        
        This ensures the solver is working with the most current game state.
        """
        self.grid = self.game_api.grid
    
    def process_events(self):
        """
        Process pygame events to keep the UI responsive.
        
        Handles window closing and other pygame events to maintain a responsive interface.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def pop_active_tile(self) -> tuple[Tile, Literal[1, 2, 3]]:
        """
        Get the highest priority tile from the active tiles queue.
        
        Returns:
            tuple[Tile, Literal[1, 2, 3]]: A tuple containing the tile and its priority
        """
        return self.active_tiles.popitem()
    
    def update_active_tiles(self, tiles: set[tuple[int, int]]):
        """
        Update the active tiles queue with newly affected tiles.
        
        Adds numbered tiles to the active queue with appropriate priorities.
        
        Args:
            tiles (set[tuple[int, int]]): Set of (row, col) coordinates of tiles to update
        """
        for row, col in tiles:
            tile = self.grid.tiles[row][col]
            if tile.is_numbered:
                self.active_tiles[tile] = self.priority_level(tile)

    @staticmethod
    def priority_level(tile: Tile) -> Literal[1, 2, 3]:
        """
        Determine the priority level for a tile.
        
        Lower numbers indicate higher priority:
        - 0: Highest priority - tile is already satisfied
        - 1: High priority - tile can be satisfied now
        - 2: Normal priority - tile needs more information
        
        Args:
            tile (Tile): The tile to evaluate
            
        Returns:
            Literal[1, 2, 3]: The priority level
        """
        if tile.is_satisfied:
            priority = 0  # Highest priority - already satisfied
        elif tile.is_satisfiable:
            priority = 1  # High priority - can be satisfied now
        else:
            priority = 2  # Normal priority - needs more information
        
        return priority
    
    def open_random_tiles(self) -> set[tuple[int, int]]:
        """
        Reveal a random hidden tile on the grid.
        
        Used when no logical moves are available and guessing is necessary.
        
        Returns:
            set[tuple[int, int]]: Set of coordinates for tiles affected by this action
        """
        print("opening random tile")

        tiles_to_update = set()
        rows = self.grid.rows
        cols = self.grid.cols
        r_row, r_col = randrange(rows), randrange(cols)
        r_tile = self.grid.tiles[r_row][r_col]
        while not r_tile.is_hidden and not r_tile.is_flagged:
            r_row, r_col = randrange(rows), randrange(cols)
            r_tile = self.grid.tiles[r_row][r_col]
        game_feedback = self.game_api.reveal_tile(r_row, r_col)
        if game_feedback["game_status"] != "playing":
            self.wait_for_exit()
            return tiles_to_update  # Return empty set
        self.refresh_grid()
        if game_feedback.get("affected_tiles") is not None:
            tiles_to_update = set().union(
                game_feedback["affected_tiles"]["revealed"],
                game_feedback["affected_tiles"]["neighbours_updated"]
            )
        return tiles_to_update
    
    def satisfy_tile(self, tile: Tile) -> set[tuple[int, int]]:
        """
        Flag all remaining hidden neighbours to satisfy the tile's value.
        
        This method is used when the number of hidden neighbors equals the 
        remaining unflagged bombs adjacent to this tile. In this case, all 
        hidden neighbors must be bombs and can be safely flagged.
        
        Args:
            tile (Tile): The tile to satisfy
            
        Returns:
            set[tuple[int, int]]: Set of coordinates for tiles affected by this action
        """
        updated_tiles: set[tuple[int, int]] = set()
        for neighbour in tile.hidden_neighbours.copy():
            if not neighbour.is_flagged:
                game_feedback = self.game_api.flag_tile(neighbour.row, neighbour.col)
                if game_feedback.get("affected_tiles") is not None:
                    updated_tiles.update(game_feedback["affected_tiles"]["neighbours_updated"])
        
        return updated_tiles
    
    def try_satisfy_tile(self, tile: Tile) -> set[tuple[int, int]]:
        """
        Attempt to satisfy a tile and chord it if possible.
        
        If a tile is satisfiable (all remaining hidden neighbors are bombs),
        this flags those neighbors and then chords the tile.
        
        Args:
            tile (Tile): The tile to try satisfying
            
        Returns:
            set[tuple[int, int]]: Set of coordinates for tiles affected by this action
        """
        if tile.is_satisfiable:
            tiles_to_update = self.satisfy_tile(tile)
            game_feedback = self.game_api.chord_tile(tile.row, tile.col)
            if game_feedback["game_status"] != "playing":
                self.wait_for_exit()
                return tiles_to_update  # Return what we have so far
            self.refresh_grid()
            if game_feedback.get("affected_tiles") is not None:
                tiles_to_update.union(
                    game_feedback["affected_tiles"]["revealed"],
                    game_feedback["affected_tiles"]["neighbours_updated"]
                )
            return tiles_to_update
        return set()
    
    def click_random_tiles_to_victory(self) -> None:
        """
        Attempt to win the game by randomly clicking tiles.
        
        A naive approach that continues clicking random hidden tiles until
        the game is won or lost. On loss, it restarts the game.
        """
        rows, cols = self.grid.rows, self.grid.cols
        # Create a list of all possible (row, col) pairs
        all_pairs = [(r, c) for r in range(rows) for c in range(cols)]

        game_status = "playing"
        count = 0
        while game_status == "playing" and all_pairs:
            game_status = self.game_api.get_game_status()
            if game_status == "lost":
                count += 1
                print(f"lost {count} times, restarting")
                self.game_api.restart_game()
                all_pairs = [(r, c) for r in range(rows) for c in range(cols)]  # reset all_pairs

            # Choose a new random (row, col) pair and remove it from the list
            idx = randrange(len(all_pairs))
            r_row, r_col = all_pairs.pop(idx)
            r_tile = self.grid.tiles[r_row][r_col]
            while not r_tile.is_hidden:
                idx = randrange(len(all_pairs))
                r_row, r_col = all_pairs.pop(idx)
                r_tile = self.grid.tiles[r_row][r_col]
            game_feedback = self.game_api.reveal_tile(r_row, r_col)
            self.check_game_status(game_feedback["game_status"])
        else:  
            print("YAY WE WON!")
    
    def wait_for_exit(self):
        """
        Wait for the user to close the window or press a key after game completion.
        
        This keeps the game window open until the user explicitly exits,
        allowing them to see the final state of the board.
        """
        print("Game finished! Press any key or close the window to exit.")
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            pygame.time.delay(100)

