import pyautogui
import sys
from queue import PriorityQueue
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

def update_active_tiles(opened_tiles: list, active_tiles: PriorityQueue):
    for tile in opened_tiles:
        if tile.numbered:
            # Assign priority based on tile status
            # Lower number = higher priority
            if tile.satisfied:
                priority = 0  # Highest priority - already satisfied
            elif tile.satisfiable:
                priority = 1  # High priority - can be satisfied now
            else:
                priority = 2  # Normal priority - needs more information
            
            # Add to priority queue with (priority, unique_id, tile)
            # unique_id ensures consistent ordering when priorities are equal
            unique_id = id(tile)  # Use object id as tie-breaker
            active_tiles.put((priority, unique_id, tile))

def update_game_status():
    won, lost = check_game_status()
    if lost:
        restart_game()
        start()
    if won:
        we_won()

def open_corner_tiles(corner_tiles: list[Tile], grid: Grid):
    n_opened_tiles = 0
    opened_tiles = []
    # first open 2-4 corner tiles
    for tile in corner_tiles:
        pyautogui.click(tile.pos_x, tile.pos_y)
        update_game_status()
        pyautogui.moveTo(10, 10)
        new_n_opened_tiles, new_opened_tiles = grid.update_grid()
        n_opened_tiles += new_n_opened_tiles
        opened_tiles.extend(new_opened_tiles)
    
    return n_opened_tiles, opened_tiles
    
def open_random_tiles(active_tiles: PriorityQueue, grid: Grid) -> None:
    print("opening random tiles")
    n_opened_tiles = 0
    opened_tiles = []
    
    while n_opened_tiles < 5:
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
        new_n_opened_tiles, new_opened_tiles = grid.update_grid()
        n_opened_tiles += new_n_opened_tiles
        opened_tiles.extend(new_opened_tiles)
    update_active_tiles(opened_tiles, active_tiles)

def explore_satisfied_tile(tile: Tile):
    """Shift-click on a satisfied tile to reveal adjacent tiles."""
    pyautogui.keyDown('shift') 
    pyautogui.click(tile.pos_x, tile.pos_y, button='left')
    pyautogui.keyUp('shift')

def try_satisfy_tile(tile: Tile, grid: Grid) -> tuple[list, bool]:
    """Try to satisfy a tile and return changed tiles and success status."""
    if tile.satisfiable:
        tile.satisfy_tile()
        explore_satisfied_tile(tile)
        update_game_status()
        pyautogui.moveTo(10, 10)
        _, opened_tiles = grid.update_grid()
        return opened_tiles, True
    return [], False

def we_won():
    sys.exit("No way we won right?")

def start():
    # Use PriorityQueue instead of Queue
    active_tiles = PriorityQueue()
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
    n_opened_tiles, opened_tiles = open_corner_tiles(corner_tiles[:num+1], grid)
    update_active_tiles(opened_tiles, active_tiles)
    if n_opened_tiles < 5:
        open_random_tiles(active_tiles, grid)


    while not active_tiles.empty():
        priority, _, tile = active_tiles.get()

        if priority == 2: # top priority was normal, i.e., no tile that can be satisfied => we should open random tiles
            open_random_tiles(active_tiles, grid)
        
        if tile.satisfied:
            explore_satisfied_tile(tile)
            update_game_status()
            pyautogui.moveTo(10, 10)
            _, opened_tiles = grid.update_grid()
            if opened_tiles:
                update_active_tiles(opened_tiles, active_tiles)
        else:
            opened_tiles, satisfied = try_satisfy_tile(tile, grid)
            if satisfied and opened_tiles:
                update_active_tiles(opened_tiles, active_tiles)
    
    print("Active tiles empty - game likely completed or stuck")




