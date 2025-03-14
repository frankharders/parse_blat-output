#!/usr/bin/env python3
import csv
import os
import matplotlib.pyplot as plt
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
        filetypes=[("TSV Files", "*.tsv"), ("All Files", "*.*")]
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

def tsv_to_gff(tsv_path: str, output_directory: str) -> str:
    """
    Convert a TSV stats report into a GFF3 file.

    The TSV file is expected to have a header with these columns:
      - chrom: Chromosome or sequence identifier.
      - target: Region coordinates in the format "start-end" OR an identifier.
      - bases_1X: Numeric coverage (if >=1, region is marked in blue).
      - Optionally, 'start' and 'end' columns for region coordinates if target does not include a hyphen.

    For each row, if the target contains a hyphen, the region is defined by parsing it.
    Otherwise, the script attempts to use the 'start' and 'end' columns.
    If the coverage (bases_1X) is at least 1, a blue color attribute (0,0,255) is added.

    Args:
        tsv_path (str): Path to the input TSV file.
        output_directory (str): Directory where the output GFF file will be written.

    Returns:
        str: Path to the generated GFF file.
    """
    base_name = os.path.basename(tsv_path)
    file_name_without_ext = os.path.splitext(base_name)[0]
    gff_path = os.path.join(output_directory, file_name_without_ext + ".gff")
    
    with open(tsv_path, 'r') as infile, open(gff_path, 'w') as outfile:
        reader = csv.DictReader(infile, delimiter='\t')
        # Write the GFF header.
        outfile.write("##gff-version 3\n")
        
        for row in reader:
            # Use 'chrom' as the sequence ID.
            seqid = row.get('chrom', 'chrUnknown')
            target = row.get('target', '')
            if target and '-' in target:
                try:
                    # Split only on the first hyphen in case there are extra hyphens.
                    start_str, end_str = target.split('-', 1)
                    start = start_str.strip()
                    end = end_str.strip()
                except Exception as e:
                    print(f"Error parsing target '{target}': {e}")
                    start = row.get('start', '')
                    end = row.get('end', '')
            else:
                # If target doesn't contain a hyphen, try to use fallback columns.
                start = row.get('start', '')
                end = row.get('end', '')
                if not start or not end:
                    print(f"Skipping row with target '{target}' due to missing region coordinates.")
                    continue

            feature = 'region'
            source = 'EHDV'
            score = '.'
            strand = '.'
            phase = '.'
            
            # Get the coverage from the bases_1X column.
            bases_1X = row.get('bases_1X', '0')
            try:
                coverage = int(bases_1X)
            except ValueError:
                coverage = 0
            
            # If coverage is at least 1, mark the feature with blue color.
            if coverage >= 1:
                attributes = f"ID={feature}_{start};Name={feature};color=0,0,255"
            else:
                attributes = f"ID={feature}_{start};Name={feature}"
            
            # Write a GFF line.
            gff_line = f"{seqid}\t{source}\t{feature}\t{start}\t{end}\t{score}\t{strand}\t{phase}\t{attributes}\n"
            outfile.write(gff_line)
    
    print(f"GFF file created: {gff_path}")
    return gff_path

def visualize_gff(gff_path: str, output_directory: str) -> str:
    """
    Generate a simple visualization of the features in the GFF file using matplotlib.

    The function groups features by chromosome and draws each feature as a horizontal line.
    It extracts the color attribute (if provided) from the GFF file. For example, if the 
    attribute contains 'color=0,0,255', the feature will be drawn in blue.

    Args:
        gff_path (str): Path to the GFF file.
        output_directory (str): Directory where the output image will be saved.

    Returns:
        str: Path to the saved visualization image.
    """
    features_data = []  # list of tuples: (seqid, start, end, type_feature, color)
    
    # Read the GFF file and extract feature information.
    with open(gff_path, 'r') as infile:
        for line in infile:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) < 9:
                continue
            seqid, source, type_feature, start, end, score, strand, phase, attributes = parts
            try:
                start_int = int(start)
                end_int = int(end)
            except ValueError:
                continue
            # Default color.
            color = 'black'
            # Check if attributes include a color specification.
            for attr in attributes.split(';'):
                if attr.startswith("color="):
                    color = attr.split("=")[1]
                    break
            features_data.append((seqid, start_int, end_int, type_feature, color))
    
    # Group features by chromosome.
    grouped_features = {}
    for feat in features_data:
        seqid, start_int, end_int, type_feature, color = feat
        grouped_features.setdefault(seqid, []).append((start_int, end_int, type_feature, color))
    
    # Plot the features.
    fig, ax = plt.subplots(figsize=(12, 8))
    y_ticks = []
    y_labels = []
    y = 0
    for chrom in sorted(grouped_features.keys()):
        for (start_int, end_int, type_feature, color) in grouped_features[chrom]:
            ax.hlines(y, start_int, end_int, colors=color, linewidth=5)
        y_ticks.append(y)
        y_labels.append(chrom)
        y += 1
    
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Genomic Position")
    ax.set_title("GFF Features Visualization")
    plt.tight_layout()
    
    base_name = os.path.basename(gff_path)
    file_name_without_ext = os.path.splitext(base_name)[0]
    image_path = os.path.join(output_directory, file_name_without_ext + "_visualization.png")
    plt.savefig(image_path)
    plt.show()
    print(f"Visualization saved to {image_path}")
    return image_path

def main():
    """
    Main function to drive the conversion and visualization.

    The user is prompted via dialogs to select the input TSV file and the output folder.
    """
    # Prompt user to select the TSV file.
    tsv_file = select_file("Select the TSV file for conversion")
    if not tsv_file:
        print("No TSV file selected. Exiting.")
        return
    
    # Prompt user to select the output directory.
    output_directory = select_directory("Select the output directory")
    if not output_directory:
        print("No output directory selected. Exiting.")
        return
    
    # Convert the TSV file to a GFF file.
    gff_file = tsv_to_gff(tsv_file, output_directory)
    
    # Create a visual output from the generated GFF file.
    visualize_gff(gff_file, output_directory)

if __name__ == "__main__":
    main()
