# BLAT PSL Processor

## Overview
This Python script processes BLAT PSL output files and generates multiple reports based on unique probe-target mappings. It provides a user-friendly GUI using Tkinter, allowing users to select an input PSL file and specify an output directory for results.

## Features
- Removes the first 5 header lines of the PSL file.
- Generates a count of unique probes per target.
- Generates a count of unique targets per probe.
- Creates mappings of probes to targets and vice versa.
- Identifies probes that hit all unique targets.
- Provides a graphical user interface (GUI) for easy file selection.

## Requirements
- Python 3.x
- Required Python libraries:
  - `pandas`
  - `tkinter`
  
To install required libraries, run:
```sh
pip install pandas
```
(Tkinter is included with standard Python installations.)

## Usage
### Running the Script
Execute the script by running:
```sh
python blat_psl_analysis.py
```

### Using the GUI
1. Click the **Browse** button to select the PSL file.
2. Click the **Browse** button to select the output directory.
3. Click **Run** to process the file.

## Output Files
After processing, the following CSV reports will be generated in the selected output directory:

- `Unique_Target_Counts.csv`: Counts of unique probes per target.
- `Unique_Probe_Counts.csv`: Counts of unique targets per probe.
- `Probe_to_Target_Hits.csv`: Mapping of probes to their respective target hits.
- `Target_to_Probe_Hits.csv`: Mapping of targets to their respective probes.
- `Probes_Hitting_All_Targets.csv`: List of probes that hit all targets.

## License
This project is open-source and available under the MIT License.

