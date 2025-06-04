import pygame
from random import shuffle
from minesweeper.tile import Tile


class Grid:
    def __init__(self, rows: int, cols: int, tile_size: int, tiles: list[list[Tile]], game_window: pygame.Surface, n_bombs: int, buffer: int):
        self.game_window = game_window
        self.tiles = tiles
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size
        self.n_bombs = n_bombs
        self.buffer = buffer

    @classmethod
    def make_grid(cls, game_window: pygame.Surface, rows: int, cols: int, tile_size: int, n_bombs: int, buffer: int) -> 'Grid':
        grid = []
        for r in range(rows):
            temp = []
            for c in range(cols):
                pos_x = c * (tile_size + buffer)
                pos_y = r * (tile_size + buffer)
                tile = Tile(None, (pos_x, pos_y), (r, c), tile_size)
                temp.append(tile)
            grid.append(temp)
        grid_obj = cls(rows, cols, tile_size, grid, game_window, n_bombs, buffer)
        grid_obj.connect_neighbours()

        return grid_obj

    def draw_grid(self):
        self.game_window.fill((192, 192, 192))
        for row in self.tiles:
            for tile in row:
                tile.draw(self.game_window)
        pygame.display.flip()

    def connect_neighbours(self) -> None:
        directions = [
            (-1, -1), # north-west
            (-1, 0),  # north
            (-1, 1),  # north-east
            (0, 1),   # east
            (1, 1),   # south-east
            (1, 0),   # south
            (1, -1),  # south-west
            (0, -1)   # west
        ]
        for i in range(self.rows):
            for j in range(self.cols):
                for d_i, d_j in directions:
                    ni, nj = i + d_i, j + d_j
                    if 0 <= ni < self.rows and 0 <= nj < self.cols:
                        self.tiles[i][j].neighbours.append(self.tiles[ni][nj])
                        self.tiles[i][j].hidden_neighbours.add(self.tiles[ni][nj])

    def place_bombs(self, all_tiles: list[Tile]) -> list[Tile]:
        shuffle(all_tiles)
        bomb_tiles = all_tiles[:self.n_bombs]
        for tile in bomb_tiles:
            tile.is_bomb = True
        
        return bomb_tiles
    
    def set_numbers(self, all_tiles: list[Tile], bomb_tiles: list[Tile]) -> None:
        # First, set all non-bomb tiles to 0
        for tile in all_tiles:
            if tile not in bomb_tiles:
                tile.value = 0
        
        # Then increment neighbors of bomb tiles
        for bomb in bomb_tiles:
            bomb.value = None  # Ensure bombs have None value
            for neighbor in bomb.neighbours:
                if neighbor not in bomb_tiles:
                    neighbor.value += 1
  

    def print_grid(self) -> None:
        for i in range(self.rows):
            for j in range(self.cols):
                print(self.tiles[i][j].value, end=' ')
            print('\n')
        print('\n')

# def update_grid_from_tile(tile: Tile) -> set[Tile]:
#     grid_left, grid_top, _, _, grid_img = find_grid(*find_game_window())
#     tiles_to_update = set()
#     affected_tiles = {tile}
#     for _tile in tile.neighbours:
#         affected_tiles.add(_tile)
#     visited = set()  # Track tiles we've already processed

#     while affected_tiles:
#         current_tile = affected_tiles.pop()
#         pos = (current_tile.row, current_tile.col)
#         if pos in visited:
#             continue  # Skip if already processed
#         visited.add(pos)

#         x = current_tile.pos_x - grid_left + 3
#         y = current_tile.pos_y - grid_top + 5
#         color = grid_img.getpixel((x, y))
#         val, closest = color_mapping(color)

#         if val == 0:  # Possibly opened tile
#             x2 = current_tile.pos_x - grid_left - 8
#             y2 = current_tile.pos_y - grid_top - 8
#             color2 = grid_img.getpixel((x2, y2))
#             opened = distance(color2, (255, 255, 255)) > distance(color2, closest)
#             if opened and current_tile.hidden:
#                 current_tile.value = 0
#                 current_tile.on_reveal()
#                 affected_tiles.update(current_tile.neighbours)
#                 tiles_to_update.update(current_tile.neighbours)
#         elif val == 7:  # Possibly flagged
#             x2 = current_tile.pos_x - grid_left - 5
#             y2 = current_tile.pos_y - grid_top - 5
#             color2 = grid_img.getpixel((x2, y2))
#             is_flag = distance(color2, (255, 0, 0)) < distance(color2, closest)
#             if is_flag and not current_tile.flagged:
#                 current_tile.value = None
#                 current_tile.flagged = True
#                 current_tile.on_flag()
#                 tiles_to_update.add(current_tile)
#                 affected_tiles.update(current_tile.neighbours)
#                 tiles_to_update.update(current_tile.neighbours)
#             elif not current_tile.flagged:
#                 current_tile.value = 7
#                 current_tile.on_reveal()
#                 tiles_to_update.add(current_tile)
#                 affected_tiles.update(current_tile.neighbours)
#                 tiles_to_update.update(current_tile.neighbours)
#         else:  # Numbered tile
#             if current_tile.value is None:
#                 current_tile.value = val
#                 current_tile.on_reveal()
#                 tiles_to_update.add(current_tile)
#                 affected_tiles.update(current_tile.neighbours)
#                 tiles_to_update.update(current_tile.neighbours)

#     return tiles_to_update
