import os
import random

def create_folds(input_file, output_dir, n_folds=5, seed=42):
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    # Read lines, remove spaces, then add a space between every character
    with open(input_file, "r", encoding="utf-8") as f:
        lines = []
        for line in f:
            stripped = line.strip().replace(" ", "")
            if stripped:  # skip empty lines
                spaced = " ".join(list(stripped))
                lines.append(spaced)

    # Shuffle to randomize order before splitting
    random.shuffle(lines)

    # Split into folds
    fold_size = len(lines) // n_folds
    folds = [lines[i*fold_size : (i+1)*fold_size] for i in range(n_folds)]

    # Add any leftover lines to the last fold
    remainder = len(lines) % n_folds
    if remainder:
        folds[-1].extend(lines[-remainder:])

    # Write 5 training files (each leaves out one fold)
    for i in range(n_folds):
        train_data = [ln for j, fold in enumerate(folds) if j != i for ln in fold]
        out_path = os.path.join(output_dir, f"fold{i+1}_train.txt")
        with open(out_path, "w", encoding="utf-8") as out:
            out.write("\n".join(train_data))
        print(f"Saved {out_path} ({len(train_data)} lines)")

# Example usage:
create_folds("PearlBrent_HumanReadable.txt", "output_folds")
