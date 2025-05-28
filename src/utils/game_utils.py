from math import sqrt
from PIL import Image
import pygetwindow as gw
import pyautogui


def distance(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    return sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def color_mapping(color: tuple[int, int, int]) -> tuple[int, tuple[int, int, int]]:
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

def find_game_window() -> tuple[int, int, int, int, 'Image.Image']:
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

def find_grid(game_window_left: int, game_window_top: int, game_window_width: int, game_window_height: int, _: 'Image.Image') -> tuple[int, int, int, int, 'Image.Image']:
    # position of grid
    grid_left, grid_top = game_window_left + 16, game_window_top + 128
    grid_width, grid_height =  game_window_width - 30, game_window_height - 141
    # capture the grid(actual playing area)
    grid_img = pyautogui.screenshot('grid.png', 
                            region=(grid_left, grid_top, grid_width, grid_height))
    
    return grid_left, grid_top, grid_width, grid_height, grid_img

def check_game_status() -> tuple[bool, bool]:
    _, _, game_window_width, _, game_window_image = find_game_window()
    
    center = game_window_width // 2
    color = game_window_image.getpixel((center, 89)) # y = 716 / 8 = 89
    # pyautogui.moveTo((game_window_left + center, game_window_top + 89))
    won = distance(color, (0, 0, 0)) < distance(color, (255, 255, 0)) # check if we won
    
    color = game_window_image.getpixel((center - 5, 98)) # x = 5
    # pyautogui.moveTo((game_window_left + center - 5, game_window_top + 98))
    lost = distance(color, (0, 0, 0)) < distance(color, (255, 255, 0)) # check if we lost
    
    return won, lost

def restart_game() -> None:
    game_window_left, game_window_top, game_window_width, _, _ = find_game_window()
    center = game_window_width // 2
    pyautogui.doubleClick((game_window_left + center, game_window_top + 89))
    
