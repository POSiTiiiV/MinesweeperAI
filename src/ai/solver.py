import pyautogui
import sys
from queue import Queue
from random import randrange, shuffle
from ..models.grid import Grid
from ..models.tile import Tile
from ..utils.game_utils import (
    check_game_status,
    restart_game
)

def click_random_tiles_to_vicotry(grid: Grid) -> None:
    rows, cols = grid.rows, grid.cols
    # Create a list of all possible (row, col) pairs
    all_pairs = [(r, c) for r in range(rows) for c in range(cols)]

    won, lost = False, False
    count = 0
    while not won and all_pairs:
        grid.print_grid()
        won, lost = check_game_status()
        if lost:
            count += 1
            print(f"lost {count} times, restarting")
            restart_game()
            all_pairs = [(r, c) for r in range(rows) for c in range(cols)] # reset all_pairs

        # Choose a new random (row, col) pair and remove it from the list
        idx = randrange(len(all_pairs))
        r_row, r_col = all_pairs.pop(idx)
        r_tile = grid.tiles[r_row][r_col]
        while not r_tile.is_hidden:
            idx = randrange(len(all_pairs))
            r_row, r_col = all_pairs.pop(idx)
            r_tile = grid.tiles[r_row][r_col]
        pyautogui.click(r_tile.pos_x, r_tile.pos_y)
        pyautogui.moveTo(10, 10) 
        _, _ = grid.update_grid()
    else:  
        print("YAY WE WON!(or you pressed spacebar)")

def update_active_tiles(changed_tiles: list, active_tiles: Queue):
    for tile in changed_tiles:
        if tile.is_num_tile:
            active_tiles.put(tile) 

def update_game_status():
    won, lost = check_game_status()
    if lost:
        restart_game()
        start()
    if won:
        we_won()

def open_random_tiles(active_tiles: Queue, grid: Grid, just_started: bool) -> None:
    if just_started:
        # first open 2-4 corner tiles
        for _ in range(randrange(2, 5)):
            r_tile = active_tiles.get()
            pyautogui.click(r_tile.pos_x, r_tile.pos_y)
            update_game_status()
        pyautogui.moveTo(10, 10)
        changed_count, changed_tiles = grid.update_grid()
    else:
        changed_count = 0
        changed_tiles = []
    
    while changed_count < 5:
        rows = grid.rows
        cols = grid.cols
        r_row, r_col = randrange(rows), randrange(cols)
        r_tile = grid.tiles[r_row][r_col]
        while not r_tile.is_hidden:
            r_row, r_col = randrange(rows), randrange(cols)
            r_tile = grid.tiles[r_row][r_col]
        pyautogui.click(r_tile.pos_x, r_tile.pos_y)
        update_game_status()
        pyautogui.moveTo(10, 10)
        new_changed_count, new_changed_tiles = grid.update_grid()
        changed_count += new_changed_count
        changed_tiles.extend(new_changed_tiles)
    update_active_tiles(changed_tiles, active_tiles)

def explore_satisfied_tile(tile: Tile):
    """Shift-click on a satisfied tile to reveal adjacent tiles."""
    pyautogui.keyDown('shift') 
    pyautogui.click(tile.pos_x, tile.pos_y, button='left')
    pyautogui.keyUp('shift')

def try_satisfy_tile(tile: Tile, grid: Grid) -> tuple[list, bool]:
    """Try to satisfy a tile and return changed tiles and success status."""
    if tile.can_be_satisfied():
        explore_satisfied_tile(tile)
        update_game_status()
        pyautogui.moveTo(10, 10)
        _, changed_tiles = grid.update_grid()
        return changed_tiles, True
    return [], False

def we_won():
    sys.exit("No way we won right?")

def start():
    active_tiles = Queue()
    grid = Grid.from_game_window()
    
    # Add corner tiles to queue
    corner_tiles = [
        grid.tiles[0][0], 
        grid.tiles[0][grid.cols-1], 
        grid.tiles[grid.rows-1][0], 
        grid.tiles[grid.rows-1][grid.cols-1]
    ]
    shuffle(corner_tiles)
    for tile in corner_tiles:
        active_tiles.put(tile)

    open_random_tiles(active_tiles, grid, True)

    marked_tile = None  # Track tile that made no progress
    progress_made = False  # Track if we've added new tiles to queue

    while not active_tiles.empty():
        tile = active_tiles.get()
        
        # If we see the marked tile again and no progress was made, we're stuck
        if marked_tile and tile == marked_tile and not progress_made:
            print("No progress detected, opening random tiles...")
            open_random_tiles(active_tiles, grid, False)
            marked_tile = None  # Reset marker
            progress_made = False  # Reset progress flag
            continue
        
        tile_made_progress = False
        
        if tile.is_satisfied():
            explore_satisfied_tile(tile)
            update_game_status()
            pyautogui.moveTo(10, 10)
            _, changed_tiles = grid.update_grid()
            if changed_tiles:
                update_active_tiles(changed_tiles, active_tiles)
                tile_made_progress = True
        else:
            changed_tiles, satisfied = try_satisfy_tile(tile, grid)
            if satisfied and changed_tiles:
                update_active_tiles(changed_tiles, active_tiles)
                tile_made_progress = True
        
        if tile_made_progress:
            progress_made = True  # We made progress globally
            marked_tile = None    # Clear the marker since we progressed
        else:
            # Put tile back and mark it if we don't have a marker yet
            if not tile.satisfied:
                active_tiles.put(tile)
            if marked_tile is None:
                marked_tile = tile
                progress_made = False  # Reset progress tracking for new cycle
    
    print("Active tiles empty - game likely completed or stuck")




