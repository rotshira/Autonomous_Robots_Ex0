import unittest
import numpy as np
import pandas as pd
from gnss_to_csv import read_data, preprocess_measurements, calculate_satellite_position, parse_gnss_log


class MyTestCase(unittest.TestCase):
    def test_read_data(self):
        # Test with a sample CSV file
        input_filepath = "C:/Users/shira/PycharmProjects/Autonomous_Robots_Ex0/Data/gnss_log_2024_04_13_19_51_17.txt"
        df = read_data(input_filepath)
        self.assertIsNotNone(df)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertFalse(df.empty)

    def test_preprocess_measurements(self):
        measurements_data = {
            'Svid': ['1', '2', '3'],
            'ConstellationType': ['1', '1', '1'],
            'Cn0DbHz': ['40', '35', '30'],
            'TimeNanos': ['1000000', '2000000', '3000000'],
            'FullBiasNanos': ['500000', '600000', '700000'],
            'ReceivedSvTimeNanos': ['800000', '900000', '1000000'],
            'PseudorangeRateMetersPerSecond': ['0.1', '0.2', '0.3'],
            'ReceivedSvTimeUncertaintyNanos': ['100', '200', '300'],
            'BiasNanos': ['0', '0', '0'],
            'TimeOffsetNanos': ['0', '0', '0']
        }
        measurements_df = pd.DataFrame(measurements_data)
        processed_df = preprocess_measurements(measurements_df)
        self.assertIsNotNone(processed_df)
        self.assertTrue(isinstance(processed_df, pd.DataFrame))
        self.assertFalse(processed_df.empty)

    def test_calculate_satellite_position(self):
        # Mock ephemeris data
        ephemeris_data = {
            'sqrtA': [1.0, 1.0, 1.0],
            'deltaN': [0.0, 0.0, 0.0],
            'M_0': [0.0, 0.0, 0.0],
            'e': [0.0, 0.0, 0.0],
            't_oe': [0.0, 0.0, 0.0],
            'C_us': [0.0, 0.0, 0.0],
            'C_uc': [0.0, 0.0, 0.0],
            'C_rs': [0.0, 0.0, 0.0],
            'C_rc': [0.0, 0.0, 0.0],
            'C_is': [0.0, 0.0, 0.0],
            'C_ic': [0.0, 0.0, 0.0],
            'i_0': [0.0, 0.0, 0.0],
            'IDOT': [0.0, 0.0, 0.0],
            'omega': [0.0, 0.0, 0.0],
            'Omega_0': [0.0, 0.0, 0.0],
            'OmegaDot': [0.0, 0.0, 0.0],
            'SVclockBias': [0.0, 0.0, 0.0],
            'SVclockDrift': [0.0, 0.0, 0.0],
            'SVclockDriftRate': [0.0, 0.0, 0.0],
            't_oc': [0.0, 0.0, 0.0]
        }
        ephemeris_df = pd.DataFrame(ephemeris_data, index=['1', '2', '3'])

        # Mock transmit time
        transmit_time = np.array([0.0, 0.0, 0.0])

        # Call the function to calculate satellite positions
        sv_position_df = calculate_satellite_position(ephemeris_df, transmit_time)

        # Perform assertions
        self.assertIsNotNone(sv_position_df)
        self.assertTrue(isinstance(sv_position_df, pd.DataFrame))
        self.assertFalse(sv_position_df.empty)
        self.assertEqual(len(sv_position_df), 3)  # Assuming 3 satellites in mock data
        # Add more specific assertions if needed based on the expected behavior of the function

    def test_parse_gnss_log(self):
        # Define input and output file paths
        input_filepath = "C:/Users/shira/PycharmProjects/Autonomous_Robots_Ex0/Data/gnss_log_2024_04_13_19_51_17.txt"
        output_path = "C:/Users/shira/PycharmProjects/Autonomous_Robots_Ex0/running_results/csv_result_driving.csv"

        # Call the function
        csv_df = parse_gnss_log(input_filepath, output_path)

        # Assert that the function returns a DataFrame
        self.assertIsInstance(csv_df, pd.DataFrame)

        # Define the expected columns
        expected_columns = ['GPS time', 'SatPRN (ID)', 'Sat.X', 'Sat.Y', 'Sat.Z', 'Pseudo-Range', 'CN0']

        # Check if all expected columns are present in the output DataFrame
        for column in expected_columns:
            self.assertIn(column, csv_df.columns)


if __name__ == '__main__':
    unittest.main()
