import math

def o_dist(pos_1, pos_2):
    sum = 0
    for i in range(len(pos_1)):
        sum += (pos_1[i] - pos_2[i]) ** 2

    return math.sqrt(sum)

def decay(epoch, epochs, start_range):
    return start_range * (1 - epoch / epochs)

def hci(dist, field_range):
    return math.e ** (- dist ** 2 / (2 * field_range ** 2))