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

    print(base)

    for i in range(1, 6):
        path = os.path.join(main_folder, str(i), "Model.txt")
        key = f"{base}{i}"

        try:
            print(path)
            with open(path, "r", encoding="utf-8") as f:
                lines = [line.rstrip("\n") for line in f]
        except FileNotFoundError:
            # If a file is missing, store an empty list (or raise, if you prefer)
            lines = []
            # To be stricter, replace the two lines above with: `raise`

        file_lists[key] = lines

    return file_lists


files = load_segmented_files("./all_corpora/AGSimple")

### First we want to check consistency of the segmented output 
##### e.g., have the right set of klattbet symbols and across the seeds we have the same corpus 

### Then we format the corpora to run through the ngram calculator 
