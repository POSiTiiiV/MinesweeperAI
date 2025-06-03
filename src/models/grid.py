from PIL import Image, ImageDraw, ImageFont
from .tile import Tile
from ..utils.game_utils import find_game_window, find_grid, color_mapping, distance


class Grid:
    def __init__(self, tiles: list[list[Tile]]):
        self.tiles = tiles
        self.rows = len(tiles)
        self.cols = len(tiles[0])

    @classmethod
    def from_game_window(cls) -> 'Grid':
        """
        Create a Grid instance by scanning the game window.
        This class method captures the current game window, detects the grid dimensions,
        and analyzes each tile to determine its state (unopened, number, or flag).
        It creates Tile objects for each cell with appropriate values and click coordinates.
        The method:
        1. Locates the game window and grid area
        2. Calculates grid dimensions (rows and columns)
        3. Analyzes each tile's color to determine its value
        4. Creates Tile objects with appropriate states and coordinates
        5. Constructs a 2D grid of these tiles
        6. Connects neighboring tiles for later analysis
        Returns:
            Grid: A fully initialized Grid object representing the current game state
        """
        grid_left, grid_top, grid_width, grid_height, grid_img = find_grid(*find_game_window())

        rows = grid_height // 20
        cols = grid_width // 20
        grid = []
        
        for i in range(rows):
            temp = []
            for j in range(cols):
                init_left = j * 20
                init_top = i * 20
                
                # Get tile position for click coordinates
                click_x = grid_left + init_left + 9
                click_y = grid_top + init_top + 9
                
                # Analyze the tile
                color = grid_img.getpixel((init_left + 12, init_top + 14))
                val, closest = color_mapping(color)
                
                if val == 0:
                    # Check if it's an unopened tile
                    color2 = grid_img.getpixel((init_left + 1, init_top + 1))
                    if distance(color2, (255, 255, 255)) < distance(color2, closest):
                        obj = Tile(None, (click_x, click_y), (i, j))
                    else:
                        obj = Tile(val, (click_x, click_y), (i, j))
                elif val == 7:
                    # Check if it's a flag
                    color2 = grid_img.getpixel((init_left + 4, init_top + 4))
                    if distance(color2, (255, 0, 0)) < distance(color2, closest):
                        obj = Tile(None, (click_x, click_y), (i, j))
                        obj.flagged = True
                    else:
                        obj = Tile(val, (click_x, click_y), (i, j))
                else:
                    obj = Tile(val, (click_x, click_y), (i, j))
                
                temp.append(obj)
            grid.append(temp)
        
        # Create and return Grid object
        grid_obj = cls(grid)
        grid_obj.connect_neighbours()
        
        return grid_obj

    def connect_neighbours(self) -> None:
        directions = [
            ('north-west', -1, -1),
            ('north', -1, 0),
            ('north-east', -1, 1),
            ('east', 0, 1),
            ('south-east', 1, 1),
            ('south', 1, 0),
            ('south-west', 1, -1),
            ('west', 0, -1)
        ]
        for i in range(self.rows):
            for j in range(self.cols):
                for d_name, d_i, d_j in directions:
                    ni, nj = i + d_i, j + d_j
                    if 0 <= ni < self.rows and 0 <= nj < self.cols:
                        self.tiles[i][j].neighbours.append(self.tiles[ni][nj])
                        self.tiles[i][j].hidden_neighbours.add(self.tiles[ni][nj])

    def draw_rectangles(self) -> None:
        # Color mapping for tile values
        tile_colors = {
            '_': (192, 192, 192),  # Unopened tile
            'F': (255, 0, 0),      # Flag
            0: (192, 192, 192),    # Empty opened tile
            1: (0, 0, 255),        # Blue
            2: (0, 128, 0),        # Green
            3: (255, 0, 0),        # Red
            4: (0, 0, 128),        # Dark Blue
            5: (128, 0, 0),        # Dark Red
            6: (0, 128, 128),      # Cyan
            7: (0, 0, 0),          # Black
            8: (128, 128, 128)     # Gray
        }

        im = Image.open("grid.png")
        img = ImageDraw.Draw(im)
        init_left, init_top = 0, 0
        
        for i in range(self.rows):
            for j in range(self.cols):
                tile = self.tiles[i][j]
                color = tile_colors.get(tile.value, (255, 255, 255))  # Default to white if value not found
                img.rectangle(
                    [(init_left, init_top), (init_left + 18, init_top + 18)], 
                    outline='red',  # Black outline
                    fill=None,
                    width=1
                )
                init_left += 20
            init_left = 0
            init_top += 20
        
        im.show()
    
    def draw_grid(self) -> None:
        """Draw the entire grid on a new canvas based on tile values."""
        width = self.cols * 20
        height = self.rows * 20
        
        # Create new blank canvas
        canvas = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        
        # Load a larger font for better visibility
        try:
            font = ImageFont.truetype("arial.ttf", 14)  # Larger, bold font
        except:
            font = ImageFont.load_default()
        
        # Color mapping for tile values (now used for text color)
        tile_colors = {
            '_': (192, 192, 192),  # Unopened tile background
            'F': (255, 0, 0),      # Flag background
            0: (192, 192, 192),    # Empty opened tile
            1: (0, 0, 255),        # Blue text
            2: (0, 128, 0),        # Green text
            3: (255, 0, 0),        # Red text
            4: (0, 0, 128),        # Dark Blue text
            5: (128, 0, 0),        # Dark Red text
            6: (0, 128, 128),      # Cyan text
            7: (0, 0, 0),          # Black text
            8: (128, 128, 128)     # Gray text
        }
        
        init_left, init_top = 0, 0
        
        # Draw each tile
        for i in range(self.rows):
            for j in range(self.cols):
                tile = self.tiles[i][j]
                color = tile_colors.get(tile.value, (255, 255, 255))
                
                # Draw base rectangle (white background for numbers)
                if tile.value in ['_', 'F']:
                    # Fill background for unopened tiles and flags
                    draw.rectangle(
                        [(init_left, init_top), (init_left + 18, init_top + 18)],
                        fill=color,
                        outline=(0, 0, 0),
                        width=1
                    )
                else:
                    # White background for numbers
                    draw.rectangle(
                        [(init_left, init_top), (init_left + 18, init_top + 18)],
                        fill=(255, 255, 255),
                        outline=(0, 0, 0),
                        width=1
                    )
                
                # Add visual indicators
                if tile.value == '_':
                    # Add 3D effect for unopened tiles
                    draw.line([(init_left + 1, init_top + 1), (init_left + 17, init_top + 1)], 
                             fill=(255, 255, 255), width=1)
                    draw.line([(init_left + 1, init_top + 1), (init_left + 1, init_top + 17)], 
                             fill=(255, 255, 255), width=1)
                elif tile.value == 'F':
                    # Draw F symbol in black on red background
                    draw.text((init_left + 6, init_top + 2), 'F', 
                             fill=(0, 0, 0), font=font)
                elif tile.value not in ['_', 'F', 0]:
                    # Draw colored numbers with larger font
                    draw.text((init_left + 5, init_top + 1), str(tile.value), 
                             fill=color, font=font)
                
                init_left += 20
            init_left = 0
            init_top += 20
        
        canvas.save('grid_view.png')
        canvas.show()

    def show_grid(self) -> None:
        im = Image.open("grid.png")
        im.show()

    def print_grid(self) -> None:
        for i in range(self.rows):
            for j in range(self.cols):
                print(self.tiles[i][j].value, end=' ')
            print('\n')
        print('\n')

