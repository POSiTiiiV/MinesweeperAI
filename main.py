import cv2
import numpy as np
from matplotlib import pyplot as plt

from grid import tile_source, colors, TILES


def find(tile, game, t_no, board):
    global all_tiles, count

    game_gray = cv2.cvtColor(game, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(tile, 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(game_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.93
    loc = np.where(res >= threshold)
    new_count = 0
    for pt in zip(*loc[::-1]):
        all_tiles[pt] = TILES(poss_tiles[t_no], (pt[0] + w/2, pt[1] + h/2))
        cv2.rectangle(board, pt, (pt[0] + w, pt[1] + h), colors[t_no], 2)
        count += 1
        new_count += 1
    print(tile, new_count)
    print("\n")

    cv2.imwrite('win98images\\res.png', board)


# create board
img = np.zeros((512, 512, 3), np.uint8)
game_win = cv2.imread('win98images\\game_window.png')
width, height = game_win.shape[:2][::-1]
cv2.rectangle(img, (0, 0), (width, height), (0, 0, 0), 2)
# cv2.imshow('window', img)
# cv2.waitKey(0)

count = 0
all_tiles = {}
poss_tiles = tuple(tile_source.keys())
for i in range(len(poss_tiles)):
    find(tile_source[poss_tiles[i]], game_win, i, game_win)

print(count)
print(len(all_tiles))
# find(tile_source[4], 'images/game_window.png', 5, img)

