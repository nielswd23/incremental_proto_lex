import random
import re
import os
import math 

# def disjoint_random_samples(corpus_size, k, slice_factor, seed=None):
#     """
#     Randomly selects k disjoint samples of n/slice_factor indices from a corpus.

#     :param corpus_size: int, total size of the corpus (n)
#     :param k: int, number of samples needed
#     :param slice_factor: int, denominator for each sample's size (e.g., 512, 128, etc.)
#     :param seed: int or None, random seed for reproducibility
#     :return: List[List[int]] -- list of k lists of indices
#     """
#     if seed is not None:
#         random.seed(seed)

#     all_indices = list(range(corpus_size))
#     random.shuffle(all_indices)

#     sample_size = corpus_size // slice_factor
#     samples = []
#     total_needed = k * sample_size

#     if total_needed > corpus_size:
#         raise ValueError(
#             f"Cannot sample {k} disjoint samples of size {sample_size} from {corpus_size} lines."
#         )

#     for i in range(k):
#         sample = all_indices[i * sample_size : (i + 1) * sample_size]
#         samples.append(sample)

#     return samples

## version 2. no longer requires disjoint set across samples. This allows for
## fractional slice facros such as 1.5 to extend the set of unsegmented lines
## beyond just 1/2 of the corpus
def disjoint_random_samples(corpus_size, k, slice_factor, seed=None):
    """
    Return k samples of size floor(n / slice_factor) indices from a corpus of size n.
    - slice_factor can be float (> 1.0). E.g., 1.5 => samples of ~2/3 of the corpus.
    - Disjointness is enforced *within each split*.
    - If k * sample_size > n, the function performs multiple independent splits,
      reshuffling each time, until k samples are produced.

    :param corpus_size: int, total size of the corpus (n)
    :param k: int, number of samples requested
    :param slice_factor: float (>1), denominator for each sample's size
    :param seed: int or None, random seed for reproducibility
    :return: List[List[int]] -- k lists of indices
    """
    if corpus_size <= 0:
        raise ValueError("corpus_size must be positive.")
    try:
        sf = float(slice_factor)
    except Exception as e:
        raise TypeError("slice_factor must be a number.") from e
    if sf <= 1.0:
        raise ValueError("slice_factor must be > 1.0 (each sample must be a proper fraction of the corpus).")

    # sample_size = floor(n / slice_factor); ensure at least 1
    sample_size_float = corpus_size / sf
    sample_size = int(math.floor(sample_size_float))
    if sample_size < 1:
        sample_size = 1

    # Max number of disjoint samples you can pack in a single split
    per_split_capacity = max(1, corpus_size // sample_size)

    rng = random.Random(seed)
    out = []
    while len(out) < k:
        # New split: shuffle the entire index set
        all_indices = list(range(corpus_size))
        rng.shuffle(all_indices)

        # Create up to per_split_capacity disjoint blocks in this split
        take = min(per_split_capacity, k - len(out))
        for j in range(take):
            start = j * sample_size
            end = start + sample_size  # end is safe: per_split_capacity * sample_size <= corpus_size
            out.append(all_indices[start:end])

    return out


# def process_corpus(corpus, indices_segmented):
#     """
#     indices_segmented determine which lines should be left unsegmented.
#     Every other line is segmented and the words are extracted.
#     """
#     processed_corpus = []
#     seen = set()
#     for i, line in enumerate(corpus):
#         if i not in indices_segmented:
#             words = line.split()
#             for word in words:
#                 formatted = ' '.join(word)
#                 if formatted not in seen:
#                     seen.add(formatted)
#                     processed_corpus.append(formatted)
#         else:
#             line_no_whitespace = re.sub(r'\s+', '', line)
#             formatted_line = ' '.join(line_no_whitespace)
#             if formatted_line not in seen:
#                 seen.add(formatted_line)
#                 processed_corpus.append(formatted_line)
#     return processed_corpus

# version of process_corpus() that only includes segmented lines 
def process_corpus(corpus, indices_segmented):
    """
    indices_segmented determine which lines should be left unsegmented.
    Every other line is segmented and the words are extracted.
    """
    processed_corpus = []
    seen = set()
    for i, line in enumerate(corpus):
        if i not in indices_segmented:
            words = line.split()
            for word in words:
                formatted = ' '.join(word)
                if formatted not in seen:
                    seen.add(formatted)
                    processed_corpus.append(formatted)
    return processed_corpus

# -----------------------
# Setup
# -----------------------
input_root = "./all_corpora"
# output_root = "./incremental_corpora_out"
output_root = "./incremental_corpora_out_v2"
# levels = [512, 128, 64, 32, 16, 8, 4, 2]
# samples_per_level = {512: 8, 128: 8, 64: 8, 32: 8, 16: 8, 8: 8, 4: 4, 2: 2}
# levels = [64, 32, 16, 8, 4, 2, 1.75, 1.5, 1.25, 1.1, 1.05, 1.025, 1.02, 1.0175, 1.01625, 1.015, 1.01]
levels = [1.01625]
# samples_per_level = {64: 8, 32: 8, 16: 8, 8: 8, 4: 8, 2: 8, 1.75: 8, 1.5:8, 1.25:8, 1.1:8, 1.05:8, 1.025:8, 1.02:8, 1.0175:8, 1.01625:8, 1.015:8, 1.01:8}
samples_per_level = {1.01625:8}
random_seed = 42

# Explicit list of folders you want to process
target_folders = [
    "AGPhonotactic",
    "AGSimple",
    "AG_Utt-T-X-Seg",
    "AG_Utt-T-X-X-Seg", 
    "AG_Utt-X-T-X-Seg", 
    "AG_Utt-X-T-X-X-Seg", 
    "JPSD_d_1.44", 
    "JPSD_d_1.55", 
    "JPSD_d_1.64", 
    "PUDDLE", 
    "PearlBrentWords"
]

# target_folders = ["PearlBrentWords"]
# target_folders = ["AG_Utt-T-X-Seg"]

# -----------------------
# Step 1. Reference corpus for shared samples
# -----------------------
first_valid = None
for folder in target_folders:
    candidate = os.path.join(input_root, folder, "1", "Model.txt")
    if os.path.isfile(candidate):
        first_valid = candidate
        break

if first_valid is None:
    raise RuntimeError("No reference corpus found in target_folders")

with open(first_valid, "r", encoding="utf-8") as f:
    ref_lines = [line.rstrip() for line in f if line.strip() != ""]

corpus_size = len(ref_lines)

# Generate shared disjoint samples
all_samples_by_level = {
    level: disjoint_random_samples(corpus_size, samples_per_level[level], level, seed=random_seed)
    for level in levels
}


# -----------------------
# Step 2. Process each corpus
# -----------------------
for folder in target_folders:
    model_path = os.path.join(input_root, folder, "1", "Model.txt")
    if not os.path.isfile(model_path):
        print(f"Skipping {folder} (no Model.txt in 1/)")
        continue

    print(f"Processing {folder}")
    with open(model_path, "r", encoding="utf-8") as f:
        corpus = [line.rstrip() for line in f if line.strip() != ""]

    for level in levels:
        level_samples = all_samples_by_level[level]
        for i, indices in enumerate(level_samples):
            processed = process_corpus(corpus, indices)

            output_dir = os.path.join(output_root, folder, str(level))
            os.makedirs(output_dir, exist_ok=True)

            output_path = os.path.join(output_dir, f"sample{i}.txt")
            with open(output_path, "w", encoding="utf-8") as f_out:
                f_out.write("\n".join(processed))

            print(f"  Saved {output_path}")









# import random
# import re
# import os
# 
# def disjoint_random_samples(corpus_size, k, slice_factor, seed=None):
    # """
    # Randomly selects k disjoint samples of n/slice_factor indices from a corpus.
# 
    # :param corpus_size: int, total size of the corpus (n)
    # :param k: int, number of samples needed
    # :param slice_factor: int, denominator for each sample's size (e.g., 512, 128, etc.)
    # :param seed: int or None, random seed for reproducibility
    # :return: List[List[int]] -- list of k lists of indices
    # """
    # if seed is not None:
        # random.seed(seed)
# 
    # all_indices = list(range(corpus_size))
    # random.shuffle(all_indices)
# 
    # sample_size = corpus_size // slice_factor
    # samples = []
    # total_needed = k * sample_size
# 
    # if total_needed > corpus_size:
        # raise ValueError(
            # f"Cannot sample {k} disjoint samples of size {sample_size} from {corpus_size} lines."
        # )
# 
    # for i in range(k):
        # sample = all_indices[i * sample_size : (i + 1) * sample_size]
        # samples.append(sample)
# 
    # return samples
# 
# def process_corpus(corpus, indices_segmented):
    # """
    # indices_segmented determine which lines should be remain segmented with
    # whitespace marking the words in the line.
    # Every other line is unsegmented and treated as a "word".
    # We typize the corpus such that each word is added to the processed_corpus
    # once.
    # Then format for the UCI phonotactic calculator by adding space between
    # each letter.
    # """
    # processed_corpus = []
    # for i, line in enumerate(corpus):
        # if i in indices_segmented:
            # words = line.split(' ')
            # for word in words:
                # formatted = ' '.join(word).replace('x', '^')
                # if formatted not in processed_corpus:
                    # processed_corpus.append(formatted)
        # else:
            # line_no_whitespace = re.sub(r'\s+', '', line)
            # formatted_line = ' '.join(line_no_whitespace).replace('x', '^')
            # if formatted_line not in processed_corpus:
                # processed_corpus.append(formatted_line)
# 
    # return processed_corpus
# 
# 
# # Setup
# input_root = "RS1_seg_outputs"
# output_root = "incremental_corpora_out"
# levels = [512, 128, 64, 32, 16, 8, 4, 2]
# samples_per_level = {512: 8, 128: 8, 64: 8, 32: 8, 16: 8, 8: 8, 4: 4, 2: 2}
# random_seed = 42
# 
# # Load one reference corpus to determine corpus size and generate shared sample indices
# ref_subfolder = sorted(os.listdir(input_root))[1]
# ref_path = os.path.join(input_root, ref_subfolder, "Model.txt")
# 
# with open(ref_path) as f:
    # ref_lines = [line.rstrip() for line in f]
# 
# corpus_size = len(ref_lines)
# 
# # Generate shared samples
# all_samples_by_level = {
    # level: disjoint_random_samples(corpus_size, samples_per_level[level], level, seed=random_seed)
    # for level in levels
# }
# 
# # Process each segmentation algorithm
# for subfolder in sorted(os.listdir(input_root)):
    # print(f"Processing {subfolder}")
    # model_path = os.path.join(input_root, subfolder, "Model.txt")
    # if not os.path.isfile(model_path):
        # continue
# 
    # with open(model_path) as f:
        # corpus = [line.rstrip() for line in f]
# 
    # for level in levels:
        # level_samples = all_samples_by_level[level]
        # for i, indices in enumerate(level_samples):
            # processed = process_corpus(corpus, indices)
# 
            # output_dir = os.path.join(output_root, subfolder, str(level))
            # os.makedirs(output_dir, exist_ok=True)
# 
            # output_path = os.path.join(output_dir, f"sample{i}.txt")
            # with open(output_path, 'w') as f_out:
                # for line in processed:
                    # f_out.write(line + '\n')
# 
# 
# 
# 





# AGPhonotactic = []
# with open("RS1_seg_outputs/AGPhonotactic/Model.txt") as file:
#     for line in file:
#         AGPhonotactic.append(line.rstrip())

# print("corpus loaded in")


# # Output directory
# base_output_dir = "incremental_corpora_out"
# os.makedirs(base_output_dir, exist_ok=True)

# # Levels and samples per level
# levels = [512, 128, 64, 32, 16, 8, 4, 2]
# samples_per_level = {
#     512: 8, 128: 8, 64: 8, 32: 8, 16: 8, 8: 8, 4: 4, 2: 2
# }

# # Generate, process, and write
# for level in levels:
#     k = samples_per_level[level]
#     print(f"Processing level 1/{level} with {k} samples...")
#     samples = disjoint_random_samples(len(AGPhonotactic), k, level, seed=42)
    
#     level_dir = os.path.join(base_output_dir, str(level))
#     os.makedirs(level_dir, exist_ok=True)
    
#     for i, sample_indices in enumerate(samples):
#         processed = process_corpus(AGPhonotactic, sample_indices)
#         output_path = os.path.join(level_dir, f"sample{i}.txt")
#         with open(output_path, 'w') as f_out:
#             for line in processed:
#                 f_out.write(line + '\n')

# print("All files written.")





# samples_512 = disjoint_random_samples(len(AGPhonotactic), 8, 512, seed=42)
# samples_128 = disjoint_random_samples(len(AGPhonotactic), 8, 128, seed=42)
# samples_64 = disjoint_random_samples(len(AGPhonotactic), 8, 64, seed=42)
# samples_32 = disjoint_random_samples(len(AGPhonotactic), 8, 32, seed=42)
# samples_16 = disjoint_random_samples(len(AGPhonotactic), 8, 16, seed=42)
# samples_8 = disjoint_random_samples(len(AGPhonotactic), 8, 8, seed=42)
# samples_4 = disjoint_random_samples(len(AGPhonotactic), 4, 4, seed=42)
# samples_2 = disjoint_random_samples(len(AGPhonotactic), 2, 2, seed=42)




# test = process_corpus(AGPhonotactic, samples_512[0])





# when running on other corpora, I'll need to ensure they are all the 
# same length as a basic check that this is the raw output of segmentation
# algorithm on the exact same corpus 

# also check if the process_corpus() with feeding it all of the indices
# gives us the same typized files I have in SupplementaryMaterials folder
