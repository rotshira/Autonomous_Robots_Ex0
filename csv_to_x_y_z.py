## Version still does not work, will replace it

import pandas as pd
import numpy as np

# Load data from CSV
data = pd.read_csv("gnss_log_2024_04_13_19_51_17_output.csv")

# Define constants
c = 299792458  # Speed of light in meters per second
epsilon = 1e-6  # Small value for convergence criterion


# Weight function for satellite signal strength (you may adjust this based on your requirements)
def weight_func(cn0):
    return 1 / (cn0 + 1)  # Example weight function: Inverse of CN0


# Positioning algorithm
def compute_position(gps_time):
    # Filter data for the given GPS time
    filtered_data = data[data['GPS Time'] == gps_time]

    # Remove rows with NaN values in columns used for computation
    filtered_data = filtered_data.dropna(subset=['Sat.X', 'Sat.Y', 'Sat.Z', 'Pseudo-Range', 'CN0'])

    # Number of satellites
    num_satellites = len(filtered_data)

    # Check if there are enough satellites for computation
    if num_satellites < 4:
        print("Not enough satellites available for computation.")
        return None, None, None

    # Initial estimate for position
    x = 0
    y = 0
    z = 0

    iteration = 0
    # Iterative numerical algorithm
    while True:
        print("Iteration:", iteration)
        # Compute pseudo-ranges
        pseudo_ranges = np.sqrt((filtered_data['Sat.X'] - x)**2 +
                                (filtered_data['Sat.Y'] - y)**2 +
                                (filtered_data['Sat.Z'] - z)**2)

        # Scale down the pseudo-ranges to prevent overflow
        max_pseudo_range = pseudo_ranges.max()
        scale_factor = max_pseudo_range / 1e9  # Scale down to a range of 1e9
        pseudo_ranges /= scale_factor

        # Check for NaN values in pseudo-ranges
        if pseudo_ranges.isnull().any():
            print("NaN values detected in pseudo-ranges. Skipping iteration.")
            break

        # Compute weights
        weights = weight_func(filtered_data['CN0'])

        # Compute weighted least squares solution
        A = np.column_stack((np.ones(num_satellites), -np.ones(num_satellites), -np.ones(num_satellites)))
        b = pseudo_ranges.values * c  # Convert to numpy array for indexing
        x_new, y_new, z_new = np.linalg.lstsq(A * weights.values[:, np.newaxis], b * weights.values, rcond=None)[0]

        # Undo scaling on the estimates
        x_new *= scale_factor
        y_new *= scale_factor
        z_new *= scale_factor

        # Check convergence
        if abs(x_new - x) < epsilon and abs(y_new - y) < epsilon and abs(z_new - z) < epsilon:
            break

        # Update estimates
        x = x_new
        y = y_new
        z = z_new

        iteration += 1

    return x, y, z

# Choose a GPS time from the data for testing
test_gps_time = data['GPS Time'].iloc[0]  # Use the first GPS time from the data

# Compute position for the chosen GPS timee
x, y, z = compute_position(test_gps_time)
print("Position (X, Y, Z) for GPS time", test_gps_time, ":", x, y, z)
