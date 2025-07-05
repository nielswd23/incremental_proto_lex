import sys
import os
import ngram_calculator
from concurrent.futures import ProcessPoolExecutor, as_completed

train_root = "../incremental_corpora_out"
output_root = "../ScoredLists"

# Test stimuli
bigram_contrast = "../InfantTestStimuli/bigram_contrast_stimuli.txt"
both_contrast = "../InfantTestStimuli/both_contrast_stimuli.txt"
unigram_contrast = "../InfantTestStimuli/unigram_contrast_stimuli.txt"

# Gather all tasks for parallelization 
tasks = []

for seg_type in sorted(os.listdir(train_root)):
    seg_type_path = os.path.join(train_root, seg_type)
    if not os.path.isdir(seg_type_path):
        continue

    for sample_number in sorted(os.listdir(seg_type_path)):
        train_dir = os.path.join(seg_type_path, sample_number)
        if not os.path.isdir(train_dir):
            continue

        output_dir = os.path.join(output_root, seg_type, sample_number)
        os.makedirs(output_dir, exist_ok=True)

        for filename in os.listdir(train_dir):
            train_path = os.path.join(train_dir, filename)
            if not os.path.isfile(train_path):
                continue

            base_name = os.path.splitext(filename)[0]

            tasks.append((train_path, bigram_contrast, os.path.join(output_dir, f"{base_name}_bigram_contrast.csv")))
            tasks.append((train_path, both_contrast, os.path.join(output_dir, f"{base_name}_both_contrast.csv")))
            tasks.append((train_path, unigram_contrast, os.path.join(output_dir, f"{base_name}_unigram_contrast.csv")))

print(f"Discovered {len(tasks)} scoring tasks.")

# Parallel execution
def run_task(args):
    train_path, test_path, out_path = args
    ngram_calculator.run(train_path, test_path, out_path)
    return out_path

with ProcessPoolExecutor() as executor:
    futures = {executor.submit(run_task, task): task for task in tasks}

    for future in as_completed(futures):
        task = futures[future]
        try:
            result = future.result()
            print(f"Done: {result}")
        except Exception as e:
            print(f"Error on task {task}: {e}")





### non parallel run ###
# # Loop through all segmentation types
# for seg_type in sorted(os.listdir(train_root)):
#     print(f"Scoring {seg_type}")
#     seg_type_path = os.path.join(train_root, seg_type)
#     if not os.path.isdir(seg_type_path):
#         continue

#     # Loop through all sample numbers (e.g., 0, 1, ..., 7)
#     for sample_number in sorted(os.listdir(seg_type_path)):
#         train_dir = os.path.join(seg_type_path, sample_number)
#         if not os.path.isdir(train_dir):
#             continue

#         output_dir = os.path.join(output_root, seg_type, sample_number)
#         os.makedirs(output_dir, exist_ok=True)

#         print(f"Scoring: {seg_type} / Sample {sample_number}")

#         # Loop through all training files
#         for filename in os.listdir(train_dir):
#             train_path = os.path.join(train_dir, filename)
#             if not os.path.isfile(train_path):
#                 continue

#             base_name = os.path.splitext(filename)[0]

#             ngram_calculator.run(train_path, bigram_contrast, os.path.join(output_dir, f"{base_name}_bigram_contrast.csv"))
#             ngram_calculator.run(train_path, both_contrast, os.path.join(output_dir, f"{base_name}_both_contrast.csv"))
#             ngram_calculator.run(train_path, unigram_contrast, os.path.join(output_dir, f"{base_name}_unigram_contrast.csv"))