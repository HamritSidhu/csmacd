import math
import random


def randomExponential(lmda, tickSize):
    randomGaussian = random.random()
    val = (-1*1.0/lmda)*math.log(1-randomGaussian)
    X = int(round(val/tickSize))
    if X == 0:
    	return 1
    return X
