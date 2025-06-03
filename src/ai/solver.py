import pyautogui
import sys
from heapdict import heapdict
from random import randrange, shuffle
from typing import Literal
from ..models.grid import Grid, update_grid_from_tile
from ..models.tile import Tile
from ..utils.game_utils import (
    check_game_status,
    restart_game
)
import time

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
        _ = update_grid_from_tile(r_tile)
    else:  
        print("YAY WE WON!(or you pressed spacebar)")

def priority_level(tile: Tile) -> Literal[1, 2, 3]:
    # Assign priority based on tile status
    # Lower number = higher priority
    if tile.satisfied:
        priority = 0  # Highest priority - already satisfied
    elif tile.satisfiable:
        priority = 1  # High priority - can be satisfied now
    else:
        priority = 2  # Normal priority - needs more information
    
    return priority

def update_active_tiles(tiles: list[Tile], active_tiles: heapdict):
    for tile in tiles:
        if tile.numbered:
            active_tiles[tile] = priority_level(tile)

def update_game_status():
    won, lost = check_game_status()
    if lost:
        restart_game()
        start()
    if won:
        we_won()

def open_corner_tiles(corner_tiles: list[Tile], grid: Grid):
    tiles_to_update = []
    # first open 2-4 corner tiles
    for tile in corner_tiles:
        pyautogui.click(tile.pos_x, tile.pos_y)
        update_game_status()
        pyautogui.moveTo(10, 10)
        tiles_to_update.extend(update_grid_from_tile(tile))
    
    return tiles_to_update
    
def open_random_tiles(active_tiles: heapdict, grid: Grid) -> None:
    print("opening random tiles")
    # time.sleep(5)
    rows = grid.rows
    cols = grid.cols
    r_row, r_col = randrange(rows), randrange(cols)
    r_tile = grid.tiles[r_row][r_col]
    while not r_tile.hidden:
        r_row, r_col = randrange(rows), randrange(cols)
        r_tile = grid.tiles[r_row][r_col]
    pyautogui.click(r_tile.pos_x, r_tile.pos_y)
    update_game_status()
    pyautogui.moveTo(10, 10)
    tiles_to_update = update_grid_from_tile(r_tile)
    update_active_tiles(tiles_to_update, active_tiles)

def pop_active_tile(active_tiles: heapdict) -> tuple[Tile, Literal[1, 2, 3]]:
    return active_tiles.popitem()

def explore_satisfied_tile(tile: Tile):
    """Shift-click on a satisfied tile to reveal adjacent tiles."""
    pyautogui.keyDown('shift') 
    pyautogui.click(tile.pos_x, tile.pos_y, button='left')
    pyautogui.keyUp('shift')

def try_satisfy_tile(tile: Tile, grid: Grid) -> list:
    """Try to satisfy a tile and return changed tiles and success status."""
    if tile.satisfiable:
        tile.satisfy_tile()
        explore_satisfied_tile(tile)
        update_game_status()
        pyautogui.moveTo(10, 10)
        tiles_to_update = update_grid_from_tile(tile)
        return tiles_to_update
    return []

def we_won():
    sys.exit("No way we won right?")

def start():
    active_tiles = heapdict[Tile, Literal[1, 2, 3]]()
    grid = Grid.from_game_window()
    
    # Add corner tiles to queue with normal priority
    corner_tiles = [
        grid.tiles[0][0], 
        grid.tiles[0][grid.cols-1], 
        grid.tiles[grid.rows-1][0], 
        grid.tiles[grid.rows-1][grid.cols-1]
    ]
    shuffle(corner_tiles)
    num = randrange(2, 5) # 2 to 4 corners
    tiles_to_update = open_corner_tiles(corner_tiles[:num+1], grid)
    update_active_tiles(tiles_to_update, active_tiles)

    while active_tiles:
        tile, priority = pop_active_tile(active_tiles)

        if priority == 2: # top priority was normal, i.e., no tile that can be satisfied => we should open random tiles
            open_random_tiles(active_tiles, grid)
        
        if tile.satisfied:
            explore_satisfied_tile(tile)
            update_game_status()
            pyautogui.moveTo(10, 10)
            tiles_to_update = update_grid_from_tile(tile)
            if tiles_to_update:
                update_active_tiles(tiles_to_update, active_tiles)
        else:
            tiles_to_update = try_satisfy_tile(tile, grid)
            if tiles_to_update:
                update_active_tiles(tiles_to_update, active_tiles)
    
    print("Active tiles empty - game likely completed or stuck")




