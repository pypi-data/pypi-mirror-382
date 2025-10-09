import itertools
from typing import List, Tuple, Union, Dict, Iterable

import numpy as np
from astartool.error import ParameterTypeError, ParameterValueError

from close_paving.core.cell import Cell
from close_paving.core.direction import Direction, get_direction_tuple
from close_paving.error import TypeNotAllowedError

npl = np.linalg

SQRT3 = np.sqrt(3)


class HexagonGrid:
    def __init__(self, seed: Union[List[float], np.ndarray, Tuple[float]] = (0, 0),
                 radius: float = 0.0,
                 shape: Tuple[int, int] = (0, 0),
                 direction=Direction.vertical | Direction.left_right,
                 value_list: Dict[str, Union[np.ndarray, list]] = None):
        self.seed = np.array(seed)
        self.radius = radius
        self.shape = shape
        self.direction = direction
        if value_list is None:
            self.value_dict = None
        elif isinstance(value_list, dict):
            self.value_dict = value_list
        elif isinstance(value_list, np.ndarray):
            self.value_dict = {"value": value_list}
        else:
            raise ParameterTypeError("Type of `value_list` must be list or np.ndarray.")

    def to_cells(self, class_type=Cell, *args, **kwargs):
        """
        获取元胞矩阵
        :param class_type: 元胞类型
        :param args:
        :param kwargs:
        :return:
        """
        half_radius = self.radius / 2
        one_and_a_half_radius = half_radius + self.radius
        root3_radius = SQRT3 * self.radius
        root3_half_radius = root3_radius / 2
        x = np.empty(shape=self.shape)
        y = np.empty(shape=self.shape)
        direction_tuple = get_direction_tuple(self.direction)
        direction = direction_tuple[0]
        if direction == Direction.horizontal:
            if direction_tuple[1] == Direction.right_right:
                xi = self.seed[0] + one_and_a_half_radius * np.arange(self.shape[0])
                x = np.repeat(np.expand_dims(xi, 1), self.shape[1], axis=1)
                yi = self.seed[1] + root3_radius * np.arange(self.shape[1])
                for col in range(0, self.shape[0]):
                    y[col, :] = yi - root3_half_radius * col
            elif direction_tuple[1] == Direction.right_left:
                xi = self.seed[0] + one_and_a_half_radius * np.arange(self.shape[0])
                x = np.repeat(np.expand_dims(xi, 1), self.shape[1], axis=1)
                yi = self.seed[1] + root3_radius * np.arange(self.shape[1])
                yii = yi - root3_half_radius
                for col in range(0, self.shape[0], 2):
                    y[col, :] = yi
                for col in range(1, self.shape[0], 2):
                    y[col, :] = yii
            elif direction_tuple[1] == Direction.left_right:
                xi = self.seed[0] + one_and_a_half_radius * np.arange(self.shape[0])
                x = np.repeat(np.expand_dims(xi, 1), self.shape[1], axis=1)
                yi = self.seed[1] + root3_radius * np.arange(self.shape[1])
                yii = yi + root3_half_radius
                for col in range(0, self.shape[0], 2):
                    y[col, :] = yi
                for col in range(1, self.shape[0], 2):
                    y[col, :] = yii
            elif direction_tuple[1] == Direction.left_left:
                xi = self.seed[0] + one_and_a_half_radius * np.arange(self.shape[0])
                x = np.repeat(np.expand_dims(xi, 1), self.shape[1], axis=1)
                yi = self.seed[1] + root3_radius * np.arange(self.shape[1])
                for col in range(0, self.shape[0]):
                    y[col, :] = yi + root3_half_radius * col
            else:
                raise ParameterValueError("Value of `direction` is unknown")
        else:
            if direction_tuple[1] == Direction.right_right:
                xi = self.seed[0] + root3_radius * np.arange(self.shape[0])
                for row in range(0, self.shape[1]):
                    x[:, row] = xi + root3_half_radius * row
                yi = self.seed[1] + one_and_a_half_radius * np.arange(self.shape[1])
                y = np.repeat(yi.reshape((1, -1)), self.shape[0], axis=0)
            elif direction_tuple[1] == Direction.right_left:
                xi = self.seed[0] + root3_radius * np.arange(self.shape[0])
                xii = xi + root3_half_radius
                for row in range(0, self.shape[1], 2):
                    x[:, row] = xi
                for row in range(1, self.shape[1], 2):
                    x[:, row] = xii
                yi = self.seed[1] + one_and_a_half_radius * np.arange(self.shape[1])
                y = np.repeat(yi.reshape((1, -1)), self.shape[0], axis=0)
            elif direction_tuple[1] == Direction.left_right:
                xi = self.seed[0] + root3_radius * np.arange(self.shape[0])
                xii = xi - root3_half_radius
                for row in range(0, self.shape[1], 2):
                    x[:, row] = xi
                for row in range(1, self.shape[1], 2):
                    x[:, row] = xii
                yi = self.seed[1] + one_and_a_half_radius * np.arange(self.shape[1])
                y = np.repeat(yi.reshape((1, -1)), self.shape[0], axis=0)
            elif direction_tuple[1] == Direction.left_left:
                xi = self.seed[0] + root3_radius * np.arange(self.shape[0])
                for row in range(0, self.shape[1]):
                    x[:, row] = xi - root3_half_radius * row
                yi = self.seed[1] + one_and_a_half_radius * np.arange(self.shape[1])
                y = np.repeat(yi.reshape((1, -1)), self.shape[0], axis=0)
            else:
                raise ParameterValueError("Value of `direction` is unknown")
        if self.value_dict is None:
            return [
                [class_type(center=(x[i, j], y[i, j]), radius=self.radius, direction=direction, *args, **kwargs) for j
                 in range(self.shape[1])] for i in range(self.shape[0])]
        else:
            return [[class_type(center=(x[i, j], y[i, j]), radius=self.radius, direction=direction, *args,
                                **{k: v[i][j] for k, v in self.value_dict.items()}) for j in
                     range(self.shape[1])] for i in range(self.shape[0])]

    def filter_index(self, indexes: Iterable[Tuple[int, int]]):
        """
        按元胞形状过滤异常的索引, 异常的坐标将返回None
        :param indexes:
        :return:
        """
        return [(index if (0 <= index[0] < self.shape[0]) and (0 <= index[1] < self.shape[1]) else None) for index in
                indexes]

    def get_distance(self, src_index, dst_index):
        """
        返回两坐标之间的距离
        :param src_index:
        :param dst_index:
        :return:
        """
        src_index = tuple(src_index)
        dst_index = tuple(dst_index)
        if not (0 <= src_index[0] < self.shape[0]):
            raise ParameterValueError("src_index is out of bounds")

        if not (0 <= src_index[1] < self.shape[1]):
            raise ParameterValueError("src_index is out of bounds")

        if not (0 <= dst_index[0] < self.shape[0]):
            raise ParameterValueError("dst_index is out of bounds")

        if not (0 <= dst_index[1] < self.shape[1]):
            raise ParameterValueError("dst_index is out of bounds")

        direction_tuple = get_direction_tuple(self.direction)
        direction = direction_tuple[1]
        if direction_tuple[0] == Direction.vertical:
            if direction == Direction.left_left:
                if dst_index[1] > src_index[1]:
                    height_delta = abs(dst_index[1] - src_index[1])
                    bound_low = src_index[0]
                    bound_high = min(src_index[0] + height_delta, self.shape[0] - 1)
                else:
                    height_delta = abs(dst_index[1] - src_index[1])
                    bound_low = max(src_index[0] - height_delta, 0)
                    bound_high = src_index[0]

                if dst_index[0] < bound_low:
                    return height_delta + bound_low - dst_index[0]
                elif bound_low <= dst_index[0] <= bound_high:
                    return height_delta
                else:
                    return height_delta + dst_index[0] - bound_high

            elif direction == Direction.left_right:
                src_col_is_odd = src_index[1] % 2
                dst_col_is_odd = dst_index[1] % 2
                if dst_index[1] > src_index[1]:
                    delta = (dst_index[1] - src_index[1]) // 2
                else:
                    delta = - (dst_index[1] - src_index[1]) // 2
                if src_col_is_odd and dst_col_is_odd:
                    height_delta = abs(dst_index[1] - src_index[1])
                    bound_low = src_index[0] - delta
                    bound_high = src_index[0] + delta
                    if bound_low <= dst_index[0] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[0]), abs(dst_index[0] - bound_high))
                elif src_col_is_odd and not dst_col_is_odd:
                    height_delta = abs(dst_index[1] - src_index[1])
                    bound_low = src_index[0] - delta - 1
                    bound_high = src_index[0] + delta
                    if bound_low <= dst_index[0] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[0]), abs(dst_index[0] - bound_high))


                elif not src_col_is_odd and dst_col_is_odd:
                    height_delta = abs(dst_index[1] - src_index[1])
                    if dst_index[1] < src_index[1]:
                        bound_low = max(0, src_index[0] - delta)
                        bound_high = min(src_index[0] + delta + 1, self.shape[0] - 1)
                    else:
                        bound_low = max(0, src_index[0] - delta)
                        bound_high = min(src_index[0] + delta + 1, self.shape[0] - 1)

                    if bound_low <= dst_index[0] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[0]), abs(dst_index[0] - bound_high))
                else:
                    # not src_col_is_odd and not dst_col_is_odd
                    height_delta = abs(dst_index[1] - src_index[1])
                    bound_low = src_index[0] - delta
                    bound_high = src_index[0] + delta
                    if bound_low <= dst_index[0] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[0]), abs(dst_index[0] - bound_high))
            elif direction == Direction.right_left:
                src_col_is_odd = src_index[1] % 2
                dst_col_is_odd = dst_index[1] % 2
                if dst_index[1] > src_index[1]:
                    delta = (dst_index[1] - src_index[1]) // 2
                else:
                    delta = - (dst_index[1] - src_index[1]) // 2
                if src_col_is_odd and dst_col_is_odd:
                    height_delta = abs(dst_index[1] - src_index[1])
                    bound_low = src_index[0] - delta
                    bound_high = src_index[0] + delta
                    if bound_low <= dst_index[0] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[0]), abs(dst_index[0] - bound_high))
                elif src_col_is_odd and not dst_col_is_odd:
                    height_delta = abs(dst_index[1] - src_index[1])
                    bound_low = src_index[0] - delta
                    bound_high = src_index[0] + delta + 1
                    if bound_low <= dst_index[0] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[0]), abs(dst_index[0] - bound_high))


                elif not src_col_is_odd and dst_col_is_odd:
                    height_delta = abs(dst_index[1] - src_index[1])
                    bound_low = max(0, src_index[0] - delta - 1)
                    bound_high = min(src_index[0] + delta, self.shape[0] - 1)
                    if bound_low <= dst_index[0] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[0]), abs(dst_index[0] - bound_high))
                else:
                    # not src_col_is_odd and not dst_col_is_odd
                    height_delta = abs(dst_index[1] - src_index[1])
                    bound_low = src_index[0] - delta
                    bound_high = src_index[0] + delta
                    if bound_low <= dst_index[0] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[0]), abs(dst_index[0] - bound_high))
            elif direction == Direction.right_right:
                if dst_index[1] > src_index[1]:
                    height_delta = abs(dst_index[1] - src_index[1])
                    bound_low = max(src_index[0] - height_delta, 0)
                    bound_high = src_index[0]
                else:
                    height_delta = abs(dst_index[1] - src_index[1])
                    bound_low = src_index[0]
                    bound_high = min(src_index[0] + height_delta, self.shape[0])

                if bound_low <= dst_index[0] <= bound_high:
                    return height_delta
                else:
                    return height_delta + min(abs(bound_low - dst_index[0]), abs(dst_index[0] - bound_high))
            else:
                raise TypeNotAllowedError(
                    "`direction` must be in (Direction.left_left, Direction.left_right, Direction.right_left, Direction.right_right)")
        else:
            if direction == Direction.left_left:
                delta = dst_index[0] - src_index[0]
                if delta >= 0:
                    bound_low = max(0, src_index[1] - delta)
                    bound_high = src_index[1]
                else:
                    delta = -delta
                    bound_low = src_index[1]
                    bound_high = min(self.shape[1] - 1, src_index[1] + delta)
                if dst_index[1] < bound_low:
                    return delta + bound_low - dst_index[1]
                elif bound_low <= dst_index[1] <= bound_high:
                    return delta
                else:
                    return delta + dst_index[1] - bound_high

            elif direction == Direction.left_right:
                src_col_is_odd = src_index[0] % 2
                dst_col_is_odd = dst_index[0] % 2
                if dst_index[0] > src_index[0]:
                    delta = (dst_index[0] - src_index[0]) // 2
                else:
                    delta = - (dst_index[0] - src_index[0]) // 2
                if src_col_is_odd and dst_col_is_odd:
                    height_delta = abs(dst_index[0] - src_index[0])
                    bound_low = src_index[1] - delta
                    bound_high = src_index[1] + delta
                    if bound_low <= dst_index[1] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[1]), abs(dst_index[1] - bound_high))
                elif src_col_is_odd and not dst_col_is_odd:
                    height_delta = abs(dst_index[0] - src_index[0])
                    bound_low = src_index[1] - delta
                    bound_high = src_index[1] + delta + 1
                    if bound_low <= dst_index[1] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[1]), abs(dst_index[1] - bound_high))


                elif not src_col_is_odd and dst_col_is_odd:
                    height_delta = abs(dst_index[0] - src_index[0])
                    bound_low = max(0, src_index[1] - delta - 1)
                    bound_high = min(src_index[1] + delta, self.shape[1] - 1)

                    if bound_low <= dst_index[1] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[1]), abs(dst_index[1] - bound_high))
                else:
                    # not src_col_is_odd and not dst_col_is_odd
                    height_delta = abs(dst_index[0] - src_index[0])
                    bound_low = src_index[1] - delta
                    bound_high = src_index[1] + delta
                    if bound_low <= dst_index[1] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[1]), abs(dst_index[1] - bound_high))
            elif direction == Direction.right_left:
                src_col_is_odd = src_index[0] % 2
                dst_col_is_odd = dst_index[0] % 2
                if dst_index[0] > src_index[0]:
                    delta = (dst_index[0] - src_index[0]) // 2
                else:
                    delta = - (dst_index[0] - src_index[0]) // 2
                if src_col_is_odd and dst_col_is_odd:
                    height_delta = abs(dst_index[0] - src_index[0])
                    bound_low = src_index[1] - delta
                    bound_high = src_index[1] + delta
                    if bound_low <= dst_index[1] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[1]), abs(dst_index[1] - bound_high))
                elif src_col_is_odd and not dst_col_is_odd:
                    height_delta = abs(dst_index[0] - src_index[0])
                    bound_low = src_index[1] - delta - 1
                    bound_high = src_index[1] + delta
                    if bound_low <= dst_index[1] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[1]), abs(dst_index[1] - bound_high))

                elif not src_col_is_odd and dst_col_is_odd:
                    height_delta = abs(dst_index[0] - src_index[0])
                    bound_low = max(0, src_index[1] - delta)
                    bound_high = min(src_index[1] + delta + 1, self.shape[1] - 1)
                    if bound_low <= dst_index[1] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[1]), abs(dst_index[1] - bound_high))
                else:
                    # not src_col_is_odd and not dst_col_is_odd
                    height_delta = abs(dst_index[0] - src_index[0])
                    bound_low = src_index[1] - delta
                    bound_high = src_index[1] + delta
                    if bound_low <= dst_index[1] <= bound_high:
                        return height_delta
                    else:
                        return height_delta + min(abs(bound_low - dst_index[1]), abs(dst_index[1] - bound_high))
            elif direction == Direction.right_right:

                if dst_index[0] > src_index[0]:
                    height_delta = abs(dst_index[0] - src_index[0])
                    bound_low = src_index[1]
                    bound_high = min(src_index[1] + height_delta, self.shape[1])
                else:
                    height_delta = abs(dst_index[0] - src_index[0])
                    bound_low = max(0, src_index[1] - height_delta)
                    bound_high = src_index[1]

                if bound_low <= dst_index[1] <= bound_high:
                    return height_delta
                else:
                    return height_delta + min(abs(bound_low - dst_index[1]), abs(dst_index[1] - bound_high))

            else:
                raise TypeNotAllowedError(
                    "`direction` must be in (Direction.left_left, Direction.left_right, Direction.right_left, Direction.right_right)")

    def neighbours(self, c, distance=1):
        """
        获取坐标c distance范围内的所有坐标
        :param c:
        :param distance:
        :return:
        """

        bound_x = (max(0, c[0] - distance - 1), min(self.shape[0], c[0] + distance + 1))
        bound_y = (max(0, c[1] - distance - 1), min(self.shape[1], c[1] + distance + 1))
        return set(filter(lambda x: self.get_distance(x, c) <= distance,
                          itertools.product(range(*bound_x), range(*bound_y)))) - {c}
