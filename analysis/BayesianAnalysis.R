library(tidyverse)
library(tidylog)
library(brms)
library(readxl)
library(bayestestR)
library(tidybayes)
library(viridis)
library(caret)
library(plotrix)

setwd("~/Desktop/incremental_proto_lex/analysis")
options(cmdstanr_write_stan_file_dir = getwd())


# set up functions

### function - bayesian
fit_and_predict_bayesian <- function(train_dataset, seed, gram, model){
  
  
  # if there is more than one value for RS
  if (length(unique(train_dataset$RS)) > 1){
    print("more than one RS value")
    my_bf <- bf(List ~ scale(pos_uni_score_smoothed)*scale(pos_bi_score_smoothed)+(1|RS))
    # my_bf <- bf(List ~ scale(uni_prob)*scale(bi_prob_smoothed)+(1|RS))
    my_priors <- c(
      prior(normal(0, 1), class = "b"),
      prior(normal(0, 2.5), class = "Intercept"),
      prior(exponential(1), class = "sd")
    )
  } else{
    print("only one RS value")
    my_bf <- bf(List ~ scale(pos_uni_score_smoothed)*scale(pos_bi_score_smoothed))
    # my_bf <- bf(List ~ scale(uni_prob)*scale(bi_prob_smoothed))
    my_priors <- c(
      prior(normal(0, 1), class = "b"),
      prior(normal(0, 2.5), class = "Intercept")
    )
  }
  
  print("fitting main model")
  b_model <- brm(my_bf,
                 data = train_dataset,
                 family = bernoulli(),
                 cores =  parallel::detectCores(),
                 chains = 4,
                 warmup = 1000,
                 iter = 2000,
                 prior = my_priors,
                 thin = 1,
                 seed = seed,
                 save_model = paste0("./KFoldModelFits_ngram/",gram,"_prob_",model,"_brmsSeed_",seed,".stan"),
                 file = paste0("./KFoldModelFits_ngram/",gram,"_prob_",model,"_brmsSeed_",seed,"fit"),
                 file_refit = "always",
                 control = list(max_treedepth =10), silent = 0,
                 sample_prior = "yes"
  )
  summary(b_model)
  print("kfolding")
  kf <- kfold(b_model, K=10, save_fits = TRUE, folds = "stratified", group="List", silent = 0, chains = 4, cores = parallel::detectCores(), refresh = 100)
  
  print("kfold predicting")
  kfp <- kfold_predict(kf, re_formula = NULL, method = "posterior_predict")
  
  preds <- kfp$yrep %>%
    as.data.frame() %>%
    rownames_to_column() %>%
    rename(DrawNum = rowname) %>%
    pivot_longer(cols = -DrawNum,
                 names_to = "ItemClassID",
                 values_to = "Predicted")
  
  actuals <- kfp$y %>%
    as.data.frame() %>%
    rownames_to_column() %>%
    rename(ItemClassID = rowname,
           GroundTruth = ".")
  
  t_a <- left_join(preds, actuals) %>%
    mutate(Correct = if_else(Predicted ==GroundTruth, 1,0 ))  %>% 
    #mutate(Correct = if_else(Predicted == GroundTruth, 1,0)) %>%
    group_by(DrawNum) %>%
    summarise(accuracy = sum(Correct)/length(Correct)) %>%
    ungroup() %>%
    select(accuracy) %>%
    median_hdi()
  
  
  print("reading in the null model")
  
  q <- readRDS("./KFoldModelFits_ngram/AccuracyPosteriorForUnigramBaseline_2_2_2025.rds")
  
  o <- left_join(preds, actuals)%>%
    mutate(Correct = if_else(Predicted == GroundTruth, 1,0)) %>%
    group_by(DrawNum) %>%
    summarise(accuracy = sum(Correct)/length(Correct)) %>%
    ungroup() %>%
    select(accuracy) %>%
    overlap(q) %>%
    tibble() %>%
    rename("OverlapWithRandom"=".")
  
  t_b <- left_join(preds, actuals)%>%
    mutate(Correct = if_else(Predicted == GroundTruth, 1,0)) %>%
    group_by(DrawNum) %>%
    summarise(accuracy = sum(Correct)/length(Correct)) %>%
    select(accuracy) %>%
    mutate(is_above_chance = if_else(accuracy > 0.5, 1,0),
           p_above_chance = mean(is_above_chance),
           p_above_random = mean(if_else(accuracy>0.58,1,0))) %>%
    select(p_above_chance,p_above_random) %>%
    distinct()
  
  
  
  m_unigram_prob_gold <- cbind(t_a,t_b,o) %>% # 
    mutate(list = gram,
           model = model)
  
  print("returning results")
  return(m_unigram_prob_gold
  )
}


## readin function ##
# helper function to parse filename 
parse_filename <- function(filename) {
  base <- basename(filename) %>% str_remove("\\.csv$")
  
  # Capture three groups: model, fold, and contrast
  #  - (.*)         = everything up to the last digit before "_"
  #  - ([0-9])      = that last digit (the fold number)
  #  - _(.*_contrast) = the contrast part
  m <- str_match(base, "^(.*)([0-9])_(.*_contrast)$")
  
  model    <- m[2]  # includes digits inside the name
  fold     <- paste0("RS_", m[3])  # fold number
  contrast <- m[4]
  
  list(model = model, fold = fold, contrast = contrast)
}

