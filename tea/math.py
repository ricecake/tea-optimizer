import numpy as np
from scipy.stats import logistic 


def find_closest_point_on_line(line_point_1: np.array, line_point_2: np.array, point: np.array) -> np.array:
    """Finds the point on a line closest to a point.

    Args:
      line_point_1: A numpy array representing the first point on the line.
      line_point_2: A numpy array representing the second point on the line.
      point: A numpy array representing the point to find the closest point to.

    Returns:
      A numpy array representing the closest point on the line to the point.
    """

    # Calculate the direction vector of the line.
    line_direction = line_point_2 - line_point_1

    # Calculate the vector from the line point to the point.
    point_vector = point - line_point_1

    # Calculate the projection of the point vector onto the line direction vector.
    projection = np.dot(point_vector, line_direction) / \
        np.dot(line_direction, line_direction)

    # Calculate the closest point on the line to the point.
    closest_point = line_point_1 + projection * line_direction

    return closest_point

def scale_to_target_weight(blend_dict, weight):
    gross_weight = sum(blend_dict.values())
    factor = weight/gross_weight
    return { field: value * factor for field, value in blend_dict.items() }

def sigmoid_curve(point, middle=15, max_val=10, min_val=0.1, scale=10):
    return ((max_val-min_val)*logistic.sf(point, loc=middle, scale=scale))+min_val
#[[tea.math.sigmoid_curve(x, scale=y) for x in range(0, 20)] for y in range(1,30)] 
# This needs to be a bit more smooth
# I think that loc needs to increase by some value proportional to scale.
# need to do some experimentation to properly make it so point zero is roughly max val, and point 2*middle is roughly min val
# and we ramp down over roughly the middle third.