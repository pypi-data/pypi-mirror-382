import numpy as np
import pandas as pd
from typing import Union, Literal
import warnings
from sklearn.preprocessing import MinMaxScaler

from autofuzzts.partition.fuzzy_clust_fun import (
    fuzzy_partition_cosine,
    fuzzy_partition_triangle,
    fuzzy_partition_gauss,
)

class FuzzyPartition:
    def __init__(self, fuzzy_function: Literal["cosine", "triangle", "gauss"], n_clusters: int, sigma: float, scaler: MinMaxScaler, verbosity: bool = False):
        self.fuzzy_function = self._get_fuzzy_partition_func(fuzzy_function)
        self.n_clusters = n_clusters
        self.sigma = sigma
        self.verbosity = verbosity
        self.scaler = scaler  

        if scaler is None:  # Check if scaler is None
            warnings.warn("Scaler must be provided for inverse transformation.")

    def _get_fuzzy_partition_func(self, fuzzy_part_func: Union[str, None]):
        if fuzzy_part_func == "cosine":
            return fuzzy_partition_cosine  # Replace with actual function
        elif fuzzy_part_func == "triangle":
            return fuzzy_partition_triangle  # Replace with actual function
        elif fuzzy_part_func == "gauss":
            return fuzzy_partition_gauss  # Replace with actual function
        else:
            return fuzzy_partition_cosine  # Default function

    def fuzzy_partition(self, X: np.ndarray) -> pd.DataFrame:
        """
        Perform fuzzy partitioning on the target variable X.

        Parameters:
            X (np.ndarray): Input data to be partitioned.

        Returns:
            pd.DataFrame: DataFrame containing partition results.
        """
        # Perform fuzzy partitioning using the selected function
        if self.fuzzy_function.__name__ == "fuzzy_partition_gauss":
            D, A = self.fuzzy_function(X=X, n=self.n_clusters, sigma=self.sigma)
        else:
            D, A = self.fuzzy_function(X=X, n=self.n_clusters)

        center_points = list(D.flatten())
        center_points = [round(i, 2) for i in center_points]
        center_points = np.array(center_points)

        if self.verbosity:
            print("Cluster center points:", center_points)

        # Unscaled center points
        center_points_unscaled = self.scaler.inverse_transform(
            center_points.reshape(-1, 1)
        )
        self.center_points_unscaled = center_points_unscaled.flatten()
        if self.verbosity:
            print("Cluster center points unscaled:", self.center_points_unscaled.flatten())

        # Create a DataFrame for membership values
        A_df = pd.DataFrame(A)
        A_df.columns = ["set_" + str(i) for i in range(A_df.shape[1])]
        
        # Prepare the fuzzy partition DataFrame
        fp_df = A_df.copy()
        fp_df.insert(0, "X_value", X)
        fp_df["membership_value"] = fp_df.iloc[:, 1:].max(axis=1)
        fp_df["cluster"] = fp_df.iloc[:, 1:].idxmax(axis=1)

        # Initialize 'left' and 'right' columns
        fp_df["left"] = 0
        fp_df["right"] = 0

        # Define sets for left and right logic
        set_min = "set_0"
        set_max = "set_" + str(len(center_points) - 1)

        # Set left and right for min and max sets
        fp_df.loc[fp_df["cluster"] == set_min, "right"] = 1
        fp_df.loc[fp_df["cluster"] == set_max, "left"] = 1

        fp_df["center_point"] = ""
        fp_df.loc[fp_df["cluster"] == set_min, "center_point"] = 0
        fp_df.loc[fp_df["cluster"] == set_max, "center_point"] = 1

        # Logic for intermediate clusters
        for i in range(1, len(center_points) - 1):
            set_i = "set_" + str(i)
            fp_df.loc[fp_df["cluster"] == set_i, "center_point"] = center_points[i]
            fp_df.loc[
                (fp_df["cluster"] == set_i) & (fp_df["X_value"] >= center_points[i]),
                "right",
            ] = 1
            fp_df.loc[
                (fp_df["cluster"] == set_i) & (fp_df["X_value"] < center_points[i]),
                "left",
            ] = 1

        # Ensure membership values are non-negative
        fp_df.loc[fp_df["membership_value"] < 0, "membership_value"] = 0
        
        # Keep only relevant columns
        fp_df = fp_df.loc[:, ["X_value", "membership_value", "cluster", "left"]]
        
        return fp_df, center_points, center_points_unscaled.flatten()