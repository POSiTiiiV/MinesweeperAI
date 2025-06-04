import pygame

class Tile:
    bomb_img = None
    hidden_img = None
    revealed_img = None
    flagged_img = None
    font = None

    @classmethod
    def load_assets(cls, bomb_path: str, hidden_path: str, revealed_path: str, flagged_path: str, font: pygame.font.Font):
        cls.bomb_img = pygame.image.load(bomb_path).convert()
        cls.hidden_img = pygame.image.load(hidden_path).convert()
        cls.revealed_img = pygame.image.load(revealed_path).convert()
        cls.flagged_img = pygame.image.load(flagged_path).convert()
        cls.font = font
    
    def __init__(self, value: int | None, pos: tuple[int, int], matrix_pos: tuple[int, int], tile_size: int) -> None:
        self.value = value
        self.is_hidden = True
        self.is_flagged = False
        self.is_bomb = False
        self.pos_x, self.pos_y = pos
        self.row, self.col = matrix_pos
        self.tile_size = tile_size
        self.neighbours = list['Tile']()
        self.hidden_neighbours = set['Tile']()
        self.flagged_neighbours = set['Tile']()

    @property
    def is_numbered(self) -> bool:
        return self.value is not None and self.value != 0
    
    @property
    def is_satisfied(self) -> bool:
        return self.value == self.n_flagged_neighbours
    
    @property
    def n_neighbours(self) -> int:
        return len(self.neighbours)
    
    @property
    def n_hidden_neighbours(self) -> int:
        return len(self.hidden_neighbours)
    
    @property
    def n_flagged_neighbours(self) -> int:
        return len(self.flagged_neighbours)

    @property
    def is_satisfiable(self) -> bool:
        """Check if tile can be satisfied"""
        return self.value == self.n_hidden_neighbours + self.n_flagged_neighbours
    
    def get_color(self) -> tuple[int, int, int]:
        tile_colors = {
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
        return tile_colors[self.value]

    def draw(self, game_window: pygame.Surface):
        # Determine which image to use
        if self.is_hidden:
            img = self.flagged_img if self.is_flagged else self.hidden_img
        elif self.is_bomb:
            img = self.bomb_img
        else:
            img = self.revealed_img
            
        # Scale and draw the base tile image
        scaled_img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
        game_window.blit(scaled_img, (self.pos_x, self.pos_y))
        
        # Add number text if its already revealed
        if not self.is_hidden and self.is_numbered:
            text_surface = self.font.render(str(self.value), True, self.get_color())
            text_rect = text_surface.get_rect(center=(
                self.pos_x + self.tile_size // 2,
                self.pos_y + self.tile_size // 2
            ))
            game_window.blit(text_surface, text_rect)

    def reveal(self, game_window: pygame.Surface) -> None:
        if not self.is_hidden:
            return  # Already revealed

        queue = [self]
        visited = set()

        while queue:
            tile = queue.pop()
            if tile in visited:
                continue
            visited.add(tile)
            tile.is_hidden = False
            tile.draw(game_window)

            if tile.value == 0:
                for neighbor in tile.neighbours:
                    if neighbor.is_hidden and neighbor not in visited:
                        queue.append(neighbor)

    def flag(self, game_window: pygame.Surface) -> None:
        if self.is_flagged:
            self.is_flagged = False
        else:
            self.is_flagged = True
        self.draw(game_window)

    def on_reveal(self) -> None:
        for neighbour in self.neighbours:
            if self in neighbour.hidden_neighbours:
                neighbour.hidden_neighbours.remove(self)

    def on_flag(self) -> None:
        for neighbour in self.neighbours:
            if self not in neighbour.flagged_neighbours:
                neighbour.flagged_neighbours.add(self)
    
    def satisfy_tile(self) -> None:
        """Flag neighbors to satisfy the tile"""
        for neighbour in list(self.hidden_neighbours):
            if not neighbour.flagged:
                neighbour.flag_it()
                self.hidden_neighbours.remove(neighbour)
                self.flagged_neighbours.add(neighbour)

