from math import pi


def weight(density, d, D, Na):
    area = 0.25 * pi * d ** 2
    length = pi * D
    volume = area * length
    return volume * Na * density, 0.25 * density * (pi ** 2) * (d ** 2) * D * Na


print(weight(2,3,5,6))