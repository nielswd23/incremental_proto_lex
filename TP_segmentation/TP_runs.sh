#!/bin/bash

mkdir ./SegOut/TP_$1_$2

cat ./PearlCorpusFolds/fold_1.txt | wordseg-tp -d $1 -t $2 > ./SegOut/TP_$1_$2/segmented.fold1.$1.$2.txt
cat ./PearlCorpusFolds/fold_2.txt | wordseg-tp -d $1 -t $2 > ./SegOut/TP_$1_$2/segmented.fold2.$1.$2.txt
cat ./PearlCorpusFolds/fold_3.txt | wordseg-tp -d $1 -t $2 > ./SegOut/TP_$1_$2/segmented.fold3.$1.$2.txt
cat ./PearlCorpusFolds/fold_4.txt | wordseg-tp -d $1 -t $2 > ./SegOut/TP_$1_$2/segmented.fold4.$1.$2.txt
cat ./PearlCorpusFolds/fold_5.txt | wordseg-tp -d $1 -t $2 > ./SegOut/TP_$1_$2/segmented.fold5.$1.$2.txt
