from typing import List, Tuple, Union

import numpy as np

from close_paving.core.cell import Cell
from close_paving.core.direction import Direction


class Hexagon(Cell):
    def __init__(self, center: Union[List[float], np.ndarray, Tuple[float]] = (0, 0),
                 radius: float = 0.0,
                 direction=Direction.horizontal, **kwargs):
        assert radius >= 0
        super().__init__()
        self.center = np.array(center)
        self.radius = radius
        self.direction = direction
        self.__dict__.update(kwargs)

    @property
    def points(self):
        if self.direction == Direction.vertical:
            half_r = self.radius / 2
            root3_half_r = np.sqrt(3) * half_r
            x1, x2, x3, x4, x5, x6 = -root3_half_r, 0, root3_half_r, root3_half_r, 0, -root3_half_r
            y1, y2, y3, y4, y5, y6 = -half_r, -self.radius, -half_r, half_r, self.radius, half_r

            delta = np.vstack([
                [x1, y1], [x2, y2], [x3, y3], [x4, y4], [x5, y5], [x6, y6], [x1, y1]
            ])
            center = np.vstack([self.center] * 7)
            return center + delta
        else:
            half_r = self.radius / 2
            root3_half_r = np.sqrt(3) * half_r
            x1, x2, x3, x4, x5, x6 = -half_r, half_r, self.radius, half_r, -half_r, -self.radius
            y1, y2, y3, y4, y5, y6 = -root3_half_r, -root3_half_r, 0, root3_half_r, root3_half_r, 0
            delta = np.vstack([
                [x1, y1], [x2, y2], [x3, y3], [x4, y4], [x5, y5], [x6, y6], [x1, y1]
            ])
            center = np.vstack([self.center] * 7)
            return center + delta


class HorizontalHexagon(Hexagon):
    def __init__(self, center: Union[List[float], np.ndarray, Tuple[float]] = (0, 0),
                 radius: float = 0.0):
        super().__init__(center, radius, direction=Direction.horizontal)


class VerticalHexagon(Hexagon):
    def __init__(self, center: Union[List[float], np.ndarray, Tuple[float]] = (0, 0),
                 radius: float = 0.0):
        super().__init__(center, radius, direction=Direction.vertical)
