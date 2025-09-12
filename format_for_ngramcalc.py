import os

def process_corpus(corpus):
    """
    Split each line into words, then:
    - Add each unique word only once
    - Format by inserting spaces between every character
    """
    processed_corpus = []
    seen = set()  # faster than checking "if ... not in list"
    for line in corpus:
        words = line.split()
        for word in words:
            formatted = ' '.join(word)
            if formatted not in seen:
                seen.add(formatted)
                processed_corpus.append(formatted)
    return processed_corpus


def load_segmented_files(main_folder: str):
    """
    Read ./<main_folder>/<1..5>/Model.txt into lists.
    Returns dict mapping "<FolderName><k>" -> list of lines.
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
            lines = []  # skip if missing

        file_lists[key] = lines

    return file_lists


# -------------------------
# Main driver
# -------------------------
def format_and_save_all(all_corpora_path="./all_corpora",
                        formatted_path="./formatted_corpora",
                        special_folders=None):
    if special_folders is None:
        special_folders = []

    for folder in os.listdir(all_corpora_path):
        full_path = os.path.join(all_corpora_path, folder)
        if not os.path.isdir(full_path):
            continue
        if folder in special_folders:
            print(f"Skipping {folder} (special folder)")
            continue

        print(f"Processing {folder}...")
        files = load_segmented_files(full_path)

        # Make output dir
        out_dir = os.path.join(formatted_path, folder)
        os.makedirs(out_dir, exist_ok=True)

        for key, corpus in files.items():
            processed = process_corpus(corpus)
            out_file = os.path.join(out_dir, f"{key}.txt")
            with open(out_file, "w", encoding="utf-8") as f:
                f.write("\n".join(processed))
            print(f"  Saved {out_file}")


if __name__ == "__main__":
    special_folders = ["AGGrammars", "TP_Absolute_BTP", "TP_Absolute_FTP", 
                       "TP_Absolute_MI", "TP_Relative_BTP", "TP_Relative_FTP", 
                       "TP_Relative_MI"]
    format_and_save_all("./all_corpora", "./formatted_corpora", special_folders)