# readin
read_in_candidate_lexicons <- function(lexicon_file_name){
  parts <- parse_filename(basename(lexicon_file_name))
  
  t <- read.csv(file.path("./ScoredLists/standard", lexicon_file_name),
                stringsAsFactors = FALSE) %>%
    rename(KlattbetAdjustedSpaced = word) %>%
    mutate(
      KlattbetAdjusted = str_remove_all(KlattbetAdjustedSpaced, " "),
      RS      = parts$fold,
      model   = parts$model,
      contrast= parts$contrast
    ) %>%
    tibble()
  
  return(t)
}

## END readin function ##

# get the list of files to iterate through
all_scored_lists <- list.files("../ScoredLists/standard", recursive = TRUE)

unigram_contrast_lists <- all_scored_lists[grepl("unigram_contrast.csv$", all_scored_lists)]
bigram_contrast_lists  <- all_scored_lists[grepl("bigram_contrast.csv$",  all_scored_lists)]
both_contrast_lists    <- all_scored_lists[grepl("both_contrast.csv$",    all_scored_lists)]
seed <- 1

check_list_compliance <- function(all_files) {
  parsed <- map_dfr(all_files, function(f) {
    parts <- parse_filename(f)
    tibble(model = parts$model, fold = parts$fold, contrast = parts$contrast)
  })
  
  # group by model + fold, make sure all 3 contrasts exist
  checks <- parsed %>%
    group_by(model, fold) %>%
    summarise(n_contrasts = n_distinct(contrast), .groups = "drop")
  
  if (any(checks$n_contrasts != 3)) {
    stop("Some model/fold combinations are missing a contrast file!")
  } else {
    print("All models have matching unigram, bigram, and both contrast files for each fold.")
  }
}

check_list_compliance(all_scored_lists)



# get a list of the model names (folder names)
list_of_model_types <- list.dirs("../ScoredLists/standard", recursive = FALSE, full.names = FALSE)



### Running model ###
for (model in list_of_model_types) {
  set.seed(seed)
  print(paste0("working on current model ", model))
  
  # grab this model's files for each contrast
  this_model_unigram_contrast_lists <- all_scored_lists[grepl(paste0("^", model, "[0-9]+_unigram_contrast.csv$"), all_scored_lists)]
  this_model_bigram_contrast_lists  <- all_scored_lists[grepl(paste0("^", model, "[0-9]+_bigram_contrast.csv$"),  all_scored_lists)]
  this_model_both_contrast_lists    <- all_scored_lists[grepl(paste0("^", model, "[0-9]+_both_contrast.csv$"),    all_scored_lists)]
  
  # read in addins
  unigram_contrast_addins <- read.csv("../infant_stim_csvs/infant_2a_stimuli_unigram_contrast.csv", stringsAsFactors = FALSE) %>%
    tibble() %>% mutate(KlattbetAdjusted = Klattbet)
  bigram_contrast_addins  <- read.csv("../infant_stim_csvs/infant_2c_stimuli_bigram_contrast.csv",  stringsAsFactors = FALSE) %>%
    tibble() %>% mutate(KlattbetAdjusted = Klattbet)
  both_contrast_addins    <- read.csv("../infant_stim_csvs/infant_2b_stimuli_both_contrast.csv",  stringsAsFactors = FALSE) %>%
    tibble() %>% mutate(KlattbetAdjusted = Klattbet)
  
  # map across folds
  unigram_contrast_stimuli <- map_dfr(this_model_unigram_contrast_lists, read_in_candidate_lexicons)
  bigram_contrast_stimuli  <- map_dfr(this_model_bigram_contrast_lists,  read_in_candidate_lexicons)
  both_contrast_stimuli    <- map_dfr(this_model_both_contrast_lists,    read_in_candidate_lexicons)
  
  # joins
  unigram_contrast_joined <- left_join(unigram_contrast_addins, unigram_contrast_stimuli, by = "KlattbetAdjusted")
  bigram_contrast_joined  <- left_join(bigram_contrast_addins,  bigram_contrast_stimuli,  by = "KlattbetAdjusted")
  both_contrast_joined    <- left_join(both_contrast_addins,    both_contrast_stimuli,    by = "KlattbetAdjusted")
  
  # fit models
  unigram_results <- fit_and_predict_bayesian(unigram_contrast_joined, seed, "unigram_contrast", model)
  bigram_results  <- fit_and_predict_bayesian(bigram_contrast_joined,  seed, "bigram_contrast",  model)
  both_results    <- fit_and_predict_bayesian(both_contrast_joined,    seed, "both_contrast",    model)
  
  res <- rbind(unigram_results, bigram_results, both_results)
  print(res)
  
  write_csv(res, paste0("./Results_ngram/", model, "_auto_kfold.csv"))
}
