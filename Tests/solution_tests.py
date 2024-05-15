import unittest
import csv
from io import StringIO
from unittest.mock import patch
import numpy as np
import pandas as pd

from solution import (
    convert_to_geodetic,
    trilateration,
    calculate_locations,
    export_to_kml,
)

class Test(unittest.TestCase):
    class TestConvertToGeodetic(unittest.TestCase):
        def test_convert_to_geodetic(self):

            # Example at equator, prime meridian, sea level
            x, y, z = 6378137.0, 0, 0
            lat, lon, alt = convert_to_geodetic(x, y, z)
            self.assertAlmostEqual(lat, 0.0)
            self.assertAlmostEqual(lon, 0.0)
            self.assertAlmostEqual(alt, 0.0)

            # Example at north pole, sea level
            x, y, z = 0, 0, 6356752.3142
            lat, lon, alt = convert_to_geodetic(x, y, z)
            self.assertAlmostEqual(lat, 90.0)
            self.assertAlmostEqual(lon, 0.0)
            self.assertAlmostEqual(alt, 0.0)

            # Example at south pole, 10,000 meters altitude
            x, y, z = 0, 0, -6356752.3142 + 10000
            lat, lon, alt = convert_to_geodetic(x, y, z)
            self.assertAlmostEqual(lat, -90.0)
            self.assertAlmostEqual(lon, 0.0)
            self.assertAlmostEqual(alt, 10000.0)

            # Example at Greenwich meridian, sea level
            x, y, z = 0, 6378137.0, 0
            lat, lon, alt = convert_to_geodetic(x, y, z)
            self.assertAlmostEqual(lat, 0.0)
            self.assertAlmostEqual(lon, 0.0)
            self.assertAlmostEqual(alt, 0.0)


    def test_trilateration(self):
        # Define sample data with non-singular matrix
        sat_positions = np.array([[0, 0, 0], [1, 1, 0], [1, 0, 1]])
        measured_pr = np.array([0, np.sqrt(2), np.sqrt(2)])
        initial_pos = np.array([0.5, 0.5, 0.5])
        initial_bias = 0

        # Call the function
        result = trilateration(sat_positions, measured_pr, initial_pos, initial_bias)

        # Check if the result has the expected shape
        self.assertEqual(len(result), 6)

    class TestCalculateLocations(unittest.TestCase):
        def test_calculate_locations(self):
            # Example input data
            measurements = pd.DataFrame({
                'GPS time': ['2024-05-15T12:00:00', '2024-05-15T12:00:00', '2024-05-15T12:00:00'],
                'Sat.X': [0, 1, 2],
                'Sat.Y': [0, 1, 2],
                'Sat.Z': [0, 1, 2],
                'Pseudo-Range': [0, 1.732, 3.464],  # sqrt(3), 2*sqrt(3)
            })

            # Calculate locations
            result_coords = calculate_locations(measurements)

            # Test if the result is a dictionary
            self.assertIsInstance(result_coords, dict)

            # Test if the expected number of entries is generated
            self.assertEqual(len(result_coords), 1)

            # Test if the coordinates are calculated correctly
            expected_coords = {
                '2024-05-15T12:00:00': (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)  # Since all satellites are at the same position
            }
            self.assertDictEqual(result_coords, expected_coords)

    def test_calculate_locations2(self):
        # Define sample data
        measurements = pd.DataFrame({
            'GPS time': ['2024-05-15T10:00:00', '2024-05-15T10:00:00', '2024-05-15T10:00:00'],
            'Sat.X': [0, 1, 2],
            'Sat.Y': [0, 1, 2],
            'Sat.Z': [0, 1, 2],
            'Pseudo-Range': [0, np.sqrt(3), 2 * np.sqrt(3)]
        })

        # Call the function
        result = calculate_locations(measurements)

        # Check if the result is a dictionary
        self.assertIsInstance(result, dict)

        # Check if the result contains the expected keys
        expected_keys = ['2024-05-15T10:00:00']
        self.assertEqual(list(result.keys()), expected_keys)

    @patch('sys.stdout', new_callable=StringIO)
    def test_export_to_kml(self, mock_stdout):
        # Define sample coordinates and output filepath
        coordinates = {
            '2024-05-15 14:00:00': (0, 0, 0, 0, 0, 0),
            '2024-05-15 14:05:00': (10, 10, 10, 10, 10, 10),
            '2024-05-15 14:10:00': (20, 20, 20, 20, 20, 20),
        }
        output_filepath = 'test_output.kml'

        # Call the function
        export_to_kml(coordinates, output_filepath)

        # Verify the output
        expected_output = f"KML file saved to: {output_filepath}\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

if __name__ == '__main__':
    unittest.main()
