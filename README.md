# GNSS Raw Measurements

This project focuses on the basic principles of GNSS (Global Navigation Satellite System). You will implement a naive positioning algorithm based on the RMS (Root Mean Square) of selected (i.e., weighted) pseudo-ranges.

## Prerequisites

Ensure you have Python installed on your system. This project requires Python 3.6 or later.

## Setup

1. Clone the repository or download the project files to your local machine.

2. Install the necessary packages using the provided `requirements.txt` file. Open your terminal and run:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To process the GNSS data and generate a KML file, follow these steps:

1. Open your terminal.

2. Run the following script, replacing the placeholders with your actual file paths and desired output filename:
    ```sh
    python run.py <input_filepath> <output_directory> <output_filename>
    ```

   - `<input_filepath>`: Path to the input GNSS log file (e.g., `Data/gnss_log_2024_04_13_19_53_33.txt`).
   - `<output_directory>`: Directory where the output files will be saved.
   - `<output_filename>`: Name of the output KML file (without extension).

### Example

```sh
python run.py /Users/user/PycharmProjects/Autonomous_Robots_Ex0/Data/gnss_log_2024_04_13_19_53_33.txt /Users/user/PycharmProjects/Autonomous_Robots_Ex0 output
```
׳׳

## Project Structure
    run.py: Main script to execute the GNSS processing.
    GnssToCsv.py: Contains functions to parse and process GNSS log data.
    solution.py: Implements the positioning algorithm and KML export functionality.

## Output
The generated KML file can be loaded into map applications like Google Earth to visualize the locations of the GNSS receiver based on the processed data.
