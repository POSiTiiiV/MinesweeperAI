import pyautogui
import pygetwindow as gw
from PIL import Image, ImageDraw
from math import sqrt
from random import randrange
import time
import keyboard


class TILES:
    def __init__(self, value, pos, matrix_pos):
        self.value = value
        self.is_open = True if value not in ('_', 'F') else False
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.row = matrix_pos[0]
        self.col = matrix_pos[1]
        self.satisfied = False
        self.neighbors = {i:None for i in range(8)}


def distance(c1, c2):
    return sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def color_mapping(color):
    color_map = {
        (192, 192, 192): 0,
        (0, 0, 255): 1,
        (0, 128, 0): 2,
        (255, 0, 0): 3,
        (0, 0, 128): 4,
        (128, 0, 0): 5,
        (0, 128, 128): 6,
        (0, 0, 0): 7,
        (128, 128, 128): 8,
    }

    closest = min(list(color_map.keys()), key=lambda x: distance(x, color))
    return color_map[closest], closest

def draw_rectangles(rows, cols):
    # draw rectangle around all the individial tiles
    im = Image.open("grid.png")
    img = ImageDraw.Draw(im)
    tiles_in_a_row = rows
    tiles_in_a_column = cols
    init_left, init_top = 0, 0
    for i in range(tiles_in_a_row):
        for j in range(tiles_in_a_column):
            img.rectangle([(init_left, init_top), (init_left + 18, init_top + 18)], outline="red", fill=None, width = 1)
            init_left += 20
        init_left = 0
        init_top += 20
    im.show()

def find_game_window():
    # find the game window
    game_window = gw.getWindowsWithTitle('Minesweeper X')[0]

    # capture game window
    game_window_left, game_window_top = game_window.left+4, game_window.top
    game_window_width, game_window_height = game_window.size[0]-8, game_window.size[1]-4
    # save image for reference
    game_window_image = pyautogui.screenshot('game.png', 
                            region=(
                                game_window_left,
                                game_window_top, 
                                game_window_width, 
                                game_window_height
                                ))

    return game_window_left, game_window_top, game_window_width, game_window_height, game_window_image

def find_grid(game_window_left, game_window_top, game_window_width, game_window_height, _):
    # position of grid
    grid_left, grid_top = game_window_left + 16, game_window_top + 128
    grid_width, grid_height =  game_window_width - 30, game_window_height - 141
    # capture the grid(actual playing area)
    grid_img = pyautogui.screenshot('grid.png', 
                            region=(grid_left, grid_top, grid_width, grid_height))
    
    return grid_left, grid_top, grid_width, grid_height, grid_img

def read_tiles():
    # find game window and then grid
    grid_left, grid_top, grid_width, grid_height, grid_img = find_grid(*find_game_window())

    tiles_in_a_row = grid_width // 20
    tiles_in_a_column = grid_height // 20
    init_left, init_top = 0, 0
    grid = []
    # draw_rectangles(tiles_in_a_row, tiles_in_a_column)
    for i in range(tiles_in_a_row):
        temp = []
        for j in range(tiles_in_a_column):
            # colored pixel=> y = 100 / 8 = 12, x = 114 / 8 = 14
            color = grid_img.getpixel((init_left + 12, init_top + 14)) # colored pixle that is present in all the tiles
            val, closest = color_mapping(color)
            if val == 0:
                color2 = grid_img.getpixel((init_left + 1, init_top + 1)) # check if its a unopened tile
                if distance(color2, (255, 255, 255)) < distance(color2, closest):
                    obj = TILES('_', (grid_left + init_left + 9, grid_top + init_top + 9), (i, j))
                    temp.append(obj)
                    init_left += 20
                    continue
            elif val == 7:
                color2 = grid_img.getpixel((init_left + 4, init_top + 4)) # check if its a flag
                if distance(color2, (255, 0, 0)) < distance(color2, closest):
                    obj = TILES('F', (grid_left+ init_left + 9, grid_top + init_top + 9), (i, j))
                    temp.append(obj)
                    init_left += 20
                    continue
            obj = TILES(val, (grid_left + init_left + 9, grid_top+ init_top + 9), (i, j))
            temp.append(obj)
            init_left += 20
        grid.append(temp)
        init_left = 0
        init_top += 20
    
    return grid, tiles_in_a_row, tiles_in_a_column

def click_random_tiles_to_vicotry():
    grid, rows, cols = read_tiles()
    # Create a list of all possible (row, col) pairs
    all_pairs = [(r, c) for r in range(rows) for c in range(cols)]

    won, lost = False, False
    count = 0
    while not won and all_pairs and not keyboard.is_pressed('space'):
        print_grid(grid, rows, cols)
        # y = 716 / 8 = 89
        game_window_left, game_window_top, game_window_width, game_window_height, game_window_image = find_game_window()
        center = game_window_width // 2
        color = game_window_image.getpixel((center, 89))
        won = distance(color, (0, 0, 0)) < distance(color, (255, 255, 0)) # check if we won
        # pyautogui.moveTo((game_window_left + center, game_window_top + 89))
        # x = 4
        color = game_window_image.getpixel((center - 5, 98))
        # pyautogui.moveTo((game_window_left + center - 5, game_window_top + 98))
        lost = distance(color, (0, 0, 0)) < distance(color, (255, 255, 0)) # check if we lost

        if lost:
            count += 1
            print(f"lost {count} times, restarting")
            pyautogui.click((game_window_left + center, game_window_top + 89)) # restart
            # reset all_pairs
            all_pairs = [(r, c) for r in range(rows) for c in range(cols)]

        # Choose a new random (row, col) pair and remove it from the list
        idx = randrange(len(all_pairs))
        random_row, random_col = all_pairs.pop(idx)
        random_tile = grid[random_row][random_col]
        while random_tile.is_open:
            idx = randrange(len(all_pairs))
            random_row, random_col = all_pairs.pop(idx)
            random_tile = grid[random_row][random_col]
        pyautogui.click(random_tile.pos_x, random_tile.pos_y)

        grid, rows, cols = read_tiles()
    else:
        print("YAY WE WON!")

def print_grid(grid, rows, cols):
    for i in range(rows):
        for j in range(cols):
            print(grid[i][j].value, end=' ')
        print('\n')
    print('\n')

if __name__ == "__main__":
    # grid, rows, cols = read_tiles()

    click_random_tiles_to_vicotry()

    # print_grid(grid, rows, cols)