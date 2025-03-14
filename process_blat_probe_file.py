#!/usr/bin/env python3
import csv
import os
import tkinter as tk
from tkinter import filedialog

def select_file(prompt: str) -> str:
    """
    Open a file selection dialog using Tkinter.
    
    Args:
        prompt (str): Title of the file selection dialog.
        
    Returns:
        str: Path to the selected file.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title=prompt,
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    return file_path

def select_directory(prompt: str) -> str:
    """
    Open a directory selection dialog using Tkinter.
    
    Args:
        prompt (str): Title of the directory selection dialog.
        
    Returns:
        str: Path to the selected directory.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    directory_path = filedialog.askdirectory(title=prompt)
    return directory_path

def process_file(input_file: str, output_directory: str) -> str:
    """
    Process the input file and create an output CSV with selected columns.
    
    The input file is expected to be comma-delimited and contain a header of 5 lines (which are skipped).
    
    Filtering criteria (applied to original file columns):
      - Column 1 (index 0) must be > 108.
      - Column 18 (index 17) must be <= 1.
      
    For rows that pass these filters, the following columns are extracted from the original file:
      - Columns: 1, 2, 9, 10, 14, 15, 16, 18 (1-indexed)
      - Corresponding to Python indices: 0, 1, 8, 9, 13, 14, 15, 17.
    
    No header is written to the output file.
    
    Args:
        input_file (str): Path to the input file.
        output_directory (str): Directory where the output file will be written.
        
    Returns:
        str: Path to the generated output file.
    """
    # Derive output file name based on input file name.
    base_name = os.path.basename(input_file)
    file_name_without_ext = os.path.splitext(base_name)[0]
    output_file = os.path.join(output_directory, file_name_without_ext + "_processed.csv")
    
    with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
        # Skip the first 5 header lines
        for _ in range(5):
            next(infile)
        
        reader = csv.reader(infile, delimiter=',')
        writer = csv.writer(outfile, delimiter=',')
        
        for row in reader:
            # Ensure the row has at least 18 columns.
            if len(row) < 18:
                continue
            
            try:
                # Filter condition: Column 1 (index 0) must be > 108.
                if float(row[0]) <= 108:
                    continue
                # Filter condition: Column 18 (index 17) must be <= 1.
                if float(row[17]) > 1:
                    continue
            except ValueError:
                # Skip rows where conversion fails.
                continue
            
            # Extract columns: 1, 2, 9, 10, 14, 15, 16, 18.
            selected = [row[0], row[1], row[8], row[9], row[13], row[14], row[15], row[17]]
            writer.writerow(selected)
    
    print(f"Processed file saved to: {output_file}")
    return output_file

def main():
    """
    Main function to prompt the user for file and directory selection, then process the file.
    """
    # Prompt user to select the input file.
    input_file = select_file("Select the input file (comma-delimited, with 5 header lines)")
    if not input_file:
        print("No input file selected. Exiting.")
        return
    
    # Prompt user to select the output directory.
    output_directory = select_directory("Select the output directory")
    if not output_directory:
        print("No output directory selected. Exiting.")
        return
    
    # Process the file with the given criteria.
    process_file(input_file, output_directory)

if __name__ == "__main__":
    main()
