import os
import sys
import csv
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pyproj
from gnssutils import EphemerisManager
import simplekml
import georinex

WEEKSEC = 604800
LIGHTSPEED = 2.99792458e8


def read_gnss_data(input_filepath):
    with open(input_filepath) as csvfile:
        reader = csv.reader(csvfile)
        android_fixes, measurements = [], []
        print(input_filepath)

        for row in reader:
            if row[0].startswith('#'):
                if 'Fix' in row[0]:
                    android_fixes.append(row[1:])
                elif 'Raw' in row[0]:
                    measurements.append(row[1:])
            else:
                if row[0] == 'Fix':
                    android_fixes.append(row[1:])
                elif row[0] == 'Raw':
                    measurements.append(row[1:])
        print((len(measurements)))

    return pd.DataFrame(pd.DataFrame(measurements[1:], columns=measurements[0]))


def preprocess_measurements(measurements):
    # Pad single-character Svid values with a leading zero
    measurements.loc[measurements['Svid'].str.len() == 1, 'Svid'] = '0' + measurements['Svid']

    # Map constellation types to their respective symbols
    measurements.loc[measurements['ConstellationType'] == '1', 'Constellation'] = 'G'
    measurements.loc[measurements['ConstellationType'] == '3', 'Constellation'] = 'R'

    # Create SvName column
    measurements['SvName'] = measurements['Constellation'] + measurements['Svid']

    # Filter measurements to include only GPS (Constellation 'G')
    measurements = measurements[measurements['Constellation'] == 'G'].copy()

    # List of numeric columns to be converted to numeric types
    numeric_columns = ['Cn0DbHz', 'TimeNanos', 'FullBiasNanos', 'ReceivedSvTimeNanos',
                       'PseudorangeRateMetersPerSecond', 'ReceivedSvTimeUncertaintyNanos']

    # Convert specified columns to numeric type
    for col in numeric_columns:
        measurements[col] = pd.to_numeric(measurements[col], errors='coerce')

    # Handle 'BiasNanos' and 'TimeOffsetNanos' columns, ensuring they exist
    measurements['BiasNanos'] = pd.to_numeric(measurements.get('BiasNanos', 0))
    measurements['TimeOffsetNanos'] = pd.to_numeric(measurements.get('TimeOffsetNanos', 0))

    # Calculate GpsTimeNanos
    measurements['GpsTimeNanos'] = measurements['TimeNanos'] - (
            measurements['FullBiasNanos'] - measurements['BiasNanos'])
    gpsepoch = datetime(1980, 1, 6, 0, 0, 0)
    measurements['UnixTime'] = pd.to_datetime(measurements['GpsTimeNanos'], utc=True, origin=gpsepoch)

    # Calculate Epoch
    measurements['Epoch'] = 0
    measurements.loc[
        measurements['UnixTime'] - measurements['UnixTime'].shift() > timedelta(milliseconds=200), 'Epoch'] = 1
    measurements['Epoch'] = measurements['Epoch'].cumsum()

    # Calculate tRxGnssNanos
    measurements['tRxGnssNanos'] = measurements['TimeNanos'] + measurements['TimeOffsetNanos'] - (
            measurements['FullBiasNanos'].iloc[0] + measurements['BiasNanos'].iloc[0])
    WEEKSEC = 604800
    LIGHTSPEED = 299792458

    # Calculate GPS week number and times
    measurements['GpsWeekNumber'] = np.floor(1e-9 * measurements['tRxGnssNanos'] / WEEKSEC)
    measurements['tRxSeconds'] = 1e-9 * measurements['tRxGnssNanos'] - WEEKSEC * measurements['GpsWeekNumber']
    measurements['tTxSeconds'] = 1e-9 * (measurements['ReceivedSvTimeNanos'] + measurements['TimeOffsetNanos'])
    measurements['prSeconds'] = measurements['tRxSeconds'] - measurements['tTxSeconds']

    # Calculate pseudorange and uncertainty
    measurements['PrM'] = LIGHTSPEED * measurements['prSeconds']
    measurements['PrSigmaM'] = LIGHTSPEED * 1e-9 * measurements['ReceivedSvTimeUncertaintyNanos']

    # Initialize satellite position columns
    measurements['Sat.X'] = np.nan
    measurements['Sat.Y'] = np.nan
    measurements['Sat.Z'] = np.nan
    measurements['Pseudo-Range'] = np.nan

    print("got here1")
    return measurements


