from close_paving.core.direction import Direction
from close_paving.core.direction import get_direction_tuple

import numpy as np
from astartool.error import ParameterValueError
from close_paving.error import TypeNotAllowedError

__all__ = [
    'gen_kernel'
]


def gen_kernel(size=3, kernel_type=Direction.left_left | Direction.vertical):
    """

    :param kernel_type:
    :return:
    """
    if size <= 0 or size & 2 == 0:
        raise ParameterValueError("Parameter `size` must be a positive odd number.")
    direction_tuple = get_direction_tuple(kernel_type)
    direction = direction_tuple[1]
    kernel = np.eye(size)
    if direction_tuple[0] == Direction.vertical:
        if direction == Direction.left_left:
            for i in range(size // 2):
                kernel += np.diag(np.ones(size - i - 1), k=i + 1)
                kernel += np.diag(np.ones(size - i - 1), k=-i - 1)
        elif direction == Direction.left_right:
            raise TypeNotAllowedError("kernel_type must be in (Direction.left_left, Direction.right_right).")
        elif direction == Direction.right_left:
            raise TypeNotAllowedError("kernel_type must be in (Direction.left_left, Direction.right_right).")
        elif direction == Direction.right_right:
            for i in range(size // 2):
                kernel += np.diag(np.ones(size - i - 1), k=i + 1)
                kernel += np.diag(np.ones(size - i - 1), k=-i - 1)
            kernel = kernel[::-1]

    else:
        kernel = np.eye(size)
        if direction == Direction.left_left:
            for i in range(size // 2):
                kernel += np.diag(np.ones(size - i - 1), k=i + 1)
                kernel += np.diag(np.ones(size - i - 1), k=-i - 1)
            kernel = kernel[::-1]
        elif direction == Direction.left_right:
            raise TypeNotAllowedError("kernel_type must be in (Direction.left_left, Direction.right_right).")
        elif direction == Direction.right_left:
            raise TypeNotAllowedError("kernel_type must be in (Direction.left_left, Direction.right_right).")
        elif direction == Direction.right_right:
            for i in range(size // 2):
                kernel += np.diag(np.ones(size - i - 1), k=i + 1)
                kernel += np.diag(np.ones(size - i - 1), k=-i - 1)
    return kernel