def update_grid_from_tile(tile: Tile) -> set[Tile]:
    grid_left, grid_top, _, _, grid_img = find_grid(*find_game_window())
    tiles_to_update = set()
    affected_tiles = {tile}
    for _tile in tile.neighbours:
        affected_tiles.add(_tile)
    visited = set()  # Track tiles we've already processed

    while affected_tiles:
        current_tile = affected_tiles.pop()
        pos = (current_tile.row, current_tile.col)
        if pos in visited:
            continue  # Skip if already processed
        visited.add(pos)

        x = current_tile.pos_x - grid_left + 3
        y = current_tile.pos_y - grid_top + 5
        color = grid_img.getpixel((x, y))
        val, closest = color_mapping(color)

        if val == 0:  # Possibly opened tile
            x2 = current_tile.pos_x - grid_left - 8
            y2 = current_tile.pos_y - grid_top - 8
            color2 = grid_img.getpixel((x2, y2))
            opened = distance(color2, (255, 255, 255)) > distance(color2, closest)
            if opened and current_tile.hidden:
                current_tile.value = 0
                current_tile.on_reveal()
                affected_tiles.update(current_tile.neighbours)
                tiles_to_update.update(current_tile.neighbours)
        elif val == 7:  # Possibly flagged
            x2 = current_tile.pos_x - grid_left - 5
            y2 = current_tile.pos_y - grid_top - 5
            color2 = grid_img.getpixel((x2, y2))
            is_flag = distance(color2, (255, 0, 0)) < distance(color2, closest)
            if is_flag and not current_tile.flagged:
                current_tile.value = None
                current_tile.flagged = True
                current_tile.on_flag()
                tiles_to_update.add(current_tile)
                affected_tiles.update(current_tile.neighbours)
                tiles_to_update.update(current_tile.neighbours)
            elif not current_tile.flagged:
                current_tile.value = 7
                current_tile.on_reveal()
                tiles_to_update.add(current_tile)
                affected_tiles.update(current_tile.neighbours)
                tiles_to_update.update(current_tile.neighbours)
        else:  # Numbered tile
            if current_tile.value is None:
                current_tile.value = val
                current_tile.on_reveal()
                tiles_to_update.add(current_tile)
                affected_tiles.update(current_tile.neighbours)
                tiles_to_update.update(current_tile.neighbours)

    return tiles_to_update