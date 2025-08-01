# ~/research/WordSegmentation/MaxEntWordSeg/Makefile
#
#  Mark Johnson, 2nd November 2021
#
# make mews   -- compiles the mews program using Boost program_options in Boost library 
#
# make run-ucla -- runs the model on the UCLA corpus
#
#
#  Morphology models
#
UCLABRENTCORPUS := Training.txt
RESULTSDIR := UCLA-Brent-2020-12-15/

UCLABrentG := 0
UCLABrentW := 1.64
# 1.55 was the original value from Mark. 
UCLABrentX := 0
UCLABrentUnderlying := \"\"
UCLABrentVowels := i I e E @ a c ^ x o U u R Y W O
UCLABrentNasals := m n G

A := 5.0
B := 0
C := 2
D := 0
E := 1e-7
# F := affixes
F := affixesX
# G := 0
G := 4
J := 1e-2
K := 2
L := 1000
P := 1
Q := 1
R := 10
X := 1

# `make run-ucla` does a single run of the model on the UCLA Brent data
#
.PHONY: run-ucla
run-ucla: ucla-brent-feature-weights.csv

ucla-brent-feature-weights.csv: mews $(UCLABRENTCORPUS)
	./brent-data.py $(UCLABRENTCORPUS) | $(EXEC) ./mews -l $(L) -e $(E) -f $(F) -g 0 -j $(J) -k $(K) -a $(A) -b $(B) -c $(C) -d $(D) -w $(UCLABrentW) -u $(UCLABrentUnderlying) -v "$(UCLABrentVowels)" -n "$(UCLABrentNasals)" -p $(P) -q $(Q) -x $(X) -F $@ > ucla-brent-boundaries.txt



############################################################
#                                                          #
#                    Program build                         #
#                                                          #
############################################################


CXXFLAGS := -std=c++11 -O3 
LDFLAGS := -lboost_program_options

SOURCES := mews.cc # program-options.cc
OBJECTS := $(patsubst %.l,%.o,$(patsubst %.c,%.o,$(SOURCES:%.cc=%.o)))

mews: mews.o # program-options.o
	$(CXX) $^ $(LDFLAGS) -o $@


############################################################
#                                                          #
#                    Administrative stuff                  #
#                                                          #
############################################################

.PHONY: 
clean:
	rm -fr *.o *.d *~ core 

.PHONY:
real-clean: clean
	rm -fr $(TARGETS) entity-types

# this command tells GNU make to look for dependencies in *.d files
-include $(patsubst %.l,%.d,$(patsubst %.c,%.d,$(SOURCES:%.cc=%.d)))
