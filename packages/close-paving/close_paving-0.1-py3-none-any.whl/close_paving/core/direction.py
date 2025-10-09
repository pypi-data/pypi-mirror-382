

class Direction:
    vertical = 0
    horizontal = 1
    left_left = 0
    left_right = 2
    right_left = 4
    right_right = 6

def get_direction_tuple(direction: int) -> tuple[int, int]:
    """
    获得Direction元祖
    :param direction:
    :return:
    """
    return direction & 1, direction & 6