def calculate_satellite_positions(ephemeris, transmit_time):
    mu = 3.986005e14
    OmegaDot_e = 7.2921151467e-5
    F = -4.442807633e-10
    sv_position = pd.DataFrame(index=ephemeris.index)
    sv_position['t_k'] = transmit_time - ephemeris['t_oe']

    A = ephemeris['sqrtA'].pow(2)
    n_0 = np.sqrt(mu / A.pow(3))
    n = n_0 + ephemeris['deltaN']
    M_k = ephemeris['M_0'] + n * sv_position['t_k']
    E_k = M_k

    for _ in range(10):
        E_k_new = M_k + ephemeris['e'] * np.sin(E_k)
        if (E_k - E_k_new).abs().min() < 1e-8:
            break
        E_k = E_k_new

    sinE_k = np.sin(E_k)
    cosE_k = np.cos(E_k)
    delT_r = F * ephemeris['e'] * A * sinE_k
    delT_oc = transmit_time - ephemeris['t_oc']
    sv_position['delT_sv'] = ephemeris['SVclockBias'] + ephemeris['SVclockDrift'] * delT_oc + ephemeris[
        'SVclockDriftRate'] * delT_oc.pow(2)

    v_k = np.arctan2(np.sqrt(1 - ephemeris['e'].pow(2)) * sinE_k, cosE_k - ephemeris['e'])
    Phi_k = v_k + ephemeris['omega']

    sin2Phi_k = np.sin(2 * Phi_k)
    cos2Phi_k = np.cos(2 * Phi_k)

    du_k = ephemeris['C_us'] * sin2Phi_k + ephemeris['C_uc'] * cos2Phi_k
    dr_k = ephemeris['C_rs'] * sin2Phi_k + ephemeris['C_rc'] * cos2Phi_k
    di_k = ephemeris['C_is'] * sin2Phi_k + ephemeris['C_ic'] * cos2Phi_k

    u_k = Phi_k + du_k
    r_k = A * (1 - ephemeris['e'] * cosE_k) + dr_k
    i_k = ephemeris['i_0'] + di_k + ephemeris['IDOT'] * sv_position['t_k']

    x_k_prime = r_k * np.cos(u_k)
    y_k_prime = r_k * np.sin(u_k)

    Omega_k = ephemeris['Omega_0'] + (ephemeris['OmegaDot'] - OmegaDot_e) * sv_position['t_k'] - OmegaDot_e * ephemeris[
        't_oe']

    sv_position['x_k'] = x_k_prime * np.cos(Omega_k) - y_k_prime * np.cos(i_k) * np.sin(Omega_k)
    sv_position['y_k'] = x_k_prime * np.sin(Omega_k) + y_k_prime * np.cos(i_k) * np.cos(Omega_k)
    sv_position['z_k'] = y_k_prime * np.sin(i_k)

    return sv_position


def update_measurements_with_satellite_positions(measurements, ephemeris_data_directory):
    manager = EphemerisManager(ephemeris_data_directory)

    for epoch in measurements['Epoch'].unique():
        one_epoch = measurements[(measurements['Epoch'] == epoch) & (measurements['prSeconds'] < 0.1)].drop_duplicates(
            subset='SvName').set_index('SvName')
        timestamp = one_epoch.iloc[0]['UnixTime'].to_pydatetime(warn=False)
        sats = one_epoch.index.unique().tolist()
        ephemeris = manager.get_ephemeris(timestamp, sats)
        sv_position = calculate_satellite_positions(ephemeris, one_epoch['tTxSeconds'])

        xs = sv_position[['x_k', 'y_k', 'z_k']].to_numpy()
        pr = one_epoch['PrM'] + LIGHTSPEED * sv_position['delT_sv'].to_numpy()

        for idx, (x, y, z), pr_val in zip(range(len(xs)), xs, pr):
            svid = sats[idx]
            epoch_mask = (measurements['Epoch'] == epoch) & (measurements['SvName'] == svid)
            measurements.loc[epoch_mask, ['Sat.X', 'Sat.Y', 'Sat.Z', 'Pseudo-Range']] = x, y, z, pr_val
        print("got here2")
    return measurements


