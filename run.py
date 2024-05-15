import os
import sys
from gnss_to_csv import parse_gnss_log
from solution import calculate_locations, export_to_kml


def main(input_path, output_path, output_filename):
    measurements = parse_gnss_log(input_path, output_filename)
    coordinates = calculate_locations(measurements)
    kml_output_filepath = os.path.join(output_path, 'running_results', 'output.kml')
    export_to_kml(coordinates, kml_output_filepath)


if __name__ == '__main__':
    input_filepath = sys.argv[1]
    output_directory = sys.argv[2]
    output_filename = sys.argv[3]
    main(input_filepath,output_directory, output_filename)