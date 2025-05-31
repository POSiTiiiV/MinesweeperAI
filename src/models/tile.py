import pyautogui

class Tile:
    def __init__(self, value: int, pos: tuple[int, int], matrix_pos: tuple[int, int]) -> None:
        self.value = value
        self.flagged = False
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.row = matrix_pos[0]
        self.col = matrix_pos[1]
        self.neighbours = {
            'north-west': None,
            'north': None,
            'north-east': None,
            'east': None,
            'south-east': None,
            'south': None,
            'south-west': None,
            'west': None
        }
        self.n_neighbours = 0
        self.hidden_neighbours = set()
        self.flagged_neighbours = set()

    @property
    def numbered(self) -> bool:
        return self.value is not None and self.value != 0
    
    @property
    def hidden(self) -> bool:
        return self.value is None

    @property
    def satisfied(self) -> bool:
        return self.value == self.n_flagged_neighbours
    
    @property
    def n_hidden_neighbours(self) -> int:
        return len(self.hidden_neighbours)
    
    @property
    def n_flagged_neighbours(self) -> int:
        return len(self.flagged_neighbours)

    @property
    def satisfiable(self) -> bool:
        """Check if tile can be satisfied"""
        return self.value == self.n_hidden_neighbours + self.n_flagged_neighbours
    
    def flag_it(self) -> None:
        pyautogui.click(self.pos_x, self.pos_y, button='right')
        self.value = None
        self.flagged = True

    def on_reveal(self) -> None:
        for neighbour in self.neighbours.values():
            if neighbour and self in neighbour.hidden_neighbours:
                neighbour.hidden_neighbours.remove(self)

    def on_flag(self) -> None:
        for neighbour in self.neighbours.values():
            if neighbour and self in neighbour.flagged_neighbours:
                neighbour.flagged_neighbours.remove(self)
    
    def satisfy_tile(self) -> None:
        """Flag neighbors to satisfy the tile"""
        for neighbour in list(self.hidden_neighbours):
            if not neighbour.flagged:
                neighbour.flag_it()
                self.hidden_neighbours.remove(neighbour)
                self.flagged_neighbours.add(neighbour)

