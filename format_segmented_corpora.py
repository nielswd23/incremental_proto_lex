import os

def load_segmented_files(main_folder: str):
    """
    Read ./<main_folder>/<1..5>/Model.txt into lists.
    
    Args:
        main_folder: Path to the main folder (e.g., "./AGSimple"). 
    
    Returns:
        dict mapping "<FolderName><k>" -> list of lines (stripped of newlines).
        Example: {"AGSimple1": [...], "AGSimple2": [...], ...}
    """
    file_lists = {}
    base = os.path.basename(os.path.normpath(main_folder))  # e.g., "AGSimple"

    for i in range(1, 6):
        path = os.path.join(main_folder, str(i), "Model.txt")
        key = f"{base}{i}"

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [line.rstrip("\n") for line in f if line.strip() != ""]
        except FileNotFoundError:
            # If a file is missing, store an empty list
            lines = []

        file_lists[key] = lines

    return file_lists


### First we want to check consistency of the segmented output 
##### 1. have the right set of klattbet symbols and 
##### 2. across the seeds we have the same corpus 

def normalize_lines(lines):
    """Remove spaces from each line and return a set."""
    return {"".join(line.split()) for line in lines}


def check_corpora(models, base_name, global_reference):
    """
    Check that all 5 variants contain ^ and x, match each other,
    and also match the global reference corpus.
    
    Args:
        models: dict with variants
        base_name: str, folder name (e.g. "AGSimple")
        global_reference: set, the global normalized reference corpus
    
    Returns:
        dict summary with booleans
    """
    all_keys = [f"{base_name}{i}" for i in range(1, 6)]
    result = {"symbols_ok": True, "local_match": True, "global_match": True}

    # 1. Symbol check
    for key in all_keys:
        lines = models.get(key, [])
        joined = " ".join(lines)
        if "^" not in joined or "x" not in joined:
            print(f"Missing symbols in {key}")
            result["symbols_ok"] = False

    # 2. Local comparison (all 5 match each other)
    corpora_sets = {key: normalize_lines(models.get(key, [])) for key in all_keys}
    reference_local = corpora_sets[all_keys[0]]
    for key, s in corpora_sets.items():
        if s != reference_local:
            print(f"{key} differs from {all_keys[0]} in {base_name}")
            result["local_match"] = False

    # 3. Global comparison (match reference corpus)
    for key, s in corpora_sets.items():
        if s != global_reference:
            print(f"[{base_name}] {key} does not match global reference corpus")
            # Show differences with global_ref
            extra = s - global_reference
            missing = global_reference - s
            if extra:
                print(f"   Extra in {key} (vs global): {list(extra)[:10]}")
            if missing:
                print(f"   Missing from {key} (vs global): {list(missing)[:10]}")
            result["global_match"] = False

    return result

# list of folders to exclude 
special_folders = ["AGGrammars", "TP_Absolute_BTP", "TP_Absolute_FTP", 
                   "TP_Absolute_MI", "TP_Relative_BTP", "TP_Relative_FTP", 
                   "TP_Relative_MI"]



all_corpora_path = "./all_corpora"

# Step 1. Build global reference (from AGSimple1)
agsimple_files = load_segmented_files(os.path.join(all_corpora_path, "AGSimple"))
global_ref = normalize_lines(agsimple_files["AGSimple1"])

# Step 2. Iterate over all folders
summaries = {}
for folder in os.listdir(all_corpora_path):
    full_path = os.path.join(all_corpora_path, folder)
    if not os.path.isdir(full_path):
        continue  # skip non-folders
    if folder in special_folders:
        print(f"Skipping {folder} (special folder)")
        continue

    files = load_segmented_files(full_path)
    summary = check_corpora(files, folder, global_ref)
    summaries[folder] = summary

# Step 3. Print summary table
print("\n=== Summary across corpora ===")
for folder, result in summaries.items():
    print(f"{folder}: {result}")



### Then we format the corpora to run through the ngram calculator 
## (I think I already have code written for this)
