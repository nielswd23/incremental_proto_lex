import random

def disjoint_random_samples(corpus_size, k, slice_factor, seed=None):
    """
    Randomly selects k disjoint samples of n/slice_factor indices from a corpus.

    :param corpus_size: int, total size of the corpus (n)
    :param k: int, number of samples needed
    :param slice_factor: int, denominator for each sample's size (e.g., 512, 128, etc.)
    :param seed: int or None, random seed for reproducibility
    :return: List[List[int]] -- list of k lists of indices
    """
    if seed is not None:
        random.seed(seed)

    all_indices = list(range(corpus_size))
    random.shuffle(all_indices)

    sample_size = corpus_size // slice_factor
    samples = []
    total_needed = k * sample_size

    if total_needed > corpus_size:
        raise ValueError(
            f"Cannot sample {k} disjoint samples of size {sample_size} from {corpus_size} lines."
        )

    for i in range(k):
        sample = all_indices[i * sample_size : (i + 1) * sample_size]
        samples.append(sample)

    return samples



AGPhonotactic = []
with open("RS1_seg_outputs/AGPhonotactic/Model.txt") as file:
    for line in file:
        AGPhonotactic.append(line.rstrip())

samples_512 = disjoint_random_samples(len(AGPhonotactic), 8, 512, seed=42)
samples_128 = disjoint_random_samples(len(AGPhonotactic), 8, 128, seed=42)
samples_64 = disjoint_random_samples(len(AGPhonotactic), 8, 64, seed=42)
samples_32 = disjoint_random_samples(len(AGPhonotactic), 8, 32, seed=42)
samples_16 = disjoint_random_samples(len(AGPhonotactic), 8, 16, seed=42)
samples_8 = disjoint_random_samples(len(AGPhonotactic), 8, 8, seed=42)
samples_4 = disjoint_random_samples(len(AGPhonotactic), 4, 4, seed=42)
samples_2 = disjoint_random_samples(len(AGPhonotactic), 2, 2, seed=42)




# function that takes in the indices and create variants of the corpora with 
# line[index] left untouched but every other line we strip whitespaces




# when running on other corpora, I'll need to ensure they are all the 
# same length