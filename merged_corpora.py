import os

src_root = "formatted_corpora"
dst_root = "formatted_corpora_merged"

# Create destination root directory if it doesn't exist
os.makedirs(dst_root, exist_ok=True)

for model_name in os.listdir(src_root):
    model_path = os.path.join(src_root, model_name)

    # Skip non-directories
    if not os.path.isdir(model_path):
        continue

    # Create corresponding model folder in the merged directory
    dst_model_path = os.path.join(dst_root, model_name)
    os.makedirs(dst_model_path, exist_ok=True)

    # Loop through each txt file in the model directory
    for fname in os.listdir(model_path):
        if not fname.endswith(".txt"):
            continue

        src_file = os.path.join(model_path, fname)
        dst_file = os.path.join(dst_model_path, fname)

        # Read, transform, and deduplicate lines
        seen = set()
        merged_words = []
        with open(src_file, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip().replace("x", "^")
                if word and word not in seen:
                    seen.add(word)
                    merged_words.append(word)

        # Write the transformed file
        with open(dst_file, "w", encoding="utf-8") as out:
            out.write("\n".join(merged_words))

        print(f"Processed: {src_file} -> {dst_file}")

print("\n All files processed. Merged corpus saved in 'formatted_corpora_merged/'")
