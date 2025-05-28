import pyautogui

class Tile:
    def __init__(self, value: int | str, pos: tuple[int, int], matrix_pos: tuple[int, int]) -> None:
        self.value = value
        self.is_num_tile = True if value not in (0, '_', 'F') else False
        self.is_hidden = True if value in ('_', 'F') else False
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.row = matrix_pos[0]
        self.col = matrix_pos[1]
        self.satisfied = False
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
    
    def look_around_for_flags(self) -> list:
        flags_around_tile = []
        for neighbour_tile in list(self.neighbours.values()):
            if neighbour_tile is not None and neighbour_tile.value == 'F':
                flags_around_tile.append(neighbour_tile)
        
        return flags_around_tile

    def flag_it(self) -> None:
        if self.value != 'F':
            pyautogui.click(self.pos_x, self.pos_y, button='right')
            self.value = 'F'
            self.is_hidden = True
            self.is_num_tile = False

    def is_satisfied(self) -> bool:
        if self.value == 0:
            return True
        flag_around_tile = self.look_around_for_flags()
        if self.value == len(flag_around_tile):
            self.satisfied = True
            return True
        return False
        
    def can_be_satisfied(self) -> bool:
        list_of_unopened_neighbours = self.look_for_unopened_neighbours()
        if self.value == len(list_of_unopened_neighbours):
            for neighbour in list_of_unopened_neighbours:
                neighbour.flag_it()
            
        return self.is_satisfied()

    def look_for_unopened_neighbours(self) -> list:
        list_of_neighbours = list(self.neighbours.values())
        list_of_unopened_neighbours = []
        for neighbour in list_of_neighbours:
            if neighbour is not None and neighbour.is_hidden:
                list_of_unopened_neighbours.append(neighbour)

        return list_of_unopened_neighbours
