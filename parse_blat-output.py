import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog

def process_psl_file(input_file, output_dir):
    """
    Processes a PSL BLAT output file and generates multiple CSV reports
    based on unique probe-target mappings.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Read PSL file, skipping the first 5 header lines
    with open(input_file, 'r') as infile:
        lines = infile.readlines()[5:]  # PSL files have a 5-line header
    
    # Define PSL column names
    columns = [
        "matches", "misMatches", "repMatches", "nCount", "qNumInsert", "qBaseInsert",
        "tNumInsert", "tBaseInsert", "strand", "qName", "qSize", "qStart", "qEnd",
        "tName", "tSize", "tStart", "tEnd", "blockCount", "blockSizes", "qStarts", "tStarts"
    ]
    df = pd.DataFrame([line.strip().split("\t") for line in lines], columns=columns)
    
    # Convert relevant columns to integers where necessary
    df["blockCount"] = df["blockCount"].astype(int)
    
    # Generate unique target counts per probe
    target_counts = df.groupby("tName")["qName"].nunique().reset_index()
    target_counts.columns = ["Target (Column 14)", "Unique Probes (Column 10)"]
    target_counts.to_csv(os.path.join(output_dir, "Unique_Target_Counts.csv"), index=False, sep=',')
    
    # Generate unique probe counts per target
    probe_counts = df.groupby("qName")["tName"].nunique().reset_index()
    probe_counts.columns = ["Probe (Column 10)", "Unique Targets (Column 14)"]
    probe_counts.to_csv(os.path.join(output_dir, "Unique_Probe_Counts.csv"), index=False, sep=',')
    
    # Create a mapping of probes to targets
    probe_hits = df.groupby("qName")["tName"].apply(lambda x: ", ".join(sorted(set(x)))).reset_index()
    probe_hits.columns = ["Probe (Column 10)", "Target Hits (Column 14)"]
    probe_hits.to_csv(os.path.join(output_dir, "Probe_to_Target_Hits.csv"), index=False, sep=',')
    
    # Create a mapping of targets to probes
    target_hits = df.groupby("tName")["qName"].apply(lambda x: ", ".join(sorted(set(x)))).reset_index()
    target_hits.columns = ["Target (Column 14)", "Probes (Column 10)"]
    target_hits.to_csv(os.path.join(output_dir, "Target_to_Probe_Hits.csv"), index=False, sep=',')
    
    # Identify probes that hit all targets
    all_targets = set(df["tName"].unique())
    probe_target_groups = df.groupby("qName")["tName"].apply(set)
    probes_hitting_all_targets = probe_target_groups[probe_target_groups.apply(lambda x: x == all_targets)].index.tolist()
    probes_hitting_all_targets_df = pd.DataFrame(probes_hitting_all_targets, columns=["Probes Hitting All Targets"])
    probes_hitting_all_targets_df.to_csv(os.path.join(output_dir, "Probes_Hitting_All_Targets.csv"), index=False, sep=',')
    
    print("Processing complete. Files saved in:", output_dir)

def select_file():
    """Opens a file dialog to select the PSL input file."""
    file_path = filedialog.askopenfilename(title="Select PSL File", filetypes=[("PSL Files", "*.psl"), ("All Files", "*.*")])
    entry_file.delete(0, tk.END)
    entry_file.insert(0, file_path)

def select_directory():
    """Opens a file dialog to select the output directory."""
    dir_path = filedialog.askdirectory(title="Select Output Directory")
    entry_dir.delete(0, tk.END)
    entry_dir.insert(0, dir_path)

def run_process():
    """Runs the PSL processing function with user-selected inputs."""
    input_file = entry_file.get()
    output_dir = entry_dir.get()
    if input_file and output_dir:
        process_psl_file(input_file, output_dir)

# GUI Setup
root = tk.Tk()
root.title("BLAT PSL Processor")

# File selection UI
tk.Label(root, text="Select PSL File:").grid(row=0, column=0, padx=5, pady=5)
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_file).grid(row=0, column=2, padx=5, pady=5)

# Directory selection UI
tk.Label(root, text="Select Output Directory:").grid(row=1, column=0, padx=5, pady=5)
entry_dir = tk.Entry(root, width=50)
entry_dir.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_directory).grid(row=1, column=2, padx=5, pady=5)

# Run button
tk.Button(root, text="Run", command=run_process).grid(row=2, column=1, pady=10)

# Start the GUI loop
root.mainloop()
