import os
import pandas as pd

def clean_csvs(input_folder, output_folder):
    # Make sure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop over all CSV files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".csv"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Read CSV
            df = pd.read_csv(input_path)

            # Remove rows where uni_prob == -inf
            df_clean = df[df["uni_prob"] != "-inf"]
            # Also handle actual negative infinity values if stored as float
            df_clean = df_clean[df_clean["uni_prob"] != float("-inf")]

            # Save cleaned CSV
            df_clean.to_csv(output_path, index=False)
            print(f"Cleaned and saved: {output_path}")

# Example usage:
# clean_csvs("./TinyInfantLexiconNoNumbers_Prepped", "./TinyInfantLexicon_cleaned")
# clean_csvs("./top_22", "./top_22_cleaned")
clean_csvs("./ScoredLists/standard/top_22Content", "./ScoredLists/standard/top_22ContentCleaned")
## doesn't output write filename! need to add "Cleaned" to all the ones in that folder 
