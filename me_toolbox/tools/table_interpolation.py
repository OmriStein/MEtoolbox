"""module containing the table interpolation function"""
import numpy as np


class NotInRangeError(ValueError):
    def __init__(self, var, num, range_):
        """Error for when value is not in the specified range

        :param str var: var assigned to
        :param float num: num to assign
        :param tuple range_: permitted range
        """

        self.num = num
        self.range_ = range_
        self.msg = f"{var} = {num} not in range {range_}"
        super().__init__(self.msg)


def table_interpolation(x_row, x_col, data):
    """ Get table in numpy array form and two coordinates and
    Interpolate the value in the table corresponding to those coordinates

    :keyword x_row: the x row from which to retrieve the value
    :type x_row: float
    :keyword x_col: the x col from which to retrieve the value
    :type x_col: float
    :keyword data: the table as numpy array
    :type data: np.ndarray
    :rtype: float
    """

    # first gear number of known teeth values
    first_column = data[:, 0]

    # second gear number of known teeth values
    first_row = data[0, :]

    if x_col > first_row[-1] or x_col < first_row[1]:
        raise NotInRangeError("x_col", x_col, (first_row[1], first_row[-1]))

    if x_row > first_column[-1] or x_row < first_column[1]:
        raise NotInRangeError("x_row", x_row, (first_column[1], first_column[-1]))

    # upper bounds indexes of x_row and x_col
    index1 = np.searchsorted(first_column, x_row, side='right')
    index2 = np.searchsorted(first_row, x_col, side='right')

    try:
        # get x_row neighbors
        x_row_low, x_row_high = data[index1 - 1, 0], data[index1, 0]
    except IndexError:
        # if x_row upper neighbor is out of the table range
        x_row_low, x_row_high = data[index1 - 1, 0], np.nan
    try:
        # get x_col neighbors
        x_col_low, x_col_high = data[0, index2 - 1], data[0, index2]
    except IndexError:
        # if x_col upper neighbor is out of the table range
        x_col_low, x_col_high = data[0, index2 - 1], np.nan

    # if gear teeth number is not in the table do an
    # interpolation on closest values inside the table
    if x_row == x_row_low and x_col == x_col_low:
        # x_row and x_col are known no need to interpolate
        result = data[index1 - 1, index2 - 1]
    elif x_row == x_row_low:
        # x_row is known and x_col is interpolated
        result = np.interp(x_col, data[0, :], data[index1 - 1, :])
    elif x_col == x_col_low:
        # x_col is known and x_row is interpolated
        result = np.interp(x_row, data[:, 0], data[:, index2 - 1])
    else:
        # both are unknown and interpolated
        lower_bound = np.interp(x_row, data[:, 0], data[:, index2 - 1])
        upper_bound = np.interp(x_row, data[:, 0], data[:, index2])
        range_ = np.array([data[0, index2 - 1], data[0, index2]])
        bounds = np.array([lower_bound, upper_bound])
        result = np.interp(x_col, range_, bounds)

    return result
