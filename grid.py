class TILES:
    def __init__(self, val, pos):
        self.value = val
        self.pos = pos
        self.adjTiles = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
        self.satisfied = False


tile_source = {
    '_': 'win98images\\none.png',
    0: 'win98images\\0.png',
    1: 'win98images\\1.png',
    2: 'win98images\\2.png',
    3: 'win98images\\3.png',
    4: 'win98images\\4.png',
    5: 'win98images\\5.png',
    6: 'win98images\\6.png',
    7: 'win98images\\7.png',
    8: 'win98images\\8.png',
    'f': 'win98images\\flag.png',
}

colors = (
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0),
    (76, 153, 0),
    (0, 0, 255),
    (102, 0, 0),
    (0, 0, 204),
    (204, 204, 0),
    (96, 96, 96),
    (160, 160, 160),
    (0, 0, 0)
)
