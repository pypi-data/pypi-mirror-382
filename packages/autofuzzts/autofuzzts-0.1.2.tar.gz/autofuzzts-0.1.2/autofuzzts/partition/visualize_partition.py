import numpy as np
import matplotlib.pyplot as plt


def visualize_partition(fp_df, center_points):
    plt.figure(figsize=(6, 3))

    # Scatter plot with size based on membership value
    plt.scatter(
        fp_df["X_value"],
        fp_df["membership_value"],
        c=fp_df["cluster"].astype("category").cat.codes,
        cmap="viridis",
        s=50,
    )
    plt.xlabel("X")
    plt.ylabel("Membership Value")
    plt.title("Fuzzy Partition")

    # Plot center points with horizontal line at y=0.5
    plt.plot(center_points, np.ones_like(center_points) * 0.5, "x", markersize=10)

    # Add labels for center points with slight vertical offset
    for i, txt in enumerate(center_points):
        plt.annotate(
            txt,
            (center_points[i], 0.5 + 0.015),
            horizontalalignment="center",
            fontsize=8,
        )

    plt.show()
