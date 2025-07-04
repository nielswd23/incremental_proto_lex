import sys
import os
import ngram_calculator

# # Get threshold and dependency from command line arguments
# if len(sys.argv) != 3:
#     print("Usage: python script.py <threshold> <dependency>")
#     sys.exit(1)

# threshold = sys.argv[1]
# dependency = sys.argv[2]

# # Define all the relevant file locations
# train_dir = f"../SegOut_ngram_format/TP_{dependency}_{threshold}/"
# output_dir = f"../ngramcalc_out/TP_{dependency}_{threshold}/"

# # Make sure output directory exists
# os.makedirs(output_dir, exist_ok=True)

# bigram_contrast = "../TestStimuli/bigram_contrast_stimuli.txt"
# both_contrast = "../TestStimuli/both_contrast_stimuli.txt"
# unigram_contrast = "../TestStimuli/unigram_contrast_stimuli.txt"

# # Loop through all files in the train directory
# for filename in os.listdir(train_dir):
#     train_path = os.path.join(train_dir, filename)
    
#     if os.path.isfile(train_path):
#         base_name = os.path.splitext(filename)[0]

#         ngram_calculator.run(train_path, bigram_contrast, os.path.join(output_dir, f"{base_name}_bigram_contrast.csv"))
#         ngram_calculator.run(train_path, both_contrast, os.path.join(output_dir, f"{base_name}_both_contrast.csv"))
#         ngram_calculator.run(train_path, unigram_contrast, os.path.join(output_dir, f"{base_name}_unigram_contrast.csv"))





train_dir = "../PearlCorpusWordTypes"
output_dir = "../PearlCorpusWordTypes_out"

# Make sure output directory exists
os.makedirs(output_dir, exist_ok=True)

bigram_contrast = "../TestStimuli2/bigram_contrast_stimuli.txt"
both_contrast = "../TestStimuli2/both_contrast_stimuli.txt"
unigram_contrast = "../TestStimuli2/unigram_contrast_stimuli.txt"

# Loop through all files in the train directory
for filename in os.listdir(train_dir):
    train_path = os.path.join(train_dir, filename)
    
    if os.path.isfile(train_path):
        base_name = os.path.splitext(filename)[0]

        ngram_calculator.run(train_path, bigram_contrast, os.path.join(output_dir, f"{base_name}_bigram_contrast.csv"))
        ngram_calculator.run(train_path, both_contrast, os.path.join(output_dir, f"{base_name}_both_contrast.csv"))
        ngram_calculator.run(train_path, unigram_contrast, os.path.join(output_dir, f"{base_name}_unigram_contrast.csv"))