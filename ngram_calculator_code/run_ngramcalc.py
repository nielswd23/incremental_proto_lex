import sys
import os
import ngram_calculator
from concurrent.futures import ProcessPoolExecutor, as_completed

# Input roots
# incremental_root = "../incremental_corpora_out"
incremental_root = "../incremental_corpora_out_v2"
formatted_root = "../formatted_corpora"

# Output root
output_root = "../ScoredLists"

# Test stimuli
bigram_contrast = "../infant_stim_formatted/infant_2c_stimuli_bigram_contrast.txt"
both_contrast   = "../infant_stim_formatted/infant_2b_stimuli_both_contrast.txt"
unigram_contrast= "../infant_stim_formatted/infant_2a_stimuli_unigram_contrast.txt"

# ---------------------------
# Gather tasks for incremental corpora
# ---------------------------
tasks = []

# selected_incremental = ["PearlBrentWords"]

# for seg_type in tasks: # quick way to skip incremental runs
# for seg_type in selected_incremental: # way to run selected corpora
for seg_type in sorted(os.listdir(incremental_root)): # original run for all of the segmentation types in incremental root
    seg_type_path = os.path.join(incremental_root, seg_type)
    if not os.path.isdir(seg_type_path):
        continue

    # for sample_number in sorted(os.listdir(seg_type_path)):
    sample_number = "1.0175"
    train_dir = os.path.join(seg_type_path, sample_number)
    if not os.path.isdir(train_dir):
        continue

    # output_dir = os.path.join(output_root, "incremental", seg_type, sample_number)
    output_dir = os.path.join(output_root, "incremental_v2", seg_type, sample_number)
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(train_dir):
        train_path = os.path.join(train_dir, filename)
        if not os.path.isfile(train_path):
            continue

        base_name = os.path.splitext(filename)[0]

        # Replace the "sample" prefix in base_name with the sample_number
        if base_name.startswith("sample"):
            base_name = base_name.replace("sample", sample_number, 1)

        tasks.append((train_path, bigram_contrast, os.path.join(output_dir, f"{base_name}_bigram_contrast.csv")))
        tasks.append((train_path, both_contrast,   os.path.join(output_dir, f"{base_name}_both_contrast.csv")))
        tasks.append((train_path, unigram_contrast,os.path.join(output_dir, f"{base_name}_unigram_contrast.csv")))


# ---------------------------
# Gather tasks for formatted corpora
# ---------------------------
# quick modification if only wanting to run a few additional folders
selected_corpora = [
    "OLDPearlCorpusUtterances",
    "OLDPearlCorpusWordTypes"
]
selected_corpora = ["OLDTinyInfantLexiconNoNumbers_Prepped"]
selected_corpora = ["TP_btp_absolute", "TP_btp_relative", "TP_ftp_absolute", "TP_ftp_relative", "TP_mi_absolute", "TP_mi_relative"]
selected_corpora = []

# for corpus_name in sorted(os.listdir(formatted_root)): # when running on all of the formatted corpora
for corpus_name in selected_corpora:
    corpus_path = os.path.join(formatted_root, corpus_name)
    if not os.path.isdir(corpus_path):
        continue

    output_dir = os.path.join(output_root, "standard", corpus_name)
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(corpus_path):
        if not filename.endswith(".txt"):
            continue

        train_path = os.path.join(corpus_path, filename)
        if not os.path.isfile(train_path):
            continue

        base_name = os.path.splitext(filename)[0]

        tasks.append((train_path, bigram_contrast, os.path.join(output_dir, f"{base_name}_bigram_contrast.csv")))
        tasks.append((train_path, both_contrast,   os.path.join(output_dir, f"{base_name}_both_contrast.csv")))
        tasks.append((train_path, unigram_contrast,os.path.join(output_dir, f"{base_name}_unigram_contrast.csv")))


print(f"Discovered {len(tasks)} scoring tasks.")


# ---------------------------
# Parallel execution
# ---------------------------
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






# import sys
# import os
# import ngram_calculator
# from concurrent.futures import ProcessPoolExecutor, as_completed
# 
# train_root = "../incremental_corpora_out"
# output_root = "../ScoredLists"
# 
# # Test stimuli
# bigram_contrast = "../InfantTestStimuli/bigram_contrast_stimuli.txt"
# both_contrast = "../InfantTestStimuli/both_contrast_stimuli.txt"
# unigram_contrast = "../InfantTestStimuli/unigram_contrast_stimuli.txt"
# 
# # Gather all tasks for parallelization
# tasks = []
# 
# for seg_type in sorted(os.listdir(train_root)):
    # seg_type_path = os.path.join(train_root, seg_type)
    # if not os.path.isdir(seg_type_path):
        # continue
# 
    # for sample_number in sorted(os.listdir(seg_type_path)):
        # train_dir = os.path.join(seg_type_path, sample_number)
        # if not os.path.isdir(train_dir):
            # continue
# 
        # output_dir = os.path.join(output_root, seg_type, sample_number)
        # os.makedirs(output_dir, exist_ok=True)
# 
        # for filename in os.listdir(train_dir):
            # train_path = os.path.join(train_dir, filename)
            # if not os.path.isfile(train_path):
                # continue
# 
            # base_name = os.path.splitext(filename)[0]
# 
            # tasks.append((train_path, bigram_contrast, os.path.join(output_dir, f"{base_name}_bigram_contrast.csv")))
            # tasks.append((train_path, both_contrast, os.path.join(output_dir, f"{base_name}_both_contrast.csv")))
            # tasks.append((train_path, unigram_contrast, os.path.join(output_dir, f"{base_name}_unigram_contrast.csv")))
# 
# print(f"Discovered {len(tasks)} scoring tasks.")
# 
# # Parallel execution
# def run_task(args):
    # train_path, test_path, out_path = args
    # ngram_calculator.run(train_path, test_path, out_path)
    # return out_path
# 
# with ProcessPoolExecutor() as executor:
    # futures = {executor.submit(run_task, task): task for task in tasks}
# 
    # for future in as_completed(futures):
        # task = futures[future]
        # try:
            # result = future.result()
            # print(f"Done: {result}")
        # except Exception as e:
            # print(f"Error on task {task}: {e}")





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
