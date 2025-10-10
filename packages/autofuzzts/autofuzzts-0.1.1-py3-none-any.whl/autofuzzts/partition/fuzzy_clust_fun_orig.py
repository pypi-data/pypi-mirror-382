## Functions for fuzzy clustering
import numpy as np
import pandas as pd


def fuzzy_partition_cosine(X: pd.Series, n:float):
    '''

    Midsteps of the calculation:

    D - distance vector (D) represents the relative position of each data point within the partition
    h - height, spread of the fuzzy sets 

    '''

    n_rows = len(X)
    x_spread = X.max() - X.min() # spread of the data

    D = np.zeros((n,1))
    for i in range(0,n):
        D[i] = i/(n-1)*x_spread   # D is adjusted by the x_spread
    h = (D[-1]-D[0])/(n-1)
 
    A = np.zeros((n_rows,n))

    x_sorted = np.sort(X) # sort the data

    for k in range(0,n_rows):
        if (D[0] <= x_sorted[k]) and (x_sorted[k] <= D[1]):
            A[k, 0] = 0.5*(np.cos(np.pi*(x_sorted[k]-D[0])/h)+1)
        else:
            if (D[n - 2] <= x_sorted[k]) and (x_sorted[k] <= D[n-1]):
                A[k, n-1] = 0.5*(np.cos(np.pi*(x_sorted[k]-D[n-1])/h)+1)
        for j in range(1,n-1):
            if (D[j - 1] <= x_sorted[k]) and (x_sorted[k] <= D[j+1]):
                A[k,j]=0.5*(np.cos(np.pi*(x_sorted[k]-D[j])/h)+1)

    return D,A





def fuzzy_partition_triangle(X: pd.Series, n:float):
    '''

    Midsteps of the calculation:

    D - distance vector (D) represents the relative position of each data point within the partition
    h - height, spread of the fuzzy sets 

    '''

    n_rows = len(X)
    x_spread = X.max() - X.min() # spread of the data

    D = np.zeros((n,1))
    for i in range(0,n):
        D[i] = i/(n-1)*x_spread   # D is adjusted by the x_spread
    h = (D[-1]-D[0])/(n-1)
 
    A = np.zeros((n_rows,n))

    x_sorted = np.sort(X) # sort the data

    for k in range(0,n_rows):

        # First column
        if (D[0] <= x_sorted[k]) and (x_sorted[k] <= D[1]):
            A[k, 0] = (D[1]-x_sorted[k])/h

        # Last column   
        else:
            if (D[n - 2] <= x_sorted[k]) and (x_sorted[k] <= D[n-1]):
                A[k, n-1] =  (x_sorted[k]-D[n-2])/h

        # All other columns
        for j in range(1,n-1):
            if (D[j - 1] <= x_sorted[k]) and (x_sorted[k]<= D[j]):
                A[k,j] =  (x_sorted[k]-D[j-1])/h

            if (D[j] <= x_sorted[k]) and (x_sorted[k] <= D[j+1]):
                A[k,j] =  (D[j+1]-x_sorted[k])/h 

    return D,A


def fuzzy_partition_gauss(X: pd.Series, n:float, sigma:float = 1):
    '''

    Midsteps of the calculation:

    D - distance vector (D) represents the relative position of each data point within the partition
    h - height, spread of the fuzzy sets 

    '''
    
    n_rows = len(X)
    x_spread = X.max() - X.min() # spread of the data

    D = np.zeros((n,1))
    for i in range(0,n):
        D[i] = i/(n-1)*x_spread   # D is adjusted by the x_spread
    h = (D[-1]-D[0])/(n-1)
 
    A = np.zeros((n_rows,n))

    x_sorted = np.sort(X) # sort the data

    for k in range(0,n_rows):

            # First column
            if (D[0] <= x_sorted[k]) and (x_sorted[k] <= D[1]):
                A[k, 0] = np.exp(-(x_sorted[k] - D[0]) ** 2 / (2 * sigma ** 2))
            
            # Last column   
            else:
                if (D[n - 2] <= k) and (x_sorted[k] <= D[n-1]):
                    A[k, n-1] =   np.exp(-(x_sorted[k] - D[n-1]) ** 2 / (2 * sigma ** 2))
                    

            # All other columns
            for j in range(1,n-1):
                if (D[j - 1] <= x_sorted[k]) and (x_sorted[k] <= D[j+1]):
                    A[k,j] = np.exp(-(x_sorted[k] - D[j]) ** 2 / (2 * sigma ** 2))


    return D,A

