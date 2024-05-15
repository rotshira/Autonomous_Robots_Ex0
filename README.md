# GNSS Raw Measurements - EX0
<p align="center">
<img height="170" src="https://imgur.com/OnoyLam.png">
</p>

First assignment of Autonomous Robotics course. This project encapsulates a comprehensive exploration of GNSS principles, culminating in the development of practical tools aimed at navigating the GNSS landscape with efficiency and accuracy.
In addition - it focuses on the basic principles of GNSS (Global Navigation Satellite System). An implementation of a naive positioning algorithm based on the RMS (Root Mean Square) of selected (i.e., weighted) pseudo-ranges.

Here's the TODO list we've worked on in order to build this project:
1. Learning GNSS Basics: We've been exploring how Global Navigation Satellite Systems (GNSS) work, focusing on something called pseudo-ranges. They're like hints from satellites about where we are.

2. Playing with Data: We grabbed some messy log files and made a tool to turn them into neat CSV files. These CSVs are like maps, showing us stuff like satellite IDs and signal strengths.

3. Finding Our Spot: We made a smart way to figure out exactly where we are using those pseudo-ranges. It's like solving a puzzle with math!

4. Going from Numbers to Places: We learned how to change our math answers into something we can understand: latitude, longitude, and altitude. Now we can tell people where we found hidden treasures.

5. All-in-One Tool: We put everything we made into one handy tool. Just give a KML reader sites this log file, and it gives you a fancy map showing where you've been and a detailed list of your journey.

6. Testing, Testing: We made sure our tool works well by trying it with different data. We wanted to be sure it works for everyone!

And finally! ready to use: Everything's packed up nicely on GitHub. Check out our simple guide to start your own treasure hunt!
## Prerequisites

Ensure you have Python installed on your system. This project requires Python 3.6 or later.

## Setup

1. Clone the repository or download the project files to your local machine.

2. Install the necessary packages using the provided `requirements.txt` file. Open your terminal and run:
    ```sh
    pip install -r requirements.txt
    ```

## How to run

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
    gnss_to_csv.py: Contains functions to parse and process GNSS log data into a csv file and in addition sending a dataframe to solution.py.
    solution.py: Implements the positioning algorithm and the dataframe (which came from gnss_to_csv.py) and KML export functionality.

## Output

#### CSV file
- A CSV file with the following format:
**GPS time, SatPRN (ID), Sat.X, Sat.Y, Sat.Z, Pseudo-Range, CN0**. 

#### KML file 
- A KML file (in the running_results folder) which can be loaded into a map applications like [Google Earth](https://earth.google.com) or [KMZView](https://kmzview.com/) to visualize the locations of the GNSS receiver based on the processed data.

## Output Example
#### CSV file (Part of it, for the rest check out the running_results folder!)

| GPS time                     | SatPRN (ID) | Sat.X            | Sat.Y           | Sat.Z           | Pseudo-Range  | CN0  |
|-----------------------------|-------------|------------------|-----------------|-----------------|---------------|------|
| 2024-04-13T16:53:51.426041+00:00 | G10         | -1620081.7744787028 | 17327678.89277763 | 20172485.06377191 | 22839528.10111702 | 48.3 |
| 2024-04-13T16:53:51.426041+00:00 | G21         | 15757452.408317765  | 1890975.957163494 | 21856363.72227612 | 21704707.75126088 | 45.7 |
| 2024-04-13T16:53:51.426041+00:00 | G27         | 23098436.983025927  | 13303367.387089958 | -3014966.440680798 | 22215117.68794983 | 37.9 |
| 2024-04-13T16:53:51.426041+00:00 | G32         | 7810468.746056126   | 17849813.844240233 | 18350828.840009507 | 21298089.881690666 | 48.5 |
| 2024-04-13T16:53:51.426041+00:00 | G08         | 25023639.6240527    | 4783845.8041696865 | 8137692.350133545 | 21196005.876491368 | 27.7 |
| 2024-04-13T16:53:52.426041+00:00 | G08         | 25024485.673475336  | 4784495.73568894  | 8134789.066819822 | 21198559.199303802 | 24.4 |

#### KML file

<p align="center">
<img height="230" src="https://imgur.com/T5RHFEZ.png"/>
</p>