def export_to_csv(dataframe, directory, filename, columns_to_keep, rename_columns):
    output_filepath = os.path.join(directory, 'data', filename)
    dataframe_to_csv = dataframe[columns_to_keep].copy()
    dataframe_to_csv.rename(columns=rename_columns, inplace=True)
    dataframe_to_csv.reset_index(drop=True, inplace=True)
    dataframe_to_csv.to_csv(output_filepath, index=False)
    print(f"{filename} has been saved to: {output_filepath}")
    return dataframe_to_csv


def convert_to_geodetic(x, y, z):
    transformer = pyproj.Transformer.from_crs("EPSG:4978", "EPSG:4326", always_xy=True)
    lon, lat, alt = transformer.transform(x, y, z)
    return lat, lon, alt


def trilateration(sat_positions, measured_pr, initial_pos, initial_bias):
    position_corr = 100 * np.ones(3)
    clock_bias = initial_bias

    while np.linalg.norm(position_corr) > 1e-3:
        ranges = np.linalg.norm(sat_positions - initial_pos, axis=1)
        pred_pr = ranges + clock_bias
        residuals = measured_pr - pred_pr

        G = np.ones((measured_pr.size, 4))
        G[:, :3] = -(sat_positions - initial_pos) / ranges[:, None]
        corrections = np.linalg.inv(G.T @ G) @ G.T @ residuals

        position_corr, clock_bias_corr = corrections[:3], corrections[3]
        initial_pos += position_corr
        clock_bias += clock_bias_corr

    lat, lon, alt = convert_to_geodetic(*initial_pos)
    return initial_pos[0], initial_pos[1], initial_pos[2], lat, lon, alt


def calculate_locations(measurements):
    result_coords = {}
    for time, group in measurements.groupby('GPS time'):
        sat_pos = group[['Sat.X', 'Sat.Y', 'Sat.Z']].values
        measured_pr = group['Pseudo-Range'].values
        initial_pos = np.array([group['Sat.X'].mean(), group['Sat.Y'].mean(), group['Sat.Z'].mean()])
        initial_bias = 0
        coords = trilateration(sat_pos, measured_pr, initial_pos, initial_bias)
        result_coords[time] = coords

    return result_coords


def export_to_kml(coordinates, output_filepath):
    kml = simplekml.Kml()
    for time, (x, y, z, lat, lon, alt) in coordinates.items():
        pnt = kml.newpoint(name=str(time), coords=[(lon, lat, alt)])
        pnt.timestamp.when = time
    kml.save(output_filepath)
    print(f"KML file saved to: {output_filepath}")


def main(input_filepath, ephemeris_data_directory, output_directory, output_filename):
    measurements = read_gnss_data(input_filepath)
    measurements = preprocess_measurements(measurements)
    measurements = update_measurements_with_satellite_positions(measurements, ephemeris_data_directory)

    columns_to_keep = ['UnixTime', 'SvName', 'Sat.X', 'Sat.Y', 'Sat.Z', 'Pseudo-Range', 'Cn0DbHz']
    rename_columns = {'UnixTime': 'GPS time', 'SvName': 'SatPRN (ID)', 'Cn0DbHz': 'CN0'}
    measurements = export_to_csv(measurements, output_directory, output_filename, columns_to_keep, rename_columns)

    coordinates = calculate_locations(measurements)
    kml_output_filepath = os.path.join(output_directory, 'data', 'output.kml')
    export_to_kml(coordinates, kml_output_filepath)


if __name__ == '__main__':
    input_filepath = sys.argv[1]
    ephemeris_data_directory = sys.argv[2]
    output_directory = sys.argv[3]
    output_filename = sys.argv[4]
    main(input_filepath, ephemeris_data_directory, output_directory, output_filename)
