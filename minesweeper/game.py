import pygame
import os
import time
from minesweeper.grid import Grid
from minesweeper.tile import Tile

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
SCREEN_WIDTH = SCREEN_HEIGHT = 628
ROWS, COLS = 8, 8
TILE_SIZE = 75
N_BOMBS = 10
BUFFER = 4

class MinesweeperGame:
    def __init__(self):
        pygame.init()

        self.game_window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MinesweeperAI")

        # Load images and font for all tiles
        Tile.load_assets(
            bomb_path=os.path.join(ASSETS_DIR, 'bomb.png'),
            hidden_path=os.path.join(ASSETS_DIR, 'hidden2.png'),
            revealed_path=os.path.join(ASSETS_DIR, 'revealed.png'),
            flagged_path=os.path.join(ASSETS_DIR, 'flag1.png'),
            font=pygame.font.Font('freesansbold.ttf', 32)
        )

    def run(self):
        # Create the grid and cache all_tiles
        self.grid = Grid.make_grid(self.game_window, ROWS, COLS, TILE_SIZE, N_BOMBS, BUFFER)
        self.all_tiles = [tile for row in self.grid.tiles for tile in row]
        self.non_bomb_tiles_count = ROWS * COLS - N_BOMBS
        self.revealed_count = 0
        
        self.setup_new_game()
        return self.game_loop()
        
    def setup_new_game(self):
        # Setup a new game (for first game or after restart)
        self.grid.draw_grid()
        
        # Start with no bombs placed - wait for first click
        self.bombs_placed = False

    def game_loop(self):
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    row, col = self.get_tile_at_pos(mouse_x, mouse_y, TILE_SIZE, BUFFER)
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        tile = self.grid.tiles[row][col]
                        
                        # Handle first click - place bombs
                        if not self.bombs_placed:
                            self.place_bombs_after_first_click(tile)
                            self.bombs_placed = True
                        
                        # Handle the click
                        self.handle_click(row, col, event.button, pygame.key.get_mods())
                        pygame.display.flip()  # Only flip once per frame
                        
                        # Check for win
                        if self.revealed_count == self.non_bomb_tiles_count:
                            print("You won!")
                            time.sleep(2)
                            self.restart()
        
        pygame.quit()
        return 0
        
    def restart(self):
        # Reset the game state without recursion
        self.grid = Grid.make_grid(self.game_window, ROWS, COLS, TILE_SIZE, N_BOMBS, BUFFER)
        self.all_tiles = [tile for row in self.grid.tiles for tile in row]
        self.non_bomb_tiles_count = ROWS * COLS - N_BOMBS
        self.revealed_count = 0
        self.bombs_placed = False
        self.grid.draw_grid()
        
    def handle_click(self, row: int, col: int, button: int, mods=0):
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
                        print("Shift+Click revealed a bomb, restarting")
                        time.sleep(2)
                        self.restart()
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
                    print("Clicked on a bomb sire, restarting")
                    time.sleep(2)
                    self.restart()
                    return
        # Right click
        elif button == 3:
            tile.flag(self.game_window)

    def check_win(self, all_tiles: list[Tile]) -> None:
        for tile in all_tiles:
            if not tile.is_bomb and tile.is_hidden:
                return
        print("We won ig")
        time.sleep(2)
        self.restart()

    def place_bombs_after_first_click(self, first_tile):
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
    def get_tile_at_pos(mouse_x, mouse_y, tile_size, buffer) -> tuple[int, int]:
        col = mouse_x // (tile_size + buffer)
        row = mouse_y // (tile_size + buffer)
        
        return int(row), int(col)
