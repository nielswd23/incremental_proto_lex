import os
import pandas as pd
import numpy as np
from pathlib import Path

def get_file_length(file_path):
    """
    Calculates the length of a file. 
    Current metric: Number of lines.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        # returns the number of lines in the file
        return sum(1 for _ in f)

def analyze_protolex_structure(root_path):
    # Dictionary to store raw data: data[condition][model] = [list of lengths]
    data_map = {}
    
    # Get all model folders
    root = Path(root_path)
    model_folders = [f for f in root.iterdir() if f.is_dir()]

    for model_dir in model_folders:
        model_name = model_dir.name
        
        # Get all condition folders within this model
        condition_folders = [f for f in model_dir.iterdir() if f.is_dir()]
        
        for cond_dir in condition_folders:
            cond_name = cond_dir.name
            
            # Initialize dict structure if not exists
            if cond_name not in data_map:
                data_map[cond_name] = {}
            
            # Get all .txt files in this condition
            txt_files = list(cond_dir.glob("*.txt"))
            
            lengths = []
            for txt_file in txt_files:
                try:
                    length = get_file_length(txt_file)
                    lengths.append(length)
                except Exception as e:
                    print(f"Error reading {txt_file}: {e}")
            
            # Store the list of lengths for this model/condition pair
            data_map[cond_name][model_name] = lengths

    # --- Construct the DataFrame ---
    
    # We want Rows = Conditions, Cols = Models
    rows_list = []
    
    for cond, models_data in data_map.items():
        row = {'Condition': cond}
        
        for model, values in models_data.items():
            if values:
                avg = np.mean(values)
                std = np.std(values)
                # Format: "Mean ± Std" (e.g., 120.5 (5.2))
                row[model] = f"{avg:.2f} ({std:.2f})"
            else:
                row[model] = "No Data"
        
        rows_list.append(row)

    # Create DataFrame and set Condition as index
    df = pd.DataFrame(rows_list)
    if not df.empty:
        df = df.set_index('Condition')
        
        # Sort index and columns for cleaner look (optional)
        df = df.sort_index().sort_index(axis=1)
    
    return df

# --- Execution ---
target_directory = "./incremental_corpora_out_v2" 

try:
    df_results = analyze_protolex_structure(target_directory)
    
    print("\n--- Analysis Results (Mean (Std Dev)) ---")
    print(df_results)
    
    # Save to CSV
    df_results.to_csv("protolex_stats.csv")
    
except Exception as e:
    print(f"An error occurred: {e}")
