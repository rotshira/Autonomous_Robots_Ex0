import logging

from csv_to_x_y_z import read_csv_sat_data, compute_receiver_pos

logging.basicConfig(filename='receiver_positions.log', level=logging.INFO, format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def main():
    # File path to CSV data
    file_path = 'gnss_log_2024_04_13_19_51_17_output.csv'

    # Read satellite data from CSV file
    sat_data = read_csv_sat_data(file_path)

    # Compute receiver position for all GPS times
    receiver_positions = compute_receiver_pos(sat_data)

    # Print receiver positions
    # for gps_time, pos in receiver_positions.items():
    #     print(f"Receiver position at GPS time {gps_time}: {pos}")


#     # Write receiver positions to log file
    for gps_time, pos in receiver_positions.items():
        logging.info(f"Receiver position at GPS time {gps_time}: {pos}")

if __name__ == "__main__":
    main()
