## Functions for fuzzy clustering
import numpy as np
import pandas as pd


def fuzzy_partition_cosine(X: pd.Series, n: int):
    """
    Midsteps of the calculation:

    D - distance vector (D) represents the relative position of each data point within the partition
    h - height, spread of the fuzzy sets
    """

    n_rows = len(X)
    x_min = X.min()
    x_max = X.max()
    
    D = np.linspace(x_min, x_max, n)
    h = (D[-1] - D[0]) / (n - 1)

    A = np.zeros((n_rows, n))

    for k in range(n_rows):
        # First column
        if (D[0] <= X[k]) and (X[k] <= D[1]):
            A[k, 0] = 0.5 * (np.cos(np.pi * (X[k] - D[0]) / h) + 1)

        # Last column    
        elif (D[n - 2] <= X[k]) and (X[k] <= D[n - 1]):
            A[k, n - 1] = 0.5 * (np.cos(np.pi * (X[k] - D[n - 1]) / h) + 1)

        # All other columns    
        for j in range(1, n - 1):
            if (D[j - 1] <= X[k]) and (X[k] <= D[j + 1]):
                A[k, j] = 0.5 * (np.cos(np.pi * (X[k] - D[j]) / h) + 1)

    return D, A


def fuzzy_partition_triangle(X: pd.Series, n: int):
    """
    Midsteps of the calculation:

    D - distance vector (D) represents the relative position of each data point within the partition
    h - height, spread of the fuzzy sets
    """

    n_rows = len(X)
    x_min = X.min()
    x_max = X.max()

    D = np.linspace(x_min, x_max, n)
    h = (D[-1] - D[0]) / (n - 1)

    A = np.zeros((n_rows, n))

    for k in range(n_rows):
        # First column
        if (D[0] <= X[k]) and (X[k] <= D[1]):
            A[k, 0] = (D[1] - X[k]) / h
        
        # Last column
        elif (D[n - 2] <= X[k]) and (X[k] <= D[n - 1]):
            A[k, n - 1] = (X[k] - D[n - 2]) / h

        # All other columns
        for j in range(1, n - 1):
            if (D[j - 1] <= X[k]) and (X[k] <= D[j]):
                A[k, j] = (X[k] - D[j - 1]) / h
            
            if (D[j] <= X[k]) and (X[k] <= D[j + 1]):
                A[k, j] = (D[j + 1] - X[k]) / h

    return D, A


def fuzzy_partition_gauss(X: pd.Series, n: int, sigma: float = 1):
    """
    Midsteps of the calculation:

    D - distance vector (D) represents the relative position of each data point within the partition
    h - height, spread of the fuzzy sets
    sigma - standard deviation of the Gaussian function
    """

    n_rows = len(X)
    x_min = X.min()
    x_max = X.max()

    D = np.linspace(x_min, x_max, n)
    A = np.zeros((n_rows, n))

    for k in range(n_rows):
        # First column
        if (D[0] <= X[k]) and (X[k] <= D[1]):
            A[k, 0] = np.exp(-((X[k] - D[0]) ** 2) / (2 * sigma**2))
        
        # Last column
        elif (D[n - 2] <= X[k]) and (X[k] <= D[n - 1]):
            A[k, n - 1] = np.exp(-((X[k] - D[n - 1]) ** 2) / (2 * sigma**2))

        # All other columns
        for j in range(1, n - 1):
            if (D[j - 1] <= X[k]) and (X[k] <= D[j + 1]):
                A[k, j] = np.exp(-((X[k] - D[j]) ** 2) / (2 * sigma**2))

    return D, A
