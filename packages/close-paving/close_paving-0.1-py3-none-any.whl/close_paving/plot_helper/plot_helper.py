# -*- coding: utf-8 -*-


import numpy as np

from close_paving.core.cell import Cell
from close_paving.core.hexagon import Hexagon
from close_paving.core.hexagonal_grid import HexagonGrid
from matplotlib import pylab as plt


def plot_hexagon(hexagon: Hexagon, *args, handler=plt, **kwargs):
    """
    绘制六角形
    :param hexagon:
    :param args:
    :param handler:
    :param kwargs:
    :return:
    """
    points = hexagon.points
    handler.plot(points[:, 0], points[:, 1], *args, **kwargs)


def plot_hexagonal_grid(hexagon_grid: HexagonGrid, *args, handler=plt, **kwargs):
    """
    绘制六角形网络
    :param hexagon_grid:
    :param args:
    :param handler:
    :param kwargs:
    :return:
    """
    cell_list = hexagon_grid.to_cells(Hexagon)
    for row_cells in cell_list:
        for hexagon in row_cells:
            plot_hexagon(hexagon, handler=handler, *args, **kwargs)
