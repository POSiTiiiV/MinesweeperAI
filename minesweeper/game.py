import pygame
from grid import Grid
from tile import Tile
import os
import time

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
SCREEN_WIDTH = SCREEN_HEIGHT = 628
ROWS, COLS = 8, 8
TILE_SIZE = 75
N_BOMBS = 10
BUFFER = 4

pygame.init()

game_window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MinesweeperAI")

def get_tile_at_pos(mouse_x, mouse_y, tile_size, buffer) -> tuple[int, int]:
    col = mouse_x // (tile_size + buffer)
    row = mouse_y // (tile_size + buffer)
    return int(row), int(col)

def start():
    grid = Grid.make_grid(game_window, ROWS, COLS, TILE_SIZE, N_BOMBS, BUFFER)
    grid.draw_grid()

    return grid

def main():
    # Load images and font for all tiles
    Tile.load_assets(
        bomb_path=os.path.join(ASSETS_DIR, 'bomb.png'),
        hidden_path=os.path.join(ASSETS_DIR, 'hidden2.png'),
        revealed_path=os.path.join(ASSETS_DIR, 'revealed.png'),
        flagged_path=os.path.join(ASSETS_DIR, 'flag1.png'),
        font=pygame.font.Font('freesansbold.ttf', 32)
    )

    grid = start()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                row, col = get_tile_at_pos(mouse_x, mouse_y, TILE_SIZE, BUFFER)
                if 0 <= row < ROWS and 0 <= col < COLS:
                    tile = grid.tiles[row][col]
                    if event.button == 1:
                        tile.reveal(game_window)
                        if tile.is_bomb:
                            print("Clicked on a bomb sire, restarting")
                            time.sleep(2)
                            grid = start()
                            break
                    elif event.button == 3:
                        tile.flag(game_window)
                    pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
