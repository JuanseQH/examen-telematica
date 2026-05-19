import random
from constants import SHAPES, SHAPE_COLORS, GRID_WIDTH

class Piece:
    def __init__(self, shape_name=None):
        if shape_name:
            self.shape_name = shape_name
        else:
            self.shape_name = random.choice(list(SHAPES.keys()))
        
        self.shape = SHAPES[self.shape_name]
        self.color = SHAPE_COLORS[self.shape_name]
        self.rotation = 0
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        self.rotation = (self.rotation + 1) % 4 