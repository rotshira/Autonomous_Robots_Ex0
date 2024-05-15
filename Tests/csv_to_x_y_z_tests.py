import unittest
import csv

from csv_to_x_y_z import read_csv_sat_data, receiver_pos_comp


class TestReadCsvSatData(unittest.TestCase):
    # Define a sample CSV file content for testing
    SAMPLE_CSV_CONTENT = [
        ['PRN', 'X', 'Y', 'Z', 'Signal_Strength'],
        ['1', '10.0', '20.0', '30.0', 'Strong'],
        ['2', '15.0', '25.0', '35.0', 'Weak'],
        ['3', '8.0', '18.0', '28.0', 'Medium']
    ]

    def setUp(self):
        # Write sample CSV content to a temporary file for testing
        with open('test_sat_data.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(self.SAMPLE_CSV_CONTENT)

    def tearDown(self):
        # Remove the temporary file after testing
        import os
        os.remove('test_sat_data.csv')

    def test_read_csv_sat_data(self):
        # Test reading the sample CSV file
        filename = 'test_sat_data.csv'
        expected_sat_data = [
            ['1', '10.0', '20.0', '30.0', 'Strong'],
            ['2', '15.0', '25.0', '35.0', 'Weak'],
            ['3', '8.0', '18.0', '28.0', 'Medium']
        ]
        actual_sat_data = read_csv_sat_data(filename)
        self.assertEqual(actual_sat_data, expected_sat_data)

    def test_read_csv_sat_data_empty_file(self):
        # Test reading an empty CSV file
        filename = 'empty_sat_data.csv'
        open(filename, 'a').close()  # Create an empty file
        expected_sat_data = []
        actual_sat_data = read_csv_sat_data(filename)
        self.assertEqual(actual_sat_data, expected_sat_data)

    def test_receiver_pos_comp(self):
        # Sample satellite data
        sample_sat_data = [
            ['1', '10.0', '20.0', '30.0'],
            ['2', '15.0', '25.0', '35.0'],
            ['3', '8.0', '18.0', '28.0'],
            ['4', '12.0', '22.0', '32.0']
        ]
        # GPS time
        gps_time = '123456.789'

        # Call the function
        receiver_pos = receiver_pos_comp(sample_sat_data, gps_time)

        # Assert that the result is not None
        self.assertIsNotNone(receiver_pos)

        # Assert that the result is a tuple
        self.assertIsInstance(receiver_pos, tuple)

        # Assert that the result contains three elements (x, y, z)
        self.assertEqual(len(receiver_pos), 3)

        # Assert that the result elements are of type float
        self.assertTrue(all(isinstance(coord, float) for coord in receiver_pos))


if __name__ == '__main__':
    unittest.main()
