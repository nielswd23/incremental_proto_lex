AGPhonotactic = []
with open("RS1_seg_outputs/AGPhonotactic/Model.txt") as file:
    for line in file:
        AGPhonotactic.append(line.rstrip())