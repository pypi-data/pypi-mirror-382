import numpy as np
from close_paving.kernel.gen_kernel import gen_kernel

npa = np.array

vertical_left_left_kernel = npa([[1, 1, 0], [1, 1, 1], [0, 1, 1]])
vertical_right_right_kernel = npa([[0, 1, 1], [1, 1, 1], [1, 1, 0]])

vertical_left_right_kernel_odd = vertical_left_left_kernel
vertical_left_right_kernel_even = vertical_right_right_kernel
vertical_right_left_kernel_odd = vertical_right_right_kernel
vertical_right_left_kernel_even = vertical_left_left_kernel


horizontal_left_left_kernel = npa([[0, 1, 1], [1, 1, 1], [1, 1, 0]])
horizontal_right_right_kernel = npa([[1, 1, 0], [1, 1, 1], [0, 1, 1]])

horizontal_left_right_kernel_odd = horizontal_left_left_kernel
horizontal_left_right_kernel_even = horizontal_right_right_kernel
horizontal_right_left_kernel_odd = horizontal_right_right_kernel
horizontal_right_left_kernel_even = horizontal_left_left_kernel
