import math

def bound_radian(value):
    while value > 2 * math.pi:
        value -= 2 * math.pi
    while value < 0:
        value += 2 * math.pi
    return value
