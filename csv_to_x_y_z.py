import csv
import numpy as np
import os
# ---------Sub-question 3-----------
# Explanation: We need the speed of light because it helps us
# calculate how long it takes for signals to travel between
# satellites and our receiver on Earth. It's like knowing
# the speed limit for data traveling through space!
SPEED_OF_LIGHT = 299792458  # Speed of light in meters per second

# Explanation: Earth's rotation rate is important because it
# influences where satellites appear in the sky relative to
# our position on Earth. Imagine trying to catch a ball while
# spinning around - it affects where you need to reach for it!
EARTH_ROTATION_RATE = 7.2921151467e-5  # Earth's rotation rate in radians per second


# Function to read the satellite data from a CSV file
def read_csv_sat_data(filename):
    """
    Reads the satellite data from a CSV file.

    Args:
        filename (str): The name of the CSV file to read.

    Returns:
        list: A list containing the satellite data.
    """
    sat_data = []
    with open(filename, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            sat_data.append(row)
    return sat_data


# Function to compute the positions of the satellites at a given GPS time
def sat_pos_comp(sat_data, gps_time):
    """
    Computes the positions of the satellites at a given GPS time.

    Args:
        sat_data (list): A list containing the satellite data.
        gps_time (str): The GPS time for which to compute the positions.

    Returns:
        list: A list of tuples containing the (x, y, z) positions of the satellites.
    """
    sat_pos = []
    for row in sat_data:
        if row[0] == gps_time:
            sat_x = float(row[2])
            sat_y = float(row[3])
            sat_z = float(row[4])
            sat_pos.append((sat_x, sat_y, sat_z))
    return sat_pos


# Function to compute the receiver's position using an iterative least-squares algorithm
def receiver_pos_comp(sat_data, gps_time):
    """
    Computes the receiver's position using an iterative least-squares algorithm.

    Args:
        sat_data (list): A list containing the satellite data.
        gps_time (str): The GPS time for which to compute the receiver's position.

    Returns:
        tuple: A tuple containing the (x, y, z) position of the receiver.
    """
    sat_pos = sat_pos_comp(sat_data, gps_time)
    num_satellites = len(sat_pos)

    # Check if there are enough satellites for positioning
    if num_satellites < 4:
        print("Not enough satellites for positioning.")
        return None

    # Set up the least-squares problem
    A = np.zeros((num_satellites, 4))
    b = np.zeros(num_satellites)

    for i, (sat_x, sat_y, sat_z) in enumerate(sat_pos):
        A[i, 0] = sat_x
        A[i, 1] = sat_y
        A[i, 2] = sat_z
        A[i, 3] = 1
        b[i] = np.sqrt(sat_x ** 2 + sat_y ** 2 + sat_z ** 2)

    # Solve the least-squares problem using NumPy
    receiver_pos = np.linalg.lstsq(A, b, rcond=None)[0][:3]

    return receiver_pos


# Function to compute the receiver's position for all GPS times
def compute_receiver_pos(sat_data):
    """
    Computes the receiver's position for all GPS times in the satellite data.

    Args:
        sat_data (list): A list containing the satellite data.

    Returns:
        dict: A dictionary where keys are GPS times and values are the corresponding receiver positions.
    """
    gps_times = set([row[0] for row in sat_data])
    positions = {}

    for gps_time in gps_times:
        receiver_pos = receiver_pos_comp(sat_data, gps_time)
        if receiver_pos is not None:
            positions[gps_time] = receiver_pos

    return positions


# Get the current working directory
current_directory = os.getcwd()

# Construct the file path, Change the file name to the wanted csv
f_name = 'gnss_log_2024_04_13_19_51_17_output.csv'
file_path = os.path.join(current_directory, f_name)

# Read the satellite data from the CSV file
satellite_data = read_csv_sat_data(file_path)

# Compute the receiver positions for all GPS times
receiver_pos = compute_receiver_pos(satellite_data)

# Print the receiver positions for each GPS time
for gps_time, receiver_position in receiver_pos.items():
    print(f"GPS Time: {gps_time}")
    print(f"Receiver Position (X, Y, Z): {receiver_position}\n")
