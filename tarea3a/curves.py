import numpy as np
from modelo import *

def generateT(t):
    return np.array([[1, t, t ** 2, t ** 3]]).T

def catmullromMatrix(P0, P1, P2, P3): # c, i
    # Catmull-Roll base maxtrix is a constant
    Mcr = (1/2)*np.array([[0,-1,2,-1], [2,0,-5,3],[0,1,4,-3],[0,0,-1,1]])

    # Generate a maxtrix concatenating the columns G = np.concatenate((c[i-1], c[i], c[i+1], c[i+2]), axis = 1)
    G = np.concatenate((P0, P1, P2, P3), axis = 1)

    return np.matmul(G,Mcr)

def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)

    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)

    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T  # x, y, z

    return curve  # N x 3